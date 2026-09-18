from datetime import datetime, timedelta

import numpy as np
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session

from app.config import settings
from app.core.models import Ticket


def _ticket_to_anomaly(
    ticket: Ticket,
    anomaly_type: str,
    reason: str,
    age_hours: float | None = None,
) -> dict:

    return {
        "ticket_id": ticket.ticket_id,
        "anomaly_type": anomaly_type,
        "reason": reason,
        "created_at": ticket.created_at,
        "priority": ticket.priority,
        "status": ticket.status,
        "resolution_time_hrs": ticket.resolution_time_hrs,
        "age_hours": (
            round(age_hours, 2)
            if age_hours is not None
            else None
        ),
    }


def detect_unresolved_old_tickets(
    db: Session,
    age_hours: float = settings.unresolved_age_hours,
):
    """
    Detect unresolved High/Critical tickets older
    than the configured threshold.

    The latest ticket timestamp is used as the
    reference time so the result is reproducible.
    """

    reference_time = (
        db.query(
            Ticket.created_at
        )
        .order_by(
            Ticket.created_at.desc()
        )
        .first()
    )

    if not reference_time:
        return [], datetime.utcnow()

    reference_time = reference_time[0]

    threshold = reference_time - timedelta(
        hours=age_hours
    )

    tickets = (
        db.query(Ticket)
        .filter(
            Ticket.status.in_(
                ["Open", "Escalated"]
            ),
            Ticket.priority.in_(
                ["High", "Critical"]
            ),
            Ticket.created_at <= threshold,
        )
        .all()
    )

    anomalies = []

    for ticket in tickets:

        age = (
            reference_time
            - ticket.created_at
        ).total_seconds() / 3600

        reason = (
            f"{ticket.priority} priority ticket is "
            f"{age:.1f} hours old and remains "
            f"{ticket.status.lower()}."
        )

        anomalies.append(
            _ticket_to_anomaly(
                ticket,
                "unresolved_old_ticket",
                reason,
                age,
            )
        )

    return anomalies, reference_time


def detect_resolution_time_anomalies(
    db: Session,
):
    """
    Detect unusually long resolution times.

    IsolationForest is used on resolution_time_hrs.
    """

    tickets = (
        db.query(Ticket)
        .filter(
            Ticket.resolution_time_hrs.isnot(None)
        )
        .all()
    )

    if len(tickets) < 10:
        return []

    values = np.array([
        [ticket.resolution_time_hrs]
        for ticket in tickets
    ])

    model = IsolationForest(
        contamination=settings.isolation_contamination,
        random_state=42,
    )

    predictions = model.fit_predict(values)

    anomalies = []

    for ticket, prediction in zip(
        tickets,
        predictions,
    ):

        if prediction == -1:

            reason = (
                f"Resolution time of "
                f"{ticket.resolution_time_hrs:.1f} hours "
                f"was identified as statistically unusual."
            )

            anomalies.append(
                _ticket_to_anomaly(
                    ticket,
                    "resolution_time_anomaly",
                    reason,
                )
            )

    return anomalies


def detect_anomalies(
    db: Session,
    age_hours: float = settings.unresolved_age_hours,
):
    """
    Run all anomaly detectors and return a combined result.
    """

    old_tickets, reference_time = (
        detect_unresolved_old_tickets(
            db,
            age_hours,
        )
    )

    resolution_anomalies = (
        detect_resolution_time_anomalies(db)
    )

    combined = (
        old_tickets
        + resolution_anomalies
    )

    # Remove duplicate ticket/type combinations
    unique = {}

    for anomaly in combined:
        key = (
            anomaly["ticket_id"],
            anomaly["anomaly_type"],
        )

        unique[key] = anomaly

    anomalies = list(unique.values())

    anomalies.sort(
        key=lambda item: item["created_at"],
        reverse=True,
    )

    return {
        "total_anomalies": len(anomalies),
        "reference_time": reference_time,
        "anomalies": anomalies,
    }