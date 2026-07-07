# Trading Reels — Editing Guide

How to edit the "trading techniques" short-form series the same way **Research reel 1** was
edited, starting from raw phone clips. Written for the next editor (human or AI). Read this
top-to-bottom once, then use the cheat-sheet at the end per video.

This guide assumes the `video-use` skill is available (read its `SKILL.md` first — the **Hard
Rules** there are non-negotiable and are not repeated in full here). This document is the
*series-specific recipe* layered on top of that skill.

---

## STANDING RULES (apply to every session — read first)

1. **Never put anything in `Final Vids/` without an explicit green light from the creator.**
   Always render to `edit/preview_vN.mp4` first and wait for approval. The final-delivery command
   (§7) runs only after the creator says "looks good, ship it."

2. **Every edit session should update this guide.** If the creator gives any feedback that
   corrects a rule, changes a preference, or reveals a new trap, add it here before closing the
   session. The guide is the single source of truth for the next editor; stale rules cause
   repeated mistakes.

---

## 0. What the series looks like (the finished product)

Vertical 9:16 talking-head reels where the creator (speaks Indonesian, mixes in English)
explains one trading concept per video, broken into beats (one technique = one beat).
Each finished reel has four layers stacked on the raw footage:

1. **The cut** — raw clips trimmed and stitched chronologically by beat. No b-roll.
2. **Bilingual burned subtitles** — Indonesian (white, top line) + English translation
   (yellow, bottom line), every spoken segment.
3. **Top-band graphics** — explanatory motion graphs + research-paper citation panels, all
   living in the **top ~40% of the frame, above the head**.
4. **A themed intro sign** — a playful title card naming the episode ("DAY 2", etc.).

### The diff that defines a finished reel: `base_preview.mp4` → final

| | `base_preview.mp4` | final (`preview_vN.mp4`) |
|---|---|---|
| Cut / stitched segments | ✅ | ✅ |
| Color grade | none (`"grade": "none"`) | none |
| Burned subtitles | ❌ | ✅ bilingual ID + EN |
| Motion-graph overlays | ❌ | ✅ top band |
| Citation/paper panels | ❌ | ✅ top band, full-bleed |
| Themed intro sign | ❌ | ✅ |

`base_preview.mp4` is just the EDL rendered with no overlays/subs — keep it as a sanity
reference for the cut. **Everything else the editor adds is the four layers above.**

---

## 1. Output spec (always)

