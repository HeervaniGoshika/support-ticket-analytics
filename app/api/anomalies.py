from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.core.database import get_db
from app.core.schemas import AnomalyResponse
from app.services.anomaly_service import (
    detect_anomalies,
)


router = APIRouter(
    prefix="/anomalies",
    tags=["Anomalies"],
)


@router.get(
    "",
    response_model=AnomalyResponse,
)
def get_anomalies(
    age_hours: float = Query(
        default=settings.unresolved_age_hours,
        gt=0,
        le=720,
        description=(
            "Age threshold for unresolved high-priority tickets."
        ),
    ),
    db: Session = Depends(get_db),
):

    result = detect_anomalies(
        db,
        age_hours=age_hours,
    )

    return result