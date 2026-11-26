# ADR 0003 — Standalone Codex plugin distribution

- Status: accepted
- Date: 2026-11-27

## Context

The repository ships the general HIQS Python package and the local Codex plugin.
Codex installs the plugin directory as a standalone package. Its launcher, prompts,
and Python runtime files must remain available from that directory after installation
or ZIP extraction. The two entry points expose different workflows and can read the
same HIQS data directory.

## Decision

- `src/hsas/` owns the shared implementation. Shared files in the plugin's
  `program/` directory are generated mirrors with the same relative paths.
- The plugin owns its narrower CLI and MCP entry points, runtime composition,
  collector adaptations, and prompts. The packager lists program files owned
  by the plugin so that an unexplained difference fails verification.
- Keep the mirrors in Git so a marketplace install can read a complete package
  from a checkout. Update a mirror from its canonical source with
  `python scripts/package_codex_plugin.py --sync`.
- Build the standalone ZIP with `python scripts/package_codex_plugin.py --output dist/hiqs-course-mastery.zip`.
  Package tracked files with stable ordering and metadata. The local gate and CI
  verify the mirrors and marketplace paths. The offline test extracts the ZIP
  and exercises the declared MCP launcher with a temporary data directory.

## Consequences

Shared rules have one editing location and both distributions retain their
existing installation paths. New plugin files must be added to Git before
packaging. Code specific to one distribution can evolve behind its existing
interfaces.
