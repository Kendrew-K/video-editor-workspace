Can you research about privacy laws in Indonesia? Like what I need for my e-commerce website or my-- or, well, my website that takes in user data needs to have in order to be compliant and not get shut down. Thank you.# Video Editor Workspace

Short-form video editor for YouTube Shorts, Instagram Reels, and TikTok.
Powered by `video-use` (transcript-driven editing) + HyperFrames (motion graphics).

## Tools

| Tool | Location | Purpose |
|---|---|---|
| `video-use` skill | `video-use/video-use/` (registered at `~/.claude/skills/video-use/`) | Transcription, filler-word cutting, multi-source EDL, rendering |
| `hyperframes-student-kit` | `hyperframes-student-kit/` | Motion graphics overlays, title cards, lower thirds |
| FFmpeg | System PATH (v8.1.1) | All video processing |

## Starting a Session

1. Drop footage into any folder:
   - `face_cam.mp4` — your talking-head clip(s)
   - `screen_record.mp4` — your laptop/build recording(s)
2. Open Claude Code in that folder
3. Tell Claude: "Read the video-use skill and let's edit these clips into a short"

Claude will transcribe, propose an EDL in plain English, wait for your approval, then render.

## Output Format

All videos target **1080×1920 @ 30fps** (vertical 9:16) for Shorts/Reels/TikTok.

Always render with `--format vertical`:
- Face-cam clips (portrait): existing portrait scaling applies
- Screen recordings (landscape): blurred-background 9:16 treatment

Mark screen recording segments in the EDL with `"type": "screen"`.

## EDL Example (multi-POV)

```json
{
  "version": 1,
  "sources": {
    "face": "/abs/path/face_cam.mp4",
    "screen": "/abs/path/screen_record.mp4"
  },
  "ranges": [
    {"source": "face",   "start": 2.5,  "end": 18.0, "type": "face",   "beat": "INTRO"},
    {"source": "screen", "start": 0.0,  "end": 45.0, "type": "screen", "beat": "BUILD"},
    {"source": "face",   "start": 18.5, "end": 30.0, "type": "face",   "beat": "OUTRO"}
  ],
  "grade": "auto",
  "subtitles": "edit/master.srt"
}
```

## Render Commands

```bash
# Draft (fast, 720p — check cut points)
python helpers/render.py edit/edl.json -o edit/draft.mp4 --format vertical --draft --no-loudnorm

# Preview (1080p, evaluable)
python helpers/render.py edit/edl.json -o edit/preview.mp4 --format vertical --preview

# Final (1080x1920, loud-normalized, social-ready)
python helpers/render.py edit/edl.json -o edit/final.mp4 --format vertical --build-subtitles
```

## Cost Per Video

- ElevenLabs Scribe: ~$0.14–0.20 per 10-min video (cached — no re-charge on re-edits)
- Claude Code: covered by subscription
- FFmpeg / HyperFrames: free, runs locally

## Download Routing

When the user asks to download a **video** (from any URL), save it to:
```
meme video/
```

When the user asks to download **audio** (from any URL), save it to:
```
meme audio/
```

Create the folder if it doesn't exist. Use `yt-dlp` via `python -m yt_dlp`. For audio, add `-x --audio-format mp3` to extract audio only.

## Key Files in video-use

- `SKILL.md` — full editing craft and hard rules (Claude reads this automatically)
- `helpers/render.py` — render pipeline (supports `--format vertical` for 9:16 output)
- `helpers/transcribe.py` — single-file ElevenLabs Scribe transcription
- `helpers/transcribe_batch.py` — parallel batch transcription
- `helpers/pack_transcripts.py` — packs transcripts into `takes_packed.md`
- `.env` — ElevenLabs API key (`ELEVENLABS_API_KEY=...`)
