from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd



DEFAULT_TOP_N = 20
DEFAULT_TOKEN_BUDGET = 6000
AVG_TOKENS_PER_CANDIDATE = 120


@dataclass
class CandidateResult:
    total_candidates_before_limit: int
    candidates_returned: int
    applied_constraints: dict[str, Any]
    relaxed_constraints: list[str]
    warnings: list[str]
    candidates: list[dict[str, Any]]

    def to_json(self) -> str:
        return json.dumps(
            {
                "total_candidates_before_limit": self.total_candidates_before_limit,
                "candidates_returned": self.candidates_returned,
                "applied_constraints": self.applied_constraints,
                "relaxed_constraints": self.relaxed_constraints,
                "warnings": self.warnings,
                "candidates": self.candidates,
            },
            indent=2,
        )


def generate_candidates(
    cleaned_data_path: Path,
    preference_object_path: Path,
    top_n: int = DEFAULT_TOP_N,
    token_budget: int = DEFAULT_TOKEN_BUDGET,
) -> CandidateResult:
    data = pd.read_csv(cleaned_data_path)
    payload = json.loads(preference_object_path.read_text(encoding="utf-8"))

    if not payload.get("valid"):
        raise ValueError("Preference object is invalid. Run Phase 2 with a valid payload.")

    pref = payload["normalized_preferences"]
    policy = payload.get("constraint_policy", {})
    warnings: list[str] = list(payload.get("warnings", []))

    working = data.copy()
    working["location_norm"] = working["location"].map(_norm)
    working["cuisines_norm"] = working["cuisines"].map(_norm)
    
    # Coerce dirty data to numeric to prevent TypeError during filtering
    working["rating"] = pd.to_numeric(working["rating"], errors="coerce").fillna(0.0)
    working["estimated_cost_for_two"] = pd.to_numeric(working["estimated_cost_for_two"], errors="coerce").fillna(99999.0)

    relaxed_constraints: list[str] = []
    filtered = _filter_with_fallback(working, pref, policy, relaxed_constraints, warnings)

    if filtered.empty:
        # Final degraded fallback (EC-14): return top rated from all data.
        warnings.append("No matches found after fallback. Returning top-rated global options.")
        filtered = working.sort_values(by=["rating", "estimated_cost_for_two"], ascending=[False, True]).head(50)

    scored = _score_candidates(filtered, pref)
    diverse = _enforce_diversity(scored)

    max_by_token = max(1, token_budget // AVG_TOKENS_PER_CANDIDATE)
    final_limit = max(1, min(top_n, max_by_token))
    final = diverse.head(final_limit).copy()

    final["rank"] = range(1, len(final) + 1)

    output_cols = [
        "rank",
        "restaurant_name",
        "location",
        "cuisines",
        "estimated_cost_for_two",
        "rating",
        "heuristic_score",
        "match_reasons",
    ]
    candidates = final[output_cols].to_dict(orient="records")

    applied_constraints = {
        "location": pref.get("location"),
        "minimum_rating": pref.get("minimum_rating"),
        "budget": pref.get("budget"),
        "cuisine": pref.get("cuisine"),
        "token_budget": token_budget,
        "top_n_requested": top_n,
        "top_n_applied": final_limit,
    }

    return CandidateResult(
        total_candidates_before_limit=int(len(diverse)),
        candidates_returned=int(len(final)),
        applied_constraints=applied_constraints,
        relaxed_constraints=relaxed_constraints,
        warnings=warnings,
        candidates=candidates,
    )


def _filter_with_fallback(
    df: pd.DataFrame,
    pref: dict[str, Any],
    policy: dict[str, Any],
    relaxed_constraints: list[str],
    warnings: list[str],
) -> pd.DataFrame:
    location = _norm(pref.get("location"))
    minimum_rating = pref.get("minimum_rating")
    budget = pref.get("budget")
    cuisine = _norm(pref.get("cuisine"))
    relaxation_order = policy.get("relaxation_order", ["minimum_rating", "budget", "cuisine"])

    current = _apply_filters(df, location=location, minimum_rating=minimum_rating, budget=budget, cuisine=cuisine)
    if not current.empty:
        return current

    # Location fallback for city-level requests on locality-level dataset (EC-09/EC-14).
    if location in {"bangalore", "bengaluru"}:
        warnings.append("Location appears city-level while dataset is locality-level. Location filter relaxed.")
        location = None
        relaxed_constraints.append("location")
        current = _apply_filters(df, location=location, minimum_rating=minimum_rating, budget=budget, cuisine=cuisine)
        if not current.empty:
            return current

    for constraint in relaxation_order:
        if constraint == "minimum_rating" and minimum_rating is not None:
            minimum_rating = max(3.5, float(minimum_rating) - 0.7)
            relaxed_constraints.append("minimum_rating")
        elif constraint == "budget" and budget is not None:
            budget = None
            relaxed_constraints.append("budget")
        elif constraint == "cuisine" and cuisine is not None:
            cuisine = None
            relaxed_constraints.append("cuisine")
        current = _apply_filters(df, location=location, minimum_rating=minimum_rating, budget=budget, cuisine=cuisine)
        if not current.empty:
            warnings.append(f"Applied fallback relaxation: {', '.join(relaxed_constraints)}")
            return current

    return current


def _apply_filters(
    df: pd.DataFrame,
    location: str | None,
    minimum_rating: float | None,
    budget: float | None,
    cuisine: str | None,
) -> pd.DataFrame:
    working = df.copy()
    if location:
        working = working[
            (working["location_norm"] == location)
            | (working["location_norm"].str.contains(location, regex=False))
        ]
    if minimum_rating is not None:
        working = working[working["rating"] >= float(minimum_rating)]
    if budget is not None:
        working = working[working["estimated_cost_for_two"] <= float(budget)]
    if cuisine:
        working = working[working["cuisines_norm"].str.contains(cuisine, regex=False)]
    return working


def _score_candidates(df: pd.DataFrame, pref: dict[str, Any]) -> pd.DataFrame:
    cuisine = _norm(pref.get("cuisine"))
    budget = pref.get("budget")
    rating_pref = pref.get("minimum_rating")

    def score_row(row: pd.Series) -> tuple[float, list[str]]:
        score = 0.0
        reasons: list[str] = []

        score += float(row["rating"]) * 2.0
        reasons.append("high rating")

        if cuisine and cuisine in str(row["cuisines_norm"]):
            score += 2.5
            reasons.append("cuisine match")

        if budget is not None:
            cost = float(row["estimated_cost_for_two"])
            if cost <= float(budget):
                score += 1.5
                reasons.append("budget fit")

        if rating_pref is not None and float(row["rating"]) >= float(rating_pref):
            score += 1.0
            reasons.append("meets minimum rating")

        return score, reasons

    scored = df.copy()
    tuple_scores = scored.apply(score_row, axis=1).tolist()
    scored["heuristic_score"] = [round(item[0], 3) for item in tuple_scores]
    scored["match_reasons"] = [item[1] for item in tuple_scores]

    scored = scored.sort_values(
        by=["heuristic_score", "rating", "estimated_cost_for_two"],
        ascending=[False, False, True],
    )
    return scored


def _enforce_diversity(df: pd.DataFrame) -> pd.DataFrame:
    # Avoid consecutive near-duplicates by restaurant name (EC-16).
    seen_names: set[str] = set()
    rows: list[pd.Series] = []
    for _, row in df.iterrows():
        name = _norm(row["restaurant_name"])
        if name in seen_names:
            continue
        seen_names.add(name)
        rows.append(row)
    if not rows:
        return df.head(0)
    return pd.DataFrame(rows).reset_index(drop=True)


def _norm(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text

