"""Generate a reproducible JSON data quality report."""

import argparse
import json
from pathlib import Path

import pandas as pd

from customer_intelligence.data.validation import (
    MAX_CSV_BYTES,
    DataValidationError,
    validate_dataframe,
)


def load_csv(path: Path) -> pd.DataFrame:
    """Load a bounded UTF-8 CSV without modifying its contents."""

    if not path.is_file():
        raise DataValidationError(f"dataset file not found: {path}")
    if path.stat().st_size > MAX_CSV_BYTES:
        raise DataValidationError("dataset file exceeds configured size limit")
    try:
        return pd.read_csv(path, encoding="utf-8")
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as exc:
        raise DataValidationError("dataset CSV could not be parsed safely") from exc


def generate_report(csv_path: Path, output_path: Path) -> bool:
    frame = load_csv(csv_path)
    result = validate_dataframe(frame)
    report = {
        "dataset_file": csv_path.as_posix(),
        "rows": int(frame.shape[0]),
        "columns": int(frame.shape[1]),
        "validation": result.to_dict(),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return result.passed


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the churn dataset quality report")
    parser.add_argument("--csv", type=Path, default=Path("data/raw/iranian_churn.csv"))
    parser.add_argument("--output", type=Path, default=Path("reports/data_quality.json"))
    args = parser.parse_args()
    passed = generate_report(args.csv, args.output)
    print(f"Wrote {args.output} ({'PASS' if passed else 'FAIL'})")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
