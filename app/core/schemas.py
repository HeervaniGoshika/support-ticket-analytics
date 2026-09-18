from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """
    Request body for the natural-language query endpoint.
    """

    question: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural language question about support tickets.",
    )


class QueryResponse(BaseModel):
    """
    Response returned by the query endpoint.
    """

    question: str
    intent: str
    answer: str
    data: list[dict[str, Any]] = []


class AnomalyItem(BaseModel):
    ticket_id: str
    anomaly_type: str
    reason: str
    created_at: datetime
    priority: str
    status: str
    resolution_time_hrs: float | None = None
    age_hours: float | None = None


class AnomalyResponse(BaseModel):
    total_anomalies: int
    reference_time: datetime
    anomalies: list[AnomalyItem]


class HealthResponse(BaseModel):
    status: Literal["healthy"]
    service: str
    version: str
    database: str
    llm: str