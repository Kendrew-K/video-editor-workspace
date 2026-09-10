import sys
"""
Static distortion transition — TV glitch / NO SIGNAL aesthetic.
Output: 1080x1920 @ 30fps, ~1.5s, H.264, saved to Assets/static_distortion_transition.mp4
"""

import os, subprocess, shutil, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Resolve fonts through the repo-root helper so these render off Windows too.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))
from fonts import font_path

W, H = 1080, 1920
FPS = 30
DURATION = 1.5
FRAMES = int(FPS * DURATION)
OUT_DIR = r"<REPO_ROOT>\Assets\_frames_tmp"
OUT_MP4 = r"<REPO_ROOT>\Assets\static_distortion_transition.mp4"

os.makedirs(OUT_DIR, exist_ok=True)

# Color bar palette (classic TV test bars, saturated)
BARS = [
    (192, 192, 192),  # white
    (192, 192, 0),    # yellow
    (0,  192, 192),   # cyan
    (0,  192,   0),   # green
    (192,  0, 192),   # magenta
    (192,  0,   0),   # red
    (0,    0, 192),   # blue
]

def color_bars_base():
    img = Image.new("RGB", (W, H), (0, 0, 0))
    bar_w = W // len(BARS)
    draw = ImageDraw.Draw(img)
    for i, color in enumerate(BARS):
        x0 = i * bar_w
        x1 = x0 + bar_w if i < len(BARS) - 1 else W
        draw.rectangle([x0, 0, x1, H], fill=color)
    return np.array(img, dtype=np.uint8)

def add_static(arr, intensity):
    noise = np.random.randint(0, int(255 * intensity), arr.shape, dtype=np.uint8)
    return np.clip(arr.astype(np.int16) + noise - int(128 * intensity), 0, 255).astype(np.uint8)

def horizontal_shift(arr, max_shift):
    result = arr.copy()
    for y in range(H):
        if random.random() < 0.3:
            shift = random.randint(-max_shift, max_shift)
            result[y] = np.roll(arr[y], shift, axis=0)
    return result

def channel_split(arr, amount):
    result = arr.copy()
    result[:, :, 0] = np.roll(arr[:, :, 0],  amount, axis=1)
    result[:, :, 2] = np.roll(arr[:, :, 2], -amount, axis=1)
    return result

def scanlines(arr, alpha=0.4):
    mask = np.ones((H, 1, 1), dtype=np.float32)
    mask[::2] = 1.0 - alpha
    return np.clip(arr * mask, 0, 255).astype(np.uint8)

def pixelate(arr, block):
    small = Image.fromarray(arr).resize((W // block, H // block), Image.NEAREST)
    return np.array(small.resize((W, H), Image.NEAREST))

def add_no_signal(arr, alpha):
    img = Image.fromarray(arr)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(font_path("arialbd"), 90)
        small = ImageFont.truetype(font_path("arial"), 36)
    except Exception:
        font = ImageFont.load_default()
        small = font

    # semi-transparent black band
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    band_h = 220
    band_y = H // 2 - band_h // 2
    od.rectangle([0, band_y, W, band_y + band_h], fill=(0, 0, 0, int(200 * alpha)))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    text = "NO SIGNAL"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (W - tw) // 2
    ty = H // 2 - th // 2 - 20
    draw.text((tx + 3, ty + 3), text, font=font, fill=(80, 80, 80))
    draw.text((tx, ty), text, font=font, fill=(255, 255, 255))

    sub = "SIGNAL LOST"
    sbbox = draw.textbbox((0, 0), sub, font=small)
    sw = sbbox[2] - sbbox[0]
    draw.text(((W - sw) // 2, ty + th + 10), sub, font=small, fill=(180, 60, 60))

    return np.array(img)

base = color_bars_base()

for i in range(FRAMES):
    t = i / FRAMES  # 0 → 1

    # Phase control: ramp in chaos, hold, ramp out
    if t < 0.15:
        chaos = t / 0.15
    elif t < 0.75:
        chaos = 1.0
    else:
        chaos = 1.0 - (t - 0.75) / 0.25

    static_intensity = 0.55 * chaos + 0.05
    shift_amount = int(60 * chaos)
    ch_split = int(18 * chaos)
    block = max(1, int(6 * chaos)) if chaos > 0.3 else 1
    no_signal_alpha = min(1.0, chaos * 1.5)

    frame = base.copy()

    if block > 1:
        frame = pixelate(frame, block)

    frame = add_static(frame, static_intensity)
    frame = horizontal_shift(frame, shift_amount)
    frame = channel_split(frame, ch_split)
    frame = scanlines(frame, alpha=0.35)

    if no_signal_alpha > 0.1:
        frame = add_no_signal(frame, no_signal_alpha)

    # Occasional full-white flash
    if chaos > 0.8 and random.random() < 0.08:
        frame = np.clip(frame.astype(np.int16) + 180, 0, 255).astype(np.uint8)

    img = Image.fromarray(frame)
    img.save(os.path.join(OUT_DIR, f"frame_{i:04d}.png"))
    if i % 10 == 0:
        print(f"  frame {i}/{FRAMES}")

print("Encoding with FFmpeg...")
subprocess.run([
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", os.path.join(OUT_DIR, "frame_%04d.png"),
    "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    OUT_MP4
], check=True)

shutil.rmtree(OUT_DIR)
print(f"Done: {OUT_MP4}")
