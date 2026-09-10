"""Build reel 1 (Day 6) overlays v4 — hybrid meme pass (creator request, Session 3).

Same timeline as v3. Meme changes: hook pill wiggles after landing, PEAD drift
label is now Impact-font STONKS, SEC card gets an "IT'S FREE REAL ESTATE" banner,
reject stamp says NOPE. Fintech navy card system otherwise unchanged.

v3 = jump-cut timeline (edl_v3.json): cold-open hook + collapsed silences, so every
payoff word moved. All sync constants retimed; tech2's $0 pill removed (that line IS
the hook now, with its own slot); tech1 stretched (drift draws on "following...weeks").

Slots (all 1080x1920 RGBA, 30 fps, top-band rule: everything inside y 0-760):
  slot_hook_pill  3.4s  cold-open gold "$0" pill (no card, floats top band)
  slot_pvz_day6   3.0s  blueprint "DAY 6" intro sign (theme: build/blueprint)
  slot_gfx_tech1 13.0s  PEAD card — flat price, earnings-beat marker, drift line
  slot_gfx_tech2 12.2s  SEC filings card — doc stack, FREE/PUBLIC badges
  slot_gfx_reject 10.8s rejected-techniques card — two X rows + SKIPPED stamp
  slot_gfx_steps 10.7s  roadmap card — 3 step rows + KTrade v1 banner + check

Payoff sync targets (output timeline, from edl_v3.json offsets):
  hook:  "track" out 0.78      -> pill pops t=0.28 (starts 0.50)
  day6:  "six" lands out 5.00  -> pop lands t=1.10 (starts 3.90)
  tech1: "PEAD" out 26.77      -> title lands t=1.17 (starts 25.60)
         "beating" out 31.35 -> marker t=5.75; "following...weeks" out 35.5-38.3
         -> drift t=9.9-12.2, label t=11.9
  tech2: "SECs" out 41.69      -> title lands t=1.30 (starts 40.39)
         "free" out 48.31 t=7.92 / "public" out 48.77 t=8.38
  reject:"money" out 58.49 t=5.69 / "corporations" out 60.73 t=7.93
         "terrible" out 62.19 t=9.39 (stamp)  (starts 52.80)
  steps: "step two" out 64.43 t=0.58 / "step three" out 67.87 t=4.02
         "KTrade" out 71.91 t=8.06 / "done" out 74.13 t=10.28  (starts 63.85)
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
BLUEPRINT = (90, 150, 220)  # blueprint grid line color

FONT_B = font_path("arialbd")
FONT_MEME = font_path("impact")  # Impact = the meme font
FONT_R = font_path("arial")

EDIT = os.path.dirname(os.path.abspath(__file__))


def f_b(size): return ImageFont.truetype(FONT_B, size)
def f_m(size): return ImageFont.truetype(FONT_MEME, size)
def f_r(size): return ImageFont.truetype(FONT_R, size)


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
    """0..1 progress of a sub-animation that begins at `start` and runs `dur`."""
    if dur <= 0:
        return 1.0 if t >= start else 0.0
    return max(0.0, min(1.0, (t - start) / dur))


def rounded(d, box, r, fill, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def draw_card(layer, alpha=238, y_shift=0):
    """Standard navy rounded card in the top band, optionally slid vertically."""
    d = ImageDraw.Draw(layer)
    rounded(d, (CX0, CY0 + y_shift, CX1, CY1 + y_shift), 26,
            PANEL + (alpha,), outline=GREEN + (200,), width=3)
    return d


def text_c(d, cx, y, s, font, fill):
    """Draw text horizontally centered on cx (top-anchored at y)."""
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


# ---------------------------------------------------------------- DAY 6 sign
def render_day6(im, t):
    # card slides down from above, ease_out_cubic, 0-0.5s
    slide = ease_out_cubic(prog(t, 0.0, 0.5))
    y_shift = int(-500 * (1 - slide))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = draw_card(layer, alpha=242, y_shift=y_shift)

    y0 = CY0 + y_shift
    y1 = CY1 + y_shift

    # blueprint grid inside the card
    grid_a = int(70 * slide)
    for gx in range(CX0 + 40, CX1, 46):
        d.line([(gx, y0 + 8), (gx, y1 - 8)], fill=BLUEPRINT + (grid_a,), width=1)
    for gy in range(y0 + 40, y1, 46):
        d.line([(CX0 + 8, gy), (CX1 - 8, gy)], fill=BLUEPRINT + (grid_a,), width=1)

    # corner drafting brackets draw in 0.2-0.6s
    bp = ease_out_cubic(prog(t, 0.2, 0.4))
    if bp > 0:
        L = int(46 * bp)
        wdt = 5
        for (cx, cy, sx, sy) in [(CX0 + 18, y0 + 18, 1, 1), (CX1 - 18, y0 + 18, -1, 1),
                                 (CX0 + 18, y1 - 18, 1, -1), (CX1 - 18, y1 - 18, -1, -1)]:
            d.line([(cx, cy), (cx + sx * L, cy)], fill=WHITE + (230,), width=wdt)
            d.line([(cx, cy), (cx, cy + sy * L)], fill=WHITE + (230,), width=wdt)

    # "DAY 6" pops with overshoot, landing at t=1.10 (0.7-1.1) = spoken "six"
    pp = prog(t, 0.7, 0.4)
    if pp > 0:
        s = ease_out_back(pp)
        txt = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
        td = ImageDraw.Draw(txt)
        fnt = f_b(148)
        msg = "DAY 6"
        tw = td.textlength(msg, font=fnt)
        td.text(((W - tw) / 2, 40), msg, font=fnt, fill=WHITE + (255,))
        # measure-line flourish under the text, blueprint style
        lw = int(tw * 0.9)
        lx = (W - lw) // 2
        td.line([(lx, 230), (lx + lw, 230)], fill=GREEN + (255,), width=4)
        td.line([(lx, 220), (lx, 240)], fill=GREEN + (255,), width=4)
        td.line([(lx + lw, 220), (lx + lw, 240)], fill=GREEN + (255,), width=4)
        sw = max(1, int(txt.width * (0.6 + 0.4 * s)))
        sh = max(1, int(txt.height * (0.6 + 0.4 * s)))
        scaled = txt.resize((sw, sh), Image.LANCZOS)
        a = scaled.split()[3].point(lambda v: int(v * min(1.0, pp * 2)))
        scaled.putalpha(a)
        cx, cy = W // 2, y0 + 145
        layer.alpha_composite(scaled, (cx - sw // 2, cy - sh // 2))

    # subtitle fades in 1.4-1.8s, gentle float afterwards
    sp = ease_out_cubic(prog(t, 1.4, 0.4))
    if sp > 0:
        d2 = ImageDraw.Draw(layer)
        bob = int(2 * math.sin((t - 1.4) * 2.2)) if t > 1.8 else 0
        fnt = f_b(40)
        msg = "BUILD PHASE — TRADING BOT"
        w2 = d2.textlength(msg, font=fnt)
        d2.text(((W - w2) / 2, y0 + 258 + bob), msg, font=fnt,
                fill=(GREEN[0], GREEN[1], GREEN[2], int(255 * sp)))

    im.alpha_composite(layer)


# ---------------------------------------------------------------- TECH 1 PEAD
def render_tech1(im, t):
    slide = ease_out_cubic(prog(t, 0.0, 0.5))
    y_shift = int(-500 * (1 - slide))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = draw_card(layer, y_shift=y_shift)
    y0 = CY0 + y_shift

    # header lands with spoken "PEAD" (t=1.17)
    hp = ease_out_cubic(prog(t, 0.82, 0.35))
    if hp > 0:
        a = int(255 * hp)
        d.text((CX0 + 40, y0 + 24), "TECHNIQUE 1", font=f_b(30),
               fill=(GREEN[0], GREEN[1], GREEN[2], a))
        d.text((CX0 + 40, y0 + 60), "PEAD", font=f_b(64), fill=WHITE + (a,))
        d.text((CX0 + 260, y0 + 84), "Post-Earnings Announcement Drift",
               font=f_r(28), fill=(DIM[0], DIM[1], DIM[2], a))

    # chart area
    ax0, ay0, ax1, ay1 = CX0 + 60, y0 + 150, CX1 - 60, y0 + 315
    base_y = ay1 - 30
    mark_x = ax0 + int((ax1 - ax0) * 0.35)

    axis_p = ease_out_cubic(prog(t, 1.2, 0.5))
    if axis_p > 0:
        a = int(150 * axis_p)
        d.line([(ax0, ay1), (ax0 + int((ax1 - ax0) * axis_p), ay1)],
               fill=(DIM[0], DIM[1], DIM[2], a), width=2)

    # flat pre-earnings price line draws 1.5-3.0s
    fp = ease_in_out_cubic(prog(t, 1.5, 1.5))
    if fp > 0:
        end_x = ax0 + int((mark_x - ax0) * fp)
        pts = [(x, base_y + int(4 * math.sin(x * 0.05)))
               for x in range(ax0, end_x + 1, 6)]
        if len(pts) > 1:
            d.line(pts, fill=(DIM[0], DIM[1], DIM[2], 220), width=4)

    # earnings-beat marker pops at t=5.75 (synced to "beating ... expectations")
    mp = prog(t, 5.75, 0.35)
    if mp > 0:
        s = ease_out_back(mp)
        r = int(13 * s)
        d.ellipse((mark_x - r, base_y - r, mark_x + r, base_y + r),
                  fill=GREEN_D + (255,), outline=GREEN + (255,), width=3)
        a = int(255 * min(1.0, mp * 2))
        d.line([(mark_x, ay0 + 26), (mark_x, base_y - r - 4)],
               fill=(GREEN[0], GREEN[1], GREEN[2], int(a * 0.55)), width=2)
        text_c(d, mark_x, ay0 - 4, "EARNINGS BEAT", f_b(26),
               (GREEN[0], GREEN[1], GREEN[2], a))

    # drift line rises 9.9-12.2s (synced to "following ... several weeks")
    dp = ease_in_out_cubic(prog(t, 9.9, 2.3))
    if dp > 0:
        n = max(2, int(40 * dp))
        pts = []
        for i in range(n):
            u = i / 39
            x = mark_x + (ax1 - mark_x) * u
            y = base_y - (base_y - (ay0 + 40)) * (u ** 0.8) * 0.92
            pts.append((x, y + 2 * math.sin(x * 0.07)))
        d.line(pts, fill=GREEN + (255,), width=5)

    # STONKS pops at drift completion t=11.9 (meme pass: was "DRIFT (WEEKS)")
    lp = prog(t, 11.9, 0.35)
    if lp > 0:
        s = ease_out_back(lp)
        a = int(255 * min(1.0, lp * 2))
        txt = Image.new("RGBA", (400, 120), (0, 0, 0, 0))
        td = ImageDraw.Draw(txt)
        td.text((20, 20), "STONKS", font=f_m(64), fill=(255, 165, 0, a),
                stroke_width=4, stroke_fill=(0, 0, 0, a))
        sw, sh = max(1, int(400 * s)), max(1, int(120 * s))
        # sits under the rising drift line, clear of the EARNINGS BEAT label (§5.3a)
        scaled = txt.resize((sw, sh), Image.LANCZOS).rotate(8, expand=True)
        layer.alpha_composite(scaled, (mark_x + 330 - scaled.width // 2,
                                       base_y - 60 - scaled.height // 2))

    im.alpha_composite(layer)


# ---------------------------------------------------------------- TECH 2 SEC
def render_tech2(im, t):
    slide = ease_out_cubic(prog(t, 0.0, 0.5))
    y_shift = int(-500 * (1 - slide))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = draw_card(layer, y_shift=y_shift)
    y0 = CY0 + y_shift

    hp = ease_out_cubic(prog(t, 0.95, 0.35))
    if hp > 0:
        a = int(255 * hp)
        d.text((CX0 + 40, y0 + 24), "TECHNIQUE 2", font=f_b(30),
               fill=(GREEN[0], GREEN[1], GREEN[2], a))
        d.text((CX0 + 40, y0 + 60), "SEC FILINGS", font=f_b(64), fill=WHITE + (a,))

    # document stack draws 1.0-2.0s (three offset pages, right side)
    dp = ease_out_cubic(prog(t, 1.0, 1.0))
    if dp > 0:
        a = int(255 * dp)
        px, py = CX1 - 300, y0 + 40
        for k in range(3):
            off = (2 - k) * 16
            pa = int(a * (0.45 + 0.275 * k))
            rounded(d, (px + off, py + off, px + off + 170, py + off + 110), 8,
                    (NAVY[0] + 12, NAVY[1] + 22, NAVY[2] + 30, pa),
                    outline=(DIM[0], DIM[1], DIM[2], pa), width=2)
        for ln in range(4):
            ly = py + 32 + 18 * ln + 32
            lw = 120 - 18 * (ln % 2)
            d.line([(px + 32 + 18, ly), (px + 32 + 18 + int(lw * dp), ly)],
                   fill=(DIM[0], DIM[1], DIM[2], a), width=4)

    # FREE / PUBLIC badges pop on their spoken words (t=7.29 / 7.75)
    def badge(label, bx, pop_t, color):
        p = prog(t, pop_t, 0.35)
        if p <= 0:
            return
        s = ease_out_back(p)
        bw, bh = 190, 66
        cxb, cyb = bx + bw // 2, y0 + 235
        w2, h2 = int(bw * s) // 2, int(bh * s) // 2
        rounded(d, (cxb - w2, cyb - h2, cxb + w2, cyb + h2), 30,
                color + (int(255 * min(1.0, p * 2)),))
        if p > 0.5:
            fnt = f_b(34)
            tw = d.textlength(label, font=fnt)
            d.text((cxb - tw / 2, cyb - 22), label, font=fnt, fill=(8, 20, 14, 255))

    badge("FREE", CX0 + 60, 7.92, GREEN)
    badge("PUBLIC", CX0 + 290, 8.38, GREEN)
    # (v1's $0 pill removed — that line is now the cold-open hook, slot_hook_pill)

    # meme banner pops during "langsung dari file-nya SEC sendiri" (t=9.5)
    p = prog(t, 9.5, 0.35)
    if p > 0:
        s = ease_out_back(p)
        a = int(255 * min(1.0, p * 2))
        txt = Image.new("RGBA", (900, 110), (0, 0, 0, 0))
        td = ImageDraw.Draw(txt)
        msg = "IT'S FREE REAL ESTATE"
        fnt = f_m(58)
        tw = td.textlength(msg, font=fnt)
        td.text(((900 - tw) / 2, 18), msg, font=fnt, fill=(255, 255, 255, a),
                stroke_width=4, stroke_fill=(0, 0, 0, a))
        sw, sh = max(1, int(900 * s)), max(1, int(110 * s))
        scaled = txt.resize((sw, sh), Image.LANCZOS).rotate(-2, expand=True)
        cxb = (CX0 + CX1) // 2
        layer.alpha_composite(scaled, (cxb - scaled.width // 2,
                                       y0 + 330 - scaled.height // 2))

    im.alpha_composite(layer)


# ---------------------------------------------------------------- REJECT card
def render_reject(im, t):
    slide = ease_out_cubic(prog(t, 0.0, 0.5))
    y_shift = int(-500 * (1 - slide))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = draw_card(layer, y_shift=y_shift)
    y0 = CY0 + y_shift

    hp = ease_out_cubic(prog(t, 0.2, 0.35))
    if hp > 0:
        a = int(255 * hp)
        d.text((CX0 + 40, y0 + 24), "THE OTHER TECHNIQUES?", font=f_b(44),
               fill=WHITE + (a,))

    # two rejection rows; X pops sync to "money" (t=5.69) / "corporations" (t=7.93)
    rows = [
        ("NEED TOO MUCH MONEY", 1.0, 5.69),
        ("COMPETE WITH WALL ST GIANTS", 1.4, 7.93),
    ]
    BH, GAP = 78, 22
    top = y0 + 110
    for i, (label, t_in, t_x) in enumerate(rows):
        rp = ease_out_cubic(prog(t, t_in, 0.4))
        if rp <= 0:
            continue
        ry = top + i * (BH + GAP)
        a = int(255 * rp)
        rx = CX0 + 40 + int(30 * (1 - rp))
        rounded(d, (rx, ry, CX1 - 140, ry + BH), 14,
                (NAVY[0] + 10, NAVY[1] + 16, NAVY[2] + 24, int(a * 0.9)),
                outline=(DIM[0], DIM[1], DIM[2], a), width=2)
        d.text((rx + 28, ry + 20), label, font=f_b(34), fill=WHITE + (a,))
        xp = prog(t, t_x, 0.3)
        if xp > 0:
            s = ease_out_back(xp)
            cross_mark(d, CX1 - 90, ry + BH // 2, int(24 * s), RED,
                       width=9, a=int(255 * min(1.0, xp * 2)))

    # diagonal SKIPPED stamp across the whole card at "terrible idea" (t=9.39)
    sp = prog(t, 9.39, 0.35)
    if sp > 0:
        scx, scy = (CX0 + CX1) // 2, (y0 + CY1 + y_shift) // 2
        stamp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(stamp)
        fnt = f_m(130)
        msg = "NOPE."
        tw = sd.textlength(msg, font=fnt)
        a = int(235 * min(1.0, sp * 2))
        sd.text((scx - tw / 2, scy - 70), msg, font=fnt,
                fill=(RED[0], RED[1], RED[2], a))
        pad = 30
        sd.rectangle((scx - tw / 2 - pad, scy - 78, scx + tw / 2 + pad, scy + 70),
                     outline=(RED[0], RED[1], RED[2], a), width=8)
        s = 0.8 + 0.2 * ease_out_back(sp)
        sw, sh = int(W * s), int(H * s)
        stamp = stamp.resize((sw, sh), Image.LANCZOS).rotate(
            -14, expand=False, center=(int(scx * s), int(scy * s)))
        layer.alpha_composite(stamp, (scx - int(scx * s), scy - int(scy * s)))

    im.alpha_composite(layer)


# ---------------------------------------------------------------- STEPS card
def render_steps(im, t):
    slide = ease_out_cubic(prog(t, 0.0, 0.4))
    y_shift = int(-500 * (1 - slide))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = draw_card(layer, y_shift=y_shift)
    y0 = CY0 + y_shift

    hp = ease_out_cubic(prog(t, 0.15, 0.3))
    if hp > 0:
        a = int(255 * hp)
        d.text((CX0 + 40, y0 + 20), "KTRADE BOT — ROADMAP", font=f_b(40),
               fill=WHITE + (a,))

    # rows appear on their spoken beats; geometry checked per guide §5.3c:
    # rows area y0+82 .. y0+272 (190px) = 3*BH(52) + 2*GAP(17) = 190  ✓
    BH, GAP = 52, 17
    top = y0 + 82
    rows = [
        ("1. RESEARCH", 0.30, True),    # already done in prior videos
        ("2. CODE THE TECHNIQUES", 0.58, False),   # "step two" t=0.58
        ("3. BACKTEST + PAPER TRADE", 4.02, False),  # "step three" t=4.02
    ]
    for i, (label, t_in, done) in enumerate(rows):
        rp = ease_out_cubic(prog(t, t_in, 0.4))
        if rp <= 0:
            continue
        ry = top + i * (BH + GAP)
        a = int(255 * rp)
        rx = CX0 + 40 + int(30 * (1 - rp))
        rounded(d, (rx, ry, CX1 - 140, ry + BH), 12,
                (NAVY[0] + 10, NAVY[1] + 16, NAVY[2] + 24, int(a * 0.9)),
                outline=(GREEN[0], GREEN[1], GREEN[2], a) if done
                else (DIM[0], DIM[1], DIM[2], a), width=2)
        d.text((rx + 24, ry + 10), label, font=f_b(30), fill=WHITE + (a,))
        if done:
            check_mark(d, CX1 - 90, ry + BH // 2, 16, GREEN, width=7, a=a)

    # gold v1 banner pops at "KTrade" (t=8.06)
    bp = prog(t, 8.06, 0.35)
    if bp > 0:
        s = ease_out_back(bp)
        bw, bh = 560, 62
        cxb, cyb = (CX0 + CX1) // 2, y0 + 300
        w2, h2 = int(bw * s) // 2, int(bh * s) // 2
        rounded(d, (cxb - w2, cyb - h2, cxb + w2, cyb + h2), 30,
                GOLD + (int(255 * min(1.0, bp * 2)),))
        if bp > 0.5:
            fnt = f_b(34)
            msg = "= KTRADE BOT  v1"
            tw = d.textlength(msg, font=fnt)
            d.text((cxb - tw / 2, cyb - 22), msg, font=fnt, fill=(40, 30, 6, 255))

    # green check next to banner at "done" (t=10.28)
    cp = prog(t, 10.28, 0.3)
    if cp > 0:
        s = ease_out_back(cp)
        check_mark(d, CX1 - 110, y0 + 300, int(22 * s), GREEN,
                   width=9, a=int(255 * min(1.0, cp * 2)))

    im.alpha_composite(layer)


# ---------------------------------------------------------------- HOOK pill
def render_hook(im, t):
    """Cold-open gold pill — pops on "track" (t=0.28), then a damped wiggle
    (meme pass: the bounce reads as a comedic stamp, not a sterile land)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    p = prog(t, 0.03, 0.35)
    if p > 0:
        s = ease_out_back(p)
        bw, bh = 760, 92
        cxb, cyb = W // 2, 250
        w2, h2 = int(bw * s) // 2, int(bh * s) // 2
        rounded(d, (cxb - w2, cyb - h2, cxb + w2, cyb + h2), 46,
                GOLD + (int(255 * min(1.0, p * 2)),),
                outline=(40, 30, 6, int(255 * min(1.0, p * 2))), width=4)
        if p > 0.5:
            fnt = f_b(40)
            msg = "$0 — TRACK EVERY CORPORATION"
            tw = d.textlength(msg, font=fnt)
            d.text((cxb - tw / 2, cyb - 27), msg, font=fnt, fill=(40, 30, 6, 255))
        # damped rotation wiggle after the pop lands
        if t > 0.38:
            wig = 6.0 * math.exp(-2.2 * (t - 0.38)) * math.sin(9 * (t - 0.38))
            if abs(wig) > 0.05:
                layer = layer.rotate(wig, resample=Image.BICUBIC,
                                     center=(cxb, cyb))
    im.alpha_composite(layer)


SLOTS = {
    "slot_hook_pill":  (3.4,  render_hook),
    "slot_pvz_day6":   (3.0,  render_day6),
    "slot_gfx_tech1":  (13.0, render_tech1),
    "slot_gfx_tech2":  (12.2, render_tech2),
    "slot_gfx_reject": (10.8, render_reject),
    "slot_gfx_steps":  (10.7, render_steps),
}

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, (dur, fn) in SLOTS.items():
        if which in ("all", name):
            save_frames(name, dur, fn)
