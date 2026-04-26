from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.phase2.preferences import build_preference_object_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 2 user preference validation and normalization.")
    parser.add_argument(
        "--input-json",
        type=Path,
        required=True,
        help="Path to JSON file containing user preference payload.",
    )
    parser.add_argument(
        "--locations-json",
        type=Path,
        default=None,
        help="Optional JSON file containing list of supported locations.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("artifacts/phase2/preference_object.json"),
        help="Output file path for normalized preference object.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = json.loads(args.input_json.read_text(encoding="utf-8"))

    known_locations = None
    if args.locations_json and args.locations_json.exists():
        known_locations = set(json.loads(args.locations_json.read_text(encoding="utf-8")))

    output = build_preference_object_json(payload, known_locations=known_locations)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(output, encoding="utf-8")

    print("Phase 2 completed.")
    print(f"Output: {args.output_json}")


if __name__ == "__main__":
    main()

