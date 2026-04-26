from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.phase1.pipeline import run_phase1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 1 data ingestion and preprocessing pipeline.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/phase1"),
        help="Directory where cleaned data and reports will be written.",
    )
    parser.add_argument(
        "--split",
        type=str,
        default="train",
        help="Dataset split to load from Hugging Face.",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=None,
        help="Optional row limit for local/testing runs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    artifacts = run_phase1(output_dir=args.output_dir, split=args.split, max_rows=args.max_rows)
    print("Phase 1 completed successfully.")
    print(f"Cleaned CSV: {artifacts.cleaned_csv_path}")
    print(f"Cleaned JSON: {artifacts.cleaned_json_path}")
    print(f"Quality Report JSON: {artifacts.quality_report_json_path}")
    print(f"Quality Report Markdown: {artifacts.quality_report_md_path}")
    print(f"Canonical Schema: {artifacts.schema_path}")


if __name__ == "__main__":
    main()

