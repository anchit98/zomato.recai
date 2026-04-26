# Phase 3 Implementation Notes

Phase 3 is implemented in a separate folder: `src/phase3`.

## Implemented Files

- `src/phase3/__init__.py`
- `src/phase3/candidates.py`
- `scripts/run_phase3.py`

## Scope Delivered

- Candidate retrieval from `artifacts/phase1/zomato_cleaned.csv`
- Preference consumption from `artifacts/phase2/preference_object.json`
- Rule-based filtering:
  - location
  - minimum rating
  - budget band
  - cuisine
- Heuristic candidate scoring and ranking
- Top-N selection with token-budget-aware cap
- Diversity control (deduplicate repeated restaurant names)
- Fallback relaxation strategy when strict filters return no results

## Edge Cases Covered (`docs/edge-cases.md`)

- **EC-14**: Zero candidates after hard filters -> stepwise relaxation + degraded fallback
- **EC-15**: Too many candidates for LLM context -> token-budget-aware output cap
- **EC-16**: Popular-chain dominance -> simple diversity control via unique names
- **EC-17**: Ambiguous cuisine tags -> substring cuisine matching
- **EC-18**: Stale cache not applicable yet (no cache layer in this phase)

## Run Command

```bash
python scripts/run_phase3.py --cleaned-data artifacts/phase1/zomato_cleaned.csv --preferences-json artifacts/phase2/preference_object.json --output-json artifacts/phase3/candidates.json --top-n 20 --token-budget 6000
```

