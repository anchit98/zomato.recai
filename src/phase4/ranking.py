from __future__ import annotations

import json
import os
import random
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.3-70b-versatile"
DEFAULT_TOP_K = 5
DEFAULT_CANDIDATE_POOL = 10
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_MAX_RETRIES = 3

SYSTEM_PROMPT = """You are a knowledgeable, friendly local foodie and restaurant scout for Zomato REC.AI.
Your job is to review a list of candidate restaurants and select the best ones based on the user's exact cravings, budget, and location.
Write explanations that sound incredibly natural, human-like, and conversational—like a friend recommending a great spot.
Return ONLY valid JSON with a "recommendations" array."""

RANKING_PROMPT_TEMPLATE = """
User Preferences:
Location: {location}
Budget (Max INR): {budget}
Cuisine/Tags: {cuisine}
Additional Vibes/Dietary: {additional}

Candidates:
{candidates}

Select the top {top_k} restaurants that best match the preferences. For each, provide a "candidate_id", a "rank" (1 to {top_k}), and a conversational 1-2 sentence "explanation". 

Guidelines for the "explanation":
- Sound like a local foodie friend (e.g., "This is a fantastic spot if you're craving...", "I highly recommend this place for its...").
- Be reasonable and practical. Mention how it perfectly fits their budget, rating, or specific cuisine preference.
- Avoid sounding robotic, overly formal, or using buzzwords. Keep it natural, casual, and highly personalized to their prompt.

Return ONLY JSON:
{{
  "recommendations": [
    {{"candidate_id": "...", "rank": 1, "explanation": "..."}}
  ]
}}
"""


@dataclass
class Phase4Result:
    status: str
    model: str
    used_llm: bool
    warnings: list[str]
    input_constraints: dict[str, Any]
    recommendations: list[dict[str, Any]]
    meta: dict[str, Any]
    usage: Optional[dict[str, Any]] = None

    def to_json(self) -> str:
        return json.dumps(
            {
                "status": self.status,
                "model": self.model,
                "used_llm": self.used_llm,
                "warnings": self.warnings,
                "input_constraints": self.input_constraints,
                "recommendations": self.recommendations,
                "meta": self.meta,
                "usage": self.usage
            },
            indent=2,
        )


def generate_ranked_recommendations(
    candidates_json_path: Path,
    preference_object_path: Path,
    top_k: int = DEFAULT_TOP_K,
    candidate_pool_size: int = DEFAULT_CANDIDATE_POOL,
    model: str = DEFAULT_MODEL,
) -> Phase4Result:
    load_dotenv()

    candidates_payload = json.loads(candidates_json_path.read_text(encoding="utf-8"))
    preference_payload = json.loads(preference_object_path.read_text(encoding="utf-8"))

    warnings: list[str] = list(candidates_payload.get("warnings", []))

    candidates = list(candidates_payload.get("candidates", []))
    if not candidates:
        raise ValueError("No candidates found in Phase 3 output.")

    top_k_applied = max(1, min(top_k, len(candidates)))
    pool_applied = max(top_k_applied, min(candidate_pool_size, len(candidates)))
    candidate_pool = candidates[:pool_applied]

    indexed_candidates = _build_indexed_candidates(candidate_pool)
    normalized_preferences = preference_payload.get("normalized_preferences", {})
    additional_preferences = normalized_preferences.get("additional_preferences", "")

    input_constraints = {
        "location": normalized_preferences.get("location"),
        "budget": normalized_preferences.get("budget"),
        "cuisine": normalized_preferences.get("cuisine"),
        "minimum_rating": normalized_preferences.get("minimum_rating"),
        "additional_preferences": additional_preferences,
        "top_k_requested": top_k,
        "top_k_applied": top_k_applied,
    }

    llm_used = False
    llm_error = None
    llm_usage = None
    final_recommendations: list[dict[str, Any]]
    groq_api_key = os.getenv("GROQ_API_KEY", "").strip()

    if groq_api_key:
        prompt = _build_prompt(
            indexed_candidates=indexed_candidates,
            preferences=normalized_preferences,
            top_k=top_k_applied,
        )
        try:
            parsed, llm_usage = _rank_with_groq(
                groq_api_key=groq_api_key,
                model=model,
                prompt=prompt,
                timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
                max_retries=DEFAULT_MAX_RETRIES,
            )
            final_recommendations = _validate_and_project_llm_output(
                parsed_output=parsed,
                indexed_candidates=indexed_candidates,
                top_k=top_k_applied,
            )
            llm_used = True
        except Exception as exc:  # noqa: BLE001
            llm_error = str(exc)
            warnings.append(
                f"LLM path failed; using deterministic fallback. Reason: {llm_error}"
            )
            final_recommendations = _deterministic_fallback(
                indexed_candidates=indexed_candidates,
                preferences=normalized_preferences,
                top_k=top_k_applied,
            )
    else:
        warnings.append(
            "GROQ_API_KEY is missing. Using deterministic fallback ranking."
        )
        final_recommendations = _deterministic_fallback(
            indexed_candidates=indexed_candidates,
            preferences=normalized_preferences,
            top_k=top_k_applied,
        )

    return Phase4Result(
        status="ok",
        model=model,
        used_llm=llm_used,
        warnings=warnings,
        input_constraints=input_constraints,
        recommendations=final_recommendations,
        usage=llm_usage,
        meta={
            "llm_provider": "groq",
            "llm_error": llm_error,
            "candidate_pool_size": pool_applied,
            "phase3_warnings": candidates_payload.get("warnings", []),
            "phase3_relaxed_constraints": candidates_payload.get("relaxed_constraints", []),
        },
    )


