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

Since Build reel 1 there are two more layers — see §10 (the viral pass, now the default):

5. **Pacing layer** — cold-open hook, jump-cut silence collapse, wide/1.12× punch-in alternation.
6. **Sound + meme layer** — SFX on every graphic event (mixed post-loudnorm), hybrid meme
   elements (Impact-font STONKS / FREE REAL ESTATE / NOPE. on the fintech cards).

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
**The folder name is whatever the creator dropped the clips into — it does not always match
`Research/VIDEO-PLANS.md`.** Build reel 3 lives in `Trading Videos/Actual build/`, not the
`Build Reel 3` the plan predicted. Find the footage, don't trust the planned path.

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
`HOOK (cold open) → INTRO → [TECHNIQUE A → TECHNIQUE B → …] → RECAP → TEASE (next video) → OUTRO → (meme button)`

**As of Build reel 1 the reel opens with a COLD-OPEN HOOK, not the "Welcome to day N" line**
— see §10. Pull the single strongest claim from anywhere in the footage to position 0 and cut
it from its original spot (no repeats).

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
- **White line is ALWAYS Indonesian, yellow ALWAYS English — even when the creator speaks
  English.** English-spoken lines get an Indonesian translation on the white top line (match his
  colloquial register: gua/lo/nggak). Never duplicate the English text on both lines — Reel 4's
  `make_ass.py` did that and it was flagged as wrong on Build reel 1; don't copy that pattern.
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
| Build 2 / DAY 7 | **Newspaper slam** — front page (masthead + BREAKING + "DAY 7" headline) spins in and unwinds into place, lands on spoken "seven" | Georgia Bold serif masthead/headline; `resize` + `rotate(expand=True)` spin, damped settle wobble |
| Build 3 / DAY 8 | **News-wire terminal** — window with traffic-light dots, a scrolling stock ticker tape, "DAY 8" in Impact green, typed `> booting news ingestion` + blinking cursor | Consolas Bold chrome; ticker is one string tiled at `-(t*150) % seg_w`; window seats in 0.14s so the DAY 8 stamp isn't clipped |

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

Also reusable from `Build reel 1/edit/` (the viral-pass reference, see §10):
- `render_v3.py` — per-range punch-in + post-loudnorm SFX mix wrapper around render.py.
- `make_sfx.py` — numpy SFX synthesizer (whoosh/pop/error/thud/ding).
- `build_overlays_v4.py` — hybrid meme cards: STONKS, FREE REAL ESTATE, NOPE. stamp,
  wiggling hook pill, blueprint DAY-6 sign.
- `edl_v4.json` — canonical viral-pass EDL (20 jump-cut ranges, punch flags, sfx events).
- `make_ass_v3.py` — per-range bilingual subtitle generator (jump-cut timeline).

And from `Actual build/edit/` (Build reel 3 — the current best starting point, §10.7-10.8):
- `render_v4.py` — **use this one.** `render_v3.py` plus a per-range `"vf"` field for any
  per-range look (B&W hook, flashback, one graded beat) without forking `render.py`.
- `build_overlays_v1.py` — the most defensive overlay builder so far. Copy its helpers wholesale:
  `fits()` (card-overflow assert), `appearing()` (raw-time entrance gate), the alpha-0 guard in
  `rounded()`, `meme_sticker()` (corner tag that doesn't bury the rows), `_wash()` (safe
  full-frame flash/fade), `render_explosion` (end card), `render_day8` (terminal intro sign).
- `edl_v1.json` — 27 jump-cut ranges, B&W hook `vf`, 13 overlays, 20 SFX, opaque end card.
- `make_ass.py` — bilingual ASS generator with a `check_lengths()` warning pass (flags any cue
  over 55 chars per language) and an overlapping-cue warning.
- `gaps.py` — dumps word-level timelines + silence gaps per source. Run this first when planning
  jump-cut ranges; it's how you find every silence ≥ 0.4s without reading raw JSON.

Keep version numbers in sync across `edl_vN.json` / `build_overlays_vN.py` / `master_vN.ass`.

---

## 10. THE VIRAL PASS — the format upgrade from Build reel 1 (now the series default)

