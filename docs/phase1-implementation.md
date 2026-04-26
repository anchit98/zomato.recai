# Phase 1 Implementation Notes

Phase 1 has been implemented with a production-oriented preprocessing pipeline.

## Implemented Files

- `src/phase1/pipeline.py`
- `scripts/run_phase1.py`
- `requirements.txt`

## What Phase 1 Covers

- Dataset ingestion from Hugging Face (`ManikaSaini/zomato-restaurant-recommendation`)
- Retry logic with exponential backoff for source unavailability
- Canonical schema mapping with alias support and schema drift detection
- Data normalization:
  - Text normalization for name/location/cuisine
  - Cost parsing to numeric value
  - Rating normalization to 0-5 scale
- Mandatory-field quality gate and fail-fast behavior
- Deterministic deduplication
- Output artifacts:
  - Cleaned CSV
  - Cleaned JSON
  - JSON quality report
  - Markdown quality report
  - Canonical schema JSON

## Run Command

```bash
python scripts/run_phase1.py --output-dir artifacts/phase1
```

Optional test run with smaller sample:

```bash
python scripts/run_phase1.py --output-dir artifacts/phase1 --max-rows 5000
```

## Edge Cases Covered (from `docs/edge-cases.md`)

- EC-01: Source dataset unavailable (retry/backoff)
- EC-02: Schema drift (canonical mapping validation)
- EC-03: Missing critical fields (quality gate + dropping invalid rows)
- EC-04: Duplicate records with conflicting values (deterministic dedup)
- EC-05: Cost format inconsistency (robust parsing)
- EC-06: Rating scale mismatch (normalization to 0-5)
- EC-07: Noisy text fields (normalization)

