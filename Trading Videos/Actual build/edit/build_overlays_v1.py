"""Build reel 3 (Day 8) overlays — news ingestion (Alpaca / SEC EDGAR / Finnhub).

Top-band rule (§5.1): every graphic lives inside y 96-404. This footage is framed
tighter than reels 1-2 (hair top y500-680 wide, y423-468 after the 1.12x punch),
so the card box is raised/shortened vs the guide's 120-455 default. Navy fintech
card system (§5.2) + hybrid meme accents (§10.5). Payoff-word sync per §5.3.

Slots (all 1080x1920 RGBA, 30 fps) with their EDL start_in_output:
  slot_hook_upcoming   2.6s  @ 0.00   COMING UP flash-forward sign over the B&W hook
  slot_pvz_day8        3.2s  @ 2.66   terminal / news-wire DAY 8 intro sign
  slot_gfx_sources     9.0s  @ 6.90   Bloomberg priced out -> Alpaca + SEC EDGAR (free)
  slot_gfx_why1        7.35s @ 15.95  why Alpaca: broker API already integrated
  slot_gfx_why2        7.9s  @ 23.50  why SEC: the technique promised on day 7
  slot_gfx_block       3.8s  @ 32.60  geo check -> BLOCKED? stamp on "Indonesia"
  slot_gfx_finnhub     8.8s  @ 37.60  Alpaca out / Finnhub in, news-only, CLUTCH.
  slot_gfx_webhook     5.75s @ 48.85  NEWS -> WEBHOOK -> BOT push flow
  slot_gfx_auto        5.5s  @ 54.90  daily fresh news, no intervention, SET AND FORGET
  slot_gfx_normalize   4.5s  @ 60.50  two formats -> NORMALIZE -> one format
  slot_gfx_sqlite     10.0s  @ 65.10  SQLite cylinder -> backtesting
  slot_gfx_outro       2.7s  @ 85.20  LIKE + FOLLOW badges
  slot_explosion       1.0s  @ 88.90  hand covers the lens, then it all detonates

All times inside a render_* function are SLOT-RELATIVE. Payoff targets were
derived as out = word.start - range.start + range.offset from edl_v1.json.
"""

import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

# Resolve fonts through the repo-root helper so these render off Windows too.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")))
from fonts import font_path

W, H = 1080, 1920
FPS = 30

# Card box — raised and shortened vs guide default (see module docstring)
CX0, CY0, CX1, CY1 = 80, 96, 1000, 404
CCX, CCY = (CX0 + CX1) // 2, (CY0 + CY1) // 2

GREEN   = (22, 199, 132)
GREEN_D = (10, 150, 98)
NAVY    = (11, 31, 58)
PANEL   = (12, 22, 40)
WHITE   = (255, 255, 255)
DIM     = (158, 168, 184)
RED     = (235, 90, 95)
RED_HOT = (255, 74, 74)   # stamps only: pops off the dark card
GOLD    = (245, 196, 90)
TERM_BG = (6, 12, 9)        # terminal window background
ID_RED  = (206, 17, 38)     # Indonesian flag red

FONT_B = font_path("arialbd")
FONT_R = font_path("arial")
FONT_MEME = font_path("impact")
FONT_MONO = font_path("consolab")

EDIT = os.path.dirname(os.path.abspath(__file__))


def f_b(size): return ImageFont.truetype(FONT_B, size)
def f_r(size): return ImageFont.truetype(FONT_R, size)
def f_m(size): return ImageFont.truetype(FONT_MEME, size)
def f_x(size): return ImageFont.truetype(FONT_MONO, size)


# -------- easing + timing helpers -------------------------------------------

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


def wiggle_deg(t, t0, amp=6.0, decay=2.2, freq=9.0):
    """Damped comedic rotation after a pop landing (§10.5)."""
    if t < t0:
        return 0.0
    return amp * math.exp(-decay * (t - t0)) * math.sin(freq * (t - t0))


# -------- drawing helpers ----------------------------------------------------

def rounded(d, box, r, fill, outline=None, width=1):
    """Rounded rect that refuses to draw a fully transparent fill.

    PIL draws onto an RGBA layer by REPLACING pixels, not compositing, so a
    fill with alpha 0 punches a hole straight through the card underneath it.
    Guarding here kills the whole class of bug rather than at each call site.
    """
    if fill is not None and len(fill) == 4 and fill[3] <= 0:
        return
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def appearing(t, t_in):
    """True once an element's entrance has started.

    Gate on raw time, never on the eased value: ease_out_back(0) can return a
    float epsilon instead of exactly 0, which let zero-alpha rows draw.
    """
    return t >= t_in


def slide_shift(t, dur_in=0.42, total=None, dur_out=0.35):
    """Card slides down from above; slides back up at the end when `total` given."""
    y = int(-520 * (1 - ease_out_cubic(prog(t, 0.0, dur_in))))
    if total is not None:
        y += int(-520 * ease_in_out_cubic(prog(t, total - dur_out, dur_out)))
    return y


def draw_card(layer, y_shift=0, alpha=251, accent=GREEN):
    # alpha 251, not the guide's 238: this room's shelving is busy enough that
    # binder rings read through a 238 card and look like empty UI chips.
    d = ImageDraw.Draw(layer)
    rounded(d, (CX0, CY0 + y_shift, CX1, CY1 + y_shift), 26,
            PANEL + (alpha,), outline=accent + (200,), width=3)
    return d


CARD_H = CY1 - CY0        # 308 px of usable card height
BODY_TOP = 62             # first row starts below the header band


