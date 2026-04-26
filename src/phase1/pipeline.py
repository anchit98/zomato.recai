from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from datasets import load_dataset

DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"
MAX_RETRIES = 3

MANDATORY_CANONICAL_FIELDS = {
    "restaurant_name",
    "location",
    "cuisines",
    "estimated_cost_for_two",
    "rating",
}

COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "restaurant_name": (
        "restaurant_name",
        "name",
        "restaurant",
        "restaurant title",
        "res_name",
    ),
    "location": ("location", "city", "locality", "address"),
    "cuisines": ("cuisines", "cuisine", "food_type", "food types"),
    "estimated_cost_for_two": (
        "average_cost_for_two",
        "cost_for_two",
        "cost",
        "price",
        "approx_cost(for two people)",
    ),
    "rating": ("rating", "rate", "aggregate_rating", "user_rating"),
}


@dataclass
class PipelineArtifacts:
    cleaned_csv_path: Path
    cleaned_json_path: Path
    quality_report_json_path: Path
    quality_report_md_path: Path
    schema_path: Path


def run_phase1(output_dir: Path, split: str = "train", max_rows: int | None = None) -> PipelineArtifacts:
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_df = _load_dataset_with_retry(DATASET_ID, split=split, max_retries=MAX_RETRIES)
    if max_rows:
        raw_df = raw_df.head(max_rows)

    canonical_df, mapping, unknown_columns = _map_to_canonical_schema(raw_df)
    cleaned_df, metrics = _clean_normalize_and_report(canonical_df, raw_df)

    quality_report = {
        "dataset_id": DATASET_ID,
        "row_counts": {
            "raw_rows": int(len(raw_df)),
            "post_mapping_rows": int(len(canonical_df)),
            "cleaned_rows": int(len(cleaned_df)),
        },
        "schema_mapping": mapping,
        "unknown_source_columns": sorted(unknown_columns),
        "quality_metrics": metrics,
    }

    cleaned_csv_path = output_dir / "zomato_cleaned.csv"
    cleaned_json_path = output_dir / "zomato_cleaned.json"
    quality_report_json_path = output_dir / "phase1_data_quality_report.json"
    quality_report_md_path = output_dir / "phase1_data_quality_report.md"
    schema_path = output_dir / "canonical_schema.json"

    cleaned_df.to_csv(cleaned_csv_path, index=False)
    cleaned_df.to_json(cleaned_json_path, orient="records", indent=2)
    quality_report_json_path.write_text(json.dumps(quality_report, indent=2), encoding="utf-8")
    quality_report_md_path.write_text(_quality_report_markdown(quality_report), encoding="utf-8")
    schema_path.write_text(json.dumps(_canonical_schema_document(), indent=2), encoding="utf-8")

    return PipelineArtifacts(
        cleaned_csv_path=cleaned_csv_path,
        cleaned_json_path=cleaned_json_path,
        quality_report_json_path=quality_report_json_path,
        quality_report_md_path=quality_report_md_path,
        schema_path=schema_path,
    )


def _load_dataset_with_retry(dataset_id: str, split: str, max_retries: int) -> pd.DataFrame:
    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            dataset = load_dataset(dataset_id, split=split)
            return dataset.to_pandas()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt == max_retries:
                break
            sleep_s = 2 ** attempt
            time.sleep(sleep_s)
    raise RuntimeError(f"Unable to load dataset '{dataset_id}' after {max_retries} attempts") from last_error


def _normalize_col_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def _map_to_canonical_schema(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, str], set[str]]:
    source_cols = {col: _normalize_col_name(col) for col in df.columns}
    reverse_lookup = {normalized: original for original, normalized in source_cols.items()}

    mapping: dict[str, str] = {}
    missing_fields: list[str] = []

    for canonical, aliases in COLUMN_ALIASES.items():
        chosen = None
        for alias in aliases:
            alias_key = _normalize_col_name(alias)
            if alias_key in reverse_lookup:
                chosen = reverse_lookup[alias_key]
                break
        if chosen is None:
            missing_fields.append(canonical)
        else:
            mapping[canonical] = chosen

    if missing_fields:
        raise ValueError(
            "Dataset schema mismatch. Missing canonical fields: "
            + ", ".join(sorted(missing_fields))
        )

    canonical_df = pd.DataFrame()
    for canonical_name, source_col in mapping.items():
        canonical_df[canonical_name] = df[source_col]

    unknown_columns = set(df.columns) - set(mapping.values())
    return canonical_df, mapping, unknown_columns


def _normalize_text(value: Any) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    normalized = str(value).strip()
    if not normalized:
        return None
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def _parse_cost(value: Any) -> float | None:
    text = _normalize_text(value)
    if not text:
        return None
    cleaned = re.sub(r"[^\d\-.]", "", text)
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_rating(value: Any) -> float | None:
    text = _normalize_text(value)
    if not text:
        return None
    match = re.search(r"(\d+(\.\d+)?)", text)
    if not match:
        return None
    numeric = float(match.group(1))
    # Normalize possible 0-10 scale to 0-5
    if numeric > 5.0 and numeric <= 10.0:
        numeric = numeric / 2
    # Reject impossible values
    if numeric < 0 or numeric > 5:
        return None
    return round(numeric, 2)


