# Short-Form Video Editor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire up a Claude Code-driven short-form video editor (YouTube Shorts / Instagram Reels) that transcribes footage, cuts fillers, stitches multi-POV clips, applies 9:16 vertical framing, and outputs a social-ready final.mp4.

**Architecture:** `video-use` (Python + FFmpeg) is the editing brain registered as a Claude Code skill. `render.py` gains a `--format vertical` flag that applies blurred-background 9:16 framing to landscape screen recordings. A workspace `CLAUDE.md` orients every editing session.

**Tech Stack:** FFmpeg, Python 3.10+, ElevenLabs Scribe, HyperFrames (for animation slots), Claude Code skill junction on Windows.

---

## File Map

| Action | Path |
|---|---|
| Install | FFmpeg via winget → system PATH |
| Create junction | `~/.claude/skills/video-use/` → `video-use/video-use/` |
| Create | `video-use/video-use/.env` |
| Modify | `video-use/video-use/helpers/render.py` |
| Create | `CLAUDE.md` (Video Editor workspace root) |
| Delete | `video-use-tools/` |

---

## Task 1: Install FFmpeg

**Files:**
- System PATH (no project file)

- [ ] **Step 1: Install FFmpeg via winget**

Run in PowerShell (as any user — winget does not require admin for this package):
```powershell
winget install --id Gyan.FFmpeg -e --source winget
```
Expected output ends with: `Successfully installed`

- [ ] **Step 2: Reload PATH and verify**

Close and reopen the terminal (PATH changes require a new shell), then run:
```powershell
ffmpeg -version
```
Expected: first line reads `ffmpeg version 7.x ...`

If `winget` is not available, download the full build from https://www.gyan.dev/ffmpeg/builds/ and add the `bin/` folder to your user PATH via System Properties → Environment Variables.

---

## Task 2: Register video-use as a Claude Code Skill

**Files:**
- Create junction: `<USER_HOME>\.claude\skills\video-use\`

- [ ] **Step 1: Create the junction**

Run in PowerShell:
```powershell
New-Item -ItemType Junction `
  -Path "$env:USERPROFILE\.claude\skills\video-use" `
  -Target "<REPO_ROOT>\video-use\video-use"
```
Expected output: a new directory entry with `Mode` containing `l` (junction) in `~/.claude/skills/`.

- [ ] **Step 2: Verify the junction resolves**

```powershell
ls "$env:USERPROFILE\.claude\skills\video-use"
```
Expected: lists `SKILL.md`, `helpers/`, `skills/`, `pyproject.toml` — the contents of `video-use/video-use/`.

- [ ] **Step 3: Verify Python deps are installed**

```powershell
cd "<REPO_ROOT>\video-use\video-use"
pip install -e . --quiet
```
Expected: no errors. If `uv` is available, prefer `uv sync`.

---

## Task 3: Create .env for ElevenLabs Key

**Files:**
- Create: `video-use/video-use/.env`

- [ ] **Step 1: Create the .env file with a placeholder**

```powershell
$envPath = "<REPO_ROOT>\video-use\video-use\.env"
Set-Content -Path $envPath -Value "ELEVENLABS_API_KEY=paste_your_key_here" -Encoding utf8
```

- [ ] **Step 2: User fills in the key**

Open `video-use/video-use/.env` and replace `paste_your_key_here` with your actual ElevenLabs API key (the one from `video-use-tools/.env`).

- [ ] **Step 3: Verify the key is readable**

```powershell
python -c "
from pathlib import Path
import os
env = Path('<REPO_ROOT>/video-use/video-use/.env')
for line in env.read_text().splitlines():
    if line.startswith('ELEVENLABS_API_KEY'):
        key = line.split('=',1)[1]
        print('Key found, length:', len(key))
"
```
Expected: `Key found, length: 80` (ElevenLabs keys are 80 hex chars).

---

## Task 4: Add `--format vertical` to render.py

**Files:**
- Modify: `video-use/video-use/helpers/render.py`

This task adds blurred-background 9:16 treatment for landscape screen recording segments. It also handles landscape face-cam footage by center-cropping to 9:16. The EDL gains an optional `"type"` field on each range: `"screen"` triggers the blur treatment; all other values (including absent) use normal extraction.

- [ ] **Step 1: Add vertical constants after the `SUB_FORCE_STYLE` block (after line 56)**

In [render.py](video-use/video-use/helpers/render.py), after the `SUB_FORCE_STYLE = (...)` block, add:

```python
# -------- Vertical (9:16) format constants -----------------------------------