def fits(*bottoms):
    """Fail loudly if any card-relative bottom edge runs past the card (§5.3c).

    Overflow is invisible until playback, so every stacked layout asserts here
    instead of being eyeballed.
    """
    for b in bottoms:
        if b > CARD_H:
            raise AssertionError(f"layout overflows card: {b} > {CARD_H}")
    return True


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


def arrow_h(d, x0, x1, y, color, a=255, width=6, head=16):
    """Horizontal arrow pointing right."""
    d.line([(x0, y), (x1 - head, y)], fill=color + (a,), width=width)
    d.polygon([(x1, y), (x1 - head, y - head * 0.62), (x1 - head, y + head * 0.62)],
              fill=color + (a,))


def header(d, y0, title, gloss=None, size=34, accent=WHITE):
    d.text((CX0 + 34, y0 + 10), title, font=f_b(size), fill=accent + (255,))
    if gloss:
        tw = d.textlength(title, font=f_b(size))
        d.text((CX0 + 44 + tw, y0 + 20), gloss, font=f_r(22), fill=DIM + (225,))


def meme_stamp(layer, t, t0, msg, color=RED, size=104, tilt=-13, fade_at=None,
               y_off=0):
    """Impact-font stamp slammed across the whole card (§5.3d state-flip pattern).

    fade_at: slot time at which the stamp starts a 0.2s fade-out (so a later
    element can own the card). None = stays for the rest of the slot.
    """
    p = prog(t, t0, 0.35)
    if p <= 0:
        return
    a_mul = 1.0
    if fade_at is not None:
        a_mul = 1.0 - prog(t, fade_at, 0.20)
        if a_mul <= 0:
            return
    scx, scy = CCX, CCY + y_off
    stamp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    fnt = f_m(size)
    tw = sd.textlength(msg, font=fnt)
    a = int(240 * min(1.0, p * 2) * a_mul)
    sd.text((scx - tw / 2, scy - size * 0.56), msg, font=fnt, fill=color + (a,),
            stroke_width=4, stroke_fill=(0, 0, 0, a))
    pad = 26
    sd.rectangle((scx - tw / 2 - pad, scy - size * 0.62,
                  scx + tw / 2 + pad, scy + size * 0.58),
                 outline=color + (a,), width=8)
    s = 0.82 + 0.18 * ease_out_back(p)
    stamp = stamp.resize((int(W * s), int(H * s)), Image.LANCZOS).rotate(
        tilt + wiggle_deg(t, t0 + 0.35, amp=3.5), expand=False,
        center=(int(scx * s), int(scy * s)))
    layer.alpha_composite(stamp, (scx - int(scx * s), scy - int(scy * s)))


def meme_sticker(layer, t, t0, msg, cx, cy, color=GREEN, size=64, tilt=-8):
    """Impact tag pinned to one corner of the card, NOT across it (§5.3a).

    A full-card `meme_stamp` buries the row labels underneath it. Use this when
    the rows still need to be readable while the punchline lands.
    """
    p = prog(t, t0, 0.30)
    if p <= 0:
        return
    a = int(255 * min(1.0, p * 2.2))
    s = 0.62 + 0.38 * ease_out_back(p)
    tag = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tag)
    fnt = f_m(size)
    tw = td.textlength(msg, font=fnt)
    td.text((cx - tw / 2, cy - size * 0.58), msg, font=fnt, fill=color + (a,),
            stroke_width=4, stroke_fill=(0, 0, 0, a))
    pad_x, pad_y = 20, int(size * 0.14)
    td.rectangle((cx - tw / 2 - pad_x, cy - size * 0.66,
                  cx + tw / 2 + pad_x, cy + size * 0.52 + pad_y),
                 outline=color + (a,), width=6)
    tag = tag.resize((int(W * s), int(H * s)), Image.LANCZOS).rotate(
        tilt + wiggle_deg(t, t0 + 0.30, amp=5.0), expand=False,
        center=(int(cx * s), int(cy * s)))
    layer.alpha_composite(tag, (cx - int(cx * s), cy - int(cy * s)))


def save_frames(name, total_s, render_fn):
    slot = os.path.join(EDIT, "animations", name, "frames")
    os.makedirs(slot, exist_ok=True)
    n = int(round(total_s * FPS))
    for i in range(n):
        t = i / FPS
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        render_fn(im, t)
        im.save(os.path.join(slot, f"f_{i:05d}.png"))
    print(f"{name}: {n} frames ({total_s:.2f}s)")


