from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.core.models import Ticket
from app.utils.validators import validate_ticket_dataframe


BASE_DIR = Path(__file__).resolve().parents[2]

DEFAULT_CSV_PATH = (
    BASE_DIR / "data" / "support_tickets.csv"
)


def load_csv(
    csv_path: str | Path = DEFAULT_CSV_PATH,
) -> pd.DataFrame:
    """
    Read support tickets CSV.
    """

    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV file not found: {csv_path}"
        )

    df = pd.read_csv(csv_path)

    return validate_ticket_dataframe(df)


def ingest_data(
    db: Session,
    csv_path: str | Path = DEFAULT_CSV_PATH,
) -> int:
    """
    Load CSV data into database.

    The ingestion is idempotent:
    if tickets already exist, we don't insert duplicates.
    """

    df = load_csv(csv_path)

    existing_ids = {
        row[0]
        for row in db.query(Ticket.ticket_id).all()
    }

    inserted = 0

    for record in df.to_dict(orient="records"):

        ticket_id = record["ticket_id"]

        if ticket_id in existing_ids:
            continue

        ticket = Ticket(
            ticket_id=ticket_id,
            created_at=record["created_at"].to_pydatetime(),
            category=record["category"],
            priority=record["priority"],
            status=record["status"],
            response_time_hrs=float(
                record["response_time_hrs"]
            ),
            resolution_time_hrs=(
                None
                if pd.isna(record["resolution_time_hrs"])
                else float(record["resolution_time_hrs"])
            ),
            agent_id=record["agent_id"],
            customer_rating=(
                None
                if pd.isna(record["customer_rating"])
                else float(record["customer_rating"])
            ),
            issue_summary=record["issue_summary"],
        )

        db.add(ticket)
        inserted += 1

    db.commit()

    return inserted