VERTICAL_W = 1080
VERTICAL_H = 1920
```

- [ ] **Step 2: Add `build_screen_blur_complex()` function before `extract_segment()`**

Add this function before the `extract_segment` definition (before line 152):

```python
def build_screen_blur_complex(duration: float, draft: bool = False) -> str:
    """Filter_complex for 16:9 landscape → 9:16 blurred-background treatment.

    Splits the source into two streams: one scaled+cropped+blurred to fill the
    9:16 canvas as background, one scaled to readable width and centered on top.
    Audio fade is included in the graph so -af is not needed separately.
    """
    if draft:
        bw, bh, fw, fh = 720, 1280, 640, 360
    else:
        bw, bh, fw, fh = VERTICAL_W, VERTICAL_H, VERTICAL_W, int(VERTICAL_W * 9 / 16)

    fade_out_start = max(0.0, duration - 0.03)
    return (
        f"[0:v]split[bg_src][fg_src];"
        f"[bg_src]scale={bw}:{bh}:force_original_aspect_ratio=increase,"
        f"crop={bw}:{bh},boxblur=20:5[bg];"
        f"[fg_src]scale={fw}:{fh}:force_original_aspect_ratio=decrease,"
        f"pad={fw}:{fh}:(ow-iw)/2:(oh-ih)/2[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2[vout];"
        f"[0:a]afade=t=in:st=0:d=0.03,"
        f"afade=t=out:st={fade_out_start:.3f}:d=0.03[aout]"
    )
