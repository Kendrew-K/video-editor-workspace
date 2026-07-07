
## Session — 2026-06-13 (v6: PvZ DAY 2 sign, graphs to top band, real paper pages)

**Strategy:** Three user changes on preview_v5. (1) Add a Plants-vs-Zombies themed "DAY 2"
sign over the head during the intro. (2) The graph animations were still covering the face —
moved all three to the TOP band (same zone as the citation panels). (3) PEAD + Merger sources
were Semantic Scholar SEARCH-RESULTS lists — replaced with single-paper pages.

**Decisions:**
- build_overlays_v6.py: added render_pvz() — wooden hanging lawn sign (posts+board, plank grain,
  bolts, sunflower + leaf accents), "DAY 2" in cartoon lawn-green w/ thick dark outline. Drops in
  with ease_out_back overshoot landing at overlay-local 1.0s = output 1.4s (on the word "day",
  src 3.28). Then damped pendulum sway. Slot slot_pvz_day2, overlay out 0.4–3.2 (dur 2.8/2.9 mov).
- Moved all three graph boxes from y 955–1290 (over face) to y 120–455 (top band). One-line change:
  the x0,y0,x1,y1 constant in render_pead/merger/fda — every internal coord is relative to it.
- Paper pages: Semantic Scholar /paper/ detail pages now hit a bot wall; PDFs gated. Used RePEc
  IDEAS abstract pages (server-rendered, clean, match the Analyst card the user already liked):
  PEAD = 1d_pead_ideas.png (ideas.repec.org/a/bla/joares/v27y1989ip1-36.html),
  Merger = 3f_merger_ideas.png (ideas.repec.org/a/bla/jfinan/v56y2001i6p2135-2175.html).
  No cookie banners -> masks removed. Captions updated to "...Journal of Accounting Research" /
  "...Journal of Finance". Old semscholar search shots (1b/3d) retired.

**Files:** edl_v6.json, preview_v6.mp4 (99.0s), build_overlays_v6.py, sources/1d_pead_ideas.png,
sources/3f_merger_ideas.png, animations/slot_pvz_day2/render.mov, re-encoded src_pead/src_merger/
gfx_pead/gfx_merger/gfx_fda movs.

**Outstanding:** Awaiting user review of preview_v6. Not yet final-rendered. Subtitles still
master_v3.ass (cat outro uncaptioned). Self-eval passed at out 1.5/6/10.5/30/45/63s.

**Post-session housekeeping (2026-06-13):**
- Wrote `Trading Videos/EDITING_GUIDE.md` — reusable recipe for the series (top-band rule,
  ProRes-4444 alpha trap, RePEc/IDEAS for paper panels, themed intro sign, cheat-sheet).
- Cleaned the reel folder 3.3G -> 1.4G. KEPT: raw IMG_*.MOV, transcripts/, takes_packed.md,
  edl_v6.json, build_overlays_v6.py, make_ass.py, master_v3.ass, shot.mjs (+node_modules),
  4 used source PNGs (1d_pead_ideas, 2_analyst_womack, 3f_merger_ideas, 4c_fda_gov2),
  the 8 used animation slots' render.mov, base_preview.mp4, project.md.
  DELETED: preview/v3/v4/v5 renders, edl/edl_v4/edl_v5, build_overlays(.py)/v5, master.srt/v2.ass,
  slot_card_* (retired v4 floating cards), all slot_*/frames (regenerable), clips_preview/, verify/,
  unused source shots (jstor/ssrn/semscholar/nber/wiki/crops/test).
- NOTE: preview_v6.mp4 was not on disk this session (moved/renamed outside the workflow);
  re-render from edl_v6.json if needed.

## Session — 2026-06-13 (v5: un-bundle animation+source, full-bleed sources, FDA buy/sell)

