# Build reel 3 (Day 8) — project log

Folder is `Trading Videos/Actual build/` (not "Build Reel 3" — the creator dropped
the footage here).

## Session 1 — 2026-08-11 (cut, overlays, self-eval loop)

**Content:** Day 8 of the trading series, and the first "actually building it"
episode: news ingestion. Bloomberg priced out ($24k/yr) → Alpaca News API + SEC
EDGAR → geo-block scare ("bisa diakses di Indonesia?") → Finnhub as the fallback
→ webhook push → normalize → SQLite → backtesting later. Delivers Build reel 2's
CTA. Own-build-plan reel, so no citation panels (§10.6).

**Creator brief:** full viral pass as usual, plus one new directive — the hook is
the *later* line "Guys, I don't know if this is possible" (IMG_1110 @8.28), and
that first scene is **black and white with an "upcoming" sign on top**. Then edit
in a loop: render, judge it myself against the guide, fix, repeat.

**Cut:** 7 raw clips → 27 jump-cut ranges (silences ≥0.4s collapsed, three filler
"Nah,"/"Guys," beats dropped), wide/1.12× punch alternation within every source.
Runtime 89.0s from ~98s raw. `edl_v1.json`.

**Hook treatment (new):** R0 is the geo-block line pulled to position 0, rendered
B&W via a per-range `vf` (`hue=s=0,eq=contrast=1.20:brightness=-0.02,vignette=PI/4.5`)
— which needed a new `render_v4.py` (= `render_v3.py` + per-range `"vf"` field).
The sign is `slot_hook_upcoming`: a black/white broadcast slug (blinking red dot,
drawn play triangle, Impact "COMING UP", "LATER IN THIS VIDEO"), deliberately NOT
the navy fintech card so it reads as a flash-forward. The line is cut from its
original spot in the PROBLEM beat per §10.1.

**Overlays (12, all ProRes 4444, card box raised to y96-404 for this tighter
framing):** hook slug, DAY 8 news-wire terminal sign, sources (Bloomberg struck
out + NOT TODAY stamp → Alpaca/SEC free), why1 (Alpaca broker API), why2 (SEC
filing, with a "DAY 7" back-reference chip), geo BLOCKED? stamp, Finnhub swap +
CLUTCH. sticker, webhook flow with a travelling packet, autopilot + SET AND
FORGET sticker, normalize (2 formats → 1), SQLite cylinder → backtesting, and
LIKE/FOLLOW badges.

**Subtitles:** bilingual ID(white)/EN(yellow), `master_v1.ass`, 44 cues, ≤55 chars
per language line (`make_ass.py` warns on overflow). Button uncaptioned.

**SFX:** 19 events post-loudnorm, 1 per 4.7s. Two new trimmed clips added to
`Meme Audio/`: `scratch_t.mp3` (record_scratch had 6.26s of leading silence) and
`taco_t.mp3`. Speech-only windows measured -16.5 / -18.1 / -17.8 / -17.7 dB mean
(1.6 dB spread, non-monotonic → no amix creep), max ≤ -0.5 dBFS.

**Self-eval loop — 5 passes, 9 defects found and fixed:**
1. Card layouts overflowed the card bottom (rows written as absolute y, added to
   `y0`). Added a `fits()` assert on card-relative bottoms.
2. **Zero-alpha PIL fills punched transparent holes through the cards** — the
   worst one, invisible in code review. `ease_out_back(0)` returned a float
   epsilon so the `p <= 0` guard never fired. Fixed at both ends: `appearing()`
   gates on raw time, and `rounded()` refuses a fill with alpha 0.
3. CLUTCH. / SET AND FORGET stamps buried the rows they punctuate → converted to
   corner `meme_sticker()`s.
4. Card alpha 238 let binder rings read through → raised to 251.
5. NOT TODAY / BLOCKED? stamps too dim → new `RED_HOT`.
6. Payoff stamps landing into the exit slide (block, normalize, sqlite) →
   slots stretched, beats retimed, SFX moved to match.
7. DAY 8 sign clipped by the frame edge while it stamped mid-slide → window now
   seats in 0.14s.
