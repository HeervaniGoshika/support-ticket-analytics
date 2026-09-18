from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Ticket(Base):
    """
    SQLAlchemy model representing a customer support ticket.
    """

    __tablename__ = "tickets"

    ticket_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    priority: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    response_time_hrs: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    resolution_time_hrs: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    agent_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    customer_rating: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    issue_summary: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )