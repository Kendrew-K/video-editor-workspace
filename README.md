# Short-Form Video Editing Workspace

Edit decision lists, transcripts, subtitle tracks and motion-graphics builders
for a run of vertical short-form videos (YouTube Shorts / Reels / TikTok), all
edited from a transcript rather than a timeline.

The point of the repo is the **edit as source code**: every cut is a range in a
JSON EDL, every overlay is a Python script that renders a PNG frame sequence,
every caption is a generated `.ass`/`.srt`. Re-running the scripts reproduces
the video, and a change to a cut is a diff instead of a drag.

## What is actually here

```
Trading Videos/<project>/edit/
    project.md              Running session notes: decisions, dead ends, why
    takes_packed.md         Every take, transcribed and labeled, for selection
    transcripts/*.json      Per-clip word-level transcripts
    edl_v*.json             The cut: which source, which range, which beat
    build_overlays_v*.py    Renders the motion graphics for that video
    make_ass.py             Builds the burned-in caption track
    master_v*.ass, *.srt    The caption track itself
Assets/
    make_distortion_transition.py   Reusable glitch transition generator
    screenshot_headline.py           Renders a news-headline citation card
fonts.py                    Cross-platform font lookup for the overlay builders
docs/superpowers/           Design docs and implementation plans
CLAUDE.md                   Workspace conventions and render commands
```

The `_v1 -> _v6` versions on the overlay builders are kept on purpose. The
header comment on each says what changed and why, so `build_overlays_v6.py`
carries the reasoning for five rejected approaches (the v6 header, for example,
records that animation and source screenshot must never share a frame).

## What is not here, and why

- **Source footage.** The `IMG_*.MOV` clips the EDLs reference are raw personal
  video, tens of GB. The transcripts of them are committed, so the edit is
  readable without them, but a render needs your own footage. EDL source paths
  are relative to the EDL file (`"../IMG_1045.MOV"`), so dropping your own
  clips beside the project folder is enough; `resolve_path` in video-use
  resolves them against the EDL's directory.
- **Rendered output.** Same reason. Regenerate it.
- **The render engine.** Editing is driven by
  [video-use](https://github.com/browser-use/video-use) (MIT), and the motion
  graphics kit is [hyperframes-student-kit](https://github.com/nateherkai/hyperframes-student-kit).
  Both are third-party, so they are gitignored rather than vendored here.

## Setup

```bash
git clone https://github.com/Kendrew-K/video-editor-workspace.git
cd video-editor-workspace

# 1. ffmpeg on PATH (v6+). ProRes 4444 support is required: alpha overlays
#    silently lose transparency under libvpx-vp9.
ffmpeg -version

# 2. Python 3.10+ for the overlay builders
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install pillow numpy

# 3. The render engine, alongside this repo
git clone https://github.com/browser-use/video-use.git
pip install -e video-use
```

Check that the overlay builders can find their fonts:

```bash
python fonts.py
```

It prints a resolved path per family, or names the ones you are missing. The
builders were written against Windows font files; `fonts.py` maps each family
to its macOS and Linux equivalents, and any single one can be overridden with
`OVERLAY_FONT_ARIALBD=/path/to/font.ttf`.

## Rebuilding one video

From inside a project's `edit/` directory:

```bash
# 1. Render the overlay frame sequences
python build_overlays_v1.py

# 2. Encode each slot to ProRes 4444 (alpha must survive; see above)
for s in animations/slot_*; do
  ffmpeg -y -framerate 30 -i "$s/frames/f_%05d.png" \
    -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le "$s/render.mov"
done

# 3. Build the caption track
python make_ass.py

# 4. Cut and render from the EDL (paths in the EDL point at your footage)
python ../../../video-use/helpers/render.py edl_v1.json \
  -o preview.mp4 --format vertical --preview
```

Everything targets 1080x1920 @ 30fps. Landscape sources (screen recordings) get
a blurred-background 9:16 treatment; mark those ranges `"type": "screen"` in the
EDL. `CLAUDE.md` has the full EDL schema and the draft/preview/final render
flags.

## Notes

- `project.md` in each folder is the useful artifact if you only read one thing.
  It is the running log of what was tried and rejected, including the ffmpeg
  gotchas that cost the most time.
- Overlay builders write PNG sequences, not video. Encoding is a separate step
  because a failed encode should not mean re-rendering thousands of frames.
