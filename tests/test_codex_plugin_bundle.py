"""Exercise the packaged plugin through its marketplace launcher."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import sys
from zipfile import ZipFile

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from scripts.package_codex_plugin import MCP_CONFIG, package_bundle


def test_packaged_plugin_starts_and_reads_empty_state(tmp_path: Path) -> None:
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"
    package_bundle(first)
    package_bundle(second)
    assert first.read_bytes() == second.read_bytes()

    extracted = tmp_path / "extracted plugin"
    with ZipFile(first) as archive:
        archive.extractall(extracted)
    settings = json.loads((extracted / MCP_CONFIG).read_text(encoding="utf-8"))
    assert set(settings["mcpServers"]) == {"hiqs-course-mastery"}
    server = settings["mcpServers"]["hiqs-course-mastery"]
    plugin = extracted / MCP_CONFIG.parent
    parameters = StdioServerParameters(
        command=server["command"],
        args=[value.replace("${PLUGIN_ROOT}", str(plugin)) for value in server["args"]],
        env={
            **os.environ,
            "HSAS_DATA_DIR": str(tmp_path / "isolated data"),
            "HIQS_PLUGIN_PYTHON": sys.executable,
        },
    )

    async def check_runtime() -> None:
        async with (
            asyncio.timeout(15),
            stdio_client(parameters) as (reader, writer),
            ClientSession(reader, writer) as session,
        ):
            await session.initialize()
            assert {tool.name for tool in (await session.list_tools()).tools} == {
                "acknowledge_pending_changes", "apply_information_update", "check_apple_sync",
                "get_apple_sync_projection", "get_apple_sync_status", "get_evidence_content",
                "get_information", "get_information_update_schema", "get_pending_changes",
                "get_sync_status", "list_materials", "query_course", "run_ocr", "search_materials",
                "sync_apple", "sync_moodle", "validate_information_update", "verify_moodle_session",
            }
            snapshot = await session.call_tool("get_information")
            assert not snapshot.is_error
            info = snapshot.structured_content or json.loads(snapshot.content[0].text)
            assert info["available"] is False
            assert info["courses"] == []

    asyncio.run(check_runtime())
