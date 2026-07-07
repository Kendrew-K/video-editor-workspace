# Research reel 3 — project log

## Session 1 — 2026-06-24

**Strategy:** 12 clips, one take per beat, no multi-take selection needed. Natural headroom (bookshelf above head). No punch-in treatment required. Grade: none.

**Decisions:**
- EDL: 12 clips trimmed to ~86.7s total. Clicking sound at end of IMG_0984 dropped (cut at 9.64s).
- Subtitles: bilingual ASS, Indonesian white (ID style, MarginV 555) + English yellow (EN style, MarginV 490). Outro "Peace! Psheww" left uncaptioned intentionally.
- 10 overlay slots: PvZ DAY 4 sign, factor zoo bar chart, 3 citation panels, neural net diagram, 2 result badges, RL reward/punishment diagram, alpha decay line chart.
- Citation sources: Hou et al. → NBER w23394 (IDEAS URL 404'd); Gu et al. → NBER w25398 ✅; AlphaPortfolio (SSRN blocked, arXiv ID unknown) → substituted FinRL arXiv 2011.09607 for the RL beat.

**Reasoning log:**
- IDEAS RFS handle for Hou et al. returned 404 — NBER is the reliable fallback for this paper.
- AlphaPortfolio SSRN blocked and arXiv ID uncertain — FinRL covers the same beat (deep RL agents) and is the more recognisable citation anyway.

**Delivered (Session 1):** `Final Vids/Research reel 3.mp4` — 60 MB (from 137 MB preview, CRF 23 slow). ← placed WITHOUT green light, mistake noted.

---

## Session 2 — 2026-06-24 (corrections + redesign)

**Corrections applied (per creator feedback):**
1. Subtitles repositioned: EN MarginV=120, ID MarginV=180 — subs now at y≈1740–1840, below chin
2. All subtitle cues split to ≤55 chars using word-level timestamps — no line wraps
3. Creator name fixed: "Kendrew" (one word) at src 13.70–14.32 of IMG_0998
4. RL diagram redesigned: 3-zone non-overlapping layout (AGENT→MARKET→REWARD/PENALTY fork), word-synced to "rewards" t=3.12s, "cuan" pulse t=4.14s, "hukum" t=4.92s, "rugi" pulse t=6.06s
5. Alpha decay replaced with sequential table (GROSS ALPHA → −Fees → −Crowding → ~0%)
6. EDITING_GUIDE.md updated with all rules from this session

**Intro sign redesign (creator request):**
- Old: PvZ wooden sign (kept from Reel 1)
- New: `render_ml_intro` — neural network activates L→R (4 input → 6 hidden → 1 output node), "DAY 4" scan-revealed in white as prediction output, "MACHINE LEARNING" subtitle
- Key bug fixed: `Image.alpha_composite` instead of `cv.paste(mask)` — paste was destroying panel background behind transparent text pixels

**Self-eval (Session 2):** All 12 spot-frames passed — top band clear, no black boxes, subtitles below chin, no overlay hiding captions, duration 87s ✓

**Delivered:** `Final Vids/Research reel 3.mp4` — 63 MB (from 157 MB final master, CRF 23 slow). Green light given by creator.
