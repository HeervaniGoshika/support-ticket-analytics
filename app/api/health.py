from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.core.database import get_db
from app.core.schemas import HealthResponse


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get(
    "",
    response_model=HealthResponse,
)
def health_check(
    db: Session = Depends(get_db),
):

    database_status = "healthy"

    try:
        db.execute(text("SELECT 1"))
    except Exception:
        database_status = "unhealthy"

    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version,
        database=database_status,
        llm=settings.ollama_model,
    )