8. Peak SFX riding the limiter at -0.4 dBFS → vine_boom/xperror/emotional trimmed.
9. Outro ran 1.5s past the peace-sign wave into a dead stare and a hand over the
   lens (Scribe had labelled the handling noise `[efek suara]`) → button cut at
   src 15.35, `yippee_t` laid on the wave instead.

All nine traps written into `EDITING_GUIDE.md` §10.7 + the intro-sign table.

**Deliverable:** `edit/final.mp4` (1080×1920, 89.0s) + `edit/preview_v5.mp4`.
**AWAITING creator green light before the §7 shrink and `Final Vids/` delivery**
(standing rule §1).

## Session 2 — 2026-08-12 (creator revision: explosion ending)

Creator reviewed session 1's cut: "everything looks good except for the final part". Asked to
**let his hand cover the lens** (extend that beat by 0.3s, instead of cutting before it as I had)
and to **end on an explosion**.

- BUTTON range 14.72→15.35 becomes 14.72→16.65. The hand-cover is visible for the extra 0.30s;
  the remaining 1.00s of hand-over-lens footage is the canvas for the blast and never shows.
- New `slot_explosion` (1.0s, opaque): white flash → jittered-polygon fireball → shockwave ring →
  debris → cool to soot → near-black with embers as the final frame.
- New SFX `Meme Audio/boom_t.mp3` at 88.90, gain 0.45. The `yippee_t` on the peace-sign wave stays.
- Runtime 89.0s → 89.9s.

**Trap hit again, harder:** the same alpha-replacement bug from session 1 bit the explosion three
more ways — the full-frame flash and burn-down `d.rectangle`s, the fading shockwave `outline`, and
the debris/ember fills all stamped partial alpha across the layer and let the footage show through.
Rule now written into the guide: on an overlay that must stay opaque, only alpha-255 draws touch
the base layer; everything that fades goes on a scratch layer and gets composited. Added a
`getextrema()[0] == 255` assert to `render_explosion` so it can't regress silently.
Guide updated: §10.7 (the wider rule) + new §10.8 (explosion end card recipe).

**Second trap, found on the first explosion render: timeline drift.** Every segment is rounded
up to a whole frame, so the real concat runs ~13ms/segment ahead of the summed EDL durations —
**+0.35s across 27 ranges** (nominal 89.90s, `base_v4.mp4` actually 90.22s). The blast fired
0.35s early and ~0.4s of footage played *after* it, so he popped back into frame past the
explosion. Retargeted off the measured output: scanned `base_v4.mp4` luma stddev (59.6 at out
88.90 → 17.3 at 89.20 as the hand fills the lens), set the overlay to 89.25 for 1.10s so it runs
past the end of the video, and shifted the tail SFX (boom 89.25, peace-wave yippee 88.62) to
match. Written up in guide §10.8.

This drift exists in reels 1-2 as well and is why mid-reel cues can sit a fraction late; it's
tolerable there (0.1-0.2s on a 1.5s cue) but must be measured for anything hard-synced at the end.

**SHIPPED 2026-08-12.** Creator approved the explosion ending ("looks good"). Delivered
`Final Vids/Build reel 3.mp4` — 1080×1920 H.264 yuv420p, 90.4s, 96.0 MB (from the 227.2 MB
master, 58% smaller). Master kept at `edit/final.mp4`. Delivered file spot-checked across
9 points end to end: hook, DAY 8 sign, sources, geo-block, Finnhub, normalize, SQLite, outro
badges, ember end frame — all graphics above the head, subs bilingual throughout, no blocking.

Guide updated this session: §2 (folder name may not match VIDEO-PLANS), §9 (Build reel 3 assets
listed as the current best starting point), §10.4/§10.6 (new SFX + check peaks on the *delivered*
file, not the master), §10.7, §10.8.

**Outstanding / worth a look on review:**
- 89.0s is long for the format (Build reel 2 shipped at 82.8s). Nothing sits
  still, but if you want it tighter the WHY beat (R5-R8, ~16s) is the softest.
- `slot_gfx_why1` / `why2` have a fair amount of empty card below the single row;
  fine, but a second row each would fill them if you'd rather.
