from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session

from app.core.models import Ticket


def get_reference_time(
    db: Session,
) -> datetime:
    """
    Get the latest ticket timestamp.

    This is used as the reference point for relative
    periods and ticket age because the dataset is historical.
    """

    result = db.query(
        func.max(Ticket.created_at)
    ).scalar()

    if result is None:

        raise ValueError(
            "No ticket data available."
        )

    return result


def apply_filters(
    query,
    filters: dict[str, Any],
    db: Session,
):
    """
    Apply normal filters to a SQLAlchemy query.
    """

    if filters.get("category"):

        query = query.filter(
            Ticket.category
            == filters["category"]
        )

    if filters.get("priority"):

        query = query.filter(
            Ticket.priority
            == filters["priority"]
        )

    if filters.get("status"):

        query = query.filter(
            Ticket.status
            == filters["status"]
        )

    if filters.get("agent_id"):

        query = query.filter(
            Ticket.agent_id
            == filters["agent_id"]
        )

    if filters.get("resolution_time_max") is not None:

        query = query.filter(
            Ticket.resolution_time_hrs
            <= float(
                filters["resolution_time_max"]
            )
        )

    if filters.get("resolution_time_min") is not None:

        query = query.filter(
            Ticket.resolution_time_hrs
            >= float(
                filters["resolution_time_min"]
            )
        )

    if filters.get("age_hours_min") is not None:

        reference_time = get_reference_time(db)

        threshold = (
            reference_time
            - timedelta(
                hours=float(
                    filters["age_hours_min"]
                )
            )
        )

        query = query.filter(
            Ticket.created_at <= threshold
        )

    period = filters.get("period")

    if period:

        reference = get_reference_time(db)

        if period == "month":

            start = reference.replace(
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )

            query = query.filter(
                Ticket.created_at >= start
            )

        elif period == "week":

            start = (
                reference
                - timedelta(
                    days=reference.weekday()
                )
            ).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )

            query = query.filter(
                Ticket.created_at >= start
            )

    return query


def apply_not_resolved_within_filter(
    query,
    filters: dict[str, Any],
    db: Session,
):
    """
    Handle questions such as:

    "Critical tickets not resolved within 12 hours"

    This means:

    1. Resolved tickets with resolution time > 12 hours

    OR

    2. Open/Escalated tickets older than 12 hours.
    """

    threshold_hours = filters.get(
        "not_resolved_within_hours"
    )

    if threshold_hours is None:
        return query

    threshold_hours = float(
        threshold_hours
    )

    reference_time = get_reference_time(db)

    age_threshold = (
        reference_time
        - timedelta(
            hours=threshold_hours
        )
    )

    slow_resolved = (
        (Ticket.status == "Resolved")
        & (
            Ticket.resolution_time_hrs
            > threshold_hours
        )
    )

    unresolved_old = (
        Ticket.status.in_(
            ["Open", "Escalated"]
        )
        & (
            Ticket.created_at
            <= age_threshold
        )
    )

    return query.filter(
        or_(
            slow_resolved,
            unresolved_old,
        )
    )


def serialize_ticket(
    ticket: Ticket,
) -> dict[str, Any]:
    """
    Convert ORM object to JSON-compatible dictionary.
    """

    return {
        "ticket_id": ticket.ticket_id,
        "created_at": ticket.created_at.isoformat(),
        "category": ticket.category,
        "priority": ticket.priority,
        "status": ticket.status,
        "response_time_hrs": ticket.response_time_hrs,
        "resolution_time_hrs": ticket.resolution_time_hrs,
        "agent_id": ticket.agent_id,
        "customer_rating": ticket.customer_rating,
        "issue_summary": ticket.issue_summary,
    }


def count_tickets(
    db: Session,
    filters: dict[str, Any],
):
    """
    Count tickets matching filters.
    """

    query = db.query(Ticket)

    query = apply_filters(
        query,
        filters,
        db,
    )

    query = apply_not_resolved_within_filter(
        query,
        filters,
        db,
    )

    count = query.count()

    return (
        f"There are {count} tickets matching "
        f"the requested criteria.",
        [
            {
                "count": count
            }
        ],
    )


def agent_resolution_count(
    db: Session,
    filters: dict[str, Any],
):
    """
    Count resolved tickets by agent.
    """

    query = db.query(
        Ticket.agent_id,
        func.count(
            Ticket.ticket_id
        ).label(
            "resolved_count"
        ),
    ).filter(
        Ticket.status == "Resolved"
    )

    query = apply_filters(
        query,
        filters,
        db,
    )

    query = query.group_by(
        Ticket.agent_id
    ).order_by(
        desc("resolved_count")
    )

    results = query.all()

    data = [
        {
            "agent_id": row.agent_id,
            "resolved_count": row.resolved_count,
        }
        for row in results
    ]

    if not data:

        return (
            "No resolved tickets matched "
            "the requested criteria.",
            [],
        )

    top_agent = data[0]

    answer = (
        f"{top_agent['agent_id']} resolved "
        f"the most tickets with "
        f"{top_agent['resolved_count']} "
        f"resolved tickets."
    )

    return answer, data


def average_customer_rating(
    db: Session,
    filters: dict[str, Any],
):
    """
    Calculate average customer rating.
    """

    query = db.query(
        func.avg(
            Ticket.customer_rating
        ).label(
            "average_rating"
        )
    ).filter(
        Ticket.customer_rating.isnot(None)
    )

    query = apply_filters(
        query,
        filters,
        db,
    )

    result = query.one()

    average = result.average_rating

    if average is None:

        return (
            "No customer ratings matched "
            "the requested criteria.",
            [],
        )

    average = round(
        float(average),
        2,
    )

    return (
        f"The average customer rating is "
        f"{average}/5.",
        [
            {
                "average_customer_rating": average
            }
        ],
    )


def list_tickets(
    db: Session,
    filters: dict[str, Any],
):
    """
    Return tickets matching filters.
    """

    query = db.query(Ticket)

    query = apply_filters(
        query,
        filters,
        db,
    )

    query = apply_not_resolved_within_filter(
        query,
        filters,
        db,
    )

    tickets = (
        query
        .order_by(
            desc(Ticket.created_at)
        )
        .limit(100)
        .all()
    )

    data = [
        serialize_ticket(ticket)
        for ticket in tickets
    ]

    return (
        f"Found {len(data)} matching tickets.",
        data,
    )


def execute_plan(
    db: Session,
    plan: dict[str, Any],
):
    """
    Execute a validated query plan.
    """

    intent = plan["intent"]

    filters = plan.get(
        "filters",
        {},
    )

    if intent == "count_tickets":

        return count_tickets(
            db,
            filters,
        )

    if intent == "agent_resolution_count":

        return agent_resolution_count(
            db,
            filters,
        )

    if intent == "average_customer_rating":

        return average_customer_rating(
            db,
            filters,
        )

    if intent == "list_tickets":

        return list_tickets(
            db,
            filters,
        )

    if intent == "anomaly_check":

        return (
            "Please use the /anomalies endpoint "
            "for anomaly analysis.",
            [],
        )

    raise ValueError(
        f"Unsupported intent: {intent}"
    )