```

- [ ] **Step 3: Add `extract_screen_segment()` function after `build_screen_blur_complex()`**

```python
def extract_screen_segment(
    source: Path,
    seg_start: float,
    duration: float,
    out_path: Path,
    preview: bool = False,
    draft: bool = False,
) -> None:
    """Extract a landscape screen recording with blurred-background 9:16 framing.

    Uses filter_complex (not -vf) because the blurred background requires
    splitting the input stream. Audio fade is embedded in the filter graph.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    filter_complex = build_screen_blur_complex(duration=duration, draft=draft)

    if draft:
        preset, crf = "ultrafast", "28"
    elif preview:
        preset, crf = "medium", "22"
    else:
        preset, crf = "fast", "20"

    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{seg_start:.3f}",
        "-i", str(source),
        "-t", f"{duration:.3f}",
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264", "-preset", preset, "-crf", crf,
        "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart",
        str(out_path),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
```

- [ ] **Step 4: Update `extract_all_segments()` to route screen segments**

In the `extract_all_segments()` function, replace the inner loop body (the block starting with `note = r.get("beat")...` and ending with `seg_paths.append(out_path)`) with:

```python
        seg_type = r.get("type", "face")
        note = r.get("beat") or r.get("note") or ""
        print(f"  [{i:02d}] {src_name}  {start:7.2f}-{end:7.2f}  ({duration:5.2f}s)  [{seg_type}]  {note}")

        if vertical and seg_type == "screen":
            print(f"        → blurred-background 9:16 treatment")
            extract_screen_segment(src_path, start, duration, out_path, preview=preview, draft=draft)
        else:
            if is_auto:
                print(f"        grade: {seg_filter or '(none)'}")
            extract_segment(src_path, start, duration, seg_filter, out_path, preview=preview, draft=draft)
        seg_paths.append(out_path)
```

Also add `vertical: bool = False` to the `extract_all_segments` signature:

```python
def extract_all_segments(
    edl: dict,
    edit_dir: Path,
    preview: bool,
    draft: bool = False,
    vertical: bool = False,
) -> list[Path]:
```

- [ ] **Step 5: Add `--format vertical` to argparse and wire it through `main()`**

In `main()`, add this argument after the `--no-loudnorm` argument block:

```python
    ap.add_argument(
        "--format",
        choices=["vertical"],
        default=None,
        help="Output format. 'vertical' enables 9:16 (1080x1920) with blurred-background "
             "treatment for EDL ranges marked type='screen'.",
    )
```

Then in `main()`, update the `extract_all_segments` call to pass `vertical`:

```python
    segment_paths = extract_all_segments(
        edl, edit_dir, preview=args.preview, draft=args.draft,
        vertical=(args.format == "vertical"),
    )
```

- [ ] **Step 6: Verify the flag is wired by running --help**

```powershell
cd "<REPO_ROOT>\video-use\video-use"
python helpers/render.py --help
```
Expected: output includes `--format {vertical}` in the options list.

- [ ] **Step 7: Smoke-test blurred-background filter with a test clip**

If you have any landscape .mp4 handy (even a 5-second clip), run:
```powershell
# Create a minimal test EDL
$edl = @"
{
  "version": 1,
  "sources": {"test": "C:/path/to/your/test_clip.mp4"},
  "ranges": [{"source": "test", "start": 0, "end": 5, "type": "screen"}]
}
"@
$edl | Out-File -FilePath "$env:TEMP\test_edl.json" -Encoding utf8

python helpers/render.py "$env:TEMP\test_edl.json" -o "$env:TEMP\test_vertical.mp4" --format vertical --draft --no-loudnorm
```
Expected: `test_vertical.mp4` created. Open it — screen should appear centered on a blurred version of itself, portrait 9:16.

---

## Task 5: Write Workspace CLAUDE.md

**Files:**
- Create: `<REPO_ROOT>\CLAUDE.md`

- [ ] **Step 1: Write the file**

Create `CLAUDE.md` at the Video Editor workspace root with this content:

```markdown
# Video Editor Workspace

Short-form video editor for YouTube Shorts, Instagram Reels, and TikTok.
Powered by `video-use` (transcript-driven editing) + HyperFrames (motion graphics).

## Tools

| Tool | Location | Purpose |
|---|---|---|
| `video-use` skill | `video-use/video-use/` (registered at `~/.claude/skills/video-use/`) | Transcription, filler-word cutting, multi-source EDL, rendering |
| `hyperframes-student-kit` | `hyperframes-student-kit/` | Motion graphics overlays, title cards, lower thirds |
| FFmpeg | System PATH | All video processing |

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
- Face-cam clips (portrait): center-scaled to fill 9:16
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

# Final (1080×1920, loud-normalized, social-ready)
python helpers/render.py edit/edl.json -o edit/final.mp4 --format vertical --build-subtitles
```

## Cost Per Video

- ElevenLabs Scribe: ~$0.14–0.20 per 10-min video (cached — no re-charge on re-edits)
- Claude Code: covered by subscription
- FFmpeg / HyperFrames: free, runs locally

## Key Files in video-use

- `SKILL.md` — full editing craft and hard rules (Claude reads this automatically)
- `helpers/render.py` — render pipeline (modified to support `--format vertical`)
- `helpers/transcribe.py` — single-file ElevenLabs Scribe transcription
- `helpers/transcribe_batch.py` — parallel batch transcription
- `helpers/pack_transcripts.py` — packs transcripts into `takes_packed.md`
- `.env` — ElevenLabs API key (`ELEVENLABS_API_KEY=...`)
```

- [ ] **Step 2: Verify the file exists**

```powershell
Test-Path "<REPO_ROOT>\CLAUDE.md"
```
Expected: `True`

---

## Task 6: Delete video-use-tools

**Files:**
- Delete: `video-use-tools/` directory

- [ ] **Step 1: Confirm ElevenLabs key is already in video-use/.env**

```powershell
$key = (Get-Content "<REPO_ROOT>\video-use\video-use\.env") -match "ELEVENLABS_API_KEY=(?!paste_your_key_here)"
if ($key) { Write-Host "Key confirmed — safe to delete video-use-tools" } else { Write-Host "Key not set — paste it first before deleting" }
```
Only proceed if output is `Key confirmed`.

- [ ] **Step 2: Delete video-use-tools/**

```powershell
Remove-Item -Recurse -Force "<REPO_ROOT>\video-use-tools"
```

- [ ] **Step 3: Verify it's gone**

```powershell
ls "<REPO_ROOT>"
```
Expected: `video-use-tools` no longer appears. `video-use` and `hyperframes-student-kit` remain.

---

## Self-Review Checklist

- [x] **Spec coverage:** FFmpeg install ✓, skill junction ✓, .env ✓, vertical render ✓, CLAUDE.md ✓, delete video-use-tools ✓
- [x] **No placeholders:** All steps have exact PowerShell/Python commands
- [x] **Type consistency:** `extract_all_segments(vertical=False)` in Task 4 Steps 4+5 match; `build_screen_blur_complex` called from `extract_screen_segment` only
- [x] **Order dependency:** Task 3 (key migration) confirmed before Task 6 (delete) via Step 1 guard