def _clean_normalize_and_report(canonical_df: pd.DataFrame, raw_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    df = canonical_df.copy()
    raw_rows = len(df)

    for col in ("restaurant_name", "location", "cuisines"):
        df[col] = df[col].map(_normalize_text)

    df["estimated_cost_for_two"] = df["estimated_cost_for_two"].map(_parse_cost)
    df["rating"] = df["rating"].map(_parse_rating)

    missing_before_drop = {
        col: int(df[col].isna().sum()) for col in MANDATORY_CANONICAL_FIELDS
    }

    # Drop rows that do not satisfy mandatory fields.
    df = df.dropna(subset=list(MANDATORY_CANONICAL_FIELDS))

    pre_dedup_rows = len(df)
    df["dedup_key"] = (
        df["restaurant_name"].str.lower()
        + "|"
        + df["location"].str.lower()
        + "|"
        + df["cuisines"].str.lower()
    )
    # Keep highest rating and then lowest cost among duplicates.
    df = df.sort_values(by=["rating", "estimated_cost_for_two"], ascending=[False, True])
    df = df.drop_duplicates(subset=["dedup_key"], keep="first").drop(columns=["dedup_key"])

    deduplicated_count = pre_dedup_rows - len(df)
    dropped_for_missing = raw_rows - pre_dedup_rows

    critical_missing_percentage = {
        col: round((count / raw_rows) * 100, 2) if raw_rows else 0.0
        for col, count in missing_before_drop.items()
    }

    quality_gate_failed = any(
        pct > 35.0 for pct in critical_missing_percentage.values()
    )

    metrics: dict[str, Any] = {
        "raw_column_count": int(len(raw_df.columns)),
        "mandatory_missing_counts_before_drop": missing_before_drop,
        "mandatory_missing_percentage_before_drop": critical_missing_percentage,
        "dropped_rows_due_to_missing_mandatory_fields": int(dropped_for_missing),
        "deduplicated_rows": int(deduplicated_count),
        "quality_gate_failed": quality_gate_failed,
        "quality_gate_policy": "Fail if any mandatory field missing percentage exceeds 35%",
    }

    if quality_gate_failed:
        raise ValueError(
            "Data quality gate failed: mandatory field missing percentage exceeded threshold."
        )

    return df.reset_index(drop=True), metrics


def _canonical_schema_document() -> dict[str, Any]:
    return {
        "name": "zomato_restaurant_canonical_schema",
        "version": "1.0.0",
        "mandatory_fields": sorted(MANDATORY_CANONICAL_FIELDS),
        "fields": [
            {
                "name": "restaurant_name",
                "type": "string",
                "description": "Primary restaurant display name",
            },
            {
                "name": "location",
                "type": "string",
                "description": "City/locality normalized for filtering",
            },
            {
                "name": "cuisines",
                "type": "string",
                "description": "Cuisine labels as normalized text",
            },
            {
                "name": "estimated_cost_for_two",
                "type": "number",
                "description": "Approximate cost for two people in normalized numeric form",
            },
            {
                "name": "rating",
                "type": "number",
                "description": "Normalized rating on a 0 to 5 scale",
            },
        ],
    }


def _quality_report_markdown(report: dict[str, Any]) -> str:
    row_counts = report["row_counts"]
    metrics = report["quality_metrics"]
    lines = [
        "# Phase 1 Data Quality Report",
        "",
        f"- Dataset: `{report['dataset_id']}`",
        f"- Raw rows: `{row_counts['raw_rows']}`",
        f"- Rows after mapping: `{row_counts['post_mapping_rows']}`",
        f"- Rows after cleaning: `{row_counts['cleaned_rows']}`",
        "",
        "## Missing Data (Mandatory Fields)",
        "",
    ]
    for key, value in metrics["mandatory_missing_percentage_before_drop"].items():
        lines.append(f"- `{key}`: `{value}%`")

    lines.extend(
        [
            "",
            "## Actions Taken",
            "",
            f"- Dropped rows due to missing mandatory fields: `{metrics['dropped_rows_due_to_missing_mandatory_fields']}`",
            f"- Deduplicated rows removed: `{metrics['deduplicated_rows']}`",
            f"- Quality gate failed: `{metrics['quality_gate_failed']}`",
            f"- Policy: {metrics['quality_gate_policy']}",
            "",
            "## Schema Mapping",
            "",
        ]
    )
    for canonical, source in report["schema_mapping"].items():
        lines.append(f"- `{canonical}` <- `{source}`")
    if report["unknown_source_columns"]:
        lines.extend(["", "## Unmapped Source Columns", ""])
        for col in report["unknown_source_columns"]:
            lines.append(f"- `{col}`")
    return "\n".join(lines) + "\n"
