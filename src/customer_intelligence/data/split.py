"""Deterministic, target-stratified splits with exact feature-vector grouping."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Final

import pandas as pd

from customer_intelligence.data.features import (
    EXCLUDED_FEATURE_NAMES,
    PREPARED_FEATURE_NAMES,
    prepare_labeled_dataset,
)
from customer_intelligence.data.schema import TARGET_COLUMN

RANDOM_SEED: Final[int] = 42
TRAIN_RATIO: Final[float] = 0.70
VALIDATION_RATIO: Final[float] = 0.15
TEST_RATIO: Final[float] = 0.15


@dataclass(frozen=True)
class DatasetSplit:
    """Prepared train, validation and test frames."""

    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame
    feature_columns: tuple[str, ...]
    target_column: str


@dataclass(frozen=True)
class SplitIntegrity:
    """Machine-readable checks for a generated split."""

    passed: bool
    errors: tuple[str, ...]
    row_counts: dict[str, int]
    target_distribution: dict[str, dict[str, int]]
    overlapping_feature_vectors: int


def _stable_group_order(key: str, seed: int) -> str:
    return hashlib.sha256(f"{seed}:{key}".encode()).hexdigest()


def _allocate_groups(
    groups: list[tuple[str, list[int]]], seed: int, ratios: tuple[float, float, float]
) -> dict[int, str]:
    """Allocate complete groups to approximate the requested cumulative ratios."""

    ordered = sorted(groups, key=lambda item: _stable_group_order(item[0], seed))
    total = sum(len(indices) for _, indices in ordered)
    boundaries = (total * ratios[0], total * (ratios[0] + ratios[1]))
    allocation: dict[int, str] = {}
    split_names = ("train", "validation", "test")
    split_index = 0
    assigned = 0
    for _, indices in ordered:
        if split_index < 2 and assigned > 0 and assigned + len(indices) > boundaries[split_index]:
            split_index += 1
        for index in indices:
            allocation[index] = split_names[split_index]
        assigned += len(indices)
    return allocation


def _group_indices(frame: pd.DataFrame) -> dict[str, list[int]]:
    fingerprints = pd.util.hash_pandas_object(
        frame.loc[:, list(PREPARED_FEATURE_NAMES)], index=False
    )
    groups: dict[str, list[int]] = {}
    for position, fingerprint in enumerate(fingerprints.tolist()):
        groups.setdefault(str(int(fingerprint)), []).append(position)
    return groups


def split_dataset(
    prepared: pd.DataFrame,
    seed: int = RANDOM_SEED,
    train_ratio: float = TRAIN_RATIO,
    validation_ratio: float = VALIDATION_RATIO,
    test_ratio: float = TEST_RATIO,
) -> DatasetSplit:
    """Split by target strata while keeping identical X vectors in one split."""

    ratios = (train_ratio, validation_ratio, test_ratio)
    if any(ratio <= 0 for ratio in ratios) or abs(sum(ratios) - 1.0) > 1e-9:
        raise ValueError("split ratios must be positive and sum to 1")
    expected = set(PREPARED_FEATURE_NAMES) | {TARGET_COLUMN}
    missing = sorted(expected - set(prepared.columns))
    if missing:
        raise ValueError(f"prepared frame is missing columns: {', '.join(missing)}")

    frame = prepared.loc[:, list(PREPARED_FEATURE_NAMES) + [TARGET_COLUMN]].reset_index(drop=True)
    group_map = _group_indices(frame)
    stratified_groups: dict[str, list[tuple[str, list[int]]]] = {"0": [], "1": []}
    for key, indices in group_map.items():
        positives = int(frame.loc[indices, TARGET_COLUMN].sum())
        stratum = "1" if positives * 2 >= len(indices) else "0"
        stratified_groups[stratum].append((key, indices))

    allocation: dict[int, str] = {}
    for label, groups in stratified_groups.items():
        if not groups:
            raise ValueError(f"target stratum {label} has no rows")
        allocation.update(_allocate_groups(groups, seed, ratios))

    split_frames: dict[str, pd.DataFrame] = {}
    for split_name in ("train", "validation", "test"):
        positions = [position for position, name in allocation.items() if name == split_name]
        split_frames[split_name] = frame.iloc[sorted(positions)].reset_index(drop=True)
    return DatasetSplit(
        train=split_frames["train"],
        validation=split_frames["validation"],
        test=split_frames["test"],
        feature_columns=PREPARED_FEATURE_NAMES,
        target_column=TARGET_COLUMN,
    )


def _target_distribution(frame: pd.DataFrame) -> dict[str, int]:
    return {str(key): int(value) for key, value in frame[TARGET_COLUMN].value_counts().items()}


def validate_split_integrity(split: DatasetSplit) -> SplitIntegrity:
    """Verify row preservation, target isolation and no cross-split X duplicates."""

    errors: list[str] = []
    frames = {"train": split.train, "validation": split.validation, "test": split.test}
    expected_columns = list(split.feature_columns) + [split.target_column]
    for name, frame in frames.items():
        if list(frame.columns) != expected_columns:
            errors.append(f"{name}: columns do not match the declared contract")
        if split.target_column in split.feature_columns:
            errors.append("target column is present in feature_columns")
        if set(EXCLUDED_FEATURE_NAMES) & set(frame.columns):
            errors.append(f"{name}: excluded feature leaked into prepared split")

    all_rows = pd.concat(list(frames.values()), ignore_index=True)
    original_fingerprints = _group_indices(all_rows)
    counts_by_split: dict[str, dict[str, int]] = {}
    seen: dict[str, str] = {}
    overlap = 0
    for split_name, frame in frames.items():
        counts_by_split[split_name] = _target_distribution(frame)
        for key in _group_indices(frame):
            previous = seen.get(key)
            if previous is not None and previous != split_name:
                overlap += 1
            seen[key] = split_name
    if sum(len(frame) for frame in frames.values()) != len(all_rows):
        errors.append("split row counts do not sum to the combined frame")
    if len(original_fingerprints) > 0 and sum(
        len(indices) for indices in original_fingerprints.values()
    ) != len(all_rows):
        errors.append("split fingerprint accounting failed")
    if overlap:
        errors.append(f"{overlap} identical feature vectors overlap across splits")

    return SplitIntegrity(
        passed=not errors,
        errors=tuple(errors),
        row_counts={name: len(frame) for name, frame in frames.items()},
        target_distribution=counts_by_split,
        overlapping_feature_vectors=overlap,
    )


def prepare_and_split(
    frame: pd.DataFrame, seed: int = RANDOM_SEED
) -> tuple[pd.DataFrame, DatasetSplit]:
    """Convenience entry point for deterministic preparation followed by splitting."""

    prepared = prepare_labeled_dataset(frame)
    return prepared, split_dataset(prepared, seed=seed)
