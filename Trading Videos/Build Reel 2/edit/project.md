# Build Reel 2 (Day 7) — project log

## Session 1 — 2026-07-20

**Content:** Day 7 of the trading series. Topic: building the news-trading bot.
5-stage pipeline (baca berita / filter duplikat / cari stok / buy-sell decision /
cek aman) + why-dedup + basic rules (merger→buy) + kill-switch safety + 5-month
roadmap (M1 collect, M2 code rules, M3-4 backtest+paper, M5 live). Maps to the
News Trading Bot project.

**Strategy:** Full viral pass (guide §10). Cold-open hook = "Trading is hard as
shit" (creator-chosen, mild profanity kept). Newspaper-slam DAY 7 intro theme
(creator-chosen). Gunshot "Peace" ending kept as the button (uncaptioned). No
research-paper citation panels this reel — it's the creator's own build plan, not
academic claims.

**Cut:** 8 raw clips → 20 jump-cut ranges (silences ≥0.4s collapsed), punch
alternation within each source clip. Runtime 81.9s (raw ~104s). `edl_v1.json`.

**Overlays (5, all ProRes 4444, top band y120-455):**
- slot_pvz_day7 — newspaper front page spins in, lands "DAY 7" on spoken "seven"
- slot_gfx_pipeline — 5 numbered stage rows pop on each stage word
- slot_gfx_dedup — 3 duplicate headlines + red DUP X's + "NO EDGE" stamp on
  "it's no longer an edge" + green "FRESH NEWS ONLY" bar
- slot_gfx_safety — 2 warning rows + "KILL SWITCH" stamp on "kill switch"
- slot_gfx_roadmap — 4-phase month timeline (M3-4 merged), M5 "GO LIVE" gold glow

**Subtitles:** bilingual ID(white)/EN(yellow), `master_v1.ass`, 39 cues, colloquial
register. English-spoken lines translated to ID on the white line.

**SFX:** 19 events, post-loudnorm mix (`render_v3.py`). vine_boom on hook/newspaper/
kill-switch/gunshot, whoosh on card slides, pop on rows/nodes, fahh on NO EDGE,
airhorn on GO LIVE, ding on resolves. Audio consistency verified: 8-16s mean
-17.8 dB vs 62-70s -16.6 dB (within 1.5 dB), no amix creep.

**Self-eval:** passed. All graphics above face, alpha intact, subs synced, payoff
sync correct, duration matches.

**Deliverable:** `edit/preview_v1.mp4` (81.9s, 720p preview). AWAITING creator green
light before final render + Final Vids delivery (standing rule §1).

**New traps learned (added to guide):**
- Arial/Arial Bold has no ⚠ or ★ glyph → renders as a tofu box. Draw the shape
  (polygon triangle, etc.) instead of using the emoji/symbol char.
- "Own build plan" reels don't need citation panels — skip the paper-screenshot step.

**Outstanding:** Newspaper "7" (Georgia numeral) sits slightly low vs "DAY" —
cosmetic, left as-is (reads as newsprint).

## Session 2 — 2026-07-21 (revisions + ship)

Creator feedback on preview_v1 → preview_v2 → preview_v3 → SHIPPED.
- Trimmed SFX (removed newspaper boom @6s + hook boom); "too many, wrong places".
- Removed "DUP" text beside dedup X marks (§28s).
- Beeped "shit" (1kHz tone, speech muted 1.84-2.14s) + caption censored to "sh*t".
  New `beeps` field in EDL, `apply_beeps()` added to render_v3.py (mute window + tone).
- Removed fahh @32s.
- 60s: "Jadi" was cut off — pulled R14 start 1.80->1.02 (+0.78s), recomputed all
  downstream offsets (subs SEGMENTS 15-19, roadmap overlay start 58.00->58.78, all
  post-58 SFX). Added "Jadi,"/"So," cue.
- Expanded SFX arsenal: ~25 new meme sounds pulled via `yt-dlp ytsearch1` into
  `meme audio/` (swoosh, riser, discord, xp-error, metal-pipe, sparkle, wow, bruh,
  boing, record-scratch, sad-violin, womp-womp, wilhelm, emotional-damage, taco-bong,
  mario-coin, yippee, goofy-bonk, metal-gear-alert, baby-laughing, noo). Diversified
  mix, no sound >2x. Dropped discord ping per creator -> mario-coin blips; NO EDGE ->
  emotional-damage, safety warning -> metal-gear-alert, GO LIVE -> yippee.

**Shipped:** `Final Vids/Build reel 2.mp4` — 1080x1920 H.264, 82.8s, 59.2 MB
(from 143.6 MB master, ~59% smaller). Frame spot-check crisp. Master at
`edit/final.mp4`.
