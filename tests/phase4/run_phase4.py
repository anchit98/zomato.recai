from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.phase4.ranking import generate_ranked_recommendations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Phase 4 LLM ranking and explanation generation."
    )
    parser.add_argument(
        "--candidates-json",
        type=Path,
        default=Path("artifacts/phase3/candidates.json"),
        help="Path to Phase 3 candidate output JSON.",
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
        default=Path("artifacts/phase4/recommendations.json"),
        help="Path to write Phase 4 recommendation output JSON.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of final recommendations to return.",
    )
    parser.add_argument(
        "--candidate-pool-size",
        type=int,
        default=10,
        help="Candidate pool size passed to LLM before final top-k selection.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="llama-3.3-70b-versatile",
        help="Groq model name.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = generate_ranked_recommendations(
        candidates_json_path=args.candidates_json,
        preference_object_path=args.preferences_json,
        top_k=args.top_k,
        candidate_pool_size=args.candidate_pool_size,
        model=args.model,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(result.to_json(), encoding="utf-8")

    print("Phase 4 completed.")
    print(f"Output: {args.output_json}")
    print(f"Model: {result.model}")
    print(f"Used LLM: {result.used_llm}")
    print(f"Recommendations returned: {len(result.recommendations)}")
    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    main()

