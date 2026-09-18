import json
import re
from typing import Any

import httpx

from app.config import settings


ALLOWED_INTENTS = {
    "count_tickets",
    "agent_resolution_count",
    "average_customer_rating",
    "list_tickets",
    "anomaly_check",
}


SYSTEM_PROMPT = """
You are an intent parser for a customer support analytics system.

Your job is to convert a user's natural language question
into a structured JSON query plan.

Available ticket fields:

- ticket_id
- created_at
- category: Billing, Technical, General
- priority: Low, Medium, High, Critical
- status: Open, Resolved, Escalated
- response_time_hrs
- resolution_time_hrs
- agent_id
- customer_rating
- issue_summary

Allowed intents:

1. count_tickets
2. agent_resolution_count
3. average_customer_rating
4. list_tickets
5. anomaly_check

Return ONLY valid JSON.

Use exactly this structure:

{
  "intent": "list_tickets",
  "filters": {
    "category": null,
    "priority": null,
    "status": null,
    "agent_id": null,
    "period": null,
    "resolution_time_max": null,
    "resolution_time_min": null,
    "age_hours_min": null,
    "not_resolved_within_hours": null
  }
}

IMPORTANT NUMERIC RULE:

If the user says:

"within 12 hours"

return:

"not_resolved_within_hours": 12

NOT:

"not_resolved_within_hours": "12 hours"

All hour values must be numbers.

Examples:

"within 12 hours" → 12
"older than 24 hours" → 24
"more than 48 hours" → 48

Do not include the word "hours" in numeric values.

FILTER RULES:

- Do not invent categories.
- Do not invent priorities.
- Do not invent statuses.
- Do not invent agent IDs.
- Use null when a filter is not present.

Category values:

Billing
Technical
General

Priority values:

Low
Medium
High
Critical

Status values:

Open
Resolved
Escalated

INTENT RULES:

Questions asking "how many" → count_tickets

Questions asking which agent resolved the most tickets →
agent_resolution_count

Questions asking about average customer rating →
average_customer_rating

Questions asking to show/list tickets →
list_tickets

Questions asking about anomalies →
anomaly_check

IMPORTANT SEMANTIC RULE:

"not resolved within X hours" means:

- a resolved ticket whose resolution time is greater than X hours
OR
- an unresolved ticket whose age is greater than X hours.

For example:

"Show me all Critical tickets not resolved within 12 hours."

should become:

{
  "intent": "list_tickets",
  "filters": {
    "priority": "Critical",
    "not_resolved_within_hours": 12
  }
}

Do not translate this into resolution_time_max.

For relative periods:

"this month" → "month"
"this week" → "week"

Return ONLY JSON.
"""


def _extract_json(text: str) -> dict[str, Any]:
    """
    Extract JSON from an LLM response.
    """

    text = text.strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        pass

    match = re.search(
        r"\{.*\}",
        text,
        flags=re.DOTALL,
    )

    if not match:
        raise ValueError(
            "LLM did not return valid JSON."
        )

    return json.loads(match.group())


def _normalize_number(
    value: Any,
) -> float | None:
    """
    Convert values such as:

    12
    "12"
    "12 hours"
    "12 hrs"

    into a numeric value.
    """

    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):

        match = re.search(
            r"[-+]?\d+(?:\.\d+)?",
            value,
        )

        if match:
            return float(match.group())

    raise ValueError(
        f"Expected a numeric value but received: {value!r}"
    )


def validate_plan(
    plan: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate and normalize the LLM query plan.
    """

    intent = plan.get("intent")

    if intent not in ALLOWED_INTENTS:
        raise ValueError(
            f"Unsupported intent: {intent}"
        )

    filters = plan.get("filters") or {}

    allowed_filters = {
        "category",
        "priority",
        "status",
        "agent_id",
        "period",
        "resolution_time_max",
        "resolution_time_min",
        "age_hours_min",
        "not_resolved_within_hours",
    }

    filters = {
        key: value
        for key, value in filters.items()
        if key in allowed_filters
    }

    # Normalize all hour-based values.
    for key in [
        "resolution_time_max",
        "resolution_time_min",
        "age_hours_min",
        "not_resolved_within_hours",
    ]:

        if key in filters:
            filters[key] = _normalize_number(
                filters[key]
            )

    # Validate known categorical values.
    valid_categories = {
        "Billing",
        "Technical",
        "General",
    }

    valid_priorities = {
        "Low",
        "Medium",
        "High",
        "Critical",
    }

    valid_statuses = {
        "Open",
        "Resolved",
        "Escalated",
    }

    if (
        filters.get("category")
        and filters["category"] not in valid_categories
    ):
        raise ValueError(
            f"Invalid category: {filters['category']}"
        )

    if (
        filters.get("priority")
        and filters["priority"] not in valid_priorities
    ):
        raise ValueError(
            f"Invalid priority: {filters['priority']}"
        )

    if (
        filters.get("status")
        and filters["status"] not in valid_statuses
    ):
        raise ValueError(
            f"Invalid status: {filters['status']}"
        )

    return {
        "intent": intent,
        "filters": filters,
    }


async def parse_question(
    question: str,
) -> dict[str, Any]:
    """
    Send the user's question to Ollama
    and receive a structured query plan.
    """

    payload = {
        "model": settings.ollama_model,
        "system": SYSTEM_PROMPT,
        "prompt": question,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0,
        },
    }

    url = (
        f"{settings.ollama_base_url.rstrip('/')}"
        "/api/generate"
    )

    try:

        async with httpx.AsyncClient(
            timeout=60.0
        ) as client:

            response = await client.post(
                url,
                json=payload,
            )

            response.raise_for_status()

            body = response.json()

    except httpx.HTTPError as exc:

        raise RuntimeError(
            f"LLM service unavailable: {exc}"
        ) from exc

    raw_response = body.get(
        "response",
        "",
    )

    if not raw_response:

        raise RuntimeError(
            "LLM returned an empty response."
        )

    plan = _extract_json(
        raw_response
    )

    return validate_plan(plan)