### 10.0 Why this section exists (creator directive, 2026-07-10)
After Build reel 1's first clean edit (cut + subs + cards, the §0-§5 recipe), the creator said
the format was **"not the quality of a viral reel"** and approved four upgrades; after seeing
them he asked for **more sound effects and memes** ("maybe it'll attract more attention if
instead of professional animations, it's more funny animations"), chose **Hybrid** meme level,
and finally directed: *"put all the things you have learnt into the guide so we can replicate
this in the future — and next time do more research on sound effects and memes to complete
your arsenal."* So: every reel from now on gets the §0-§5 base PLUS the four layers below, and
**the next editor should spend time expanding the SFX/meme library before editing** (see 10.6).

### 10.1 Cold-open hook (biggest lever)
- First 1-1.5s decides retention. "Welcome to day N" is a dead opener — never open with it.
- Find the punchiest claim in the transcript (money numbers, "free", contrarian claims),
  move it to position 0, and **delete it from its original beat** (a repeat 50s later is
  noticeable). Build reel 1: "I can track and oversee multiple corporations without spending
  a dime" moved from TECH2's tail to the front; TECH2 now ends one line earlier.
- Give the hook its own overlay slot (Build reel 1: gold "$0 — TRACK EVERY CORPORATION" pill,
  pops on the payoff word, damped-wiggle after landing) + an SFX hit (money.mp3).
- Then the DAY-N sign plays over the *intro* beat, not at 0s.

### 10.2 Jump-cut silence tightening
- Collapse **every intra-clip silence ≥ 0.4s** by splitting the clip into multiple EDL ranges
  (pad ~80ms lead / ~100ms tail per range, word boundaries as always).
- Build reel 1: 7 ranges became 20; runtime 90.2s → 84.3s. Target runtime is 30-55s for pure
  educational shorts; long reels survive only if nothing sits still.
- **This moves every downstream payoff word** — all overlay sync constants and every subtitle
  offset must be recomputed per-range (make_ass SEGMENTS becomes one entry per range, cues
  mapped to the range that contains them; cues spanning a collapsed gap must be split in two).

### 10.3 Punch-in alternation
- Alternate wide / 1.12× punch at each cut **within the same source clip** (cuts between
  different clips already read as a reframe). Punch = `scale=-2:2150,crop=1080:1920:
  (iw-1080)/2:(ih-1920)*2/5` — the 40%-from-top bias keeps the face centered.
- Implemented as per-range `"punch": true` in the EDL, rendered by `edit/render_v3.py`
  (Build reel 1) — a thin wrapper importing `render.py` internals, because `render.py` only
  supports one global filter. Reuse that wrapper; don't fork render.py itself.
- **Wrapper cache trap:** `render_v3.py` skips extraction when the segment file exists. If you
  change any range times, DELETE `clips_v3*/` first or you silently render stale cuts.

### 10.4 SFX layer
- **Mix SFX AFTER loudnorm** (speech normalized to -14 LUFS first, then SFX summed on top at
  fixed gains) — otherwise normalization ducks/squashes them. `render_v3.py` does this.
- **THE amix TRAP:** ffmpeg's `amix` with default normalize re-scales every time a short SFX
  stream ends → speech crept +7 dB and clipped. Always `amix=inputs=N:duration=first:
  normalize=0` + `alimiter=limit=0.98:level=false`. Verify with `volumedetect` on an early vs
  late window — mean volume must match within ~1.5 dB, max ≤ -1.0 dB.
- Current arsenal:
  | Sound | File | Use |
  |---|---|---|
  | cash register | `meme audio/money.mp3` (trim 1.6s) | money claims, hook |
  | vine boom | `meme audio/vine_boom.mp3` (trim 1.0s) | sign/stamp landings |
  | MLG airhorn | `meme audio/airhorn.mp3` (trim 1.2s, gain ≤0.3) | celebratory banner |
  | fahh (fart horn) | `meme audio/fahh.mp3` | rejection / failure beats |
  | whoosh/pop/error/thud/ding | `Build reel 1/edit/sfx/*.wav` | card slides, badge pops, X marks, checks (synthesized — `make_sfx.py`, numpy, copy it) |
- Typical gains 0.25-0.55 against loudnormed speech. ~13-16 events per 85s reel; every card
  entry, badge pop, X, stamp and check gets one. Don't exceed ~1 event / 4s average.
- **Creator wants a BIGGER arsenal.** Before the next reel: research + download a proper meme-SFX
  pack (bruh, metal pipe, taco bell bong, discord ping, "oh no no no", Windows XP error, boom
  variations, riser/sub-drop transitions...) via `python -m yt_dlp -x --audio-format mp3
  "ytsearch1:<name> sound effect" -o "meme audio/<name>.%(ext)s"`. Also collect meme IMAGE
  assets (stonks man, doge, thug-life glasses, deep-fried emoji) into an `Assets/memes/` folder
  for compositing into cards.

### 10.5 Hybrid meme layer (the approved level)
Creator picked **Hybrid** from {SFX-only, Hybrid, Full meme chaos}: keep the navy fintech card
system (§5.2) for brand consistency, inject meme elements into it:
- Impact font (`C:/Windows/Fonts/impact.ttf`) + white/orange fill + 4px black stroke = the meme
  register. Used for: **STONKS** (tilted 8°, pops when the PEAD drift line completes),
  **IT'S FREE REAL ESTATE** (SEC card, -2° tilt, half-overlapping the card edge like a sticker),
  stamp text changed **SKIPPED → NOPE.**
- Comedic motion: damped-rotation wiggle after a pop landing
  (`6.0*exp(-2.2*(t-t0))*sin(9*(t-t0))` degrees, rotate the whole layer around the element).
- Meme text obeys ALL existing rules: top band, no element overlap (§5.3a — first STONKS
  placement landed on the EARNINGS BEAT label and had to move), payoff-word sync.
- Declined this reel (ask each time, don't assume): full-screen reaction-clip insert
  ("Whaaaat! Oh hell naw"), happy-cat meme tail. Both remain available in `meme video/` /
  `meme audio/`.

### 10.6 Misc traps learned on Build reel 1
- **Windows console encoding:** the helpers print "→" and crash under cp1252. Always run them
  with `PYTHONIOENCODING=utf-8`.
- **transcribe_batch.py only reads `.env` from the cwd**, and copying a `.env` that has a UTF-8
  BOM breaks `export`-style parsing. Write a fresh BOM-less `.env` into the reel folder.
- **Scribe timestamp collapse:** occasionally all word timestamps after some word are stamped
  with one identical time (Build reel 1 IMG_1045 after "techniques"). Cut edges at the collapsed
  region are fine (use the last good boundary + pad); mid-region subtitle splits must be
  estimated by ear.
- Deliver flow unchanged: preview → creator green light → final render (via the same wrapper,
  no `--preview`) → §7 shrink → `Final Vids/`.
- **Arial/Arial Bold have no `⚠` or `★` glyph** — they render as a tofu box (□) in PIL. Draw the
  shape instead (e.g. a filled `polygon` triangle + "!" for a warning marker); don't paste the
  unicode char. Learned on Build reel 2 (safety-card warning rows, newspaper masthead separator).
- **Profanity censor (beep):** `render_v3.py` supports an EDL `"beeps": [{"at": <out_s>, "dur": <s>}]`
  field (`apply_beeps()`): it mutes `[0:a]` in each window via `volume=0:enable='between(...)'` and
  lays a 1 kHz `sine` tone over it, runs AFTER the SFX mix, video stream-copied. Also censor the
  caption text to match (e.g. `shit`→`sh*t`). Build reel 2 beeped "shit" in the cold-open hook.
- **Expanding the SFX arsenal (§10.6 ask):** `python -m yt_dlp -x --audio-format mp3 --no-playlist
  "ytsearch1:<name> sound effect" -o "meme audio/<slug>.%(ext)s"`. TRAP: downloaded clips have
  leading silence/intro — the actual hit is NOT at t=0. Detect onset with
  `ffmpeg -i x.mp3 -af silencedetect=noise=-40dB:d=0.05 -f null -` (first `silence_end`), then
  pre-trim to a clean `*_t.mp3` (`ffmpeg -ss <onset> -t <keep>`) and reference THAT in the EDL, so
  the sound lands on the beat. Also dedup: `ytsearch1` sometimes returns the same video for two
  queries (Build reel 2: spongebob-fail == womp-womp). Keep no sound playing >2x across a reel.
  Build reel 2 library added: swoosh, riser, discord, xp-error, metal-pipe, sparkle, wow-anime,
  bruh, boing, record-scratch, sad-violin, womp-womp, wilhelm, emotional-damage, taco-bong,
  mario-coin, yippee, goofy-bonk, metal-gear-alert, baby-laughing, noo.
  Build reel 3 added the pre-trimmed `Meme Audio/scratch_t.mp3` (record_scratch had **6.26s** of
  leading silence — the worst offender yet, always run the onset check), `taco_t.mp3`, and
  `boom_t.mp3` (explosion, §10.8).
- **Watch the peak on the DELIVERED file, not just the master.** `alimiter=limit=0.98` holds the
  master at about -0.5 dBFS, but the §7 shrink's AAC re-encode overshoots and can land a loud hit
  at 0.0 dBFS. Build reel 3's explosion needed its gain dropped 0.45 → 0.32 to keep headroom
  after the shrink. Run `volumedetect` on the shrunk file over the loudest SFX window before
  delivering.
- **"Own build plan" reels don't need citation panels.** When the creator is explaining *his own*
  bot design (not citing academic claims), skip §5.4 entirely — no paper screenshots. Build reel 2
  (Day 7, news-trading-bot pipeline) shipped with 4 top-band graphics + intro sign and zero panels.

### 10.7 Traps learned on Build reel 3 (Day 8, 2026-08-11)

- **PIL fills with alpha 0 PUNCH HOLES through the card.** `ImageDraw` writes onto an RGBA layer
  by *replacing* pixels, not compositing — so a not-yet-visible row drawn at alpha 0 erases the
  card behind it and the background shows straight through. On playback it reads as an empty UI
  chip, not as a bug. Two causes and both need fixing:
  1. `ease_out_back(0)` can return a float **epsilon instead of exactly 0**, so a
     `p = ease_out_back(prog(...)); if p <= 0: continue` guard silently fails to fire.
     **Gate entrances on raw time** (`if t < t_in: continue`), never on the eased value.
  2. Make the shared `rounded()` helper `return` early when `fill[3] <= 0`. Belt and braces —
     it kills the whole class of bug at one call site.

  **The same trap bites ANY PIL draw at partial alpha, not just alpha 0** — it hit the explosion
  end card three separate ways. The rule for an overlay that must stay opaque: **only draw
  alpha-255 things directly onto the layer.** Everything that fades goes on its own transparent
  scratch layer and gets `Image.alpha_composite`d on:
  - full-frame washes (a white flash, a burn-to-black) — composite a solid `Image.new`, never
    `d.rectangle((0,0,W,H), fill=(...,a))`, which stamps alpha `a` across the *whole frame*
  - fading strokes (an expanding shockwave ring drawn with `outline=col+(a,)`)
  - fading fills (debris chunks, embers)

  Assert it. One line at the end of the render function catches every future regression:
  ```python
  assert layer.split()[3].getextrema()[0] == 255, "layer must stay opaque"
  ```
- **The §5.3c card-overflow trap is worse than it looks.** Row tops written as "150" read like
  absolute y but get added to `y0` (the card top), so a "150..330" layout actually lands at
  246..426 and overflows a card ending at 404. Add a `fits(*bottoms)` helper that raises on any
  **card-relative** bottom > `CY1 - CY0`, and call it in every stacked layout.
- **A full-card `meme_stamp` buries the rows it's supposed to punctuate.** Reel 3's CLUTCH. and
  SET AND FORGET sat dead-centre and hid the FINNHUB / TANPA INTERVENSI labels underneath. Use a
  full-card stamp ONLY when covering the card *is* the joke (BLOCKED? over the geo-check boxes).
  Otherwise use a `meme_sticker()`: same Impact + stroke + wiggle, but pinned to a bottom corner
  at ~60px so the rows stay readable. Same §5.3a no-overlap rule, applied to memes.
- **Every payoff needs ~0.8s of hold before the card's exit slide.** A stamp timed at
  `total - 0.5` lands *into* the slide-out and the viewer never reads it. Check every slot:
  `stamp_t0 + 0.35 (pop) + 0.8 (hold) <= total - dur_out`. Stretch the slot into the gap before
  the next one rather than rushing the pop.
- **Card alpha 238 is too transparent for a busy background.** This room's shelving reads through
  the card and binder rings look like empty UI elements. **Use alpha 251** for these reels.
- **Two motions at once during an intro sign muddies it.** If the sign's window slides in over
  0.28s while the big text also stamps at t≈0.05, the text is clipped by the frame edge for
  ~8 frames. Seat the window fast (≈0.14s) so it's home before the payoff text pops.
- **Check the LAST second of the button clip visually, not just by transcript.** Reel 3's outro
  clip ran 1.5s past the peace-sign wave: silence, a dead stare, then his hand filling the lens
  on the way to stopping the recording. Scribe labelled that handling noise `[efek suara]`, which
  looks like a real sound effect in the transcript. Cut on the last clean gesture frame (here src
  15.35) and lay a real SFX from `Meme Audio/` on the gesture instead.
- **This footage is framed tighter than reels 1-2** (hair top y500-680 wide; y423-468 after the
  1.12× punch, which lifts the head ~30px). Card box was raised/shortened to
  `CX0,CY0,CX1,CY1 = 80, 96, 1000, 404`. Re-measure hair-top per reel before reusing a card box,
  and remember the punch raises it further.
- **Flash-forward cold open (creator-directed, 2026-08-11):** the hook can be a *later* moment
  shown up front in **black and white** with a "COMING UP" sign, then replayed in place. Recipe:
  per-range `"vf": "hue=s=0,eq=contrast=1.20:brightness=-0.02,vignette=PI/4.5"` (needs the
  `render_v4.py` per-range `vf` field), plus a black/white broadcast slug overlay — deliberately
  NOT the navy fintech card, so it reads as "this clip is from later". Blinking red dot + drawn
  play triangle + "LATER IN THIS VIDEO" sub-label. §10.1's delete-it-from-its-original-spot rule
  still applies.
- **`render_v4.py` (this reel) = `render_v3.py` + per-range `"vf"`**, a raw ffmpeg filter string
  appended after the scale/punch stage. Use it for any per-range look (B&W hook, a flashback, a
  single graded beat) without forking `render.py`.

### 10.8 Explosion end card (creator-directed, 2026-08-12)

Kendrew's sign-off has him reach past the camera to stop the recording, so his hand sweeps over
the lens. Rather than cut before it, **let the hand cover the frame and detonate on it** —
`slot_explosion` in Build reel 3's `build_overlays_v1.py`.

- **No new machinery needed.** Extend the BUTTON range far enough to cover the hand-over-lens
  footage, then lay a **fully opaque** overlay on top. The footage underneath is hidden, so it
  doesn't matter that it's a blurry smear. This is how you append *any* end card without adding
  a synthetic range to the EDL.
- Find the cover point from luma stats, not by eye: `mean_luma` stays mid but **`stddev`
  collapses** (Reel 3 IMG_1121: 59.7 at src 15.35 → 23.1 at 15.60 → 8.7 at 16.20) as detail
  disappears behind the hand.
- Timing that worked: hand-cover visible +0.30s, then a 1.00s blast. Beat map (slot-relative):
  white flash 0-0.08, fireball expands 0.02-0.42 (`ease_out_cubic` to r≈1250, covers the 1102px
  corner radius), shockwave ring 0.05-0.55, debris 0.08-0.86, cool-to-soot from 0.38, burn down
  to near-black 0.60-1.00 with embers surviving. Last frame is near-black — a clean end screen.
- Draw the fireball as a **jittered polygon** (per-angle radius × 0.80-1.14 from a seeded
  `random.Random`), not an ellipse. A perfect circle reads as a graphic, not a blast.
- SFX: `Meme Audio/boom_t.mp3` (from `ytsearch1:explosion sound effect`, onset at 0.86s, trimmed
  to 1.6s with a 0.2s out-fade), **gain 0.32** on the impact frame — 0.45 survived the master's
  limiter at -0.5 dBFS but the §7 shrink's AAC pushed it to 0.0. See the §10.6 note on checking
  peaks on the delivered file.
- Obeys the opacity rule in §10.7 — every fading element on its own scratch layer, with the
  `getextrema()[0] == 255` assert at the end.

**TIMELINE DRIFT — target any end card off the MEASURED output, never the nominal offsets.**
Each extracted segment is rounded up to a whole frame, so the real concat runs ahead of the
summed EDL range durations by roughly 13ms per segment. Across Reel 3's 27 ranges that is
**+0.35s by the end** (nominal 89.90s, actual 90.29s). Mid-reel it is harmless — a 0.1-0.2s
offset on a 1.5s subtitle cue or a card reveal reads fine, which is why reels 1-2 shipped on the
nominal math without anyone noticing. At the very end it is fatal: the first pass fired the blast
0.35s early and then played 0.4s of footage *after* it, so he reappeared past the explosion.

Fix, and the rule for any future end card:
1. Render once, then `ffprobe` the real duration of `base_v4.mp4`.
2. Find the true cue point by scanning the rendered base, not the EDL (here: luma stddev per
   frame, 59.6 → 17.3 across out 88.90-89.20).
3. Set `start_in_output` from that measurement and make `duration` reach **past** the measured
   end, so no footage can survive the card. An overlay window running past the output is
   harmless; `enable='between(t,...)'` just stops.
4. Shift any hard-synced tail SFX by the same amount.
