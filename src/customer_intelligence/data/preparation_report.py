"""Generate the deterministic Phase 5C preparation and split report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from customer_intelligence.data.features import (
    DERIVED_FEATURE_NAMES,
    EXCLUDED_FEATURE_NAMES,
    PREPARED_FEATURE_NAMES,
    prepare_labeled_dataset,
)
from customer_intelligence.data.quality_report import load_csv
from customer_intelligence.data.schema import TARGET_COLUMN
from customer_intelligence.data.split import RANDOM_SEED, split_dataset, validate_split_integrity
from customer_intelligence.data.validation import validate_dataframe

DUPLICATE_POLICY = "KEEP"
CHARGE_AMOUNT_POLICY = "DOCUMENTATION_CONFLICT: accept operational values 0-10; retain raw values"


def generate_preparation_report(csv_path: Path, output_path: Path) -> bool:
    frame = load_csv(csv_path)
    validation = validate_dataframe(frame)
    report: dict[str, object] = {
        "dataset_file": csv_path.as_posix(),
        "rows_before": int(len(frame)),
        "rows_after": 0,
        "features_included": list(PREPARED_FEATURE_NAMES),
        "features_excluded": list(EXCLUDED_FEATURE_NAMES) + [TARGET_COLUMN],
        "derived_features": list(DERIVED_FEATURE_NAMES),
        "duplicate_policy": DUPLICATE_POLICY,
        "charge_amount_policy": CHARGE_AMOUNT_POLICY,
        "random_seed": RANDOM_SEED,
        "validation_status": validation.to_dict(),
        "warnings": list(validation.warnings),
    }
    if not validation.passed:
        report["status"] = "FAIL"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return False

    prepared = prepare_labeled_dataset(frame)
    split = split_dataset(prepared, seed=RANDOM_SEED)
    integrity = validate_split_integrity(split)
    report.update(
        {
            "rows_after": int(len(prepared)),
            "train_rows": len(split.train),
            "validation_rows": len(split.validation),
            "test_rows": len(split.test),
            "target_distribution": {
                "all": {
                    str(key): int(value)
                    for key, value in prepared[TARGET_COLUMN].value_counts().items()
                },
                **integrity.target_distribution,
            },
            "split_integrity": {
                "status": "PASS" if integrity.passed else "FAIL",
                "errors": list(integrity.errors),
                "row_counts": integrity.row_counts,
                "overlapping_feature_vectors": integrity.overlapping_feature_vectors,
            },
            "status": "PASS" if integrity.passed else "FAIL",
        }
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return integrity.passed


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare and split the churn dataset")
    parser.add_argument("--csv", type=Path, default=Path("data/raw/iranian_churn.csv"))
    parser.add_argument("--output", type=Path, default=Path("reports/prepared_data_quality.json"))
    args = parser.parse_args()
    passed = generate_preparation_report(args.csv, args.output)
    print(f"Wrote {args.output} ({'PASS' if passed else 'FAIL'})")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
