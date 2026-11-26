"""Shared calendar and task rules for fact validation and Apple delivery."""

from typing import Any

from hsas.domain.information.calendar import calendar_milestones, expand_occurrences
from hsas.domain.information.models import InformationItem


def is_actionable(item: dict[str, Any]) -> bool:
    if item.get("task_role") == "reference":
        return False
    if item.get("task_role") == "action":
        return True
    if item["category"] == "reading":
        return bool(item.get("due_at") or item.get("due_on") or item.get("requirements"))
    return item["category"] in {"assignment", "quiz", "exam", "presentation", "project",
                                "report", "deadline"}


def expand_calendar(item: dict[str, Any], timezone: str) -> list[dict[str, Any]]:
    """Expand weekly rules including cancellations, additions and overrides."""
    # Callers may pass minimal dictionaries as well as fully dumped models.
    model = InformationItem.model_validate({"course_id": "projection", "category": "other", **item})
    rows = []
    for role, start, end in calendar_milestones(model):
        value = start.isoformat()
        label = {"due": "Deadline", "opens": "Opens"}.get(role)
        rows.append({"identity": f"{item['item_id']}:{value[:10]}" + (f":{role}" if role else ""),
            "title": f"{item['title']} · {label}" if label else item["title"],
            "start": value, "end": end.isoformat() if end else None,
            "location": item.get("location")})
    recurrence = item.get("recurrence")
    if not recurrence:
        return rows
    exceptions = {value.date: value for value in model.recurrence.exceptions}
    for start, end in expand_occurrences(model, timezone):
        day = start.date()
        exception = exceptions.get(day)
        rows.append({"identity": f"{item['item_id']}:{day.isoformat()}",
            "title": exception.title if exception and exception.title else item["title"],
            "start": start.isoformat(), "end": end.isoformat() if end else None,
            "location": exception.location if exception and exception.location else item.get("location")})
    return rows