def _build_indexed_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed: list[dict[str, Any]] = []
    for idx, candidate in enumerate(candidates, start=1):
        item = dict(candidate)
        item["candidate_id"] = f"C{idx}"
        indexed.append(item)
    return indexed


def _build_prompt(indexed_candidates: list[dict[str, Any]], preferences: dict[str, Any], top_k: int) -> str:
    candidates_str = ""
    for c in indexed_candidates:
        candidates_str += f"- ID: {c['candidate_id']} | {c['restaurant_name']} | Rating: {c['rating']} | Cuisines: {c['cuisines']} | Cost: {c['estimated_cost_for_two']}\n"
        
    return RANKING_PROMPT_TEMPLATE.format(
        location=preferences.get("location", "Any"),
        budget=preferences.get("budget", "Any"),
        cuisine=preferences.get("cuisine", "Any"),
        additional=preferences.get("additional_preferences", "None"),
        candidates=candidates_str,
        top_k=top_k
    )


def _rank_with_groq(
    groq_api_key: str,
    model: str,
    prompt: str,
    timeout_seconds: int,
    max_retries: int,
) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {"role": "user", "content": prompt},
        ],
    }

    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                GROQ_CHAT_COMPLETIONS_URL,
                headers=headers,
                json=payload,
                timeout=timeout_seconds,
            )

            if response.status_code >= 400:
                if response.status_code in (429, 500, 502, 503, 504) and attempt < max_retries:
                    _backoff_sleep(attempt)
                    continue
                raise RuntimeError(
                    f"LLM HTTP error {response.status_code} | body: {response.text[:300]}"
                )

            body = response.json()
            content = body["choices"][0]["message"]["content"]
            usage = body.get("usage")
            return _parse_json_object(content), usage
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < max_retries:
                _backoff_sleep(attempt)
                continue
            break

    raise RuntimeError(f"Failed to get valid LLM response after retries: {last_error}")


def _parse_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise RuntimeError("Malformed LLM output: no JSON object found")
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise RuntimeError("Malformed LLM output: invalid JSON") from exc