**Strategy:** User feedback on preview_v4: stop showing animation and source in the SAME frame.
For each technique, play the graph first (lower band, face visible), then slide it away and drop
a FULL-BLEED screenshot source down from the top to cover the shelf above the head (like
Final Vids/Intro Video.mp4, ~top 45%). Applied to all four sections. Built a NEW FDA graph:
+20% rise over weeks 4-8 before the FDA announcement, with BELI marker at week 0 (low) synced to
"beli...dipublikasikan" and JUAL marker at week 8 (high) synced to "jual sebelum announcement".

**Decisions:**
- build_overlays_v5.py replaces v4's floating cards with render_src() full-bleed panels
  (1080-wide screenshot strip, 700px tall + 56px navy citation bar, slide down/up).
- Source picks (clean, no captcha/block pages): PEAD=1b_pead_semscholar (cookie banner masked,
  box (776,0,W,240)), Analyst=2_analyst_womack (clean), Merger=3d_merger_semscholar (banner masked
  (738,0,W,240)), FDA=4c_fda_gov2 (clean PDUFA page). NOTE: 1_pead/3_merger/4_fda_pdufa are
  captcha/Motley-Fool block pages — do NOT use.
- Overlay timeline (output s): gfx_pead 3.9-8.0 → src_pead 8.1-13.0 → src_analyst 13.3-25.4 →
  gfx_merger 25.9-43.5 ($2 glow @42.5) → src_merger 43.7-46.8 → src_fda 46.9-55.8 →
  gfx_fda 56.0-70.0 (rise drawn 56.5-61, BELI @64.5, JUAL @67.4). No graph/source overlap.
- Analyst section has no graph (none existed); source-only full-bleed.

**Files:** edl_v5.json, preview_v5.mp4 (98.9s), build_overlays_v5.py,
animations/slot_{src_pead,src_analyst,src_merger,src_fda,gfx_pead,gfx_merger,gfx_fda}/render.mov

**Outstanding:** Awaiting user review of preview_v5. Not yet final-rendered. Subtitles still
master_v3.ass (cat segment uncaptioned). Word-sync verified at PEAD "sixty days", merger "$2",
FDA "20%"/"beli"/"jual".

## Session — 2026-06-13 (v4: sources + animations + cat outro)

**Strategy:** Built preview_v4 on top of the v3 cut. Added floating source-card overlays (top band) for the 4 techniques in the reel, two lower-band motion-graphic panels, and appended the cat meme outro from Final Vids/Intro Video.mp4 (76.40–80.90) after "Peace!".

**Decisions:**
- Source display = floating top cards (user choice). Links = academic papers (user choice), but JSTOR + SSRN block headless screenshots → used Semantic Scholar paper pages for PEAD & Merger; RePEc for Analyst; FDA.gov for FDA (no paper exists). Screenshots via Playwright/chromium in edit/shot.mjs, cropped to edit/sources/crop_*.png.
- Motion graphics: PEAD = green line climbing "~60 hari" (the "stocks increasing" ask); Merger = A→B acquisition + animated $30−$28=$2 with glowing green $2, synced to "garanti dua dolar profit".
- Cat outro appended with original audio.

**Reasoning log:**
- Overlays MUST be ProRes 4444 .mov (yuva444). First pass encoded libvpx-vp9 which SILENTLY dropped alpha (output yuv420p) → overlays rendered opaque black over the face. ProRes 4444 fixed it. If revisiting alpha overlays on this machine, do NOT use libvpx-vp9.
- Layout bands: cards y~70–470 (top, clears face), gfx panels y~960–1290 (lower, above .ass subs at MarginV 490/555). Three clean bands, face stays visible.

**Files:** edl_v4.json, preview_v4.mp4, build_overlays.py, animations/slot_{card_pead,card_analyst,card_merger,card_fda,gfx_pead,gfx_merger}/render.mov

**Outstanding:** Awaiting user feedback. Not yet rendered final (use render.py without --preview when approved). Subtitles still master_v3.ass (cat segment has no captions).
