#!/usr/bin/env python3
"""A'Space adapter for claude-video (fork Amdkn/claude-video, gel 03ceb42).

Contract-only surface, offline by construction: this module never imports
upstream code, never downloads, never calls a transcription provider, and
never touches the network. It only READS the skill tree and reports.

Commands (exit 0 = ok, exit 2 = structure failure):
  version             print skill version + gel + adapter version
  validate [path]     check the skill structure at <path> (default: repo root)
  doctor              offline posture, informative only (never prints secrets)
  env                 print the offline environment the adapter enforces

Stdlib only. No network import anywhere in this file (see smoke test 7).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
from pathlib import Path

ADAPTER_VERSION = "0.1.0"
PINNED_CLAUDE_VIDEO_COMMIT = "03ceb42f7fa2c4439aca01752118044baabffb8f"
SKILL_VERSION = "0.3.2"

REQUIRED_SCRIPTS = (
    "watch.py", "download.py", "frames.py", "transcribe.py", "whisper.py",
    "gemini.py", "local_whisperx.py", "setup.py", "config.py", "runtime.py",
)

API_KEY_VARS = ("GROQ_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY")


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _frontmatter_version(skill_md: Path) -> str | None:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    head = text[3:].split("---", 1)[0]
    match = re.search(r'^\s*version:\s*"([^"]+)"\s*$', head, re.MULTILINE)
    return match.group(1) if match else None


def _json_version(path: Path) -> str | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    version = data.get("version")
    return version if isinstance(version, str) else None


def cmd_version() -> int:
    print(f"claude-video {SKILL_VERSION} (gel {PINNED_CLAUDE_VIDEO_COMMIT[:7]}, "
          f"adapter {ADAPTER_VERSION})")
    return 0


def cmd_validate(path: Path) -> int:
    failures: list[str] = []
    skill = path / "skills" / "watch"
    skill_md = skill / "SKILL.md"
    if not skill_md.is_file():
        failures.append("missing skills/watch/SKILL.md")
    else:
        text = skill_md.read_text(encoding="utf-8")
        if "name: watch" not in text:
            failures.append("SKILL.md: name is not 'watch'")
        if "license: MIT" not in text:
            failures.append("SKILL.md: license is not MIT")
        version = _frontmatter_version(skill_md)
        if version != SKILL_VERSION:
            failures.append(f"SKILL.md version {version!r} != {SKILL_VERSION!r}")
    scripts = skill / "scripts"
    for name in REQUIRED_SCRIPTS:
        if not (scripts / name).is_file():
            failures.append(f"missing skills/watch/scripts/{name}")
    for label, rel in ((".claude-plugin", ".claude-plugin/plugin.json"),
                       (".codex-plugin", ".codex-plugin/plugin.json")):
        plugin = path / rel
        version = _json_version(plugin)
        if version is None:
            failures.append(f"missing or unreadable {rel}")
        elif version != SKILL_VERSION:
            failures.append(f"{label} version {version!r} != {SKILL_VERSION!r}")
    license_file = path / "LICENSE"
    if not license_file.is_file():
        failures.append("missing LICENSE")
    elif not license_file.read_text(encoding="utf-8").startswith("MIT License"):
        failures.append("LICENSE is not MIT")
    if not (path / "hooks" / "hooks.json").is_file():
        failures.append("missing hooks/hooks.json")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 2
    print(f"OK: claude-video {SKILL_VERSION} structure valid at {path}")
    return 0


def cmd_doctor() -> int:
    print("doctor: offline posture (informative, no network, no secret values)")
    for tool in ("ffmpeg", "ffprobe", "yt-dlp"):
        found = shutil.which(tool)
        print(f"  binary {tool}: {'present' if found else 'absent'}")
    for var in API_KEY_VARS:
        print(f"  {var} {'present' if os.environ.get(var) else 'absent'} "
              f"(boolean only, value never printed)")
    print("  telemetry: 0 third-party SDK in the skill; "
          "Pyannote metrics disabled by the code (PYANNOTE_METRICS_ENABLED=0); "
          "cloud backends (Groq/OpenAI/Gemini) only run with an explicit key")
    print("  adapter: never downloads, never calls a provider, never opens a socket")
    return 0


def cmd_env() -> int:
    print("DO_NOT_TRACK=1")
    print("WATCH_WHISPER_BACKEND=none  # no transcription provider, local files only")
    print("HF_HUB_OFFLINE=1  # no model download")
    print("HOME=<scratch>  # no ~/.config/watch/.env read by the adapter")
    return 0


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip().splitlines()[0])
        print("usage: validate.py {version|validate [path]|doctor|env}")
        return 0 if argv else 2
    command, rest = argv[0], argv[1:]
    if command == "--version":
        return cmd_version()
    if command == "version":
        return cmd_version()
    if command == "validate":
        target = Path(rest[0]).expanduser().resolve() if rest else repo_root()
        return cmd_validate(target)
    if command == "doctor":
        return cmd_doctor()
    if command == "env":
        return cmd_env()
    print(f"unknown command: {command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
