# Phase 4 Implementation Notes

Phase 4 is implemented in a separate folder: `src/phase4`.

## Implemented Files

- `src/phase4/__init__.py`
- `src/phase4/ranking.py`
- `scripts/run_phase4.py`

## Scope Delivered

- Prompt builder combining user preferences and candidate data
- Groq LLM connector (`https://api.groq.com/openai/v1/chat/completions`)
- JSON output parsing with repair attempt (`extract first JSON object`)
- Post-validation of LLM output against candidate IDs
- Deterministic fallback when LLM fails or key is missing

## Environment Configuration

Create `.env` in repo root:

```env
GROQ_API_KEY=your_key_here
```

The script automatically loads `.env` via `python-dotenv`.

## Edge Cases Covered (`docs/edge-cases.md`)

- **EC-19**: Hallucinated restaurants blocked by candidate ID validation
- **EC-20**: Prompt and deterministic validator keep preferences grounded
- **EC-21**: Explanation length capped to concise output
- **EC-22**: Malformed output handled via JSON extraction + validation + fallback
- **EC-23**: Retry with exponential backoff for transient API errors

## Run Command

```bash
python scripts/run_phase4.py --candidates-json artifacts/phase3/candidates.json --preferences-json artifacts/phase2/preference_object.json --output-json artifacts/phase4/recommendations.json --top-k 5 --candidate-pool-size 10 --model llama-3.3-70b-versatile
```

