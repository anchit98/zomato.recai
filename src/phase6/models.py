from __future__ import annotations
import src.bootstrap  # Force clean environment
from pydantic import BaseModel, Field
from typing import Any, Optional, List

class RecommendationRequest(BaseModel):
    location: str = Field(..., example="Bellandur")
    budget: Optional[Any] = Field(None, example=1500)
    cuisine: Optional[str] = Field(None, example="North Indian")
    minimum_rating: Optional[float] = Field(None, ge=0, le=5, example=4.0)
    additional_preferences: Optional[str] = Field(None, example="family friendly")
    session_id: str = Field(default="default-session")
    top_k: int = Field(default=5, ge=1, le=10)

class RecommendationItem(BaseModel):
    restaurant_name: str
    location: str
    cuisines: str
    estimated_cost_for_two: float
    rating: float
    explanation: str
    rank: int

class RecommendationResponse(BaseModel):
    status: str
    session_id: str
    recommendations: List[RecommendationItem]
    warnings: List[str] = []
    meta: dict[str, Any] = {}

class HistoryItem(BaseModel):
    id: str
    created_at: str
    location: str
    budget: Optional[Any]
    min_rating: Optional[float]
    cuisine: Optional[str]
    recommendations: List[Any]

class FeedbackRequest(BaseModel):
    session_id: str
    restaurant_name: str
    is_positive: bool
    feedback_text: Optional[str] = None
