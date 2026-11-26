"""Compose the local Moodle, evidence, and Apple operations."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from threading import Lock

from hsas.application.material_search import invalidate_material_index, refresh_material_index
from hsas.application.moodle_sync import CourseSynchronizationService
from hsas.core.ports import HIQSPortError
from hsas.core.services.apple import AppleDeliveryService
from hsas.core.services.information import InformationContractService
from hsas.core.services.materials import MaterialQueryService
from hsas.core.services.reviews import SourceReviewService
from hsas.domain.information import InformationStore
from hsas.infrastructure.documents.ocr import run_ocr_queue
from hsas.infrastructure.moodle.gateway import MoodleCourseGateway
from hsas.infrastructure.moodle.settings import Settings
from hsas.infrastructure.runtime import get_runtime_paths, hku_portal_profile_dir
from hsas.infrastructure.storage import JsonInformationRepository, exclusive_file_lock
from hsas.infrastructure.storage.json_store import read_json


class HIQSCore:
    def __init__(self, resources_dir: Path, *, moodle: CourseSynchronizationService | None = None):
        self.resources_dir = resources_dir
        self._moodle = moodle
        self._source_lock = resources_dir / ".transactions" / "plugin-moodle.lock"
        self._mutation_lock = Lock()
        self.materials = MaterialQueryService(resources_dir)
        self.reviews = SourceReviewService(resources_dir)
        self.information = InformationContractService(resources_dir, JsonInformationRepository())
        self.apple = AppleDeliveryService(resources_dir)

    def _moodle_service(self) -> CourseSynchronizationService:
        if self._moodle is None:
            settings = Settings.load(
                output_dir=self.resources_dir,
                profile_dir=hku_portal_profile_dir(self.resources_dir),
            )
            return CourseSynchronizationService(MoodleCourseGateway(settings))
        return self._moodle

    def login_moodle(self) -> dict:
        with exclusive_file_lock(self._source_lock):
            return asdict(self._moodle_service().login_until_ready())

    def verify_moodle_session(self) -> dict:
        with exclusive_file_lock(self._source_lock):
            return asdict(self._moodle_service().check_login_status())

    def sync_moodle(self, course: str | None = None, *, confirmed: bool = False) -> dict:
        if not confirmed:
            raise HIQSPortError("Moodle synchronization requires confirmation.")
        if course is not None and not course.strip():
            raise HIQSPortError("Supply a Moodle course ID or URL, or omit course to sync all.")
        with exclusive_file_lock(self._source_lock):
            service = self._moodle_service()
            if course is None:
                result = service.sync_all()
                response = {**asdict(result), "report_path": str(result.report_path)}
                affected = None
            else:
                result = service.sync_course(course.strip())
                response = {**asdict(result), "output_path": str(result.output_path)}
                affected = {result.course_id}
            self._refresh_index(affected)
            return response

    def sync_status(self) -> dict:
        path = self.resources_dir / "sync-report.json"
        return read_json(path) if path.is_file() else {}

    def run_ocr(self, course_ids: list[str] | None = None, *, confirmed: bool = False) -> dict:
        if not confirmed:
            raise HIQSPortError("OCR requires confirmation.")
        with exclusive_file_lock(self._source_lock):
            selected = set(course_ids) if course_ids else None
            result = run_ocr_queue(self.resources_dir, course_ids=selected)
            self._refresh_index(selected)
            return result

    def _refresh_index(self, course_ids: set[str] | None) -> None:
        try:
            refresh_material_index(self.resources_dir, course_ids)
        except (OSError, ValueError):
            invalidate_material_index(self.resources_dir)

    def read_information(self) -> dict:
        store = self.reviews.load_information_optional()
        return {"available": store is not None, **(store or InformationStore()).model_dump(mode="json")}

    def apply_information(self, payload: dict) -> dict:
        with exclusive_file_lock(self._source_lock):
            report = self.information.apply(payload, self.reviews, self._mutation_lock)
        return {**report, "information": self.read_information()}

    def acknowledge_changes(self, payload: dict) -> dict:
        with exclusive_file_lock(self._source_lock):
            return self.reviews.acknowledge_changes(payload)


def build_port() -> HIQSCore:
    return HIQSCore(get_runtime_paths().create().resources_dir)
