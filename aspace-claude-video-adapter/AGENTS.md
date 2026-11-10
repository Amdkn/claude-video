# aspace-claude-video-adapter — AGENTS.md (local)

This directory is the A'Space adapter for claude-video. It is the only
A'Space code in this fork; everything else is upstream (`bradautomates/claude-video`).

- **Read-only on upstream.** The adapter only reads the skill tree
  (`skills/watch/`, plugins, `LICENSE`, `hooks/`). It never edits, moves,
  or deletes an upstream file — the skill must stay one self-contained
  folder (`skills/watch/` with `SKILL.md` and `scripts/` as siblings).
- **Offline by construction.** No network import, no download, no provider
  call, no socket. `validate.py` is stdlib only.
- **No secrets.** `doctor` reports API-key presence as booleans only; it
  never prints a value. Never commit a real key or `.env` content.
- **Version rule.** The skill version (`0.3.2`) must stay in sync across
  `skills/watch/SKILL.md` (`metadata.version`), `.claude-plugin/plugin.json`
  and `.codex-plugin/plugin.json` — `validate` enforces it (exit 2 on drift).