# ---------------------------------------------------- 1. COMING UP hook sign
def render_hook_upcoming(im, t):
    """Flash-forward marker over the black-and-white cold open.

    Deliberately NOT the navy fintech card: a black/white broadcast slug reads
    as "this clip is from later", which is the whole point of the B&W treatment.
    """
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    p = ease_out_back(prog(t, 0.0, 0.35))
    y = int(150 - 320 * (1 - p))
    a = int(255 * min(1.0, prog(t, 0.0, 0.18) * 2))

    bx0, bx1 = 130, 950
    bh = 150
    rounded(d, (bx0, y, bx1, y + bh), 18, (8, 8, 8, int(a * 0.88)),
            outline=(255, 255, 255, a), width=3)

    # blinking record dot — 2 Hz, the "we are showing you a clip" tell
    blink = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * 4 * math.pi))
    d.ellipse((168, y + 58, 202, y + 92), fill=(235, 60, 60, int(a * blink)))

    # play triangle (Arial has no glyph for it — draw the shape, §10.6)
    d.polygon([(228, y + 56), (228, y + 94), (262, y + 75)],
              fill=(255, 255, 255, a))

    txt = "COMING UP"
    fnt = f_m(84)
    tw = d.textlength(txt, font=fnt)
    d.text((610 - tw / 2, y + 26), txt, font=fnt, fill=(255, 255, 255, a),
           stroke_width=5, stroke_fill=(0, 0, 0, a))
    sub = "LATER IN THIS VIDEO"
    fs = f_b(24)
    sw = d.textlength(sub, font=fs)
    d.text((610 - sw / 2, y + 112), sub, font=fs, fill=(210, 210, 210, a))

    # damped wiggle after the landing, rotated about the slug's own centre
    ang = wiggle_deg(t, 0.35, amp=2.4, decay=2.6, freq=10.0)
    if abs(ang) > 0.02:
        layer = layer.rotate(ang, expand=False, center=(540, y + bh // 2),
                             resample=Image.BICUBIC)
    im.alpha_composite(layer)


# ---------------------------------------------------- 2. DAY 8 terminal sign
def render_day8(im, t):
    """News-wire terminal window. 'DAY 8' stamps on the spoken '8' (slot t 0.35)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    y_shift = int(-380 * (1 - ease_out_cubic(prog(t, 0.0, 0.14))))
    y_shift -= int(460 * ease_in_out_cubic(prog(t, 2.85, 0.35)))
    d = ImageDraw.Draw(layer)
    y0 = CY0 + y_shift

    rounded(d, (CX0, y0, CX1, CY1 + y_shift), 18, TERM_BG + (242,),
            outline=GREEN + (210,), width=3)

    # title bar
    d.line([(CX0 + 2, y0 + 44), (CX1 - 2, y0 + 44)], fill=GREEN + (90,), width=2)
    for i, col in enumerate([(235, 90, 95), (245, 196, 90), (22, 199, 132)]):
        cx = CX0 + 34 + i * 30
        d.ellipse((cx - 8, y0 + 14, cx + 8, y0 + 30), fill=col + (235,))
    d.text((CX0 + 150, y0 + 12), "kendrew@bot: ~/news-ingest", font=f_x(21),
           fill=DIM + (225,))

    # scrolling ticker tape — continuous motion keeps the card alive
    tape = ("AAPL +1.2%   MSFT -0.4%   NVDA +3.8%   SEC 8-K FILED   "
            "TSLA +0.9%   MERGER ALERT   ")
    ftk = f_x(23)
    seg_w = d.textlength(tape, font=ftk)
    strip = Image.new("RGBA", (CX1 - CX0 - 8, 34), (0, 0, 0, 0))
    sd = ImageDraw.Draw(strip)
    off = -(t * 150) % seg_w
    x = -off
    while x < strip.width:
        sd.text((x, 3), tape, font=ftk, fill=GREEN + (150,))
        x += seg_w
    layer.alpha_composite(strip, (CX0 + 4, y0 + 56))

    # DAY 8 — slams in, lands on the spoken "8"
    p = prog(t, 0.05, 0.30)
    if p > 0:
        s = 0.55 + 0.45 * ease_out_back(p)
        big = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bd = ImageDraw.Draw(big)
        fnt = f_m(120)
        msg = "DAY 8"
        tw = bd.textlength(msg, font=fnt)
        a = int(255 * min(1.0, p * 2.2))
        bd.text((540 - tw / 2, y0 + 96), msg, font=fnt, fill=GREEN + (a,),
                stroke_width=5, stroke_fill=(0, 40, 24, a))
        big = big.resize((int(W * s), int(H * s)), Image.LANCZOS)
        ang = wiggle_deg(t, 0.35, amp=3.0, decay=3.0, freq=11.0)
        big = big.rotate(ang, expand=False,
                         center=(int(540 * s), int((y0 + 156) * s)),
                         resample=Image.BICUBIC)
        layer.alpha_composite(big, (540 - int(540 * s),
                                    (y0 + 156) - int((y0 + 156) * s)))

    # typed status line + blinking cursor
    line = "> booting news ingestion"
    tp = prog(t, 0.70, 0.90)
    shown = line[:int(len(line) * tp)]
    d.text((CX0 + 40, y0 + 236), shown, font=f_x(26), fill=GREEN + (235,))
    if tp >= 1.0 and int(t * 2.5) % 2 == 0:
        cw = d.textlength(line, font=f_x(26))
        d.rectangle((CX0 + 44 + cw, y0 + 238, CX0 + 60 + cw, y0 + 264),
                    fill=GREEN + (220,))

    im.alpha_composite(layer)


# ---------------------------------------------------- 3. news sources
def render_sources(im, t):
    """Bloomberg priced out, then the two free sources land on their spoken names."""
    total = 9.0
    ys = slide_shift(t, total=total)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = draw_card(layer, y_shift=ys)
    y0 = CY0 + ys

    if prog(t, 0.08, 0.30) > 0:
        header(d, y0, "NEWS SOURCES", "// from where?")

    # (label, right-tag, tag colour, appear-at, cross-at)
    rows = [
        ("BLOOMBERG TERMINAL", "$24K / YR", RED,   0.20, 1.70),
        ("ALPACA NEWS API",    "FREE",      GREEN, 2.90, None),
        ("SEC EDGAR API",      "FREE",      GREEN, 4.95, None),
    ]
    BH, GAP, TOP = 58, 12, 72
    fits(TOP + 3 * BH + 2 * GAP)
    for i, (label, tag, tcol, t_in, t_x) in enumerate(rows):
        if not appearing(t, t_in):
            continue
        p = ease_out_back(prog(t, t_in, 0.32))
        a = int(255 * min(1.0, prog(t, t_in, 0.16) * 2))
        ry = y0 + TOP + i * (BH + GAP)
        rx = CX0 + 34 + int(20 * (1 - min(1.0, p)))
        killed = t_x is not None and prog(t, t_x, 0.3) > 0.4
        oc = RED if killed else (GREEN if tag == "FREE" else DIM)
        rounded(d, (rx, ry, CX1 - 34, ry + BH), 12,
                (NAVY[0] + 10, NAVY[1] + 16, NAVY[2] + 24, int(a * 0.92)),
                outline=oc + (a,), width=2)
        lab_col = DIM if killed else WHITE
        d.text((rx + 22, ry + 14), label, font=f_b(30), fill=lab_col + (a,))
        ftag = f_b(26)
        tw = d.textlength(tag, font=ftag)
        d.text((CX1 - 66 - tw, ry + 17), tag, font=ftag, fill=tcol + (a,))
        if killed:
            d.line([(rx + 16, ry + BH // 2), (CX1 - 48, ry + BH // 2)],
                   fill=RED + (a,), width=4)

    im.alpha_composite(layer)
    # meme sticker for the price, cleared before the free sources land
    meme_stamp(im, t, 1.70, "NOT TODAY", RED_HOT, size=112, tilt=-12,
               fade_at=2.50, y_off=ys)


# ---------------------------------------------------- 4/5. why these two
def _why_card(im, t, total, title, gloss, big, sub_id, sub_en, t_row, t_check,
              chip=None):
    """Shared layout for the two 'why this source' cards."""
    ys = slide_shift(t, total=total)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = draw_card(layer, y_shift=ys)
    y0 = CY0 + ys

    if prog(t, 0.08, 0.30) > 0:
        header(d, y0, title, gloss)

    if chip and prog(t, 0.30, 0.3) > 0:
        # back-reference chip, e.g. "DAY 7" — left triangle drawn, not a glyph
        cw = d.textlength(chip, font=f_b(22))
        x1c, y1c = CX1 - 40, y0 + 16
        x0c = x1c - cw - 52
        rounded(d, (x0c, y1c, x1c, y1c + 34), 17, NAVY + (230,),
                outline=GOLD + (200,), width=2)
        d.polygon([(x0c + 18, y1c + 17), (x0c + 30, y1c + 9), (x0c + 30, y1c + 25)],
                  fill=GOLD + (235,))
        d.text((x0c + 38, y1c + 6), chip, font=f_b(22), fill=GOLD + (240,))

    p = ease_out_cubic(prog(t, t_row, 0.35))
    if p > 0:
        a = int(255 * p)
        fits(80 + 150)
        bx0, by0, bx1, by1 = 120, y0 + 80, 960, y0 + 230
        rounded(d, (bx0, by0, bx1, by1), 16,
                (NAVY[0] + 10, NAVY[1] + 16, NAVY[2] + 24, int(a * 0.92)),
                outline=GREEN + (a,) if prog(t, t_check, 0.3) > 0.4 else DIM + (a,),
                width=2)
        d.text((bx0 + 28, by0 + 14), big, font=f_b(44), fill=WHITE + (a,))
        cp = prog(t, t_check, 0.32)
        if cp > 0:
            ca = int(255 * min(1.0, cp * 2))
            d.text((bx0 + 28, by0 + 72), sub_id, font=f_b(26), fill=GREEN + (ca,))
            d.text((bx0 + 28, by0 + 108), sub_en, font=f_r(20), fill=DIM + (ca,))
            check_mark(d, bx1 - 66, by0 + 68, int(24 * ease_out_back(cp)), GREEN,
                       width=8, a=ca)

    im.alpha_composite(layer)


def render_why1(im, t):
    _why_card(im, t, 7.35, "KENAPA DUA INI?", "// why these two",
              "ALPACA", "BROKER API UDAH TERINTEGRASI",
              "the broker API is built into their app",
              t_row=0.35, t_check=3.10)


def render_why2(im, t):
    _why_card(im, t, 7.90, "KENAPA SEC?", "// reason #2",
              "SEC FILING", "TEKNIK YANG UDAH GUA JANJIIN",
              "the technique promised last episode",
              t_row=0.60, t_check=3.85, chip="DAY 7")


# ---------------------------------------------------- 6. geo block
def render_block(im, t):
    """ALPACA -> INDONESIA flow, red X on the arrow, BLOCKED? stamp on 'Indonesia'."""
    ys = slide_shift(t, dur_in=0.30, total=4.40, dur_out=0.28)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = draw_card(layer, y_shift=ys, accent=GOLD)
    y0 = CY0 + ys

    if prog(t, 0.05, 0.25) > 0:
        header(d, y0, "GEO CHECK", "// bisa diakses?", accent=GOLD)

    BOX_T, BOX_B = 90, 220
    BOX_MID = (BOX_T + BOX_B) // 2
    fits(BOX_B)

    a1 = int(255 * ease_out_cubic(prog(t, 0.15, 0.30)))
    if a1 > 0:
        rounded(d, (130, y0 + BOX_T, 430, y0 + BOX_B), 14,
                (NAVY[0] + 10, NAVY[1] + 16, NAVY[2] + 24, int(a1 * 0.92)),
                outline=DIM + (a1,), width=2)
        text_c(d, 280, y0 + BOX_T + 24, "ALPACA", f_b(34), WHITE + (a1,))
        text_c(d, 280, y0 + BOX_T + 72, "news api", f_r(22), DIM + (a1,))

    a2 = int(255 * ease_out_cubic(prog(t, 0.60, 0.30)))
    if a2 > 0:
        rounded(d, (650, y0 + BOX_T, 950, y0 + BOX_B), 14,
                (NAVY[0] + 10, NAVY[1] + 16, NAVY[2] + 24, int(a2 * 0.92)),
                outline=DIM + (a2,), width=2)
        # Indonesian flag: red over white
        d.rectangle((676, y0 + BOX_T + 22, 736, y0 + BOX_T + 44), fill=ID_RED + (a2,))
        d.rectangle((676, y0 + BOX_T + 44, 736, y0 + BOX_T + 66),
                    fill=(245, 245, 245, a2))
        d.text((752, y0 + BOX_T + 20), "INDONESIA", font=f_b(30), fill=WHITE + (a2,))
        d.text((752, y0 + BOX_T + 62), "your location", font=f_r(20), fill=DIM + (a2,))

    ap = prog(t, 0.90, 0.35)
    if ap > 0:
        blocked = prog(t, 2.99, 0.25) > 0.3
        col = RED if blocked else GREEN
        arrow_h(d, 452, 452 + int(176 * ease_out_cubic(ap)), y0 + BOX_MID, col,
                a=int(255 * min(1.0, ap * 2)))
        if blocked:
            cross_mark(d, 540, y0 + BOX_MID, 26, RED, width=9)

    im.alpha_composite(layer)
    meme_stamp(im, t, 2.99, "BLOCKED?", RED_HOT, size=100, tilt=-14, y_off=ys)


# ---------------------------------------------------- 7. finnhub alternative
def render_finnhub(im, t):
    total = 8.80
    ys = slide_shift(t, total=total)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = draw_card(layer, y_shift=ys)
    y0 = CY0 + ys

    if prog(t, 0.05, 0.30) > 0:
        header(d, y0, "ALTERNATIF", "// setelah research")

    R1_T, R1_B = 68, 124
    R2_T, R2_B = 138, 208
    NOTE_T = 228
    fits(R1_B, R2_B, NOTE_T + 34)

    # row 1 — Alpaca out
    p1 = ease_out_cubic(prog(t, 0.20, 0.32))
    if p1 > 0:
        a = int(255 * p1)
        rounded(d, (CX0 + 34, y0 + R1_T, CX1 - 34, y0 + R1_B), 12,
                (NAVY[0] + 10, NAVY[1] + 16, NAVY[2] + 24, int(a * 0.9)),
                outline=RED + (a,), width=2)
        d.text((CX0 + 56, y0 + R1_T + 12), "ALPACA NEWS API", font=f_b(30),
               fill=DIM + (a,))
        cross_mark(d, CX1 - 70, y0 + (R1_T + R1_B) // 2, 18, RED, width=7, a=a)

    # row 2 — Finnhub in, lands on the spoken "Finhub"
    if appearing(t, 2.53):
        p2 = ease_out_back(prog(t, 2.53, 0.32))
        a = int(255 * min(1.0, prog(t, 2.53, 0.16) * 2))
        rounded(d, (CX0 + 34, y0 + R2_T, CX1 - 34, y0 + R2_B), 12,
                (NAVY[0] + 14, NAVY[1] + 24, NAVY[2] + 34, int(a * 0.94)),
                outline=GREEN + (a,), width=3)
        d.text((CX0 + 56, y0 + R2_T + 14), "FINNHUB API", font=f_b(40),
               fill=WHITE + (a,))
        check_mark(d, CX1 - 74, y0 + (R2_T + R2_B) // 2, int(22 * min(1.0, p2)),
                   GREEN, width=8, a=a)

    # caveat line — honest about what Finnhub is not
    p3 = prog(t, 5.45, 0.30)
    if p3 > 0:
        a = int(255 * min(1.0, p3 * 2))
        d.text((CX0 + 56, y0 + NOTE_T), "NEWS ONLY", font=f_b(26), fill=GOLD + (a,))
        d.text((CX0 + 210, y0 + NOTE_T + 4), "no broker API, cukup buat sekarang",
               font=f_r(21), fill=DIM + (a,))

    im.alpha_composite(layer)
    meme_sticker(im, t, 7.15, "CLUTCH.", 812, CY0 + ys + 262, GREEN,
                 size=62, tilt=-8)


# ---------------------------------------------------- 8. webhook flow
def render_webhook(im, t):
    """NEWS -> WEBHOOK -> BOT. A packet dot rides the rail on the 'kekirim' line."""
    total = 5.75
    ys = slide_shift(t, dur_in=0.30, total=total, dur_out=0.30)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = draw_card(layer, y_shift=ys)
    y0 = CY0 + ys

    if prog(t, 0.03, 0.25) > 0:
        header(d, y0, "WEBHOOK", "// push, bukan polling")

    fits(212)
    NODE_Y0, NODE_Y1 = y0 + 82, y0 + 212
    NODE_CY = (NODE_Y0 + NODE_Y1) // 2
    nodes = [
        (140, 320, "NEWS", "api", 1.00, DIM),
        (450, 630, "WEBHOOK", "push", 0.05, GREEN),
        (760, 940, "BOT", "gua", 2.00, DIM),
    ]
    for x0n, x1n, lab, sub, t_in, col in nodes:
        if not appearing(t, t_in):
            continue
        p = ease_out_back(prog(t, t_in, 0.32))
        a = int(255 * min(1.0, prog(t, t_in, 0.16) * 2))
        rounded(d, (x0n, NODE_Y0, x1n, NODE_Y1), 14,
                (NAVY[0] + 12, NAVY[1] + 20, NAVY[2] + 30, int(a * 0.94)),
                outline=col + (a,), width=3)
        text_c(d, (x0n + x1n) // 2, NODE_Y0 + 30, lab, f_b(32), WHITE + (a,))
        text_c(d, (x0n + x1n) // 2, NODE_Y0 + 76, sub, f_r(21), DIM + (a,))

    # rails draw once both ends exist
    for (xa, xb, t_in) in ((332, 438, 1.35), (642, 748, 2.35)):
        rp = ease_out_cubic(prog(t, t_in, 0.30))
        if rp > 0:
            arrow_h(d, xa, xa + int((xb - xa) * rp), NODE_CY, GREEN,
                    a=int(255 * min(1.0, rp * 2)), width=5, head=14)

    # packet dot: NEWS -> WEBHOOK -> BOT, two passes over the "kekirim" line
    if 3.20 <= t <= 5.40:
        cycle = ((t - 3.20) % 1.10) / 1.10
        px = 230 + (850 - 230) * ease_in_out_cubic(cycle)
        d.ellipse((px - 11, NODE_CY - 11, px + 11, NODE_CY + 11),
                  fill=GREEN + (255,), outline=WHITE + (220,), width=2)

    im.alpha_composite(layer)


# ---------------------------------------------------- 9. autopilot
def render_auto(im, t):
    total = 5.50
    ys = slide_shift(t, total=total, dur_out=0.30)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = draw_card(layer, y_shift=ys)
    y0 = CY0 + ys

    if prog(t, 0.05, 0.28) > 0:
        header(d, y0, "AUTOPILOT", "// tiap hari")

    rows = [
        ("BERITA TERBARU TIAP HARI", "fresh news every day", 0.40),
        ("TANPA INTERVENSI", "zero manual work", 2.20),
    ]
    BH, GAP, TOP = 72, 14, 74
    fits(TOP + 2 * BH + GAP)
    for i, (lab, gloss, t_in) in enumerate(rows):
        if not appearing(t, t_in):
            continue
        p = ease_out_back(prog(t, t_in, 0.32))
        a = int(255 * min(1.0, prog(t, t_in, 0.16) * 2))
        ry = y0 + TOP + i * (BH + GAP)
        rounded(d, (CX0 + 34, ry, CX1 - 34, ry + BH), 12,
                (NAVY[0] + 10, NAVY[1] + 16, NAVY[2] + 24, int(a * 0.92)),
                outline=GREEN + (a,), width=2)
        check_mark(d, CX0 + 74, ry + BH // 2 - 4, int(19 * min(1.0, p)), GREEN,
                   width=7, a=a)
        d.text((CX0 + 116, ry + 10), lab, font=f_b(29), fill=WHITE + (a,))
        d.text((CX0 + 116, ry + 44), gloss, font=f_r(20), fill=DIM + (a,))

    im.alpha_composite(layer)
    meme_sticker(im, t, 4.05, "SET AND FORGET", 700, CY0 + ys + 272, GREEN,
                 size=52, tilt=-6)


# ---------------------------------------------------- 10. normalize
def render_normalize(im, t):
    """Two differently-shaped payloads collapse into one format."""
    total = 4.95
    ys = slide_shift(t, dur_in=0.32, total=total, dur_out=0.28)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = draw_card(layer, y_shift=ys)
    y0 = CY0 + ys

    if prog(t, 0.03, 0.25) > 0:
        header(d, y0, "NORMALIZE", "// satu format")

    CHIP_T, CHIP_H, CHIP_GAP = 78, 64, 16
    MID_Y = CHIP_T + CHIP_H + CHIP_GAP // 2      # rail height, between the chips
    fits(CHIP_T + 2 * CHIP_H + CHIP_GAP)

    for i, (lab, col, t_in) in enumerate((("FINNHUB · JSON", GOLD, 0.20),
                                          ("SEC · XML", (120, 170, 245), 0.42))):
        p = ease_out_cubic(prog(t, t_in, 0.30))
        if p <= 0:
            continue
        a = int(255 * p)
        cy0 = y0 + CHIP_T + i * (CHIP_H + CHIP_GAP)
        rounded(d, (110, cy0, 350, cy0 + CHIP_H), 12,
                (NAVY[0] + 10, NAVY[1] + 16, NAVY[2] + 24, int(a * 0.92)),
                outline=col + (a,), width=2)
        text_c(d, 230, cy0 + 18, lab, f_b(24), WHITE + (a,))

    ap = ease_out_cubic(prog(t, 0.95, 0.28))
    if ap > 0:
        arrow_h(d, 366, 366 + int(46 * ap), y0 + MID_Y, GREEN,
                a=int(255 * ap), width=5, head=13)

    if appearing(t, 1.30):
        a = int(255 * min(1.0, prog(t, 1.30, 0.16) * 2))
        rounded(d, (430, y0 + MID_Y - 52, 690, y0 + MID_Y + 52), 14,
                (NAVY[0] + 14, NAVY[1] + 24, NAVY[2] + 34, int(a * 0.94)),
                outline=GREEN + (a,), width=3)
        text_c(d, 560, y0 + MID_Y - 32, "NORMALIZE", f_b(28), WHITE + (a,))
        text_c(d, 560, y0 + MID_Y + 6, "ubah ke 1 format", f_r(20), DIM + (a,))

    op = ease_out_cubic(prog(t, 3.80, 0.28))
    if op > 0:
        arrow_h(d, 706, 706 + int(44 * op), y0 + MID_Y, GREEN,
                a=int(255 * op), width=5, head=13)

    if appearing(t, 3.63):
        a = int(255 * min(1.0, prog(t, 3.63, 0.15) * 2))
        rounded(d, (766, y0 + MID_Y - 34, 970, y0 + MID_Y + 34), 34, GREEN + (a,))
        text_c(d, 868, y0 + MID_Y - 14, "1 FORMAT", f_b(27), (8, 20, 14, a))

    im.alpha_composite(layer)


# ---------------------------------------------------- 11. sqlite storage
def render_sqlite(im, t):
    """DB cylinder draws, SQLite lands on the spoken word, then feeds backtesting."""
    total = 9.50
    ys = slide_shift(t, total=total)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = draw_card(layer, y_shift=ys)
    y0 = CY0 + ys

    if prog(t, 0.05, 0.28) > 0:
        header(d, y0, "STORAGE", "// simpan semua berita")

    cp = ease_out_cubic(prog(t, 0.30, 0.55))
    if cp > 0:
        a = int(255 * cp)
        landed = prog(t, 2.90, 0.30) > 0.4
        col = GREEN if landed else DIM
        fits(268)
        cx0v, cx1v = 190, 410
        top, bot = y0 + 76, y0 + 268
        rr = 26
        d.ellipse((cx0v, top, cx1v, top + 2 * rr), outline=col + (a,), width=4)
        d.line([(cx0v, top + rr), (cx0v, bot - rr)], fill=col + (a,), width=4)
        d.line([(cx1v, top + rr), (cx1v, bot - rr)], fill=col + (a,), width=4)
        d.arc((cx0v, bot - 2 * rr, cx1v, bot), 0, 180, fill=col + (a,), width=4)
        for k in range(1, 3):
            yk = top + rr + k * (bot - top - 2 * rr) / 3
            d.arc((cx0v, yk - rr, cx1v, yk + rr), 0, 180, fill=col + (int(a * 0.5),),
                  width=3)
        if landed:
            lp = prog(t, 2.90, 0.30)
            la = int(255 * min(1.0, lp * 2))
            text_c(d, 300, top + 52, "SQLite", f_b(int(40 * ease_out_back(lp))),
                   WHITE + (la,))

    sp = prog(t, 4.05, 0.30)
    if sp > 0:
        a = int(255 * min(1.0, sp * 2))
        d.text((452, y0 + 92), "SIMPLE SETUP", font=f_b(28), fill=WHITE + (a,))
        d.text((452, y0 + 130), "1 file, no server", font=f_r(21), fill=DIM + (a,))
        d.text((452, y0 + 162), "append-only", font=f_r(21), fill=DIM + (a,))

    RAIL_Y, CHIP_T, CHIP_B = 232, 200, 264
    fits(CHIP_B)

    ap = ease_out_cubic(prog(t, 8.00, 0.30))
    if ap > 0:
        arrow_h(d, 452, 452 + int(240 * ap), y0 + RAIL_Y, GREEN,
                a=int(255 * ap), width=5, head=14)

    if appearing(t, 8.25):
        a = int(255 * min(1.0, prog(t, 8.25, 0.16) * 2))
        rounded(d, (724, y0 + CHIP_T, 976, y0 + CHIP_B), 32, GREEN + (a,))
        text_c(d, 850, y0 + CHIP_T + 18, "BACKTESTING", f_b(26), (8, 20, 14, a))

    im.alpha_composite(layer)


# ---------------------------------------------------- 12. like + follow
def render_outro(im, t):
    """Two badges, popped on the spoken 'like' and 'follow'. No card behind them."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    for x0b, x1b, lab, t_in, kind in ((180, 500, "LIKE", 0.40, "heart"),
                                      (580, 900, "FOLLOW", 0.85, "person")):
        if not appearing(t, t_in):
            continue
        p = ease_out_back(prog(t, t_in, 0.30))
        a = int(255 * min(1.0, prog(t, t_in, 0.15) * 2))
        cxb, cyb = (x0b + x1b) // 2, 250
        s = 0.6 + 0.4 * min(1.0, p)
        hw, hh = int((x1b - x0b) * s) // 2, int(94 * s) // 2
        rounded(d, (cxb - hw, cyb - hh, cxb + hw, cyb + hh), hh, GREEN + (a,))
        if p > 0.45:
            ix = cxb - hw + 44
            if kind == "heart":
                d.ellipse((ix - 20, cyb - 18, ix + 2, cyb + 4), fill=(8, 20, 14, a))
                d.ellipse((ix - 2, cyb - 18, ix + 20, cyb + 4), fill=(8, 20, 14, a))
                d.polygon([(ix - 20, cyb - 5), (ix + 20, cyb - 5), (ix, cyb + 22)],
                          fill=(8, 20, 14, a))
            else:
                d.ellipse((ix - 12, cyb - 22, ix + 12, cyb + 2), fill=(8, 20, 14, a))
                d.chord((ix - 20, cyb - 2, ix + 20, cyb + 34), 180, 360,
                        fill=(8, 20, 14, a))
            fnt = f_b(38)
            tw = d.textlength(lab, font=fnt)
            d.text((cxb + 22 - tw / 2, cyb - 22), lab, font=fnt, fill=(8, 20, 14, a))

    ang = wiggle_deg(t, 1.05, amp=2.0, decay=2.4, freq=9.0)
    if abs(ang) > 0.02:
        layer = layer.rotate(ang, expand=False, center=(540, 250),
                             resample=Image.BICUBIC)
    im.alpha_composite(layer)