- **1080×1920, 30fps, vertical 9:16.** Render with `--format vertical`.
- All clips are portrait phone footage already, so no blurred-background treatment is needed
  (that's only for landscape screen-records — none in this series so far).
- Grade: **none.** The footage looks fine; don't grade unless asked.

---

## 2. The pipeline (raw clips → final)

Raw clips land in `Trading Videos/<reel name>/` as `IMG_####.MOV` (one clip per beat/take).

1. **Inventory + transcribe.** `ffprobe` each clip. Run `transcribe_batch.py` on the folder,
   then `pack_transcripts.py` → `takes_packed.md`. **Transcripts are cached per source — never
   re-transcribe** (Hard Rule 9). Cost ≈ $0.15/10min, charged once.
2. **Read `takes_packed.md`.** Note slips/false starts to avoid. This is the primary reading view.
3. **Assemble the cut (EDL).** One range per beat, chronological. Trim each clip to the clean
   take of its line. Pad cut edges 30–200ms, snap to word boundaries, 30ms audio fades at
   every boundary (the render handles fades). Output `edl_vN.json`.
4. **Write the subtitles** (`master_vN.ass`) — see §4.
5. **Build the overlays** (`build_overlays_vN.py`) — see §5. Encode each to ProRes 4444 `.mov`.
6. **Wire overlays into the EDL** (`overlays` array, `start_in_output` + `duration`).
7. **Render preview:** `render.py edl_vN.json -o preview_vN.mp4 --format vertical --preview`.
8. **Self-eval** (§6), iterate on feedback, then final render.

### Beat structure used for these reels
`INTRO → [TECHNIQUE A → TECHNIQUE B → …] → RECAP → TEASE (next video) → OUTRO → (meme button)`

Reel 1 had 4 techniques: PEAD, Analyst-driven momentum, Merger arbitrage, FDA/PDUFA.
A small meme clip (cat) was appended after the sign-off as a "button". Keep that pattern if
the creator supplies a meme tail; source it from `Final Vids/Intro Video.mp4` or wherever noted.

---

## 3. The cut (EDL conventions)

```json
{
  "version": 1,
  "sources": { "IMG_0909": "<abs path>", ... , "INTRO": "<abs path to meme tail>" },
  "ranges": [
    {"source": "IMG_0909", "start": 1.93, "end": 5.14, "beat": "INTRO", "quote": "..."},
    ...
  ],
  "grade": "none",
  "overlays": [ ... ],            // see §5
  "subtitles": "master_vN.ass",   // applied LAST, see §4
  "total_duration_s": 99.0
}
```

- `start`/`end` are seconds into each raw clip, on **word boundaries** (read them from the
  transcript JSON `words[]`).
- Most raw clips start with ~1.5–2s of dead air / setup — trim it (Reel 1 clips started clean
  around 1.0–2.0s).
- Keep one beat per range; order ranges by narrative beat, not filename.

---

## 4. Subtitles — bilingual, burned, applied LAST

- Format: ASS (`master_vN.ass`), generated by `make_ass.py`.
- **Exactly 2 lines on screen at any time:** 1 Indonesian (white, top) + 1 English (yellow,
  bottom). Never 4 lines (1 ID + 1 EN wrapping each = unacceptable). Enforce by splitting every
  cue to ≤55 chars per language line using word-level timestamps.
- Output-timeline offsets: `output_time = word.start − segment_start + segment_offset`
  (Hard Rule 5). `make_ass.py` already does this — feed it the EDL + transcripts.
- **Position low — below the chin, not the mouth.** Use `EN MarginV=120, ID MarginV=180`
  (ASS bottom-aligned: MarginV = distance from frame bottom to text bottom). This places subs
  at roughly y 1740–1840 in a 1920-tall frame. Never use MarginV values ≥ 490 — those push subs
  up onto the mouth/chin region.
- **Subtitles are the LAST thing in the filter chain** (Hard Rule 1). `render.py` handles this;
  don't burn subs into the base before overlays.
- **NEVER render with `--build-subtitles`.** That flag ignores `master_vN.ass` and burns
  `master.srt` instead — a single-line, UPPERCASE, Indonesian-only auto-caption at default
  (huge) size. It silently destroys the bilingual format. This is what broke Reel 4's first
  delivery. The EDL's `subtitles: master_vN.ass` is used automatically when you render *without*
  that flag — so always omit it. (Use `--no-subtitles` only for the `base_preview.mp4` sanity cut.)
- **Creator's name is "Kendrew" (one word).** Scribe transcribes it as "Ken Drew" — always
  override in the subtitle text.
- **No em dashes (—) in subtitle text.** Replace a trailing em dash with a comma; replace a
  mid-sentence em dash with a comma. Em dashes render inconsistently across players and look
  choppy at small subtitle sizes.
- The meme-tail/button clip is left uncaptioned (intentional).

---

## 5. Overlays — the design system (this is the important part)

### 5.1 THE TOP-BAND RULE
**Every graphic lives in the top ~40% of the frame (roughly y 0–760). Nothing goes over the
face.** In Reel 1 the head sits around y 900–1400, so the old mistake was placing graphs at
y 955–1290 — directly on the face. They were moved to a box at **y 120–455** (graphs) and the
citation panels occupy the full-bleed top strip **y 0–756**. Two cases:

- **Motion graphs** → navy rounded card, box `x0,y0,x1,y1 = 80, 120, 1000, 455`. All internal
  geometry is relative to that box, so to move a graph you change only that one line.
- **Citation / research-paper panels** → full 1080-wide screenshot strip, top 700px, with a
  56px navy caption bar under it. Slides down from the top, holds, slides back up.

Graphs and source panels for the same technique are shown **sequentially, never overlapping**
(graph first while explaining, then it slides away and the paper drops in as "proof").

**Two full-bleed citation panels can never overlap in time** — they're both top-strip
screenshots, so a second one drops on top of the first and you see neither. If two adjacent
claims each need a source, sequence them back-to-back (~5s each), don't stack them. (Reel 2:
the parking-lot paper at 25–30s, the transaction-data source at 30–35s.)

