# aspace-claude-video-adapter

A'Space adapter for **claude-video** (fork `Amdkn/claude-video`, gel `03ceb42`,
skill version `0.3.2`, MIT). Contract-only seam: the adapter never imports
upstream code, never downloads, never calls a transcription provider, and
never opens a socket. It only reads the skill tree and reports.

## Surface (stdlib only, offline)

```bash
python3 aspace-claude-video-adapter/validate.py --version
# claude-video 0.3.2 (gel 03ceb42, adapter 0.1.0)

python3 aspace-claude-video-adapter/validate.py validate [path]
# checks skills/watch/SKILL.md (name watch, license MIT, version 0.3.2),
# the 10 scripts, plugin versions (.claude-plugin + .codex-plugin),
# LICENSE (MIT), hooks/hooks.json. Exit 0 ok, 2 on structure failure.

python3 aspace-claude-video-adapter/validate.py doctor
# offline posture, informative: ffmpeg/ffprobe/yt-dlp present or absent,
# API keys present or absent (booleans only, values never printed),
# telemetry posture. Exit 0.

python3 aspace-claude-video-adapter/validate.py env
# the offline environment the adapter enforces (DO_NOT_TRACK=1,
# WATCH_WHISPER_BACKEND=none, HF_HUB_OFFLINE=1, HOME scratch).
```

## Smoke tests

```bash
python3 aspace-claude-video-adapter/smoke_test.py
# 7 tests, stdlib unittest only (one runs `doctor` under `unshare -n`).
```

## Telemetry

Zero by construction: no third-party telemetry SDK anywhere in the skill.
Pyannote metrics are disabled by the upstream code itself
(`PYANNOTE_METRICS_ENABLED=0` in `local_whisperx.py`). The cloud backends
(Groq, OpenAI, Gemini) only run with an explicit user key on a
user-triggered transcription; the adapter never calls them. `yt-dlp` and
`ffmpeg` only run on a user-triggered `/watch`; the adapter never invokes
them. See `../..` — the full audit is `claude-video-TELEMETRY-AUDIT.md`
in the V5 domicile `01_Forkable/FKB08_Plugins/00_A0_Core/`.
