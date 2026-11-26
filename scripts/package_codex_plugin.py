"""Check, refresh, or package the standalone Codex plugin."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import stat
import subprocess
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = Path("hiqs-course-mastery-bundle")
PLUGIN = Path("plugins/hiqs-course-mastery")
PROGRAM = BUNDLE / PLUGIN / "program"

# Every other program file is a generated mirror at the same path in the repository.
PLUGIN_OWNED = frozenset(map(Path, (
    "README.md",
    "docs/apple-integration.md",
    "pyproject.toml",
    "scripts/run-hiqs.sh",
    "src/hsas/__main__.py",
    "src/hsas/core/__init__.py",
    "src/hsas/core/facade.py",
    "src/hsas/core/ports.py",
    "src/hsas/core/services/apple.py",
    "src/hsas/core/services/reviews.py",
    "src/hsas/infrastructure/browser/__init__.py",
    "src/hsas/infrastructure/moodle/gateway.py",
    "src/hsas/infrastructure/moodle/progress.py",
    "src/hsas/mcp/__main__.py",
    "src/hsas/mcp/server.py",
)))

MARKETPLACE = Path(".agents/plugins/marketplace.json")
PLUGIN_MANIFEST = PLUGIN / ".codex-plugin/plugin.json"
MCP_CONFIG = PLUGIN / ".mcp.json"
PRIVATE_STATE = {
    "information.json", "connection.json", "storage-state.json", "sync-report.json",
    "course.json", "selectors.local.json", ".DS_Store",
}


def _tracked_files(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", str(BUNDLE)],
        cwd=root, check=True, capture_output=True, text=True,
    )
    files = sorted({Path(name) for name in result.stdout.split("\0") if name})
    if not files:
        raise ValueError("No tracked files found in the Codex plugin bundle")
    for relative in files:
        path = root / relative
        if not path.is_file() or path.resolve() != path:
            raise ValueError(f"Expected a regular bundle file: {relative}")
        inside = relative.relative_to(BUNDLE)
        if (relative.name in PRIVATE_STATE or relative.name.startswith(".env")
                or {".venv", "__pycache__", "resources", "browser-profile"}.intersection(inside.parts)):
            raise ValueError(f"Private or generated runtime state in bundle: {relative}")
    return files


def _refresh_mirrors(root: Path, files: list[Path], *, sync: bool = False) -> None:
    program = {path.relative_to(PROGRAM) for path in files if path.is_relative_to(PROGRAM)}
    if missing := PLUGIN_OWNED - program:
        raise ValueError("Missing plugin-owned paths: " + ", ".join(map(str, sorted(missing))))
    stale = []
    for relative in sorted(program - PLUGIN_OWNED):
        canonical, mirror = root / relative, root / PROGRAM / relative
        if not canonical.is_file() or canonical.resolve() != canonical:
            raise ValueError(f"Missing canonical source for plugin mirror: {relative}")
        contents = canonical.read_bytes()
        if mirror.read_bytes() != contents:
            if sync:
                mirror.write_bytes(contents)
            else:
                stale.append(str(relative))
    if stale:
        raise ValueError("Refresh plugin mirrors with --sync: " + ", ".join(stale))


def _check_layout(root: Path, files: list[Path]) -> None:
    bundled = {path.relative_to(BUNDLE) for path in files}
    marketplace = json.loads((root / BUNDLE / MARKETPLACE).read_text(encoding="utf-8"))
    manifest = json.loads((root / BUNDLE / PLUGIN_MANIFEST).read_text(encoding="utf-8"))
    entry = next((entry for entry in marketplace["plugins"] if entry["name"] == manifest["name"]), None)
    if entry is None or Path(entry["source"]["path"]) != PLUGIN:
        raise ValueError("Marketplace entry must point to the bundled plugin")
    skill_dir = PLUGIN / manifest["skills"]
    if not any(path.parent.parent == skill_dir and path.name == "SKILL.md" for path in bundled):
        raise ValueError("Plugin manifest must point to bundled skills")
    if PLUGIN / manifest["mcpServers"] != MCP_CONFIG:
        raise ValueError("Plugin manifest must point to the bundled MCP configuration")
    servers = json.loads((root / BUNDLE / MCP_CONFIG).read_text(encoding="utf-8"))["mcpServers"]
    for server in servers.values():
        launcher = server["args"][0].removeprefix("${PLUGIN_ROOT}/")
        if PLUGIN / launcher not in bundled:
            raise ValueError(f"Missing bundled MCP launcher: {launcher}")


def check_bundle(*, root: Path = ROOT, sync: bool = False) -> list[Path]:
    root = root.resolve()
    files = _tracked_files(root)
    _check_layout(root, files)
    _refresh_mirrors(root, files, sync=sync)
    return files


def package_bundle(output: Path, *, root: Path = ROOT) -> None:
    root = root.resolve()
    if output.resolve().is_relative_to(root / BUNDLE):
        raise ValueError("Output must be outside the Codex plugin bundle")
    files = check_bundle(root=root)
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent) as temporary:
        archive = Path(temporary) / "plugin.zip"
        with ZipFile(archive, "w", compression=ZIP_DEFLATED) as package:
            for relative in files:
                source = root / relative
                info = ZipInfo(relative.relative_to(BUNDLE).as_posix())
                mode = 0o755 if source.stat().st_mode & stat.S_IXUSR else 0o644
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | mode) << 16
                info.compress_type = ZIP_DEFLATED
                package.writestr(info, source.read_bytes())
        archive.replace(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--check", action="store_true")
    actions.add_argument("--sync", action="store_true")
    actions.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.output:
            package_bundle(args.output)
            print(args.output)
        else:
            files = check_bundle(sync=args.sync)
            print(f"Validated {len(files)} Codex plugin files")
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"Codex plugin: {exc}\n")


if __name__ == "__main__":
    main()
