from typing import Iterable

import pandas as pd


REQUIRED_COLUMNS = {
    "ticket_id",
    "created_at",
    "category",
    "priority",
    "status",
    "response_time_hrs",
    "resolution_time_hrs",
    "agent_id",
    "customer_rating",
    "issue_summary",
}


ALLOWED_CATEGORIES = {
    "Billing",
    "Technical",
    "General",
}


ALLOWED_PRIORITIES = {
    "Low",
    "Medium",
    "High",
    "Critical",
}


ALLOWED_STATUSES = {
    "Open",
    "Resolved",
    "Escalated",
}


def validate_required_columns(
    columns: Iterable[str],
) -> None:
    """
    Check whether all required columns exist.
    """

    columns = set(columns)

    missing = REQUIRED_COLUMNS - columns

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )


def validate_ticket_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and normalize the support ticket dataframe.
    """

    validate_required_columns(df.columns)

    df = df.copy()

    # Parse timestamps
    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce",
    )

    if df["created_at"].isna().any():
        raise ValueError(
            "Some created_at values could not be parsed."
        )

    # Numeric fields
    numeric_columns = [
        "response_time_hrs",
        "resolution_time_hrs",
        "customer_rating",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # Ticket IDs must be unique
    if df["ticket_id"].duplicated().any():
        raise ValueError(
            "Duplicate ticket_id values found."
        )

    # Validate categorical fields
    invalid_categories = (
        set(df["category"].dropna().unique())
        - ALLOWED_CATEGORIES
    )

    if invalid_categories:
        raise ValueError(
            f"Invalid categories: {invalid_categories}"
        )

    invalid_priorities = (
        set(df["priority"].dropna().unique())
        - ALLOWED_PRIORITIES
    )

    if invalid_priorities:
        raise ValueError(
            f"Invalid priorities: {invalid_priorities}"
        )

    invalid_statuses = (
        set(df["status"].dropna().unique())
        - ALLOWED_STATUSES
    )

    if invalid_statuses:
        raise ValueError(
            f"Invalid statuses: {invalid_statuses}"
        )

    # Ratings should be between 1 and 5
    invalid_ratings = df[
        df["customer_rating"].notna()
        & (
            (df["customer_rating"] < 1)
            | (df["customer_rating"] > 5)
        )
    ]

    if not invalid_ratings.empty:
        raise ValueError(
            "customer_rating must be between 1 and 5."
        )

    # Resolution time can be null for unresolved tickets
    unresolved = df["status"].isin(
        ["Open", "Escalated"]
    )

    invalid_resolution = df[
        unresolved
        & df["resolution_time_hrs"].notna()
    ]

    # We don't fail here because real-world data can be inconsistent.
    # The value is retained and can be investigated.

    # Strip string columns
    string_columns = [
        "ticket_id",
        "category",
        "priority",
        "status",
        "agent_id",
        "issue_summary",
    ]

    for column in string_columns:
        df[column] = df[column].astype(str).str.strip()

    return df