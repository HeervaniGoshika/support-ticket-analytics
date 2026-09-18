from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.schemas import (
    QueryRequest,
    QueryResponse,
)
from app.services.llm_service import (
    parse_question,
)
from app.services.query_service import (
    execute_plan,
)


router = APIRouter(
    prefix="/query",
    tags=["Query"],
)


@router.post(
    "",
    response_model=QueryResponse,
)
async def query_tickets(
    request: QueryRequest,
    db: Session = Depends(get_db),
):
    """
    Answer a natural-language question about support tickets.
    """

    try:

        plan = await parse_question(
            request.question
        )

        answer, data = execute_plan(
            db,
            plan,
        )

        return QueryResponse(
            question=request.question,
            intent=plan["intent"],
            answer=answer,
            data=data,
        )

    except RuntimeError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {exc}",
        )