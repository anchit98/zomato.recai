# Phase 2 Implementation Notes

Phase 2 is implemented in a separate folder: `src/phase2`.

## Implemented Files

- `src/phase2/__init__.py`
- `src/phase2/preferences.py`
- `scripts/run_phase2.py`

## What Phase 2 Covers

- Input contract handling from JSON payload
- Validation and normalization of:
  - `location`
  - `budget`
  - `cuisine`
  - `minimum_rating`
  - `additional_preferences`
- Standardized internal preference object
- Constraint policy for later filtering fallback logic

## Edge Cases Addressed (`docs/edge-cases.md`)

- **EC-08**: Empty request payload handling
- **EC-09**: Unsupported location detection with nearest suggestion
- **EC-10**: Invalid budget values with explicit accepted options
- **EC-11**: Non-numeric/out-of-range minimum rating handling
- **EC-12**: Conflicting preferences detection and relaxation order policy
- **EC-13**: Additional preference sanitization against prompt-injection patterns

## Run Command

Create an input JSON file (example):

```json
{
  "location": "Bengaluru",
  "budget": "affordable",
  "cuisine": "indo chinese",
  "minimum_rating": "4.2",
  "additional_preferences": "family friendly and quick service"
}
```

Run:

```bash
python scripts/run_phase2.py --input-json path/to/input.json --output-json artifacts/phase2/preference_object.json
```

Optional supported locations file:

```bash
python scripts/run_phase2.py --input-json path/to/input.json --locations-json path/to/locations.json --output-json artifacts/phase2/preference_object.json
```