# ---------------------------------------------------- 13. explosion end card
def _blast_edge(seed, n=72):
    """Per-angle radius multipliers — a perfect circle reads as a graphic, not a blast."""
    rnd = random.Random(seed)
    return [0.80 + 0.34 * rnd.random() for _ in range(n)]


_JITTER = [_blast_edge(s) for s in (3, 11, 19, 27, 35)]


def _wash(layer, color, alpha):
    """Composite a full-frame colour wash. Never draw one — see render_explosion."""
    if alpha <= 0:
        return layer
    wash = Image.new("RGBA", (W, H), color + (int(min(255, alpha)),))
    return Image.alpha_composite(layer, wash)


def _blob(d, cx, cy, r, jitter, fill):
    n = len(jitter)
    pts = [(cx + r * j * math.cos(2 * math.pi * i / n),
            cy + r * j * math.sin(2 * math.pi * i / n))
           for i, j in enumerate(jitter)]
    d.polygon(pts, fill=fill)


def render_explosion(im, t):
    """Final screen: the hand covers the lens, then the whole thing detonates.

    Opaque from frame 0 (fills the frame with black before drawing) so the
    hand-over-lens footage underneath never shows through. Ends near-black with
    a few embers, which is the last frame of the reel.
    """
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(layer)
    cx, cy = 540, 900

    # fireball: fast expansion, then cools toward soot and collapses
    fp = ease_out_cubic(prog(t, 0.02, 0.40))
    cool = prog(t, 0.38, 0.52)
    radius = (60 + 1240 * fp) * (1.0 - 0.32 * cool)
    if fp > 0:
        shells = [
            (1.00, (122, 26, 10)),
            (0.82, (198, 58, 12)),
            (0.60, (246, 138, 26)),
            (0.40, (252, 214, 96)),
            (0.22, (255, 252, 232)),
        ]
        for k, (scale, col) in enumerate(shells):
            soot = tuple(int(c * (1 - cool) + s * cool)
                         for c, s in zip(col, (30, 17, 13)))
            _blob(d, cx, cy, radius * scale, _JITTER[k], soot + (255,))

    # Everything below fades, i.e. draws at partial alpha, so it goes on its own
    # transparent scratch layer and gets composited. Drawing it straight onto
    # `layer` would replace the alpha there and punch holes in the blast.
    fx = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fx)

    # shockwave ring races out past the frame edge
    sp = ease_out_cubic(prog(t, 0.05, 0.50))
    if 0 < sp < 1:
        rr = 80 + 1500 * sp
        a = int(235 * (1 - sp) ** 1.4)
        for wdt, col in ((16, (255, 236, 190)), (6, (255, 255, 255))):
            fd.ellipse((cx - rr, cy - rr, cx + rr, cy + rr),
                       outline=col + (a,), width=wdt)

    # debris chunks, thrown out and pulled down
    rnd = random.Random(11)
    for _ in range(22):
        ang = rnd.uniform(0, 2 * math.pi)
        spd = rnd.uniform(700, 1550)
        sz = rnd.randint(12, 38)
        dp = prog(t, 0.08 + rnd.uniform(0.0, 0.10), 0.78)
        if dp <= 0:
            continue
        e = ease_out_cubic(dp)
        px = cx + math.cos(ang) * spd * e
        py = cy + math.sin(ang) * spd * e + 340 * dp * dp
        a = int(255 * (1 - dp) ** 0.8)
        fd.polygon([(px, py - sz), (px + sz * 0.8, py), (px, py + sz * 0.7),
                    (px - sz * 0.9, py + sz * 0.2)], fill=(24, 14, 10, a))

    layer = Image.alpha_composite(layer, fx)

    # Full-frame washes must COMPOSITE, not draw. A `d.rectangle` covering the
    # frame at partial alpha replaces every pixel's alpha and wipes the opaque
    # layer transparent, letting the footage underneath show through (same trap
    # as `rounded()`, guide §10.7).
    layer = _wash(layer, (255, 255, 255), 255 * (1.0 - prog(t, 0.0, 0.08)))
    dk = prog(t, 0.60, 0.40)
    layer = _wash(layer, (0, 0, 0), 238 * dk)

    # embers glow on after the burn-down, so they survive it (own layer again)
    if dk > 0:
        embers = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ed = ImageDraw.Draw(embers)
        er = random.Random(5)
        for _ in range(26):
            ex = er.uniform(120, 960)
            ey = er.uniform(420, 1400) - 150 * dk
            a = int(er.uniform(90, 210) * (1 - dk * 0.45))
            r = er.uniform(2.5, 6.0)
            ed.ellipse((ex - r, ey - r, ex + r, ey + r), fill=(255, 150, 50, a))
        layer = Image.alpha_composite(layer, embers)

    assert layer.split()[3].getextrema()[0] == 255, "explosion layer must stay opaque"
    im.alpha_composite(layer)


SLOTS = {
    "slot_hook_upcoming": (2.60,  render_hook_upcoming),
    "slot_pvz_day8":      (3.20,  render_day8),
    "slot_gfx_sources":   (9.00,  render_sources),
    "slot_gfx_why1":      (7.35,  render_why1),
    "slot_gfx_why2":      (7.90,  render_why2),
    "slot_gfx_block":     (4.40,  render_block),
    "slot_gfx_finnhub":   (8.80,  render_finnhub),
    "slot_gfx_webhook":   (5.75,  render_webhook),
    "slot_gfx_auto":      (5.50,  render_auto),
    "slot_gfx_normalize": (4.95,  render_normalize),
    "slot_gfx_sqlite":    (9.50, render_sqlite),
    "slot_gfx_outro":     (2.70,  render_outro),
    "slot_explosion":     (1.00,  render_explosion),
}

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, (dur, fn) in SLOTS.items():
        if which in ("all", name):
            save_frames(name, dur, fn)
