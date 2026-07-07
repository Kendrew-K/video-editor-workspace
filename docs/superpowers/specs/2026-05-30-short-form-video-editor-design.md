# Short-Form Video Editor — Design Spec
**Date:** 2026-05-30  
**Status:** Approved

## Goal

A Claude Code-driven video editor for short-form social content (YouTube Shorts, Instagram Reels, TikTok). Takes raw footage from multiple sequential recordings — face cam and screen recordings — and produces a polished 1080×1920 vertical final.mp4.

## Tool Stack

| Tool | Role |
|---|---|
| `video-use` (Python + FFmpeg) | Primary editing brain: transcription, filler-word cutting, multi-source EDL, rendering |
| `hyperframes-student-kit` (HTML + GSAP) | Motion graphics: overlays, title cards, lower thirds — called as animation slots inside video-use |
| ElevenLabs Scribe | Word-level transcription (~$0.14–0.20 per 10-min video, cached) |
| FFmpeg | All video processing — local, free |

## What Gets Cleaned Up

- `video-use-tools/` — **deleted** (redundant duplicate of `video-use/video-use/`). ElevenLabs key migrated by user before deletion.
- `video-use/video-use/` — **kept**, registered as a Claude Code skill
- `hyperframes-student-kit/` — **kept** as animation slot source

## Per-Video Workflow

```
1. Drop footage into any folder
   ├── face_cam.mp4        ← talking head clips
   └── screen_record.mp4   ← laptop/build recordings

2. Open Claude Code in that folder
   → video-use skill activates automatically

3. Claude transcribes face cam (ElevenLabs Scribe, word-level, cached)
   → Reads takes_packed.md
   → User describes structure: "intro on cam → show build → outro on cam"
   → Claude proposes EDL in plain English

4. User approves EDL

5. Automated render pipeline:
   face_cam segments    → center-crop to 9:16
   screen segments      → blurred-background 9:16 treatment
   → lossless concat
   → HyperFrames animation slots (parallel sub-agents)
   → captions burned LAST
   → final.mp4 (1080×1920 @ 30fps)

6. Claude self-evals every cut boundary before showing output

7. Session memory saved to edit/project.md
```

## Multi-POV Stitching

Sequential recordings (different clips, same story). EDL references multiple named source files. Claude picks segments from each based on transcript and user-described structure, then concats in order.

## 9:16 Screen Recording Treatment

**Blurred background**: source screen recording (16:9) is scaled to fill the full 9:16 canvas with heavy blur applied, then the sharp original is centered on top at a size that preserves readability.

FFmpeg filter (per screen segment):
```
[0:v]scale=1080:1920,boxblur=20:5[bg];
[0:v]scale=1080:608:force_original_aspect_ratio=decrease[fg];
[bg][fg]overlay=(W-w)/2:(H-h)/2
```

## One-Time Setup

1. Register `video-use` as Claude Code skill (Windows junction to `~/.claude/skills/video-use/`)
2. User pastes ElevenLabs key into `video-use/video-use/.env`
3. Verify FFmpeg on Windows PATH (install via winget if missing)
4. Add `--format vertical` flag to `video-use/video-use/helpers/render.py` applying the 9:16 profiles above
5. Write workspace `CLAUDE.md` at Video Editor root to orient Claude Code to the workflow
6. Delete `video-use-tools/`

## Cost Per Video

- ElevenLabs Scribe: ~$0.14–0.20 per 10-min video (cached, no re-charge on re-edits)
- Claude Code: covered by subscription
- FFmpeg / HyperFrames: free, runs locally
