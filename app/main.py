from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.anomalies import router as anomaly_router
from app.api.health import router as health_router
from app.api.query import router as query_router
from app.config import settings
from app.core.database import SessionLocal, init_db
from app.services.ingestion import ingest_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown lifecycle.
    """

    # Create database tables
    init_db()

    # Load CSV into database
    db = SessionLocal()

    try:
        inserted = ingest_data(db)

        print(
            f"Data ingestion completed. "
            f"Inserted {inserted} tickets."
        )

    finally:
        db.close()

    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-powered customer support ticket "
        "analytics and anomaly detection system."
    ),
    lifespan=lifespan,
)


app.include_router(
    health_router
)

app.include_router(
    query_router
)

app.include_router(
    anomaly_router
)


@app.get("/")
def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "message": "Support Intelligence API is running.",
        "docs": "/docs",
    }