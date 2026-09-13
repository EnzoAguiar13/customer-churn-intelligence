"""Secure, reproducible acquisition of the selected UCI dataset."""

import argparse
import csv
import hashlib
import io
import json
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Final
from urllib.parse import urlparse
from urllib.request import Request, urlopen

DATASET_NAME: Final[str] = "Iranian Churn"
DATASET_VERSION: Final[str] = "UCI dataset 563"
SOURCE_URL: Final[str] = (
    "https://archive.ics.uci.edu/static/public/563/iranian%2Bchurn%2Bdataset.zip"
)
SOURCE_HOST: Final[str] = "archive.ics.uci.edu"
LICENSE: Final[str] = "CC BY 4.0"
ARCHIVE_FILENAME: Final[str] = "iranian_churn_dataset.zip"
RAW_FILENAME: Final[str] = "iranian_churn.csv"
SOURCE_MEMBER: Final[str] = "Customer Churn.csv"
MAX_ARCHIVE_BYTES: Final[int] = 5 * 1024 * 1024
MAX_RAW_BYTES: Final[int] = 5 * 1024 * 1024


class AcquisitionError(RuntimeError):
    """Raised when external input cannot be acquired safely."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _assert_source_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != SOURCE_HOST:
        raise AcquisitionError(f"untrusted dataset URL: {url}")


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        temporary_path = Path(handle.name)
        handle.write(payload)
    temporary_path.replace(path)


def _download_archive(destination: Path) -> None:
    _assert_source_url(SOURCE_URL)
    request = Request(SOURCE_URL, headers={"User-Agent": "customer-churn-intelligence/0.1"})
    try:
        with urlopen(request, timeout=30) as response:
            status = getattr(response, "status", 200)
            if status != 200:
                raise AcquisitionError(f"dataset source returned HTTP {status}")
            declared_size = response.headers.get("Content-Length")
            if declared_size is not None and int(declared_size) > MAX_ARCHIVE_BYTES:
                raise AcquisitionError("dataset archive exceeds configured size limit")
            chunks: list[bytes] = []
            total = 0
            while chunk := response.read(1024 * 1024):
                total += len(chunk)
                if total > MAX_ARCHIVE_BYTES:
                    raise AcquisitionError("dataset archive exceeds configured size limit")
                chunks.append(chunk)
    except OSError as exc:
        raise AcquisitionError("dataset download failed") from exc
    _atomic_write(destination, b"".join(chunks))


def _extract_csv(archive_path: Path, destination: Path) -> bytes:
    try:
        with zipfile.ZipFile(archive_path) as archive:
            members = archive.namelist()
            candidates = [
                member for member in members if PurePosixPath(member).name == SOURCE_MEMBER
            ]
            if candidates != [SOURCE_MEMBER]:
                raise AcquisitionError("dataset archive has an unexpected file layout")
            info = archive.getinfo(SOURCE_MEMBER)
            if info.file_size > MAX_RAW_BYTES:
                raise AcquisitionError("raw dataset exceeds configured size limit")
            payload = archive.read(info)
    except (OSError, zipfile.BadZipFile, KeyError) as exc:
        raise AcquisitionError("dataset archive is invalid") from exc
    if not payload:
        raise AcquisitionError("raw dataset is empty")
    try:
        header = next(csv.reader(io.StringIO(payload.decode("utf-8"))))
    except (UnicodeDecodeError, StopIteration, csv.Error) as exc:
        raise AcquisitionError("raw dataset is not a valid UTF-8 CSV") from exc
    if not header:
        raise AcquisitionError("raw dataset has no header")
    _atomic_write(destination, payload)
    return payload


def _csv_shape(payload: bytes) -> tuple[int, int]:
    rows = list(csv.reader(io.StringIO(payload.decode("utf-8"))))
    if not rows:
        raise AcquisitionError("raw dataset has no rows")
    return len(rows) - 1, len(rows[0])


def acquire_dataset(data_dir: Path = Path("data")) -> Path:
    """Download and extract the immutable raw CSV, recording its checksums."""

    raw_dir = data_dir / "raw"
    metadata_dir = data_dir / "metadata"
    archive_path = raw_dir / ARCHIVE_FILENAME
    raw_path = raw_dir / RAW_FILENAME
    metadata_path = metadata_dir / "iranian_churn.json"
    metadata: dict[str, object] | None = None
    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    if not archive_path.exists():
        _download_archive(archive_path)
    archive_hash = sha256_file(archive_path)
    if metadata is not None and metadata.get("archive_sha256") != archive_hash:
        raise AcquisitionError("existing archive checksum differs from recorded metadata")

    if raw_path.exists():
        raw_payload = raw_path.read_bytes()
    else:
        raw_payload = _extract_csv(archive_path, raw_path)
    raw_hash = sha256_file(raw_path)
    if metadata is not None and metadata.get("raw_sha256") != raw_hash:
        raise AcquisitionError("existing raw CSV checksum differs from recorded metadata")

    if metadata is None:
        row_count, column_count = _csv_shape(raw_payload)
        metadata = {
            "dataset_name": DATASET_NAME,
            "dataset_version": DATASET_VERSION,
            "source_url": SOURCE_URL,
            "provider": "UCI Machine Learning Repository",
            "license": LICENSE,
            "retrieved_at": datetime.now(UTC).isoformat(),
            "archive_filename": ARCHIVE_FILENAME,
            "archive_sha256": archive_hash,
            "raw_filename": RAW_FILENAME,
            "raw_sha256": raw_hash,
            "row_count": row_count,
            "column_count": column_count,
        }
        _atomic_write(metadata_path, json.dumps(metadata, indent=2).encode("utf-8"))
    return raw_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Download the documented UCI churn dataset")
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()
    path = acquire_dataset(args.data_dir)
    print(f"Acquired {path}")


if __name__ == "__main__":
    main()
