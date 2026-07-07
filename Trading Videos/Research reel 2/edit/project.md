# Research reel 2 — Day 3: "Alternative Data" (how funds predict prices before news)

## Session — 2026-06-17 (v1/v2: full build from raw clips, reframed top-band layout)

**Topic/beats:** Day 3 of the trading series. One concept: alternative data.
INTRO → SATELLITE (parking-lot imagery + transaction data, +10% acc) → WEB SCRAPING
(job listings/prices/downloads = growth factors) → GOOGLE TRENDS ('tarif'/'utang' search
spikes signal market moves; "barely an edge") → RECAP → TEASE (machine learning, next video).
14 raw clips, each a single clean take (no retakes to choose between). Cut = trim+stitch
chronologically. Final ≈ 89.1s.

**KEY DIFFERENCE FROM REEL 1 — framing.** This footage is shot close/high: head sits high &
large (hair-top ~y180, chin ~y870 of 1920), so there is NO natural empty top band like Reel 1
(whose head sat y900-1400). Dropping standard top-band graphics on it as-is lands them on the
forehead. User chose "punch-in & reframe down". Solution baked into the EDL `grade` field as a
raw ffmpeg graph (keeps render.py untouched — grade accepts raw filters):
  split -> blurred+darkened copy as background, foreground punched in 1.1x and shifted DOWN 620px
  over it. Head now sits ~y820-1570 (Reel-1-like), top band 0-620 freed for graphics, subs go
  below the chin. There IS a visible seam at y620 (sharp/blur boundary) but graphics/panels cover
  most of it. If revisiting, could feather the seam.
  Filter: split=2[fg][bgsrc];[bgsrc]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:6,eq=brightness=-0.30:saturation=0.40[bg];[fg]scale=1188:-2,crop=1080:1920:(in_w-1080)/2:0[fgc];[bg][fgc]overlay=0:620

**Overlays (top-band system inherited from Reel 1, build_overlays_v1.py):**
- spy_day3: NEW satellite/spy-HUD "DAY 3" sign (user picked this theme). Converging reticle
  brackets frame the head, crosshair, sweeping scanline, "SAT-LINK ESTABLISHED" + blinking REC +
  fake LAT/LON/ALT, "DAY 3" in HUD green, "● TARGET LOCKED" stamp pops at lock. Lands ~out 1.3
  ("three"). render_spy(). out 0.3, dur 2.9.
- gfx_satellite: parking-lot grid fills green + counter animates to 67,120 (matches paper's
  67,120 stores) + "+10% AKURASI" badge. out 17, dur 8.
- src_satellite: citation panel — Katona, Painter, Patatoukas & Zeng (2024), JFQA, "Evidence
  from Outer Space" (the parking-lot satellite paper). Screenshot = escholarship.org/uc/item/
  7s80w2v1 (clean, server-rendered). out 26, dur 7.
- gfx_webscrape: 3 counters (lowongan kerja 1.24M, harga produk 845K, downloads 3.41M) with
  bars + "→ SINYAL PERTUMBUHAN". Graph-only (no paper). out 39, dur 11.
- gfx_gtrends: search-volume area chart with a spike marked "lonjakan pencarian" + "→ gerakan
  pasar". Spike lands on "tarif atau utang" (~out 66.8). out 60, dur 9.5.
- src_gtrends: citation panel — Preis, Moat & Stanley (2013), Scientific Reports (Nature),
  "Quantifying Trading Behavior Using Google Trends" (the famous 'debt' study). Screenshot =
  nature.com/articles/srep01684, crop_y=95 to skip the top ad bar & exclude the cookie banner.
  out 70, dur 6.

**Subtitles (master_v1.ass):** bilingual ID (white) / EN (gold). v1 used two separate styles
(ID/EN) at MarginV 250/185 — libass collision-avoidance REORDERED the two lines (gold above
white) whenever BOTH wrapped to 2 lines. FIX: emit ONE Dialogue event per cue, `ID\NEN` with
inline \c color tags, single BL style MarginV 200. Order now consistent everywhere. MarginV
tuned so the block clears the reframed chin (~y1450).

**Pipeline notes:**
- ELEVENLABS_API_KEY lives in the skill's .env (has a BOM); export with sed BOM-strip. Set
  PYTHONUTF8=1 or transcribe_batch's "→" print crashes on cp1252 (transcripts still write).
- EDL overlay/subtitle paths are relative to the EDIT dir (the edl's folder): "animations/..."
  and "master_v1.ass" — NOT prefixed "edit/" (that double-resolves to edit/edit/...).
- Reused Reel 1's shot.mjs + node_modules for screenshots; render_src/palette/easing from
  build_overlays_v6.py.

**Files:** edl_v1.json, master_v1.ass, make_ass.py, build_overlays_v1.py, preview_v2.mp4
(89.1s, current good preview), base_preview.mp4, sources/{satellite_escholar,gtrends_nature}.png,
animations/slot_{spy_day3,gfx_satellite,src_satellite,gfx_webscrape,gfx_gtrends,src_gtrends}/render.mov

## Session — 2026-06-18 (v3: relocate +10% badge, add transaction source)

User caught two issues: (1) the "+10% AKURASI" badge was baked into gfx_satellite, so it
popped on the 67k-stores parking line (~21s) instead of the line that actually says it; (2)
only the parking-lot paper was cited — no source for the "beli data transaksi" claim.

Changes:
- Stripped the badge block out of render_satellite() (gfx_satellite is now grid+counter only).
- New render_akurasi() -> slot_gfx_akurasi: standalone hero "+10% AKURASI" pill + "MENURUT
  REPORT" label, badge_t=1.85. Overlay out 35.3 dur 3.8; pop lands on "sepuluh persen"
  (IMG_0955 word "sepuluh" src 7.059 - trim 1.88 + offset 32.37 = out 37.55). Verified.
- New src_transaction citation: screenshotted Paragon Intel "Consumer Transaction Data For
  Investors" (sources/transaction_paragon.png via Reel 1 shot.mjs); caption cites Paragon
  Intel / Daloopa (user-supplied URLs). render_src 5.0s, crop_y=0.
- Retimed citations to avoid full-bleed collision: src_satellite 25.0/5.0, src_transaction
  30.0/5.0 (was just src_satellite 26.0/7.0). NOTE: this re-timing of src_satellite was my
  call to make room — flag if you'd rather keep the parking citation longer/earlier.
- Self-eval at 21s/31s/37.6s all pass. preview_v3.mp4 = 89.4s, current good preview.

- User approved preview_v3. Final-rendered (final_v3.mp4, 119MB master, kept in edit/ as the
  master backup) then shrunk per EDITING_GUIDE §7 (CRF23 preset slow) -> "Final Vids/Research
  reel 2.mp4" = 51MB (~57% smaller), 1080x1920 h264/aac 89.4s. Spot-frame at 37.6s verified
  (badge crisp, subs sharp). DELIVERED.
- Updated EDITING_GUIDE.md with this session's learnings: §5.1a close-shot reframe punch-in;
  §5.3a one-claim-per-graphic / sync-to-line rule; §5.4 industry/provider sources (Paragon
  Intel/Daloopa) + eScholarship/Nature rows; two-citations-can't-overlap note in §5.1.

**Outstanding:** None — delivered. (If revisiting: feather the y620 reframe seam; consider
giving the parking-paper citation more screen time if 5s feels tight.)
On approval: render.py without --preview --build-subtitles=no (uses master_v1.ass) -> final,
then shrink (CRF 23 preset slow) -> "Final Vids/Research reel 2.mp4" per EDITING_GUIDE §7.
