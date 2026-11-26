"""Expose the program operations used by the packaged prompts."""

from __future__ import annotations

from functools import wraps

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from hsas.core.facade import HIQSCore
from hsas.core.ports import HIQSPortError


def build_mcp_server(port: HIQSCore) -> MCPServer:
    server = MCPServer(
        "HIQS",
        instructions="Sync and read local Moodle materials. Use verified course facts "
        "to preview and synchronize the HIQS Calendar and Reminders projection.",
    )

    def tool(function):
        @wraps(function)
        def invoke(**kwargs):
            try:
                return function(**kwargs)
            except (HIQSPortError, ValueError) as exc:
                raise ToolError(str(exc)) from exc

        server.tool()(invoke)
        return function

    @tool
    def sync_moodle(course: str | None = None, confirmed: bool = False) -> dict:
        """Collect Moodle materials for a Moodle ID or same-origin URL; omit course for all."""
        return port.sync_moodle(course, confirmed=confirmed)

    @tool
    def get_sync_status() -> dict:
        """Return the saved Moodle collection report, or an empty object before the first sync."""
        return port.sync_status()

    @tool
    def verify_moodle_session() -> dict:
        """Check whether the existing Moodle session can access the course catalog."""
        return port.verify_moodle_session()

    @tool
    def list_materials(course_ids: list[str] | None = None) -> dict:
        """Inventory synchronized Moodle files, activities, and coverage gaps."""
        return port.materials.manifest(course_ids)

    @tool
    def search_materials(query: str, course_ids: list[str] | None = None, limit: int = 6) -> dict:
        """Find page-aware local Moodle evidence."""
        return port.materials.search({"query": query, "course_ids": course_ids, "limit": limit})

    @tool
    def get_evidence_content(evidence_id: str, chunk_index: int | None = None,
                             context_chunks: int = 1) -> dict:
        """Read one evidence result and a bounded neighborhood."""
        return port.materials.evidence_content({
            "evidence_id": evidence_id, "chunk_index": chunk_index, "context_chunks": context_chunks,
        })

    @tool
    def run_ocr(course_ids: list[str] | None = None, confirmed: bool = False) -> dict:
        """Run local OCR over queued documents in the selected Moodle courses."""
        return port.run_ocr(course_ids, confirmed=confirmed)

    @tool
    def get_information() -> dict:
        """Read the existing validated course facts and Moodle source identities."""
        return port.read_information()

    @tool
    def query_course(question: str, course_ids: list[str] | None = None,
                     material_limit: int = 6, item_limit: int = 20) -> dict:
        """Return a cited packet from validated facts and local Moodle materials."""
        return port.materials.query_course({
            "question": question, "course_ids": course_ids,
            "material_limit": material_limit, "item_limit": item_limit,
        })

    @tool
    def get_pending_changes(course_ids: list[str] | None = None) -> dict:
        """Get Moodle changes and coverage for review before updating Apple source facts."""
        return port.reviews.pending_changes({"course_ids": course_ids})

    @tool
    def get_information_update_schema() -> dict:
        """Return the existing JSON schema for validated course-fact updates."""
        return port.information.schema()

    @tool
    def validate_information_update(update: dict) -> dict:
        """Validate the proposed changes and evidence without updating the fact store."""
        return port.information.validate({"update": update})

    @tool
    def apply_information_update(update: dict, review_batches: dict | None = None,
                                 confirmed: bool = False) -> dict:
        """Apply confirmed course facts using the existing store and optional Moodle checkpoint."""
        return port.apply_information({
            "update": update, "review_batches": review_batches or {}, "confirmed": confirmed,
        })

    @tool
    def acknowledge_pending_changes(batch: dict, confirmed: bool = False,
                                    reviewed_no_information_change: bool = False) -> dict:
        """Checkpoint a reviewed Moodle batch containing no changes to verified facts."""
        return port.acknowledge_changes({
            "batch": batch, "confirmed": confirmed,
            "reviewed_no_information_change": reviewed_no_information_change,
        })

    @tool
    def get_apple_sync_status() -> dict:
        """Read the configured Apple account and last synchronization receipt."""
        return port.apple.status()

    @tool
    def check_apple_sync() -> dict:
        """Inspect the available Apple Calendar and Reminders accounts."""
        return port.apple.check()

    @tool
    def get_apple_sync_projection() -> dict:
        """Preview the existing confirmed-fact projection without writing to Apple."""
        return port.apple.projection()

    @tool
    def sync_apple(confirmed: bool = False) -> dict:
        """Write the confirmed projection to the dedicated HIQS containers and read it back."""
        if not confirmed:
            raise HIQSPortError("Apple synchronization requires confirmation.")
        return port.apple.synchronize()

    return server
