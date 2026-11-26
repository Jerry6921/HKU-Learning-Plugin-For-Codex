"""Exercise the packaged plugin through its marketplace launcher."""

from __future__ import annotations

import asyncio
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import sys
from zipfile import ZipFile

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from hsas.application.apple_projection import reminder_identity

from scripts.package_codex_plugin import MCP_CONFIG, PROGRAM, ROOT, package_bundle


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
                "get_apple_reminder_completion", "get_apple_sync_projection", "get_apple_sync_status", "get_evidence_content",
                "get_information", "get_information_update_schema", "get_pending_changes",
                "get_sync_status", "list_materials", "query_course", "run_ocr", "search_materials",
                "sync_apple", "sync_moodle", "validate_information_update", "verify_moodle_session",
            }
            snapshot = await session.call_tool("get_information")
            assert not snapshot.is_error
            info = snapshot.structured_content or json.loads(snapshot.content[0].text)
            assert info["available"] is False
            assert info["courses"] == []
            snapshot = await session.call_tool("get_apple_reminder_completion", {"item_ids": ["demo"]})
            assert not snapshot.is_error
            completion = snapshot.structured_content or json.loads(snapshot.content[0].text)
            assert completion == {
                "status": "not_configured",
                "items": {"demo": {"completed": None, "source": None}},
            }

    asyncio.run(check_runtime())


def test_completion_receipt_reuses_canonical_identity_and_preserves_unknown(tmp_path, monkeypatch):
    module_name = "bundled_apple_delivery"
    source = ROOT / PROGRAM / "src/hsas/core/services/apple.py"
    spec = spec_from_file_location(module_name, source)
    module = module_from_spec(spec)
    monkeypatch.setitem(sys.modules, module_name, module)
    spec.loader.exec_module(module)

    namespace = "9639226b-a87c-4e60-9720-46f04e59ff9d"
    identities = {key: reminder_identity(namespace, key) for key in ("due", "archived", "missing")}
    config = {
        "namespace": namespace, "account_mode": "icloud",
        "reminder_list_id": "list", "reminder_source_id": "source",
    }

    class Gateway:
        def execute(self, payload):
            assert payload == {
                "operation": "reminder-completion",
                "config": config,
                "identities": list(identities.values()),
            }
            return {
                "status": "ready",
                "items": [
                    {"identity": identities["due"], "completed": False, "source": "reminders"},
                    {"identity": identities["archived"], "completed": True, "source": "archive"},
                ],
            }

    apple_dir = tmp_path / "apple"
    apple_dir.mkdir()
    config_file = apple_dir / "config.json"
    config_file.write_text(json.dumps(config))
    service = module.AppleDeliveryService(tmp_path, Gateway())
    assert service.reminder_completion(["due", "archived", "missing", "due"]) == {
        "status": "ready",
        "items": {
            "due": {"completed": False, "source": "reminders"},
            "archived": {"completed": True, "source": "archive"},
            "missing": {"completed": None, "source": None},
        },
    }
    assert json.loads(config_file.read_text()) == config
    assert not (apple_dir / "state.json").exists()