### 5.1a Close-shot footage — reframe to manufacture a top band
The top-band rule needs empty space above the head. Some clips are shot **close/high** (head
fills the upper frame, e.g. Reel 2: hair-top ~y180, chin ~y870) so there is **no natural top
band** — dropping graphics on as-is lands them on the forehead. Fix: bake a **punch-in-and-shift-
down** treatment into the EDL `grade` field as a raw ffmpeg graph (keeps `render.py` untouched —
`grade` accepts raw filters). Split the frame into a blurred+darkened background copy and a
foreground punched in ~1.1× and pushed **down** ~620px over it; the head drops to a Reel-1-like
y820–1570 and the top band 0–620 is freed for graphics, subs sit below the chin. There's a
visible seam at the punch boundary but graphics/panels cover most of it (feather it if revisiting).
Reference graph (Reel 2 `edl_v1.json`):
```
split=2[fg][bgsrc];[bgsrc]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:6,eq=brightness=-0.30:saturation=0.40[bg];[fg]scale=1188:-2,crop=1080:1920:(in_w-1080)/2:0[fgc];[bg][fgc]overlay=0:620
```

### 5.2 Palette + type (navy/green "fintech" look)
```
GREEN   (22,199,132)   accent / up-lines / highlights
GREEN_D (10,150,98)    marker fills
NAVY    (11,31,58)     caption bar
PANEL   (12,22,40)     graph card bg (alpha ~238)
WHITE   (255,255,255)  headings
DIM     (158,168,184)  sub-labels
RED     (235,90,95) / GOLD (245,196,90)   warnings / sell markers
Font: Arial Bold (C:/Windows/Fonts/arialbd.ttf), Arial (arial.ttf)
```

### 5.3 Engine: PIL → PNG frames → ProRes 4444 `.mov`
All Reel 1 overlays are PIL-drawn PNG sequences encoded to ProRes 4444.

- **ALPHA MUST BE ProRes 4444 on this machine.** `libvpx-vp9` SILENTLY drops alpha (outputs
  yuv420p) → overlays render as opaque black boxes over the face. This is the #1 trap.
  ```bash
  ffmpeg -y -framerate 30 -i frames/f_%05d.png \
    -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le render.mov
  ```
- One slot = one directory under `edit/animations/slot_<id>/` with `frames/` + `render.mov`.
- Easing is always cubic (`ease_out_cubic` for reveals, `ease_in_out_cubic` for draws), never
  linear. For bouncy intro elements use `ease_out_back` (overshoot).
- **Payoff sync:** start a reveal `reveal_duration` seconds *before* the payoff word so the
  landing frame coincides with the spoken word. Get the word's timestamp from the transcript.
  To convert a source-clip word time to output time:
  `out = word.start − segment_start + segment_offset` (segment_offset = running sum of prior
  range durations). Reel 2 example: "sepuluh" at src 7.059, clip trimmed at 1.88, offset 32.37
  → badge lands at out 37.55.

