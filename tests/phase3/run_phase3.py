from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.phase3.candidates import generate_candidates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 3 candidate retrieval and filtering.")
    parser.add_argument(
        "--cleaned-data",
        type=Path,
        default=Path("artifacts/phase1/zomato_cleaned.csv"),
        help="Path to Phase 1 cleaned CSV.",
    )
    parser.add_argument(
        "--preferences-json",
        type=Path,
        default=Path("artifacts/phase2/preference_object.json"),
        help="Path to Phase 2 normalized preference object JSON.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("artifacts/phase3/candidates.json"),
        help="Path to write Phase 3 candidate output JSON.",
    )
    parser.add_argument("--top-n", type=int, default=20, help="Max candidates to return.")
    parser.add_argument("--token-budget", type=int, default=6000, help="Token budget for downstream LLM stage.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = generate_candidates(
        cleaned_data_path=args.cleaned_data,
        preference_object_path=args.preferences_json,
        top_n=args.top_n,
        token_budget=args.token_budget,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(result.to_json(), encoding="utf-8")
    print("Phase 3 completed.")
    print(f"Output: {args.output_json}")
    print(f"Candidates returned: {result.candidates_returned}")
    if result.relaxed_constraints:
        print(f"Relaxed constraints: {', '.join(result.relaxed_constraints)}")


if __name__ == "__main__":
    main()

