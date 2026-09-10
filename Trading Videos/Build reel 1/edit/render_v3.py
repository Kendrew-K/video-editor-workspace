"""Render Build reel 1 v3 — wrapper around the video-use render pipeline.

Why this exists (instead of plain render.py):
  1. Per-range punch-in: edl ranges carry "punch": true -> 1.12x center crop
     (scale=-2:2150 then crop 1080x1920, crop window biased 40% from top so the
     head stays centered). render.py only supports one global grade filter.
  2. SFX mix: edl "sfx" events are mixed AFTER loudnorm at fixed gains so the
     -14 LUFS normalization of speech can't duck or squash them. Video stream
     is stream-copied in the SFX pass (no quality loss, fast).

Reuses render.py for everything else: HDR tonemap detection, 30ms fades,
lossless concat, overlay PTS-shift compositing, subtitles LAST, loudnorm.

Usage:
    python edit/render_v3.py edit/edl_v3.json -o edit/preview_v3.mp4 --preview
    python edit/render_v3.py edit/edl_v3.json -o edit/final_v3.mp4
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

HELPERS = Path("<USER_HOME>/.claude/skills/video-use/helpers")
sys.path.insert(0, str(HELPERS))
import render as R  # noqa: E402

PUNCH = 1.12
PUNCH_H = 2150  # 1920 * 1.12, rounded to even


def extract_ranges(edl: dict, edit_dir: Path, preview: bool) -> list[Path]:
    """Per-range extract with optional punch-in, 30ms fades, HDR tonemap."""
    clips_dir = edit_dir / ("clips_v3_preview" if preview else "clips_v3")
    clips_dir.mkdir(parents=True, exist_ok=True)
    preset, crf = ("medium", "22") if preview else ("fast", "20")

    paths = []
    for i, r in enumerate(edl["ranges"]):
        src = R.resolve_path(edl["sources"][r["source"]], edit_dir)
        start, end = float(r["start"]), float(r["end"])
        dur = end - start
        out = clips_dir / f"seg_{i:02d}_{r['source']}.mp4"

        if r.get("punch"):
            # 40%-from-top crop bias keeps the face centered after the punch
            scale = (f"scale=-2:{PUNCH_H},"
                     f"crop=1080:1920:(iw-1080)/2:(ih-1920)*2/5")
        else:
            scale = "scale=-2:1920"

        vf_parts = []
        if R.is_hdr_source(src):
            vf_parts.append(R.TONEMAP_CHAIN)
        vf_parts.append(scale)
        vf = ",".join(vf_parts)

        fade_out = max(0.0, dur - 0.03)
        af = f"afade=t=in:st=0:d=0.03,afade=t=out:st={fade_out:.3f}:d=0.03"

        if out.exists():
            print(f"  [{i:02d}] cached {out.name}")
            paths.append(out)
            continue
        print(f"  [{i:02d}] {r['source']} {start:7.2f}-{end:7.2f} ({dur:5.2f}s)"
              f" {'PUNCH' if r.get('punch') else 'wide '} {r.get('beat', '')}")
        cmd = ["ffmpeg", "-y", "-ss", f"{start:.3f}", "-i", str(src),
               "-t", f"{dur:.3f}", "-vf", vf, "-af", af,
               "-c:v", "libx264", "-preset", preset, "-crf", crf,
               "-pix_fmt", "yuv420p", "-r", "30",
               "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
               "-movflags", "+faststart", str(out)]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        paths.append(out)
    return paths


def mix_sfx(video: Path, sfx_events: list[dict], edit_dir: Path, out: Path) -> None:
    """Mix SFX events into the (already loudnormed) video. Video stream-copied."""
    if not sfx_events:
        video.replace(out)
        return

    inputs = ["-i", str(video)]
    filters = []
    labels = []
    for i, ev in enumerate(sfx_events, start=1):
        p = R.resolve_path(ev["file"], edit_dir)
        inputs += ["-i", str(p)]
        delay_ms = int(float(ev["at"]) * 1000)
        gain = float(ev.get("gain", 0.35))
        trim = f"atrim=0:{float(ev['trim']):.2f}," if ev.get("trim") else ""
        filters.append(
            f"[{i}:a]{trim}volume={gain},adelay={delay_ms}|{delay_ms}[s{i}]")
        labels.append(f"[s{i}]")

    n = len(sfx_events) + 1
    # normalize=0: plain sum — amix's default 1/active_inputs scaling renormalizes
    # every time a short SFX stream ends, progressively boosting speech (v3 bug:
    # tail came out +7 dB and clipped). Limiter catches speech+SFX sum peaks.
    filters.append(
        f"[0:a]{''.join(labels)}amix=inputs={n}:duration=first:normalize=0,"
        f"alimiter=limit=0.98:level=false[aout]")

    cmd = ["ffmpeg", "-y", *inputs,
           "-filter_complex", ";".join(filters),
           "-map", "0:v", "-map", "[aout]",
           "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-movflags", "+faststart", str(out)]
    print(f"mixing {len(sfx_events)} SFX events -> {out.name}")
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("edl", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--preview", action="store_true")
    args = ap.parse_args()

    edl = json.loads(args.edl.read_text(encoding="utf-8"))
    edit_dir = args.edl.resolve().parent
    out_path = args.output.resolve()

    print(f"extracting {len(edl['ranges'])} ranges")
    segs = extract_ranges(edl, edit_dir, args.preview)

    base = edit_dir / ("base_v3_preview.mp4" if args.preview else "base_v3.mp4")
    R.concat_segments(segs, base, edit_dir)

    subs = R.resolve_path(edl["subtitles"], edit_dir) if edl.get("subtitles") else None
    composite = out_path.with_suffix(".prenorm.mp4")
    R.build_final_composite(base, edl.get("overlays") or [], subs, composite, edit_dir)

    normed = out_path.with_suffix(".normed.mp4")
    print("loudnorm (-14 LUFS)")
    R.apply_loudnorm_two_pass(composite, normed, preview=args.preview)
    composite.unlink(missing_ok=True)

    mix_sfx(normed, edl.get("sfx") or [], edit_dir, out_path)
    normed.unlink(missing_ok=True)

    print(f"done: {out_path} ({out_path.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
