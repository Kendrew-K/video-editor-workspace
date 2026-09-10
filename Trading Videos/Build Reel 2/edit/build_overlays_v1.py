"""Build Reel 2 (Day 7) overlays — news-trading-bot build plan.

Top-band rule (§5.1): every graphic lives inside y 0-500, above the head
(head top ~y620 in this footage). Navy fintech card system (§5.2) + hybrid
meme accents (§10.5). Payoff-word sync per §5.3.

Slots (all 1080x1920 RGBA, 30 fps):
  slot_pvz_day7    3.2s  Newspaper-slam DAY 7 intro sign (theme: breaking news)
  slot_gfx_pipeline 9.4s 5-stage bot pipeline, rows pop on each stage word
  slot_gfx_dedup  12.5s  duplicate-filter card, DUPLICATE X's + NO EDGE stamp
  slot_gfx_safety 11.3s  kill-switch card, 2 warning rows + toggle slams OFF
  slot_gfx_roadmap 15.9s 4-phase month timeline, nodes light L->R, GO LIVE

Payoff sync targets (output timeline, from edl_v1.json offsets):
  day7:     "seven" out 5.40    -> slot t 1.30 (slot starts 4.10)
  pipeline: baca berita out 11.70 t1.10 / filter 12.68 t2.08 / cari 13.86 t3.26
            buy/sell 14.96 t4.36 / cek aman 17.42 t6.82   (slot starts 10.60)
  dedup:    "no longer an edge" out 31.02 t10.92 / "fresh news" 31.78 t11.68
            (slot starts 20.10)
  safety:   "position too big" out ~48 t~1.5 / "loss limit" ~52 t~5.5
            "kill switch" out 55.26 t8.76   (slot starts 46.50)
  roadmap:  M1 out 58.16 t0.16 / M2 60.46 t2.46 / M3-4 64.18 t6.18
            "live trading" 71.26 t13.26   (slot starts 58.00)
"""

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

# Resolve fonts through the repo-root helper so these render off Windows too.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")))
from fonts import font_path

W, H = 1080, 1920
FPS = 30

# Card box (guide §5.1) — all internal geometry relative to this
CX0, CY0, CX1, CY1 = 80, 120, 1000, 455

GREEN   = (22, 199, 132)
GREEN_D = (10, 150, 98)
NAVY    = (11, 31, 58)
PANEL   = (12, 22, 40)
WHITE   = (255, 255, 255)
DIM     = (158, 168, 184)
RED     = (235, 90, 95)
GOLD    = (245, 196, 90)
PAPER   = (238, 234, 224)   # newsprint off-white
INK     = (24, 22, 20)      # newsprint black

FONT_B = font_path("arialbd")
FONT_R = font_path("arial")
FONT_MEME = font_path("impact")
FONT_SERIF = font_path("georgiab")   # newspaper masthead/headline

EDIT = os.path.dirname(os.path.abspath(__file__))


def f_b(size): return ImageFont.truetype(FONT_B, size)
def f_r(size): return ImageFont.truetype(FONT_R, size)
def f_m(size): return ImageFont.truetype(FONT_MEME, size)
def f_s(size): return ImageFont.truetype(FONT_SERIF, size)


