## Session 1 — 2026-06-10

**Strategy:** 7-source multi-take EDL. Selected best takes per beat across all 7 iPhone clips. Smart-stitched into a ~68s vertical (1080x1920) reel. Applied bilingual EN/ID subtitles (Helvetica 18 Bold, MarginV=90, 2-word uppercase chunks).

**Decisions:** HOOK_A = "I want to earn money" (IMG_0882 2.31–4.78). HOOK_B = "rupiah yang lagi anjlok + no better time" (IMG_0882 8.61–15.42). QUESTION/TRADING_REVEAL from IMG_0883. MASTER_PLAN from IMG_0884 (cleanest, skips first rustling). STEP2 from IMG_0887 used the retake at 31.45 (no false start). OUTRO trimmed right as hand covers screen.

**Outstanding:** SFX and meme insertions deferred.

---

## Session 2 — 2026-06-10

**Strategy:** Custom `make_final.py` render pipeline adding 5 effects on top of the session-1 EDL. Output: `edit/final_v2.mp4` (84s, 108 MB). All 14 clips cached in `edit/clips_v2/`.

**Effects:**
- HOOK_A zoom: per-word zoompan (12% max, 10-frame triangle bump per word, 5 words)
- HOOK_B screenshot: headline_screenshot.png overlaid at y=80 from 0.35–2.63s in clip
- HOOK_B fahh.mp3: delayed 1289ms (when "lagi" is spoken)
- HOOK_B money.mp3: delayed 3129ms (when "no better time" starts)
- After TRADING_REVEAL: Whaaaat (5.8s, blurred-bg 9:16) + static_distortion (1.5s)
- OUTRO extended to source 20.80 to include hand cover
- After OUTRO: happy cat GIF (7.55s, song + 0.5s fade-out, centered on black)
- Subtitles rebuilt with updated offsets: master_v2.srt (91 cues)

**Verified frames:** overlay ✓, Whaaaat ✓, distortion ✓, zoom ✓, happy_cat ✓

**Outstanding:** May want loudnorm pass on final_v2.mp4 for social upload.