def _validate_and_project_llm_output(
    parsed_output: dict[str, Any],
    indexed_candidates: list[dict[str, Any]],
    top_k: int,
) -> list[dict[str, Any]]:
    recs = parsed_output.get("recommendations")
    if not isinstance(recs, list):
        raise RuntimeError("Malformed LLM output: recommendations must be a list")

    candidate_by_id = {item["candidate_id"]: item for item in indexed_candidates}
    output: list[dict[str, Any]] = []
    used: set[str] = set()

    for raw in recs:
        if not isinstance(raw, dict):
            continue
        candidate_id = str(raw.get("candidate_id", "")).strip()
        if candidate_id not in candidate_by_id or candidate_id in used:
            continue
        rank_value = raw.get("rank", len(output) + 1)
        try:
            rank = int(rank_value)
        except (TypeError, ValueError):
            rank = len(output) + 1
        explanation = str(raw.get("explanation", "")).strip()
        if not explanation:
            explanation = "Selected for overall fit against your stated preferences."
        explanation = _truncate_words(explanation, 28)

        candidate = candidate_by_id[candidate_id]
        output.append(
            {
                "candidate_id": candidate_id,
                "restaurant_name": candidate.get("restaurant_name"),
                "location": candidate.get("location"),
                "cuisines": candidate.get("cuisines"),
                "estimated_cost_for_two": candidate.get("estimated_cost_for_two"),
                "rating": candidate.get("rating"),
                "heuristic_score": candidate.get("heuristic_score") or 0.0,
                "explanation": explanation,
                "reasoning_source": "llm",
                "rank": rank,
            }
        )
        used.add(candidate_id)
        if len(output) >= top_k:
            break

    if len(output) < top_k:
        needed = top_k - len(output)
        leftovers = [item for item in indexed_candidates if item["candidate_id"] not in used]
        output.extend(
            _deterministic_from_candidates(leftovers[:needed], rank_start=len(output) + 1)
        )

    # Stable ordering by rank then heuristic score
    output = sorted(output, key=lambda x: (x["rank"], -float(x.get("heuristic_score") or 0.0)))
    for idx, item in enumerate(output, start=1):
        item["rank"] = idx
    return output[:top_k]


def _deterministic_fallback(
    indexed_candidates: list[dict[str, Any]],
    preferences: dict[str, Any],
    top_k: int,
) -> list[dict[str, Any]]:
    selected = indexed_candidates[:top_k]
    budget = preferences.get("budget")
    cuisine = preferences.get("cuisine")
    min_rating = preferences.get("minimum_rating")

    output: list[dict[str, Any]] = []
    for idx, candidate in enumerate(selected, start=1):
        reasons: list[str] = []
        cuisines_text = str(candidate.get("cuisines", "")).lower()
        if cuisine and str(cuisine).lower() in cuisines_text:
            reasons.append("matches your cuisine preference")
        if min_rating is not None and float(candidate.get("rating", 0)) >= float(min_rating):
            reasons.append("meets your minimum rating")
        if budget:
            reasons.append(f"fits a {budget} budget")
        if not reasons:
            reasons.append("has a strong overall score in your candidate set")
        explanation = "Good match because it " + ", ".join(reasons) + "."

        output.append(
            {
                "candidate_id": candidate.get("candidate_id"),
                "restaurant_name": candidate.get("restaurant_name"),
                "location": candidate.get("location"),
                "cuisines": candidate.get("cuisines"),
                "estimated_cost_for_two": candidate.get("estimated_cost_for_two"),
                "rating": candidate.get("rating"),
                "heuristic_score": candidate.get("heuristic_score") or 0.0,
                "explanation": _truncate_words(explanation, 28),
                "reasoning_source": "deterministic",
                "rank": idx,
            }
        )
    return output


def _deterministic_from_candidates(candidates: list[dict[str, Any]], rank_start: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for offset, candidate in enumerate(candidates):
        rows.append(
            {
                "candidate_id": candidate.get("candidate_id"),
                "restaurant_name": candidate.get("restaurant_name"),
                "location": candidate.get("location"),
                "cuisines": candidate.get("cuisines"),
                "estimated_cost_for_two": candidate.get("estimated_cost_for_two"),
                "rating": candidate.get("rating"),
                "heuristic_score": candidate.get("heuristic_score") or 0.0,
                "explanation": "Selected as a strong deterministic match from the filtered candidate set.",
                "reasoning_source": "deterministic",
                "rank": rank_start + offset,
            }
        )
    return rows


def _truncate_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).rstrip(".,;:") + "."


def _backoff_sleep(attempt: int) -> None:
    base = 2 ** attempt
    jitter = random.uniform(0, 0.5)
    time.sleep(base + jitter)