def ease_out_cubic(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def ease_in_out_cubic(t):
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return 4 * t ** 3
    return 1 - (-2 * t + 2) ** 3 / 2


def ease_out_back(t):
    t = max(0.0, min(1.0, t))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def prog(t, start, dur):
    """0..1 progress of a sub-animation beginning at `start`, running `dur`."""
    if dur <= 0:
        return 1.0 if t >= start else 0.0
    return max(0.0, min(1.0, (t - start) / dur))


def rounded(d, box, r, fill, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def draw_card(layer, alpha=238, y_shift=0):
    d = ImageDraw.Draw(layer)
    rounded(d, (CX0, CY0 + y_shift, CX1, CY1 + y_shift), 26,
            PANEL + (alpha,), outline=GREEN + (200,), width=3)
    return d


def text_c(d, cx, y, s, font, fill):
    w = d.textlength(s, font=font)
    d.text((cx - w / 2, y), s, font=font, fill=fill)


def check_mark(d, cx, cy, size, color, width=7, a=255):
    d.line([(cx - size, cy), (cx - size * 0.25, cy + size * 0.7)],
           fill=color + (a,), width=width)
    d.line([(cx - size * 0.25, cy + size * 0.7), (cx + size, cy - size * 0.6)],
           fill=color + (a,), width=width)


def cross_mark(d, cx, cy, size, color, width=7, a=255):
    d.line([(cx - size, cy - size), (cx + size, cy + size)], fill=color + (a,), width=width)
    d.line([(cx - size, cy + size), (cx + size, cy - size)], fill=color + (a,), width=width)


def save_frames(name, total_s, render_fn):
    slot = os.path.join(EDIT, "animations", name, "frames")
    os.makedirs(slot, exist_ok=True)
    n = int(round(total_s * FPS))
    for i in range(n):
        t = i / FPS
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        render_fn(im, t)
        im.save(os.path.join(slot, f"f_{i:05d}.png"))
    print(f"{name}: {n} frames")


# ----------------------------------------------------- DAY 7 newspaper slam
def _build_newspaper():
    """The front page, drawn once at full size; spun/scaled in per frame."""
    pw, ph = 920, 400
    paper = Image.new("RGBA", (pw, ph), PAPER + (255,))
    d = ImageDraw.Draw(paper)
    # outer ink border
    d.rectangle((6, 6, pw - 6, ph - 6), outline=INK + (255,), width=3)
    # masthead
    text_c(d, pw // 2, 20, "THE DAILY TRADER", f_s(46), INK + (255,))
    d.line([(30, 82), (pw - 30, 82)], fill=INK + (255,), width=3)
    d.line([(30, 90), (pw - 30, 90)], fill=INK + (255,), width=1)
    text_c(d, pw // 2, 96, "DAY 7 EDITION    //    MARKETS DESK", f_r(20), INK + (230,))
    d.line([(30, 128), (pw - 30, 128)], fill=INK + (255,), width=1)
    # dummy column text left + right of the headline
    for col_x in (44, pw - 190):
        for k in range(6):
            ly = 150 + k * 20
            lw = 146 - (k % 3) * 22
            d.line([(col_x, ly), (col_x + lw, ly)], fill=INK + (120,), width=3)
    # BREAKING tag
    rounded(d, (pw // 2 - 120, 140, pw // 2 + 120, 178), 6, RED + (255,))
    text_c(d, pw // 2, 146, "BREAKING", f_b(26), WHITE + (255,))
    # giant headline
    text_c(d, pw // 2, 188, "DAY 7", f_s(150), INK + (255,))
    d.line([(230, 356), (pw - 230, 356)], fill=INK + (255,), width=2)
    text_c(d, pw // 2, 362, "NEWS-TRADING BOT : THE BUILD", f_b(28), INK + (240,))
    return paper


_NEWSPAPER = None


def render_day7(im, t):
    global _NEWSPAPER
    if _NEWSPAPER is None:
        _NEWSPAPER = _build_newspaper()
    cx, cy = W // 2, 300
    # spin-in: 0-1.15s, then settle wobble. Lands ~t=1.2 (spoken "seven" t=1.30)
    p = ease_out_cubic(prog(t, 0.0, 1.15))
    scale = 0.06 + 0.94 * p
    angle = 540 * (1 - p)              # ~1.5 turns, unwinding into place
    if t > 1.2:
        angle += 2.2 * math.exp(-3.0 * (t - 1.2)) * math.sin(11 * (t - 1.2))
    pw, ph = _NEWSPAPER.size
    sw, sh = max(1, int(pw * scale)), max(1, int(ph * scale))
    frame = _NEWSPAPER.resize((sw, sh), Image.LANCZOS).rotate(angle, expand=True,
                                                              resample=Image.BICUBIC)
    a = frame.split()[3].point(lambda v: int(v * min(1.0, p * 2.5)))
    frame.putalpha(a)
    im.alpha_composite(frame, (cx - frame.width // 2, cy - frame.height // 2))


# ----------------------------------------------------- 5-stage pipeline
def render_pipeline(im, t):
    slide = ease_out_cubic(prog(t, 0.0, 0.5))
    y_shift = int(-500 * (1 - slide))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = draw_card(layer, y_shift=y_shift)
    y0 = CY0 + y_shift

    hp = ease_out_cubic(prog(t, 0.1, 0.35))
    if hp > 0:
        d.text((CX0 + 34, y0 + 16), "THE BOT", font=f_b(30),
               fill=WHITE + (int(255 * hp),))
        d.text((CX0 + 200, y0 + 22), "— 5 STAGES", font=f_b(26),
               fill=(GREEN[0], GREEN[1], GREEN[2], int(255 * hp)))

    # rows pop on their spoken stage word (slot-relative t)
    rows = [
        ("1", "BACA BERITA", "read the news", 1.10),
        ("2", "FILTER DUPLIKAT", "drop duplicates", 2.08),
        ("3", "CARI STOK", "find the stock hit", 3.26),
        ("4", "BUY / SELL", "make the decision", 4.36),
        ("5", "CEK AMAN", "safety check", 6.82),
    ]
    # §5.3c fit check: rows area y0+52 .. y0+52+4*48+37 = y0+281 (< card 335)
    BH, GAP = 40, 8
    top = y0 + 52
    for i, (num, label, gloss, t_in) in enumerate(rows):
        rp = ease_out_back(prog(t, t_in, 0.32))
        if rp <= 0:
            continue
        ry = top + i * (BH + GAP)
        a = int(255 * min(1.0, prog(t, t_in, 0.16) * 2))
        rx = CX0 + 40 + int(24 * (1 - min(1.0, rp)))
        # number badge
        r = BH // 2 - 3
        bcy = ry + BH // 2
        d.ellipse((rx, bcy - r, rx + 2 * r, bcy + r),
                  fill=GREEN_D + (a,), outline=GREEN + (a,), width=2)
        text_c(d, rx + r, bcy - 15, num, f_b(24), WHITE + (a,))
        d.text((rx + 2 * r + 20, ry + 2), label, font=f_b(27), fill=WHITE + (a,))
        d.text((rx + 2 * r + 20, ry + 30), gloss, font=f_r(18),
               fill=(DIM[0], DIM[1], DIM[2], a))
        # connector arrow to next row
        if i < len(rows) - 1 and prog(t, rows[i + 1][3], 0.16) > 0:
            ax = rx + r
            d.line([(ax, ry + BH), (ax, ry + BH + GAP)], fill=GREEN + (160,), width=3)

    im.alpha_composite(layer)


# ----------------------------------------------------- dedup filter
def render_dedup(im, t):
    slide = ease_out_cubic(prog(t, 0.0, 0.5))
    y_shift = int(-500 * (1 - slide))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = draw_card(layer, y_shift=y_shift)
    y0 = CY0 + y_shift

    hp = ease_out_cubic(prog(t, 0.2, 0.35))
    if hp > 0:
        d.text((CX0 + 34, y0 + 16), "FILTER DUPLIKAT", font=f_b(36),
               fill=WHITE + (int(255 * hp),))

    # three identical headlines stack in; rows 2 & 3 get a red DUPLICATE X
    rows = [
        (1.0, None),
        (1.8, 5.2),
        (2.5, 5.8),
    ]
    BH, GAP = 52, 14
    top = y0 + 70
    for i, (t_in, t_x) in enumerate(rows):
        rp = ease_out_cubic(prog(t, t_in, 0.35))
        if rp <= 0:
            continue
        ry = top + i * (BH + GAP)
        a = int(255 * rp)
        rx = CX0 + 40
        dupe = t_x is not None and prog(t, t_x, 0.3) > 0.4
        oc = RED if dupe else DIM
        rounded(d, (rx, ry, CX1 - 150, ry + BH), 10,
                (NAVY[0] + 10, NAVY[1] + 16, NAVY[2] + 24, int(a * 0.92)),
                outline=oc + (a,), width=2)
        d.text((rx + 24, ry + 12), "REUTERS: MERGER NEWS", font=f_b(28),
               fill=WHITE + (a,) if not dupe else (DIM[0], DIM[1], DIM[2], a))
        if t_x is not None:
            xp = prog(t, t_x, 0.3)
            if xp > 0:
                s = ease_out_back(xp)
                cross_mark(d, CX1 - 100, ry + BH // 2, int(20 * s), RED,
                           width=8, a=int(255 * min(1.0, xp * 2)))

    # NO EDGE stamp across card at "no longer an edge" (t=10.92)
    sp = prog(t, 10.92, 0.35)
    if sp > 0:
        scx, scy = (CX0 + CX1) // 2, (y0 + CY1 + y_shift) // 2
        stamp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(stamp)
        fnt = f_m(120)
        msg = "NO EDGE"
        tw = sd.textlength(msg, font=fnt)
        a = int(235 * min(1.0, sp * 2))
        sd.text((scx - tw / 2, scy - 66), msg, font=fnt, fill=(RED[0], RED[1], RED[2], a),
                stroke_width=4, stroke_fill=(0, 0, 0, a))
        pad = 26
        sd.rectangle((scx - tw / 2 - pad, scy - 72, scx + tw / 2 + pad, scy + 66),
                     outline=(RED[0], RED[1], RED[2], a), width=8)
        s = 0.8 + 0.2 * ease_out_back(sp)
        stamp = stamp.resize((int(W * s), int(H * s)), Image.LANCZOS).rotate(
            -13, expand=False, center=(int(scx * s), int(scy * s)))
        layer.alpha_composite(stamp, (scx - int(scx * s), scy - int(scy * s)))

    # green "FRESH NEWS ONLY" bar pops at "fokus news baru" (t=11.68)
    fp = prog(t, 11.68, 0.32)
    if fp > 0:
        s = ease_out_back(fp)
        bw, bh = 560, 60
        cxb, cyb = (CX0 + CX1) // 2, y0 + 300
        w2, h2 = int(bw * s) // 2, int(bh * s) // 2
        rounded(d, (cxb - w2, cyb - h2, cxb + w2, cyb + h2), 30,
                GREEN + (int(255 * min(1.0, fp * 2)),))
        if fp > 0.5:
            text_c(d, cxb, cyb - 20, "FRESH NEWS ONLY", f_b(34), (8, 20, 14, 255))

    im.alpha_composite(layer)


# ----------------------------------------------------- kill switch
def render_safety(im, t):
    slide = ease_out_cubic(prog(t, 0.0, 0.5))
    y_shift = int(-500 * (1 - slide))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = draw_card(layer, y_shift=y_shift)
    y0 = CY0 + y_shift

    hp = ease_out_cubic(prog(t, 0.2, 0.35))
    if hp > 0:
        d.text((CX0 + 34, y0 + 16), "SAFETY CHECK", font=f_b(36),
               fill=WHITE + (int(255 * hp),))

    # two trigger conditions; each flags red when its line is spoken
    rows = [
        ("POSITION TOO BIG", 2.0, 3.2),
        ("DAILY LOSS LIMIT HIT", 5.2, 6.6),
    ]
    BH, GAP = 56, 14
    top = y0 + 66
    for i, (label, t_in, t_flag) in enumerate(rows):
        rp = ease_out_cubic(prog(t, t_in, 0.35))
        if rp <= 0:
            continue
        ry = top + i * (BH + GAP)
        a = int(255 * rp)
        rx = CX0 + 40
        flagged = prog(t, t_flag, 0.3) > 0.4
        oc = RED if flagged else DIM
        rounded(d, (rx, ry, CX1 - 150, ry + BH), 12,
                (NAVY[0] + 10, NAVY[1] + 16, NAVY[2] + 24, int(a * 0.92)),
                outline=oc + (a,), width=2)
        # warning triangle (Arial has no ⚠ glyph — draw it)
        tx, tcy = rx + 34, ry + BH // 2
        d.polygon([(tx - 15, tcy + 12), (tx + 15, tcy + 12), (tx, tcy - 14)],
                  fill=GOLD + (a,))
        text_c(d, tx, tcy - 10, "!", f_b(22), (40, 30, 6, a))
        d.text((rx + 66, ry + 13), label, font=f_b(30), fill=WHITE + (a,))
        fp = prog(t, t_flag, 0.3)
        if fp > 0:
            s = ease_out_back(fp)
            cross_mark(d, CX1 - 100, ry + BH // 2, int(20 * s), RED,
                       width=8, a=int(255 * min(1.0, fp * 2)))

    # kill-switch toggle slams to OFF at "kill switch" (t=8.76)
    kp = prog(t, 8.76, 0.4)
    if kp > 0:
        scx, scy = (CX0 + CX1) // 2, (y0 + CY1 + y_shift) // 2
        stamp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(stamp)
        fnt = f_m(104)
        msg = "KILL SWITCH"
        tw = sd.textlength(msg, font=fnt)
        a = int(240 * min(1.0, kp * 2))
        sd.text((scx - tw / 2, scy - 58), msg, font=fnt, fill=(RED[0], RED[1], RED[2], a),
                stroke_width=4, stroke_fill=(0, 0, 0, a))
        pad = 26
        sd.rectangle((scx - tw / 2 - pad, scy - 64, scx + tw / 2 + pad, scy + 60),
                     outline=(RED[0], RED[1], RED[2], a), width=8)
        s = 0.82 + 0.18 * ease_out_back(kp)
        stamp = stamp.resize((int(W * s), int(H * s)), Image.LANCZOS).rotate(
            -11, expand=False, center=(int(scx * s), int(scy * s)))
        layer.alpha_composite(stamp, (scx - int(scx * s), scy - int(scy * s)))

    im.alpha_composite(layer)


# ----------------------------------------------------- 4-phase roadmap
def render_roadmap(im, t):
    slide = ease_out_cubic(prog(t, 0.0, 0.5))
    y_shift = int(-500 * (1 - slide))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = draw_card(layer, y_shift=y_shift)
    y0 = CY0 + y_shift

    hp = ease_out_cubic(prog(t, 0.05, 0.3))
    if hp > 0:
        d.text((CX0 + 34, y0 + 14), "5-MONTH ROADMAP", font=f_b(34),
               fill=WHITE + (int(255 * hp),))

    # nodes across the card; phase M3-4 merged (spoken as one beat)
    nodes = [
        ("M1", "COLLECT", "NEWS", 0.16, False),
        ("M2", "CODE", "RULES", 2.46, False),
        ("M3-4", "BACKTEST", "PAPER", 6.18, False),
        ("M5", "GO LIVE", "TRADING", 13.26, True),
    ]
    line_y = y0 + 150
    x0, x1 = CX0 + 90, CX1 - 90
    step = (x1 - x0) // (len(nodes) - 1)
    xs = [x0 + i * step for i in range(len(nodes))]

    # progress rail fills L->R up to the latest activated node
    active = [i for i, n in enumerate(nodes) if prog(t, n[3], 0.3) > 0.2]
    d.line([(x0, line_y), (x1, line_y)], fill=(DIM[0], DIM[1], DIM[2], 120), width=4)
    if active:
        fill_to = xs[max(active)]
        d.line([(x0, line_y), (fill_to, line_y)], fill=GREEN + (255,), width=5)

    for i, (m, l1, l2, t_in, final) in enumerate(nodes):
        p = prog(t, t_in, 0.32)
        x = xs[i]
        base_col = DIM if p <= 0.2 else (GOLD if final else GREEN)
        r = 16
        if p > 0:
            s = ease_out_back(p)
            r = int(16 * (0.6 + 0.4 * s))
        d.ellipse((x - r, line_y - r, x + r, line_y + r),
                  fill=(base_col[0], base_col[1], base_col[2],
                        255 if p > 0.2 else 140),
                  outline=WHITE + (220 if p > 0.2 else 90,), width=3)
        a = int(255 * ease_out_cubic(p)) if p > 0 else 90
        text_c(d, x, line_y - 58, m, f_b(28),
               (base_col[0], base_col[1], base_col[2], max(a, 120)))
        text_c(d, x, line_y + 34, l1, f_b(23), WHITE + (a,) if p > 0.2 else (DIM + (110,)))
        text_c(d, x, line_y + 60, l2, f_r(19),
               (DIM[0], DIM[1], DIM[2], max(a, 110)))
        # GO LIVE glow on final node
        if final and p > 0.4:
            gp = prog(t, t_in + 0.1, 0.4)
            gr = int(r + 10 + 6 * math.sin(t * 6))
            d.ellipse((x - gr, line_y - gr, x + gr, line_y + gr),
                      outline=GOLD + (int(180 * gp),), width=3)

    im.alpha_composite(layer)


SLOTS = {
    "slot_pvz_day7":     (3.2,  render_day7),
    "slot_gfx_pipeline": (9.4,  render_pipeline),
    "slot_gfx_dedup":    (12.5, render_dedup),
    "slot_gfx_safety":   (11.3, render_safety),
    "slot_gfx_roadmap":  (15.9, render_roadmap),
}

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, (dur, fn) in SLOTS.items():
        if which in ("all", name):
            save_frames(name, dur, fn)
