# Contributing

HIQS is an AI Skill Set with Notion as its primary workspace. Edit product
workflows and authored guidance in `skills/<skill>/`; add reusable deterministic
capabilities to the existing Python services through `HIQSPort`. Keep the MCP
and CLI adapters thin. Repository engineering guidance lives separately in
`.agents/skills/hiqs-product-development` and is not a student-facing Skill.

Product skill directories under `.agents/skills` and the old `src/AI_Skills`
path are relative links to `skills/`. Edit the canonical source, preserve each
Skill's references and metadata, and verify its local links. Package product
Skills independently of the Python wheel:

```bash
python scripts/package_agent_skills.py --output work/hiqs-agent-skills.zip
```

Keep all intended public scripts/assets with the Skill; private runtime files
belong outside `skills/`. The packager includes every non-hidden resource,
excluding Python bytecode, and rejects symlinks inside distribution sources.
Validate changed Skills with the skill-creator quick validator when available.

After changing `skills/` and completing its checks, install the current
product Skills into the local Agent environment:

```bash
python scripts/install_agent_skills.py
```

This is the user's standing development requirement. The installer defaults to
`$CODEX_HOME/skills` or `~/.codex/skills`; `--destination` selects another local
Agent directory. It verifies installed content, skips identical versions,
backs up replaced directories outside Skill discovery, and rolls back failed
replacements. Inspect its report before declaring delivery complete. This does
not configure MCP or credentials. New Skills are available on the next turn.

Keep user data outside the checkout. Git tracks source and public fixtures;
`.env`, browser profiles, downloaded course materials, extracted text, and
`information.json` stay in the private runtime directory.

Install and verify changes with:

```bash
python -m pip install -c requirements.lock -e '.[dev]'
python scripts/check_all.py
```

`scripts/check_all.py` runs lint, checks contract snapshots and the Codex bundle,
and runs the offline test suite.

Preserve the dependency direction documented in `ARCHITECTURE.md`. Collector
changes require download-coverage, last-known-good and failure-path tests.
Information changes require strict-schema, atomic-upsert, and data-preservation tests;
calendar changes require API and browser-level rendering checks.

## Working on the Codex plugin

Edit plugin prompts under `hiqs-course-mastery-bundle/plugins/hiqs-course-mastery/prompt/`.
Edit shared program files at their canonical repository paths, then refresh the
plugin mirrors. Stage any new bundle files before packaging.

```sh
python scripts/package_codex_plugin.py --sync
python scripts/check_all.py
python scripts/package_codex_plugin.py --output dist/hiqs-course-mastery.zip
```

CI packages the standalone plugin and general HIQS skills, tests the Python
package, and checks the wheel. See [the distribution ADR](docs/adr/0003-standalone-codex-plugin.md).

## Code layout

Place code under the architectural `hsas/domain`, `hsas/application`,
`hsas/infrastructure`, `hsas/core`, `hsas/cli`, `hsas/viewer`, `hsas/mcp`, or
`hsas/codegen` hierarchy. Use responsibility-oriented, lowercase snake_case module
names such as `material_search.py`, `change_tracking.py`, `course_publisher.py`, or
`session_store.py`. Generic action prefixes such as `define_`, `manage_`, `build_`,
and `run_` are reserved for function names rather than module names. Group related
adapters and services into focused subpackages instead of adding loose modules at
the package root. Tests retain pytest's `test_*.py` naming convention.
