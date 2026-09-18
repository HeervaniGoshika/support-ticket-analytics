from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.models import Ticket
from app.services.query_service import (
    count_tickets,
    average_customer_rating,
    agent_resolution_count,
)


def create_test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={
            "check_same_thread": False
        },
    )

    Base.metadata.create_all(engine)

    Session = sessionmaker(
        bind=engine
    )

    return Session()


def seed_data(db):

    tickets = [
        Ticket(
            ticket_id="T1",
            created_at=datetime(
                2024, 3, 1, 10, 0
            ),
            category="Billing",
            priority="Critical",
            status="Resolved",
            response_time_hrs=1.0,
            resolution_time_hrs=4.0,
            agent_id="AGT-01",
            customer_rating=5,
            issue_summary="Billing issue",
        ),
        Ticket(
            ticket_id="T2",
            created_at=datetime(
                2024, 3, 2, 10, 0
            ),
            category="Technical",
            priority="High",
            status="Open",
            response_time_hrs=2.0,
            resolution_time_hrs=None,
            agent_id="AGT-02",
            customer_rating=None,
            issue_summary="Login issue",
        ),
    ]

    db.add_all(tickets)
    db.commit()


def test_count_tickets():

    db = create_test_db()

    try:

        seed_data(db)

        answer, data = count_tickets(
            db,
            {
                "status": "Open"
            },
        )

        assert data[0]["count"] == 1
        assert "1 tickets" in answer

    finally:
        db.close()


def test_average_customer_rating():

    db = create_test_db()

    try:

        seed_data(db)

        answer, data = average_customer_rating(
            db,
            {},
        )

        assert data[0][
            "average_customer_rating"
        ] == 5.0

    finally:
        db.close()


def test_agent_resolution_count():

    db = create_test_db()

    try:

        seed_data(db)

        answer, data = agent_resolution_count(
            db,
            {},
        )

        assert data[0]["agent_id"] == "AGT-01"
        assert data[0]["resolved_count"] == 1

    finally:
        db.close()