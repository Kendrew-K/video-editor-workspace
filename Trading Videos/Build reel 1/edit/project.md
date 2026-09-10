# Build reel 1 — project log

## Session 1 — 2026-07-10

**Strategy:** Day 6 reel ("techniques for my trading bot"). 7 raw clips, one clean take
each — straight chronological stitch, no retake picking. Four layers per series recipe:
cut, bilingual ID/EN subs, top-band graphics, themed intro sign. Grade none. No meme tail
(none supplied).

**Decisions:**
- EDL `edl_v1.json`: 7 ranges, 90.42s total. Word-boundary cuts, ~100ms lead pad, ~250ms tail pad.
- Intro sign theme: **blueprint/drafting** ("DAY 6", grid + corner brackets + measure line,
  "BUILD PHASE — TRADING BOT" sub) — series is now in build phase. Slot kept as `slot_pvz_day6`.
- Overlays (5, all PIL → ProRes 4444):
  - `slot_gfx_tech1` PEAD card — flat price line, EARNINGS BEAT marker pop, drift line draw,
    synced to "beating its own expectations" (out 30.8).
  - `slot_gfx_tech2` SEC FILINGS card — doc stack, FREE/PUBLIC badges pop on spoken words
    (out 48.09/48.55), gold "$0 — TRACK EVERY CORPORATION" pill at "without spending" (out 56.15).
  - `slot_gfx_reject` — two X rows ("money" out 63.44, "corporations" out 65.68), diagonal
    red SKIPPED stamp at "terrible idea" (out 67.14) per guide §5.3d.
  - `slot_gfx_steps` roadmap — rows pop on "step two"/"step three", gold "= KTRADE BOT v1"
    banner at "KTrade" (out 77.03), green check at "done" (out 79.25). Geometry verified §5.3c.
- Subs `master_v1.ass` via `make_ass.py`: reel-4 pattern (single style, ID white \N EN yellow,
  MarginV=200). Outro "See you next time. Peace." uncaptioned. No citation panels this reel —
  both techniques already sourced in Research reels; only label cards used.
- No reframe needed: framing matches Reel 1 (natural top band above head).

**Reasoning log:**
- IMG_1045 Scribe glitch: word timestamps collapse after "techniques" (5.52→10.02 all stamped
  10.02). Intro cue splits estimated, cut end taken at 10.02+0.25.
- `.env` copied into reel folder (transcribe_batch only reads cwd/.env; source had UTF-8 BOM
  that broke `export`).
- Windows cp1252 console: helpers print "→" and crash — always run with `PYTHONIOENCODING=utf-8`.
- "$0" pill widened 620→740 after frame check (text overflowed pill).

**Output:** `edit/preview_v1.mp4` (90.59s, 1080×1920). Self-eval passed (2 frame grids, all
overlay windows + boundaries + outro checked).

**Outstanding:**
- Creator review of preview_v1 → then final render (NO --build-subtitles) + §7 shrink + deliver.
- Virality notes given to creator: hook weak ("Welcome to day six" opener), 90s long vs 30-55s
  sweet spot, no jump-cut/zoom energy. Optional sub-30s teaser cut offered.

## Session 2 — 2026-07-10 (same day, creator feedback round 1)

**Feedback applied:**
- IMG_1045 end 10.27 → 10.07 (−0.2s), IMG_1054 end 11.32 → 11.12 (−0.2s).
- All post-intro offsets shifted −0.2s (EDL overlay starts + make_ass SEGMENTS). Overlay
  frames untouched — internal payoff sync is relative to overlay start.
- Subtitles: English-spoken lines had EN duplicated on both lines (copied Reel 4 pattern).
  Creator wants white line ALWAYS Indonesian — added ID translations (colloquial gua/lo
  register) for every English line. Guide §4 updated with this trap.

**Output:** `edit/preview_v2.mp4` (total 90.02s).

## Session 3 — 2026-07-10 (viral pass v3 + meme pass v4)

**v3 (creator: "format not viral quality" — agreed, 4 upgrades approved):**
- Cold-open hook: TECH2's closing line ("track every corporation without spending a dime",
  IMG_1051 14.14-18.10) moved to position 0 with gold "$0" pill overlay + money.mp3. TECH2 now
  ends at "files." (no repeat).
- Jump cuts: every silence >=0.4s collapsed; 7 ranges became 20. 90.2s -> 84.3s.
- Punch-in alternation: per-range "punch": true = 1.12x center crop (40%-from-top bias),
  alternating wide/punch within each source clip.
- SFX layer: synthesized whoosh/pop/error/thud/ding (make_sfx.py, numpy) + money.mp3, mixed
  POST-loudnorm by edit/render_v3.py (wrapper reusing render.py internals).
- New files: edl_v3.json, make_ass_v3.py -> master_v3.ass, build_overlays_v3.py (all sync
  constants retimed), render_v3.py, make_sfx.py, slot_hook_pill.

**TRAP (fixed): ffmpeg amix renormalizes when short SFX streams end** — with default
normalize, speech crept +7 dB and clipped after the last SFX. Fix: `amix=normalize=0` +
`alimiter=limit=0.98`. Never use bare amix for SFX beds.

**render_v3.py segment cache:** skips extraction if seg file exists. If range times change,
DELETE clips_v3_preview/ + clips_v3/ first or you render stale cuts.

**v4 (creator: more SFX + memes; chose Hybrid via menu, no reaction-clip insert, no cat tail):**
- Overlays: hook pill damped wiggle; STONKS (Impact, orange) pops at PEAD drift completion;
  "IT'S FREE REAL ESTATE" Impact banner on SEC card (t=9.5); reject stamp now "NOPE." Impact.
  STONKS first landed on the EARNINGS BEAT label — moved to mark_x+330/base_y-60 (§5.3a).
- SFX (16 events): + vine_boom.mp3 (DAY6 land 4.85, NOPE stamp 62.19), airhorn.mp3 (v1 banner
  71.91, g0.28), fahh.mp3 (2nd X 60.73), pops on STONKS/meme banner. vine_boom + airhorn
  downloaded via yt-dlp into meme audio/.
- Timeline/subs/cut identical to v3 (master_v3.ass reused).

**Output:** `edit/preview_v4.mp4` (84.3s). Audio verified flat (-16.8 dB tail, -1.0 dB peak).

**DELIVERED (creator green light):** final_v4.mp4 (179 MB master, kept in edit/) → shrunk
CRF 23 → 72 MB → `Final Vids/Build reel 1.mp4` (84.26s). Shrunk frame verified crisp,
audio flat (-15.8 dB mean tail, -0.8 dB peak). Guide §10 written this session.
Optional ideas parked: sub-30s technique-1 teaser; music bed (no suitable stock on disk).
Next session directive: research + download bigger meme SFX/image arsenal BEFORE editing.