### 5.3c Verify badge geometry before encoding — overflow is invisible until playback
Always compute and verify that all boxes fit within the CARD boundary (`y0=120`, `y1=455`,
335px height) before running the encoder. The common trap: stacking N boxes where
`N * BH + (N-1) * GAP > available_height`. Fix: compute `_start_y` and `badge_ys[]` from
explicit `_BOX_AREA_TOP` / `_BOX_AREA_BOT` bounds, never assume a fixed top offset leaves
enough room. Reel 4 hook: `BADGE_TOP=268`, 4×BH=44+3×GAP=12 = 212px needed but only 187px
available → last badge clipped below card edge. Fixed by reducing BH to 38 and deriving
positions from `(BADGE_AREA_BOT - BADGE_AREA_TOP - total_h) // 2`.

### 5.3d "State-flip" animation pattern: hold all elements, then stamp the whole card
When an animation needs to show a state change (e.g. "ACTIVE → DEAD"), do NOT change each
element's label individually. Instead: keep all existing elements visible and composite a
large diagonal stamp across the **entire card** at the flip moment. Technique (same as
CROWDED in `render_gfx_sharpe`, and DEAD in `render_gfx_hook`):
```python
stamp_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(stamp_layer)
# draw stamp text centered on card center (scx, scy)
# draw red rectangle border around it
rotated = stamp_layer.rotate(-18, expand=False, center=(scx, scy))
layer = Image.alpha_composite(layer, rotated)
```
Use `pop(t, T_FLIP, 0.35)` so the stamp snaps in fast on the payoff word.

### 5.3a Animation elements must NEVER overlap each other
**Every element in a graphic must have a clear, non-overlapping position.** Before finalising an
animation layout, verify that no box, arrow, or label occupies the same screen region as another
at any frame. Common trap: reward/penalty boxes side-by-side with a too-small gap — if `box_right
> sibling_box_left`, they collide. Fix: spread boxes to opposite columns, or use a vertical stack.
Use a table (sequentially-appearing rows) instead of a line chart for concepts that show stepwise
reductions (fees, crowding, alpha decay) — line charts with overlapping dots/labels almost always
produce visual clutter. See `render_gfx_decay` (Reel 3) for the table pattern.

### 5.3b One claim = its own graphic, synced to the line that states it
**Do not bake a value-claim into a graphic that plays over a *different* line than the one that
says it.** Reel 2 trap: the "+10% AKURASI" badge was baked into the satellite/parking graphic,
so it popped on the "67k stores" line — ~16s before the line that actually claims the 10% lift.
Fix: pull the claim into its **own overlay slot** and time its pop to the payoff word on the
correct line (here, "sepuluh persen" at out 37.55). When you reuse a graphic across versions,
re-check that every label/badge on it still belongs to the line underneath it.

### 5.4 Research-paper citation panels — WHICH pages render and which don't
The panel should show a **single research paper page** (title, authors, abstract), NOT a search-
results list. Hard-won source reliability for headless screenshots (via `shot.mjs`, Playwright):

