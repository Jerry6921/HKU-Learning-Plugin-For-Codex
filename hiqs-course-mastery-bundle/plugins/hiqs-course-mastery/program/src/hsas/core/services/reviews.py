"""Manage source-review batches and their independent checkpoints."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from hsas.application.change_tracking import (
    ChangeQueueError,
    acknowledge_change_batch,
    collect_pending_changes,
    validate_change_batch,
)
from hsas.application.ports.repositories import (
    ChangeQueueRepository,
    InformationRepository,
)
from hsas.core.ports import HIQSPortError
from hsas.domain.courses import PendingChangeBatch
from hsas.domain.information import InformationStore
from hsas.infrastructure.storage import (
    JsonChangeQueueRepository,
    JsonInformationRepository,
)


@dataclass(slots=True)
class SourceReviewService:
    """Export, validate and checkpoint Moodle review batches."""

    resources_dir: Path
    change_repository: ChangeQueueRepository = field(
        default_factory=JsonChangeQueueRepository,
        repr=False,
    )
    information_repository: InformationRepository = field(
        default_factory=JsonInformationRepository,
        repr=False,
    )

    def pending_changes(self, payload: dict[str, Any]) -> dict[str, Any]:
        source = payload.get("source", "moodle")
        if source != "moodle":
            raise HIQSPortError(f"Unsupported change source: {source}")
        course_ids = payload.get("course_ids")
        if course_ids is not None and (
            not isinstance(course_ids, list)
            or not all(isinstance(value, str) for value in course_ids)
        ):
            raise HIQSPortError("course_ids must be a list of strings.")
        return self.pending_batch(
            self.load_information_optional(),
            course_ids=set(course_ids or []),
        ).model_dump(mode="json")

    def acknowledge_changes(self, payload: dict[str, Any]) -> dict[str, Any]:
        if payload.get("confirmed") is not True:
            raise HIQSPortError("Change acknowledgement requires confirmation.")
        if payload.get("reviewed_no_information_change") is not True:
            raise HIQSPortError(
                "Use apply_information_update when facts changed; otherwise confirm "
                "reviewed_no_information_change."
            )
        source = payload.get("source", "moodle")
        batch = payload.get("batch")
        if not isinstance(batch, dict):
            raise HIQSPortError("batch must be an exported review object.")
        try:
            validated = self.validate_review_batches({str(source): batch})
            checkpoints = self.acknowledge_validated_batches(validated)
        except (
            OSError,
            ValueError,
            ValidationError,
            ChangeQueueError,
        ) as exc:
            raise HIQSPortError(str(exc)) from exc
        return {"source": source, "checkpoint": checkpoints[str(source)]}

    def pending_batch(
        self,
        information: InformationStore | None,
        *,
        course_ids: set[str] | None = None,
    ) -> PendingChangeBatch:
        try:
            return collect_pending_changes(
                self.resources_dir,
                self.change_repository,
                information=information,
                course_ids=course_ids,
            )
        except (OSError, ValueError, ValidationError) as exc:
            raise HIQSPortError(
                f"待处理 Moodle 变化无法读取：{type(exc).__name__}"
            ) from exc

    def load_information_optional(self) -> InformationStore | None:
        path = self.resources_dir / "information.json"
        if not self.information_repository.exists(path):
            return None
        try:
            return self.information_repository.load(path)
        except (OSError, ValueError, ValidationError) as exc:
            raise HIQSPortError(
                f"information.json cannot be loaded: {type(exc).__name__}"
            ) from exc

    def validate_review_batches(self, batches: dict[str, Any]) -> dict[str, Any]:
        unsupported = batches.keys() - {"moodle"}
        if unsupported:
            raise ValueError(f"Unsupported change source: {', '.join(sorted(unsupported))}")
        if not batches:
            return {}
        batch = PendingChangeBatch.model_validate(batches["moodle"])
        validate_change_batch(self.resources_dir, batch, self.change_repository)
        return {"moodle": batch}

    def acknowledge_validated_batches(self, batches: dict[str, Any]) -> dict[str, Any]:
        if not batches:
            return {}
        checkpoint = acknowledge_change_batch(
            self.resources_dir, batches["moodle"], self.change_repository, confirmed=True
        )
        return {"moodle": checkpoint.model_dump(mode="json")}


def pending_summary(batch: PendingChangeBatch) -> dict[str, int]:
    """Summarize a pending review batch for workflow and status payloads."""
    return {
        "course_count": len(batch.courses),
        "change_count": batch.pending_change_count,
        "full_review_count": sum(course.mode == "full" for course in batch.courses),
    }


__all__ = ["SourceReviewService", "pending_summary"]
