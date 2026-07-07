# Research reel 4 — project log

## Session 1 — 2026-06-29

**Strategy:** 12 clips, one take per beat, no multi-take selection needed. DAY 5: AI News Trading series. Natural headroom (bookshelf). No punch-in treatment required. Grade: none.

**Decisions:**
- EDL: 12 clips trimmed to 116.95s total. Dead air (~1.3–2s per clip) trimmed from each head.
- `(suara memasukkan kartu kredit ke mesin)` and `(suara berdecak)` in transcript are Scribe SFX notes, not speech — not subtitled.
- `(suara klik)` tail of IMG_1018 at src 11.18s cut off — uncaptioned sound effect.
- Outro "See you next time! Peace! Pshew!" left uncaptioned per series convention.
- Subtitles: bilingual ASS, ID white MarginV=200 + EN yellow (inline \\N same cue), ≤55 chars/line.
- "Kepala FDA of America" in IMG_1011 is a verbal slip (should be "Federal Reserve") — kept in ID subtitle as-is, EN subtitle silently corrects to "head of the Fed."

**7 overlay slots:**
- `slot_news_day5`: Breaking-news broadcast intro (BREAKING|NEWS banners + DAY 5 pop + LIVE badge), 2.9s, lands on "Day 5" at out ~17.1s
- `slot_gfx_expect`: Earnings surprise bar chart (FORECAST 250k vs ACTUAL 200k, GAP bracket), 9.0s over IMG_1009
- `slot_gfx_nlp`: Linguistic signal flow diagram (POWELL SPEECH → NLP PARSER → TRADE SIGNAL ▲▼), 7.5s over IMG_1014
- `slot_src_bloomberg`: BloombergGPT citation (arXiv:2303.17564), 5.5s over IMG_1016
- `slot_gfx_sharpe`: Sharpe 3.8 badge → CROWDED stamp flip, 6.0s over IMG_1019
- `slot_src_chatgpt`: Lopez-Lira & Tang (2023) citation (arXiv:2304.07619), 5.0s, immediately after sharpe badge
- `slot_gfx_agents`: Multi-agent debate diagram + RETURN +26% badge (Xiao et al. 2024), 8.5s over IMG_1020

**Citation sources used:**
- Bloomberg beat → arXiv:2303.17564 (BloombergGPT, Wu et al. / Bloomberg LP 2023)
- ChatGPT Sharpe 3.8 → arXiv:2304.07619 (Lopez-Lira & Tang 2023, GPT-4 strategy Sharpe 3.8 confirmed)
- Agent teams 26% → arXiv:2412.20138 (TradingAgents, Xiao et al. 2024) — cited inline in agents badge, no separate screenshot panel (would overlap with gfx_agents)

**Self-eval (Session 1):** All 8 spot-frames passed — top band clear on all overlays, face visible below on every frame, no black boxes (ProRes 4444 alpha correct), subtitles visible and not hidden, outro ends cleanly on "Pshew!" hand gesture at ~116.8s, duration 117.19s ≈ 116.95s expected ✓

**Status:** preview_v1.mp4 ready for creator review. Awaiting green light before final render + shrink → Final Vids/.

## Session 2 — 2026-06-29

**Round 2 feedback applied:**
- Agents box overflow fixed: AH 58→46, explicit `_BOX_AREA_Y0/Y1` bounds, gap derived from area (not top offset)
- +26% badge display extended: `T_RETURN` 7.77→4.50, overlay duration 8.5→10.5s (badge holds ~5s)
- Jerome Powell photo added (`slot_src_powell`): CNBC Jackson Hole article screenshot, start_in_output=38.0s, dur=6s

**Round 3 feedback applied:**
- All 6 em dashes removed from `make_ass.py` (trailing — → comma); `master_v1.ass` regenerated
- EDITING_GUIDE.md §4 updated: no em dashes rule added
- Hook animation `slot_gfx_hook` built (12s, start_in_output=0.50):
  - "2024" year stamp + "WALL STREET AI TRADERS" header + 4 strategy badges (✓ ACTIVE, green)
  - Diagonal "DEAD" stamp across full card at local t=9.02s (synced to "sudah mati" at output 9.52s)
  - v1 had badge overflow (BH=44 → 212px needed, 187px available); fixed to BH=38, positions derived from explicit area bounds
  - v1 had per-badge ✗ DEAD pills; replaced with full-card diagonal stamp per creator preference

**EDITING_GUIDE.md additions:**
- §5.3c: verify badge geometry before encoding (overflow trap + fix pattern)
- §5.3d: state-flip animation pattern (hold elements, composite diagonal stamp across card)

**Self-eval (Session 2):** preview_v3 spot-frames passed — hook badges contained within card on t=1–5s; DEAD stamp visible across card on t=9.5–11s; hook faded out by t=12.5s; no overlap with DAY5 intro at t=14.6s ✓

**Delivery:** final.mp4 rendered (211 MB) → shrunk to 84 MB → `Final Vids/Research reel 4.mp4` ✓