| Source | Result | Verdict |
|---|---|---|
| **RePEc / IDEAS** (`ideas.repec.org/a/...`) | clean server-rendered paper page | ✅ **USE THIS** |
| NBER (`nber.org/.../wXXXX`) | clean paper landing | ✅ ok when paper exists there |
| Semantic Scholar **search** page | renders, but it's a results LIST | ❌ looks like a search |
| Semantic Scholar **/paper/** detail | bot wall ("confirm you are human") | ❌ blocked |
| JSTOR | reCAPTCHA "Access Check" | ❌ blocked |
| SSRN | Cloudflare "verifying you are not a bot" | ❌ blocked |
| **eScholarship** (`escholarship.org/uc/item/...`) | clean server-rendered paper page | ✅ ok |
| **Nature** (`nature.com/articles/...`) | clean, but has top ad bar + cookie banner | ✅ use `crop_y≈95` |
| **Industry / provider explainers** (e.g. Paragon Intel, Daloopa blog posts) | clean article page, no bot wall | ✅ **when no paper exists** |

**Not every claim has an academic paper.** Some techniques (e.g. funds *buying* consumer
transaction data) are best evidenced by alternative-data **provider/industry explainers** rather
than a journal article. These screenshot cleanly (no bot wall) — use them, and caption with the
provider name(s): Reel 2 used Paragon Intel ("Consumer Transaction Data For Investors") with a
caption crediting `Paragon Intel / Daloopa`. The creator can supply the URLs. Prefer a page whose
**headline is a clean title** (it lands in the top-700px crop and reads like a source).

**Default to RePEc/IDEAS for academic papers.** Find the handle via the Semantic Scholar API match endpoint
(for the title/citation count) then map to the journal's IDEAS URL, or just search
`ideas.repec.org <paper title>`. Screenshot with:
```bash
node shot.mjs "https://ideas.repec.org/a/<handle>.html" "sources/<slug>.png" 4000
```
Crop happens in the build script (top 700px of the 1080-wide resize). IDEAS pages have no
cookie banner, so no masking needed. Caption format: `Author(s) (Year), Journal — short tag`.

### 5.5 Themed intro sign — one distinct style per episode
Each episode opens with a themed title sign, **different every reel**, timed to land on the
spoken episode number. The sign lives in the top band (y 0–455) so the face stays visible.
Duration ~2.5–3s. Encode as ProRes 4444 slot `slot_pvz_dayN` (keep slot name for EDL
compatibility even when the visual is no longer PvZ).

| Reel | Theme | Key technique |
|---|---|---|
| 1 / DAY 2 | **Plants vs. Zombies** wooden lawn sign | `ease_out_back` drop + damped pendulum sway |
| 2 / DAY 3 | **Satellite / spy HUD** — converging corner brackets lock on target | Sweeping scanline, "TARGET LOCKED" stamp pop |
| 3 / DAY 4 | **Neural network prediction** — nodes activate L→R, "DAY 4" scan-reveals as output | `alpha_composite` text reveal over live network |

**Reel 3 implementation notes (`render_ml_intro` in `build_overlays_v1.py`):**
- 3-layer net: 4 input nodes (gray) → 6 hidden (green) → 1 output node (large glow)
- Connections draw with `eio` easing between layers sequentially
- "DAY 4" in Arial Bold 148 revealed by a left-to-right scan line (bright white edge)
- Text must be composited with `Image.alpha_composite(cv, revealed_strip)` — **never**
  `cv.paste(txt_img, mask)` which destroys the panel background behind transparent pixels
- "MACHINE LEARNING" subtitle appears after scan completes
- Subtle binary rain in top ~90px (matrix flavour, alpha ≈ 55, `random.Random(42)` seeded)

---

## 6. Self-eval before showing the creator
Render the preview, then extract frames at: the intro sign landing, each graph window, each
paper-panel window, plus first/last 2s. Check every frame for:
- Sign/graph/panel over the **top band**, face fully visible below. (No graphic on the face.)
- Alpha correct (no black boxes — if you see one, the `.mov` lost alpha → re-encode ProRes 4444).
- Subtitles visible and not hidden by any overlay.
- Subtitles are the **bilingual two-line** format (white ID on top, yellow EN below) — NOT a
  single huge UPPERCASE line. A single line = `master.srt` leaked in (see §4); re-render without
  `--build-subtitles`.
- Overlay shows the right frames (PTS-shifted) and is synced to the right word.
- `ffprobe` the output duration ≈ `total_duration_s`.
Fix → re-render → re-check. Cap at 3 passes, then flag remaining issues.

---

## 7. Export / shrink the final for upload

`render.py` final output is high-bitrate (Reel 1 came out ~13.4 Mbps H.264, ~161 MB for 99s) —
fine as a master, but heavier than needed for upload. Re-encode the delivered file to a sane
bitrate before handing it off. Reel 1: **161 MB → 70 MB (~56% smaller)**, visually identical.

```bash
ffmpeg -y -i "Research reel 1.mp4" \
  -c:v libx264 -crf 23 -preset slow -pix_fmt yuv420p \
  -c:a aac -b:a 128k -movflags +faststart \
  "Research reel 1_shrunk.mp4"
```

- **CRF 23 / preset slow** is the sweet spot for these talking-head reels (mostly static frame
  → compresses well). Bump to CRF 25–26 if you want smaller; drop to 20–21 for a higher-quality
  master. Never go above ~26 (subtitle edges and the graph lines start to mush).
- **`-pix_fmt yuv420p`** is mandatory for broad player/upload compatibility.
- **`-movflags +faststart`** moves the moov atom to the front so it streams/previews instantly.
- Keep **H.264**, not H.265 — IG Reels / TikTok / YT Shorts all re-compress on upload anyway, and
  H.264 is the most universally accepted source. (H.265 CRF 28 would reach ~35–45 MB if you ever
  need a tiny file for messaging.)
- **Verify, then replace:** spot-check one frame from the shrunk file (graph crisp, subtitle
  edges sharp, no blocking), confirm it's actually smaller, *then* swap it in. Keep the original
  master as a `*_original.bak.mp4` until the creator signs off, then delete the backup (otherwise
  it eats back the space you just saved).

---

## 8. Per-video cheat-sheet

```bash
# 0. drop IMG_*.MOV into Trading Videos/<reel>/ , cd there
# 1. transcribe (cached) + pack
python <video-use>/helpers/transcribe_batch.py .
python <video-use>/helpers/pack_transcripts.py --edit-dir edit
# 2. read edit/takes_packed.md, write edit/edl_vN.json (ranges by beat)
# 3. write subtitles
python edit/make_ass.py            # -> edit/master_vN.ass  (bilingual, output-timeline)
# 4. screenshot paper sources (RePEc/IDEAS), build + encode overlays
node  edit/shot.mjs "<ideas url>" "edit/sources/<slug>.png" 4000
python edit/build_overlays_vN.py all
for s in edit/animations/slot_*; do
  ffmpeg -y -framerate 30 -i "$s/frames/f_%05d.png" \
    -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le "$s/render.mov"; done
# 5. wire overlays into edl_vN.json (start_in_output + duration), then preview
python <video-use>/helpers/render.py edit/edl_vN.json -o edit/preview_vN.mp4 \
    --format vertical --preview
# 6. self-eval (extract frames), iterate, then final:
#    NOTE: no --build-subtitles — that would override the bilingual .ass with master.srt (see §4).
python <video-use>/helpers/render.py edit/edl_vN.json -o edit/final.mp4 \
    --format vertical
# 7. shrink for upload (see §7), verify a frame, then deliver to Final Vids/
ffmpeg -y -i edit/final.mp4 -c:v libx264 -crf 23 -preset slow -pix_fmt yuv420p \
    -c:a aac -b:a 128k -movflags +faststart "Final Vids/<reel name>.mp4"
```

---

## 9. Reusable assets in `Research reel 1/edit/` (reference implementations)
- `build_overlays_v6.py` — overlay builder: `render_pead/merger/fda` (top-band graphs),
  `render_src` (full-bleed paper panels), `render_pvz` (themed intro sign). Copy & adapt.
- `make_ass.py` — bilingual ASS subtitle generator.
- `shot.mjs` (+ `package.json`, `node_modules`) — Playwright headless screenshotter for sources.
- `edl_v6.json` — canonical EDL example (cut + overlays + subs wired).
- `transcripts/*.json`, `takes_packed.md` — cached transcripts (immutable; reuse, don't redo).
- `project.md` — running session log; append one section per session.

Keep version numbers in sync across `edl_vN.json` / `build_overlays_vN.py` / `master_vN.ass`.
