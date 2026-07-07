#!/usr/bin/env python3
"""make_final.py — Trading Reel Day 1, v2 render with all custom effects.

Effects applied:
  1. HOOK_A ("I want to earn money"): subtle zoom-in punch after each word, then zoom out
  2. HOOK_B ("rupiah yang lagi anjlok"): headline screenshot overlay + fahh.mp3 SFX
  3. HOOK_B ("no better time"): money.mp3 SFX
  4. After TRADING_REVEAL: stitch Whaaaat video + static distortion transition
  5. After OUTRO hand-cover: happy cat GIF + happy cat song
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

ROOT      = Path("<REPO_ROOT>")
REEL      = ROOT / "Trading Videos/first reel"
EDIT      = REEL / "edit"
ASSETS    = ROOT / "Assets"
MEME_A    = ROOT / "Meme Audio"
MEME_V    = ROOT / "Meme Video"
CLIPS     = EDIT / "clips_v2"
CLIPS.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "IMG_0882": REEL / "IMG_0882.MOV",
    "IMG_0883": REEL / "IMG_0883.MOV",
    "IMG_0884": REEL / "IMG_0884.MOV",
    "IMG_0887": REEL / "IMG_0887.MOV",
    "IMG_0894": REEL / "IMG_0894.MOV",
    "IMG_0897": REEL / "IMG_0897.MOV",
    "IMG_0898": REEL / "IMG_0898.MOV",
}

FPS = 30
W, H = 1080, 1920

# ── Helpers ───────────────────────────────────────────────────────────────────

def run(cmd: list, **kw) -> None:
    try:
        print("  $", " ".join(str(c) for c in cmd[:7]), "...")
    except UnicodeEncodeError:
        print("  $ [command with unicode chars in path]")
    result = subprocess.run([str(c) for c in cmd], **kw)
    if result.returncode != 0:
        try:
            print("FAILED:", " ".join(str(c) for c in cmd))
        except UnicodeEncodeError:
            print("FAILED: [command with unicode chars]")
        sys.exit(1)


def ffprobe_duration(path: Path) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ], text=True)
    return float(out.strip())


TONEMAP = (
    "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
    "tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p"
)


def is_hdr(path: Path) -> bool:
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=color_transfer",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ], text=True)
    return out.strip() in {"smpte2084", "arib-std-b67"}


def is_portrait(path: Path) -> bool:
    raw = subprocess.check_output([
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-select_streams", "v:0", "-show_streams", str(path),
    ], text=True)
    s = json.loads(raw)["streams"][0]
    w, h = int(s["width"]), int(s["height"])
    for sd in s.get("side_data_list", []):
        rot = sd.get("rotation")
        if rot is not None and abs(int(rot)) in (90, 270):
            w, h = h, w
            break
    return h > w


def vf_base(path: Path) -> str:
    parts = []
    if is_hdr(path):
        parts.append(TONEMAP)
    parts.append("scale=-2:1920" if is_portrait(path) else "scale=1920:-2")
    return ",".join(parts)


ENC_ARGS = [
    "-c:v", "libx264", "-preset", "fast", "-crf", "20",
    "-pix_fmt", "yuv420p", "-r", str(FPS),
    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
    "-movflags", "+faststart",
]

# ── 1. HOOK_A — per-word abrupt staircase zoom, then snap back ───────────────
#
# "I want to earn money." (IMG_0882, 2.31–5.20)
# Each word triggers an instant +3% zoom step; snaps back to 1.0 after phrase.
# Word frames (clip-relative @ 30fps): I=1, want=23, to=32, earn=39, money=63
# Phrase ends at frame 71; remaining frames return to 1.0.

def _staircase_zoom_expr() -> str:
    clip_start  = 2.31
    word_starts = [2.359, 3.079, 3.419, 3.619, 4.420]
    phrase_end  = 4.699
    frames = [int((ts - clip_start) * FPS) for ts in word_starts]
    f_end  = int((phrase_end - clip_start) * FPS)
    step   = 0.05
    n      = len(word_starts)

    expr = "1.0"
    expr = f"if(lt(on,{f_end}),{1.0+n*step:.2f},{expr})"
    for i in range(n - 2, -1, -1):
        level = 1.0 + (i + 1) * step
        expr = f"if(lt(on,{frames[i+1]}),{level:.2f},{expr})"
    expr = f"if(lt(on,{frames[0]}),1.0,{expr})"
    return expr


def make_hook_a(out: Path) -> None:
    src        = SOURCES["IMG_0882"]
    start, end = 2.31, 5.20
    dur        = end - start
    fade_out   = max(0.0, dur - 0.03)

    zoom = _staircase_zoom_expr()
    vf   = (
        f"{vf_base(src)},"
        f"zoompan=z='{zoom}':x='iw/2*(1-1/zoom)':y='ih/2*(1-1/zoom)'"
        f":d=1:s={W}x{H}:fps={FPS}"
    )
    af = f"afade=t=in:st=0:d=0.03,afade=t=out:st={fade_out:.3f}:d=0.03"

    run([
        "ffmpeg", "-y",
        "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", str(src),
        "-vf", vf, "-af", af,
        *ENC_ARGS, str(out),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


# ── 2. HOOK_B — screenshot overlay + audio SFX ───────────────────────────────
#
# "dengan rupiah yang sekarang lagi anjlok, there's no better time…"
# (IMG_0882, 8.61–15.42)
#
# Screenshot overlay: show headline_screenshot.png from "rupiah" to past "anjlok"
# fahh.mp3: starts when "lagi" is spoken
# money.mp3: starts when "no" is spoken

def make_hook_b(out: Path) -> None:
    src   = SOURCES["IMG_0882"]
    start, end = 8.61, 15.42
    dur   = end - start                    # 6.81 s
    fade_out = max(0.0, dur - 0.03)

    # Clip-relative timestamps (source ts − clip start)
    ss_t0 = 8.960 - start            # 0.350 s — "rupiah" starts
    ss_t1 = min(12.10 - start, dur)  # 3.490 s — runs through "anjlok", more reading time

    fahh_ms  = int((9.899 - start) * 1000)   # 1289 ms — "lagi" starts
    money_ms = int((15.339 - start) * 1000)  # 6729 ms — after "dollars." ends

    screenshot = ASSETS / "article_screenshot.png"
    fahh       = MEME_A / "fahh.mp3"
    money      = MEME_A / "money.mp3"

    # Scale article screenshot (1280×900) to full 1080 width
    ss_info = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "stream=width,height",
        "-of", "csv=p=0", str(screenshot),
    ], text=True).strip().split(",")
    orig_w, orig_h = int(ss_info[0]), int(ss_info[1])
    ss_w = W
    ss_h = int(orig_h * ss_w / orig_w)
    ss_h = ss_h if ss_h % 2 == 0 else ss_h + 1
    ss_y = 60                  # top margin

    vf = vf_base(src)
    fc = (
        f"[0:v]{vf}[base_v];"
        f"[3:v]scale={ss_w}:{ss_h}[ss];"
        f"[base_v][ss]overlay=x=0:y={ss_y}:enable='between(t,{ss_t0:.3f},{ss_t1:.3f})'[v_out];"
        f"[0:a]afade=t=in:st=0:d=0.03,afade=t=out:st={fade_out:.3f}:d=0.03[a_main];"
        f"[1:a]adelay={fahh_ms}:all=1,volume=0.03[a_fahh];"
        f"[2:a]adelay={money_ms}:all=1[a_money];"
        f"[a_main][a_fahh][a_money]amix=inputs=3:normalize=0:duration=first[a_out]"
    )

    run([
        "ffmpeg", "-y",
        "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", str(src),
        "-i", str(fahh),
        "-i", str(money),
        "-i", str(screenshot),
        "-filter_complex", fc,
        "-map", "[v_out]", "-map", "[a_out]",
        *ENC_ARGS, str(out),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


# ── 3. Standard segment extract ───────────────────────────────────────────────

def extract_std(src_key: str, start: float, end: float, out: Path) -> None:
    src  = SOURCES[src_key]
    dur  = end - start
    fade_out = max(0.0, dur - 0.03)
    vf   = vf_base(src)
    af   = f"afade=t=in:st=0:d=0.03,afade=t=out:st={fade_out:.3f}:d=0.03"

    run([
        "ffmpeg", "-y",
        "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", str(src),
        "-vf", vf, "-af", af,
        *ENC_ARGS, str(out),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


# ── 3b. QUESTION — standard extract + money.mp3 bleed for 0.5s ───────────────
#
# money.mp3 fires at the very end of HOOK_B (barely audible there).
# Bridge it into QUESTION: play money.mp3 from t=0 in this clip, fade it
# out by 0.5s so it sounds like it's carrying over from the previous scene.

def make_question(out: Path) -> None:
    src = SOURCES["IMG_0883"]
    start, end = 2.27, 4.74
    dur      = end - start
    fade_out = max(0.0, dur - 0.03)
    money    = MEME_A / "money.mp3"

    vf = vf_base(src)
    fc = (
        f"[0:v]{vf}[v_out];"
        f"[0:a]afade=t=in:st=0:d=0.03,afade=t=out:st={fade_out:.3f}:d=0.03[a_main];"
        f"[1:a]atrim=duration=1.20,volume=0.40,afade=t=out:st=0.90:d=0.30[a_money];"
        f"[a_main][a_money]amix=inputs=2:normalize=0:duration=first[a_out]"
    )

    run([
        "ffmpeg", "-y",
        "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", str(src),
        "-i", str(money),
        "-filter_complex", fc,
        "-map", "[v_out]", "-map", "[a_out]",
        *ENC_ARGS, str(out),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


# ── 4. Whaaaat video (854×480) → blurred-bg 1080×1920 ────────────────────────

def make_whaaaat(out: Path) -> None:
    src = MEME_V / "Whaaaat!？ Oh hell naw ｜ Vlipsy.mp4"
    dur = 5.8
    fade_out = max(0.0, dur - 0.03)

    # Foreground: 854×480 fitted inside 1080×608 (≈16:9 slot)
    fg_h = int(480 / 854 * W)
    fg_h = fg_h if fg_h % 2 == 0 else fg_h + 1   # → 606

    # Remove VLIPSY watermark: blur the 130x35 region so text dissolves naturally
    fc = (
        f"[0:v]split[wm_src][wm_base];"
        f"[wm_src]crop=165:44:0:436,format=yuv420p,boxblur=luma_radius=15:luma_power=5:chroma_radius=9:chroma_power=5[wm_blurred];"
        f"[wm_base][wm_blurred]overlay=x=0:y=436[v_nowm];"
        f"[v_nowm]split[bg][fg_src];"
        f"[bg]scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},boxblur=20:5[bg_out];"
        f"[fg_src]scale={W}:{fg_h}:force_original_aspect_ratio=decrease,"
        f"pad={W}:{fg_h}:(ow-iw)/2:(oh-ih)/2[fg_out];"
        f"[bg_out][fg_out]overlay=(W-w)/2:(H-h)/2[v_out];"
        f"[0:a]afade=t=in:st=0:d=0.03,afade=t=out:st={fade_out:.3f}:d=0.03[a_out]"
    )

    run([
        "ffmpeg", "-y", "-i", str(src),
        "-t", f"{dur:.3f}",
        "-filter_complex", fc,
        "-map", "[v_out]", "-map", "[a_out]",
        *ENC_ARGS, str(out),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


# ── 5. Static distortion (1080×1920, no audio) ───────────────────────────────

def make_distortion(out: Path) -> None:
    src = MEME_V / "static_distortion_transition.mp4"
    dur = 1.5
    fade_out = max(0.0, dur - 0.03)

    # Source has no audio — generate TV-static noise
    fc = (
        f"[0:v]scale={W}:{H}[v_out];"
        f"anoisesrc=r=48000:color=white:seed=42,"
        f"atrim=duration={dur:.3f},"
        f"highpass=f=800,lowpass=f=8000,"
        f"volume=0.05,"
        f"afade=t=in:st=0:d=0.03,afade=t=out:st={fade_out:.3f}:d=0.03[a_out]"
    )

    run([
        "ffmpeg", "-y", "-i", str(src),
        "-filter_complex", fc,
        "-map", "[v_out]", "-map", "[a_out]",
        *ENC_ARGS, str(out),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


# ── 6. Happy cat GIF + song → 1080×1920 ─────────────────────────────────────

def make_happy_cat(out: Path) -> None:
    gif  = MEME_V / "happy cat.gif"
    song = MEME_A / "happy cat song.mp3"
    dur  = 5.0    # shorter outro; GIF loops to fill

    # GIF: 386×480 → scale to 1080 wide (1080×1344), pad to 1080×1920 (black)
    gif_h = int(480 / 386 * W)
    gif_h = gif_h if gif_h % 2 == 0 else gif_h + 1   # → 1344

    fc = (
        f"[0:v]scale={W}:{gif_h}:flags=lanczos,"
        f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black,"
        f"fps={FPS}[v_out];"
        f"[1:a]volume=0.50,afade=t=in:st=0:d=0.10,"
        f"afade=t=out:st={max(0.0, dur - 0.50):.3f}:d=0.50[a_out]"
    )

    run([
        "ffmpeg", "-y",
        "-ignore_loop", "0", "-ss", "0.30", "-i", str(gif),
        "-i", str(song),
        "-t", f"{dur:.3f}",
        "-filter_complex", fc,
        "-map", "[v_out]", "-map", "[a_out]",
        *ENC_ARGS, str(out),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


# ── master.ass timestamp adjuster ────────────────────────────────────────────
#
# The original master.ass was calibrated for the old preview.mp4 (no memes).
# In v2 we:
#   • Extended HOOK_A by 0.42 s (source 2.31-4.78 → 2.31-5.20)
#   • Inserted WHAAAAT (5.80 s) + DISTORTION (1.50 s) after TRADING_REVEAL
#
# Shift rules (original output-timeline seconds):
#   t < 2.47            → no shift  (within HOOK_A)
#   2.47 ≤ t < 13.45   → +0.42 s   (HOOK_A extension propagates to HOOK_B onwards)
#   t ≥ 13.45           → +7.72 s   (above + meme insertion)

CUT1 = 2.47    # old HOOK_A end
CUT2 = 13.45   # old TRADING_REVEAL end
D1   = 0.42    # HOOK_A extension
D2   = 7.30    # WHAAAAT + DISTORTION duration


def _ass_ts_to_s(ts: str) -> float:
    """Parse H:MM:SS.cc → seconds."""
    h, rest = ts.split(":", 1)
    m, rest = rest.split(":", 1)
    s, cc   = rest.split(".", 1)
    return int(h)*3600 + int(m)*60 + int(s) + int(cc)/100


def _s_to_ass_ts(sec: float) -> str:
    """Seconds → H:MM:SS.cc (centiseconds)."""
    cs  = int(round(sec * 100))
    h, rem = divmod(cs, 360000)
    m, rem = divmod(rem, 6000)
    s, cc  = divmod(rem, 100)
    return f"{h}:{m:02d}:{s:02d}.{cc:02d}"


def _shift(t: float) -> float:
    if t < CUT1:
        return t
    if t < CUT2:
        return t + D1
    return t + D1 + D2


def adjust_master_ass(src_ass: Path, out_ass: Path) -> None:
    """Read master.ass, shift Dialogue timestamps, write adjusted copy."""
    lines_in  = src_ass.read_text(encoding="utf-8").splitlines()
    lines_out = []
    for line in lines_in:
        if line.startswith("Dialogue:"):
            parts = line.split(",", 9)   # Layer,Start,End,Style,Name,ML,MR,MV,Eff,Text
            if len(parts) >= 3:
                parts[1] = _s_to_ass_ts(_shift(_ass_ts_to_s(parts[1])))
                parts[2] = _s_to_ass_ts(_shift(_ass_ts_to_s(parts[2])))
                line = ",".join(parts)
        lines_out.append(line)
    out_ass.write_text("\n".join(lines_out), encoding="utf-8")
    print(f"  ASS adjusted -> {out_ass.name}")


# ── SRT builder ──────────────────────────────────────────────────────────────

PUNCT_BREAK = set(".,!?;:")

# Map segment key → (transcript_source, seg_start, seg_end)  |  None for meme clips
SEG_INFO: dict[str, tuple[str, float, float] | None] = {
    "hook_a":      ("IMG_0882", 2.31,  5.20),
    "hook_b":      ("IMG_0882", 8.61,  15.42),
    "question":    ("IMG_0883", 2.27,  4.74),
    "trading_rev": ("IMG_0883", 5.20,  6.90),
    "whaaaat":     None,
    "distortion":  None,
    "master_plan": ("IMG_0884", 2.57,  8.24),
    "step1":       ("IMG_0887", 1.73,  8.82),
    "step2":       ("IMG_0887", 31.45, 40.44),
    "step3":       ("IMG_0894", 1.63,  13.78),
    "step5":       ("IMG_0897", 1.57,  8.26),
    "cta":         ("IMG_0898", 1.69,  8.12),
    "outro":       ("IMG_0898", 12.55, 20.80),
    "happy_cat":   None,
}


def _srt_ts(s: float) -> str:
    ms = int(round(s * 1000))
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    sec, ms = divmod(rem, 1_000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def build_srt(order: list[str], clips: dict[str, Path], out: Path) -> None:
    tr_dir   = EDIT / "transcripts"
    entries: list[tuple[float, float, str]] = []
    offset   = 0.0

    for key in order:
        info = SEG_INFO.get(key)
        if info is None:
            offset += ffprobe_duration(clips[key])
            continue

        src_name, seg_start, seg_end = info
        seg_dur = seg_end - seg_start
        tr_path = tr_dir / f"{src_name}.json"

        if not tr_path.exists():
            offset += seg_dur
            continue

        transcript = json.loads(tr_path.read_text())
        words = [
            w for w in transcript.get("words", [])
            if w.get("type") == "word"
            and w.get("start") is not None and w.get("end") is not None
            and w["end"] > seg_start and w["start"] < seg_end
        ]

        # Group into 2-word chunks, break on punctuation
        chunks: list[list[dict]] = []
        cur: list[dict] = []
        for w in words:
            text = (w.get("text") or "").strip()
            if not text:
                continue
            cur.append(w)
            if len(cur) >= 2 or (text and text[-1] in PUNCT_BREAK):
                chunks.append(cur)
                cur = []
        if cur:
            chunks.append(cur)

        for chunk in chunks:
            t0 = max(seg_start, chunk[0]["start"])
            t1 = min(seg_end,   chunk[-1]["end"])
            out_s = max(0.0, t0 - seg_start) + offset
            out_e = max(0.0, t1 - seg_start) + offset
            if out_e <= out_s:
                out_e = out_s + 0.4
            text = " ".join((w.get("text") or "").strip() for w in chunk)
            text = re.sub(r"\s+", " ", text).strip().rstrip(",:;").upper()
            entries.append((out_s, out_e, text))

        offset += seg_dur

    entries.sort(key=lambda e: e[0])
    lines: list[str] = []
    for i, (a, b, t) in enumerate(entries, 1):
        lines += [str(i), f"{_srt_ts(a)} --> {_srt_ts(b)}", t, ""]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"  SRT written: {len(entries)} cues -> {out.name}")


# ── Main ─────────────────────────────────────────────────────────────────────

ORDER = [
    "hook_a",
    "hook_b",
    "question",
    "trading_rev",
    "whaaaat",
    "distortion",
    "master_plan",
    "step1",
    "step2",
    "step3",
    "step5",
    "cta",
    "outro",
    "happy_cat",
]

STD_SEGS: dict[str, tuple[str, float, float]] = {
    "trading_rev": ("IMG_0883", 5.20,  6.90),
    "master_plan": ("IMG_0884", 2.57,  8.24),
    "step1":       ("IMG_0887", 1.73,  8.82),
    "step2":       ("IMG_0887", 31.45, 40.44),
    "step3":       ("IMG_0894", 1.63,  13.78),
    "step5":       ("IMG_0897", 1.57,  8.26),
    "cta":         ("IMG_0898", 1.69,  8.12),
}


def make_outro(out: Path) -> None:
    """Outro trimmed to hand-cover moment + 0.3s fade-to-black for smooth cat transition."""
    src = SOURCES["IMG_0898"]
    start, end = 12.55, 20.13   # ends right as hand fully covers camera
    dur        = end - start     # 7.58 s
    fade_out   = max(0.0, dur - 0.03)
    vf_fade_t  = max(0.0, dur - 0.30)

    vf = f"{vf_base(src)},fade=t=out:st={vf_fade_t:.3f}:d=0.30"
    af = f"afade=t=in:st=0:d=0.03,afade=t=out:st={fade_out:.3f}:d=0.03"

    run([
        "ffmpeg", "-y",
        "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", str(src),
        "-vf", vf, "-af", af,
        *ENC_ARGS, str(out),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def main() -> None:
    print("=" * 60)
    print("  Trading Reel Day 1 - v2 render")
    print("=" * 60)

    clips: dict[str, Path] = {}

    # ── Custom clips ──────────────────────────────────────────────
    print("\n[1] HOOK_A — per-word zoom")
    clips["hook_a"] = CLIPS / "hook_a_zoom.mp4"
    if not clips["hook_a"].exists():
        make_hook_a(clips["hook_a"])
    else:
        print("  ok cached")

    print("\n[2] HOOK_B — screenshot overlay + SFX")
    clips["hook_b"] = CLIPS / "hook_b_fx.mp4"
    if not clips["hook_b"].exists():
        make_hook_b(clips["hook_b"])
    else:
        print("  ok cached")

    print("\n[3] QUESTION — with money.mp3 bleed")
    clips["question"] = CLIPS / "question.mp4"
    if not clips["question"].exists():
        make_question(clips["question"])
    else:
        print("  ok cached")

    print("\n[3b] Standard segments")
    for key, (src_key, s, e) in STD_SEGS.items():
        clips[key] = CLIPS / f"{key}.mp4"
        if not clips[key].exists():
            print(f"  extracting {key} ({src_key} {s}–{e})")
            extract_std(src_key, s, e, clips[key])
        else:
            print(f"  ok {key} cached")

    print("\n[4] Whaaaat meme (blurred-bg 9:16)")
    clips["whaaaat"] = CLIPS / "whaaaat.mp4"
    if not clips["whaaaat"].exists():
        make_whaaaat(clips["whaaaat"])
    else:
        print("  ok cached")

    print("\n[5] Static distortion transition")
    clips["distortion"] = CLIPS / "distortion.mp4"
    if not clips["distortion"].exists():
        make_distortion(clips["distortion"])
    else:
        print("  ok cached")

    print("\n[5b] Outro — fade-to-black at hand cover")
    clips["outro"] = CLIPS / "outro.mp4"
    if not clips["outro"].exists():
        make_outro(clips["outro"])
    else:
        print("  ok cached")

    print("\n[6] Happy cat GIF + song")
    clips["happy_cat"] = CLIPS / "happy_cat.mp4"
    if not clips["happy_cat"].exists():
        make_happy_cat(clips["happy_cat"])
    else:
        print("  ok cached")

    # ── Concat ────────────────────────────────────────────────────
    seg_paths = [clips[k] for k in ORDER]
    base = EDIT / "base_v2.mp4"
    concat_txt = EDIT / "_concat_v2.txt"
    concat_txt.write_text(
        "".join(f"file '{p.resolve()}'\n" for p in seg_paths),
        encoding="utf-8",
    )
    print(f"\n[7] Concat {len(seg_paths)} segments -> base_v2.mp4")
    run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_txt),
        "-c", "copy", "-movflags", "+faststart", str(base),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    concat_txt.unlink(missing_ok=True)

    # ── Subtitles: shift original master.ass to new timeline ─────
    ass_src = EDIT / "master.ass"
    ass_adj = EDIT / "master_v3.ass"
    print("\n[8] Adjusting subtitle timestamps")
    adjust_master_ass(ass_src, ass_adj)

    # ── Apply subtitles → final ───────────────────────────────────
    final   = EDIT / "final_v2.mp4"
    ass_esc = str(ass_adj.resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'").replace(" ", r"\ ")
    print(f"\n[9] Applying subtitles -> final_v2.mp4")
    run([
        "ffmpeg", "-y", "-i", str(base),
        "-vf", f"ass='{ass_esc}'",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-movflags", "+faststart", str(final),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    size_mb = final.stat().st_size / (1024 ** 2)
    print(f"\n{'='*60}")
    print(f"  Done -> {final.name}  ({size_mb:.1f} MB)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
