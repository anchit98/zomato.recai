from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from typing import Any



LOCATION_ALIASES = {
    "blr": "bangalore",
    "bengaluru": "bangalore",
    "new delhi": "delhi",
    "ncr": "delhi",
}

CUISINE_ALIASES = {
    "north indian": "indian",
    "south indian": "indian",
    "indo chinese": "chinese",
}

RELAXATION_ORDER = ("minimum_rating", "budget", "cuisine")


@dataclass
class ValidationErrorItem:
    field: str
    code: str
    message: str


@dataclass
class ValidationResult:
    valid: bool
    errors: list[ValidationErrorItem]
    warnings: list[str]
    normalized_preferences: "PreferenceInput | None"
    constraint_policy: dict[str, Any] | None


@dataclass
class PreferenceInput:
    location: str
    budget: str | None = None
    cuisine: str | None = None
    minimum_rating: float | None = None
    additional_preferences: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_and_normalize_preferences(
    payload: dict[str, Any],
    known_locations: set[str] | None = None,
) -> ValidationResult:
    errors: list[ValidationErrorItem] = []
    warnings: list[str] = []

    if not payload:
        return ValidationResult(
            valid=False,
            errors=[
                ValidationErrorItem(
                    field="request",
                    code="empty_payload",
                    message="Request body is empty. Provide at least location.",
                )
            ],
            warnings=[],
            normalized_preferences=None,
            constraint_policy=None,
        )

    location = _normalize_text(payload.get("location"))
    budget = _normalize_budget(payload.get("budget"), errors)
    cuisine = _normalize_cuisine(payload.get("cuisine"))
    minimum_rating = _normalize_rating(payload.get("minimum_rating"), errors)
    additional_preferences = _sanitize_additional_preferences(
        payload.get("additional_preferences"),
        warnings,
    )

    if not location:
        errors.append(
            ValidationErrorItem(
                field="location",
                code="missing_required",
                message="Location is required.",
            )
        )
    else:
        location = _normalize_location(location)
        if known_locations:
            if location not in known_locations:
                suggestion = _closest_location(location, known_locations)
                message = (
                    f"Unsupported location '{location}'."
                    + (f" Try '{suggestion}'." if suggestion else " Try one of supported locations.")
                )
                errors.append(
                    ValidationErrorItem(
                        field="location",
                        code="unsupported_location",
                        message=message,
                    )
                )

    if errors:
        return ValidationResult(
            valid=False,
            errors=errors,
            warnings=warnings,
            normalized_preferences=None,
            constraint_policy=None,
        )

    normalized = PreferenceInput(
        location=location or "",
        budget=budget,
        cuisine=cuisine,
        minimum_rating=minimum_rating,
        additional_preferences=additional_preferences,
    )

    policy = _build_constraint_policy(normalized)
    if policy["is_conflicting"]:
        warnings.append(
            "Preferences are highly restrictive; fallback may relax constraints in order: "
            + ", ".join(policy["relaxation_order"])
            + "."
        )

    return ValidationResult(
        valid=True,
        errors=[],
        warnings=warnings,
        normalized_preferences=normalized,
        constraint_policy=policy,
    )


def build_preference_object_json(
    payload: dict[str, Any],
    known_locations: set[str] | None = None,
) -> str:
    result = validate_and_normalize_preferences(payload, known_locations=known_locations)
    serializable = {
        "valid": result.valid,
        "errors": [asdict(e) for e in result.errors],
        "warnings": result.warnings,
        "normalized_preferences": result.normalized_preferences.to_dict()
        if result.normalized_preferences
        else None,
        "constraint_policy": result.constraint_policy,
    }
    return json.dumps(serializable, indent=2)


def _normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    return re.sub(r"\s+", " ", text)


def _normalize_location(location: str) -> str:
    return LOCATION_ALIASES.get(location, location)


def _normalize_budget(value: Any, errors: list[ValidationErrorItem]) -> float | None:
    if value is None or str(value).strip() == "":
        return None
        
    text = str(value).strip().lower()
    # Extract numeric part
    match = re.search(r"(\d+(\.\d+)?)", text)
    if not match:
        errors.append(
            ValidationErrorItem(
                field="budget",
                code="invalid_budget",
                message="Budget must be a numeric value representing maximum cost for two.",
            )
        )
        return None

    try:
        budget = float(match.group(1))
        if budget <= 0:
            errors.append(
                ValidationErrorItem(
                    field="budget",
                    code="out_of_range",
                    message="Budget must be a positive number.",
                )
            )
            return None
        return budget
    except ValueError:
        return None


def _normalize_cuisine(value: Any) -> str | None:
    text = _normalize_text(value)
    if text is None:
        return None
    return CUISINE_ALIASES.get(text, text)


def _normalize_rating(value: Any, errors: list[ValidationErrorItem]) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    text = str(value).strip().lower()

    if text in {"excellent", "awesome", "best"}:
        return 4.5
    if text in {"good", "nice"}:
        return 4.0

    match = re.search(r"(\d+(\.\d+)?)", text)
    if not match:
        errors.append(
            ValidationErrorItem(
                field="minimum_rating",
                code="invalid_rating",
                message="Minimum rating must be numeric and in range 0-5.",
            )
        )
        return None

    rating = float(match.group(1))
    if rating > 5 and rating <= 10:
        rating = rating / 2

    if rating < 0 or rating > 5:
        errors.append(
            ValidationErrorItem(
                field="minimum_rating",
                code="out_of_range",
                message="Minimum rating must be between 0 and 5.",
            )
        )
        return None
    return round(rating, 2)


def _sanitize_additional_preferences(value: Any, warnings: list[str]) -> str | None:
    text = _normalize_text(value)
    if text is None:
        return None

    # Remove common injection primitives and role-override patterns.
    sanitized = re.sub(r"(```|<\|.*?\|>|system:|assistant:|ignore previous instructions)", "", text)
    sanitized = re.sub(r"\s+", " ", sanitized).strip()

    if sanitized != text:
        warnings.append("Additional preferences were sanitized for safety.")
    return sanitized[:400] if sanitized else None


def _closest_location(location: str, known_locations: set[str]) -> str | None:
    if not known_locations:
        return None
    if location in known_locations:
        return location

    candidates = sorted(known_locations, key=lambda item: _simple_distance(location, item))
    return candidates[0] if candidates else None


def _simple_distance(a: str, b: str) -> int:
    # Lightweight heuristic distance for suggestions.
    a_chars = set(a)
    b_chars = set(b)
    return len(a_chars.symmetric_difference(b_chars))


def _build_constraint_policy(preferences: PreferenceInput) -> dict[str, Any]:
    hard_constraints: list[str] = ["location"]
    soft_constraints: list[str] = []

    if preferences.minimum_rating is not None:
        hard_constraints.append("minimum_rating")
    if preferences.budget:
        hard_constraints.append("budget")
    if preferences.cuisine:
        soft_constraints.append("cuisine")
    if preferences.additional_preferences:
        soft_constraints.append("additional_preferences")

    # Heuristic conflict detection for very restrictive queries.
    restrictiveness_score = 0
    if preferences.minimum_rating is not None and preferences.minimum_rating >= 4.5:
        restrictiveness_score += 2
    if preferences.budget is not None and preferences.budget < 800:
        restrictiveness_score += 1
    if preferences.additional_preferences:
        restrictiveness_score += 1

    is_conflicting = restrictiveness_score >= 3
    return {
        "hard_constraints": hard_constraints,
        "soft_constraints": soft_constraints,
        "is_conflicting": is_conflicting,
        "relaxation_order": RELAXATION_ORDER,
    }

