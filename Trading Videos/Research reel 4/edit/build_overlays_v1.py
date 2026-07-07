"""Build overlays for Research reel 4 — AI News Trading (Day 5).

Slots:
  slot_news_day5       Breaking-news themed "DAY 5" intro sign (~2.9s)
  slot_gfx_expect      Earnings surprise bar chart: FORECAST vs ACTUAL gap
  slot_gfx_nlp         Linguistic signal flow: SPEECH -> NLP -> TRADE SIGNAL
  slot_src_bloomberg   Citation panel: BloombergGPT / Bloomberg NLP (arXiv)
  slot_gfx_sharpe      ChatGPT result badge: Sharpe 3.8 -> CROWDED flip
  slot_src_chatgpt     Citation panel: Lopez-Lira & Tang (2023), arXiv
  slot_gfx_agents      Multi-agent debate diagram + RETURN: +26% badge

Encode each slot after running this script:
  for s in edit/animations/slot_*; do
    ffmpeg -y -framerate 30 -i "$s/frames/f_%05d.png"
      -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le "$s/render.mov"
  done
"""

import os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
ANIM = os.path.join(HERE, "animations")
SRC  = os.path.join(HERE, "sources")

ARIALBD = "C:/Windows/Fonts/arialbd.ttf"
ARIAL    = "C:/Windows/Fonts/arial.ttf"

# Series palette
GREEN   = (22, 199, 132)
GREEN_D = (10, 150, 98)
NAVY    = (11, 31, 58)
PANEL   = (12, 22, 40)
WHITE   = (255, 255, 255)
DIM     = (158, 168, 184)
RED     = (235, 90, 95)
GOLD    = (245, 196, 90)
RED_LIVE = (220, 40, 40)   # breaking-news red accent

# Top-band card (same as prior reels — proven position)
CARD = (80, 120, 1000, 455)


def font(sz, bold=True):
    return ImageFont.truetype(ARIALBD if bold else ARIAL, sz)

def eo(t):
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3

def eio(t):
    t = max(0.0, min(1.0, t))
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2

def eo_back(t, s=1.70158):
    """ease_out_back: overshoots then settles."""
    t = max(0.0, min(1.0, t))
    return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2

def lerp(a, b, p): return a + (b - a) * p

def tw(d, s, f): b = d.textbbox((0, 0), s, font=f); return b[2] - b[0]
def th(d, s, f): b = d.textbbox((0, 0), s, font=f); return b[3] - b[1]

def rrect(draw, box, r, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

def pop(t, t0, d=0.5):
    if t < t0: return 0.0
    return eo((t - t0) / d)

def new_frame():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))

def card_fade(layer, t, dur, t_in=0.4, t_out=0.4):
    """Global alpha fade-in / fade-out on a layer."""
    if t < t_in:
        ga = eo(t / t_in)
    elif t > dur - t_out:
        ga = eo((dur - t) / t_out)
    else:
        return layer
    a = layer.split()[3].point(lambda v: int(v * ga))
    layer.putalpha(a)
    return layer

def note(slot, n):
    print(f"  {slot}: {n} frames")


# ─────────────────────────────────────────── CITATION PANEL (full-bleed)
SHOT_H  = 700
CAP_H   = 56
PANEL_H = SHOT_H + CAP_H

def render_src(slot, img_path, caption, dur):
    """Full-bleed screenshot panel: slides down from top, holds, slides back up."""
    out_dir = os.path.join(ANIM, slot, "frames")
    os.makedirs(out_dir, exist_ok=True)

    shot = Image.open(img_path).convert("RGBA")
    shot = shot.resize((W, int(shot.height * W / shot.width)), Image.LANCZOS)
    shot = shot.crop((0, 0, W, SHOT_H))

    panel = Image.new("RGBA", (W, PANEL_H), (0, 0, 0, 0))
    panel.paste(shot, (0, 0))
    d = ImageDraw.Draw(panel)
    d.rectangle((0, SHOT_H, W, PANEL_H), fill=NAVY + (255,))
    d.rectangle((0, SHOT_H, 12, PANEL_H), fill=GREEN + (255,))
    fc = font(24)
    d.text((30, SHOT_H + (CAP_H - th(d, caption, fc)) // 2 - 4),
           caption, font=fc, fill=(225, 232, 242))
    d.line((0, SHOT_H, W, SHOT_H), fill=(255, 255, 255, 60), width=2)

    shadow = Image.new("RGBA", (W, 60), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rectangle((0, 0, W, 60), fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))

    n = int(round(dur * FPS))
    t_in, t_out = 0.5, 0.42
    for i in range(n):
        t = i / FPS
        if t < t_in:
            y = lerp(-(PANEL_H + 50), 0, eo(t / t_in))
        elif t > dur - t_out:
            y = lerp(-(PANEL_H + 50), 0, eo((dur - t) / t_out))
        else:
            y = 0
        cv = new_frame()
        yy = int(round(y))
        cv.paste(shadow, (0, yy + PANEL_H - 20), shadow)
        cv.paste(panel, (0, yy), panel)
        cv.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)


# ─────────────────────────────────────────── HOOK: WALL STREET AI TRADERS
def render_gfx_hook(slot, dur):
    """Hook graphic for first ~12s (IMG_0999 HOOK segment).

    Phase 1 (t=0–~9s): "2024" year + "WALL STREET AI TRADERS" header
    + 4 strategy badges appear one by one with green ✓ ACTIVE pill.
    Phase 2 (t≈9.02s): big red "DEAD" stamp rotated diagonally across the
    whole card (same technique as CROWDED in gfx_sharpe).
    Synced: "sudah mati" at output 9.52s → local t 9.02s (start_in_output=0.50).

    Badge geometry fits within CARD (y 120–455, 335px height):
      header area:  y0..y0+120  (120px)
      badge area:   y0+122..y1-8 (205px) → 4×BH=38 + 3×gap=9 = 179px ✓
    """
    out_dir = os.path.join(ANIM, slot, "frames")
    os.makedirs(out_dir, exist_ok=True)

    x0, y0, x1, y1 = CARD
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    n = int(round(dur * FPS))

    fyr    = font(58)
    fhdr   = font(20, False)
    fbadge = font(18)
    fpill  = font(18)
    fstamp = font(80)

    BADGES = [
        ("NEWS READER",    GREEN, 0.40),
        ("SENTIMENT BOT",  GREEN, 0.80),
        ("NLP PARSER",     GOLD,  1.20),
        ("SPEED TRADER",   GREEN, 1.60),
    ]
    BH, BH_GAP = 38, 9
    BW = 840   # full card width minus margins
    bx = x0 + 40

    # Compute badge positions that fit within card
    BADGE_AREA_TOP  = y0 + 122
    BADGE_AREA_BOT  = y1 - 8
    _total_h = len(BADGES) * BH + (len(BADGES) - 1) * BH_GAP
    _start_y = BADGE_AREA_TOP + (BADGE_AREA_BOT - BADGE_AREA_TOP - _total_h) // 2
    badge_ys = [_start_y + i * (BH + BH_GAP) for i in range(len(BADGES))]

    T_DEAD = 9.02

    for i in range(n):
        t = i / FPS
        layer = new_frame()
        d = ImageDraw.Draw(layer)

        rrect(d, (x0, y0, x1, y1), 24, fill=PANEL + (238,),
              outline=(40, 54, 80, 255), width=2)

        # Year stamp + header (top 120px of card)
        yr = "2024"
        yw = tw(d, yr, fyr)
        d.text((x0 + 38, y0 + 14), yr, font=fyr, fill=(*GOLD, 230))
        hdr = "WALL STREET AI TRADERS"
        d.text((x0 + 38 + yw + 16, y0 + 48), hdr, font=fhdr, fill=(*DIM, 200))

        # Badges
        for idx, (name, color, t_on) in enumerate(BADGES):
            p = pop(t, t_on, 0.35)
            if p <= 0:
                continue
            a = int(255 * p)
            by = badge_ys[idx]

            rrect(d, (bx, by, bx + BW, by + BH), 8,
                  fill=(color[0] // 7, color[1] // 7, color[2] // 7, a),
                  outline=(*color, a), width=2)
            d.text((bx + 14, by + (BH - th(d, name, fbadge)) // 2),
                   name, font=fbadge, fill=(*WHITE, a))

            pill = "✓ ACTIVE"
            pw = tw(d, pill, fpill)
            d.text((bx + BW - pw - 14, by + (BH - th(d, pill, fpill)) // 2),
                   pill, font=fpill, fill=(*GREEN, a))

        # Phase 2: big diagonal "DEAD" stamp across the whole card
        p_dead = pop(t, T_DEAD, 0.35)
        if p_dead > 0:
            stamp_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            sd = ImageDraw.Draw(stamp_layer)
            stamp = "DEAD"
            sw = tw(sd, stamp, fstamp)
            sh = th(sd, stamp, fstamp)
            scx = (x0 + x1) // 2
            scy = (y0 + y1) // 2
            # thick red outline
            da = int(230 * p_dead)
            for ox in range(-4, 5, 2):
                for oy in range(-4, 5, 2):
                    sd.text((scx - sw // 2 + ox, scy - sh // 2 + oy),
                            stamp, font=fstamp, fill=(*RED, da))
            sd.text((scx - sw // 2, scy - sh // 2),
                    stamp, font=fstamp, fill=(*RED, da))
            # red border box around it
            pad = 18
            sd.rectangle((scx - sw // 2 - pad, scy - sh // 2 - pad,
                           scx + sw // 2 + pad, scy + sh // 2 + pad),
                          outline=(*RED, da), width=6)
            rotated = stamp_layer.rotate(-18, expand=False, center=(scx, scy))
            layer = Image.alpha_composite(layer, rotated)

        layer = card_fade(layer, t, dur)
        layer.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)


# ─────────────────────────────────────────── BREAKING NEWS "DAY 5" INTRO
def render_news_day5(slot, dur):
    """Breaking-news broadcast intro sign for DAY 5 (AI News Trading theme).

    Layout (top band, y 120–455):
      Left ticker bar slides in from left with 'BREAKING'
      Right ticker bar slides in from right with 'NEWS'
      Both converge as 'DAY 5' pops in center with scale-up
      'AI NEWS TRADING' subtitle fades in below
      Pulsing red LIVE badge top-right
    """
    out_dir = os.path.join(ANIM, slot, "frames")
    os.makedirs(out_dir, exist_ok=True)

    n = int(round(dur * FPS))
    fday  = font(120)
    ftick = font(38)
    fsub  = font(26, False)
    flive = font(22)

    x0, y0, x1, y1 = CARD
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2

    TICKER_H   = 66
    TICKER_Y   = y0 + 54          # top of ticker bars
    DAY5_Y     = cy - 30          # vertical center of "DAY 5"
    SUB_Y      = cy + 80

    # Timing
    T_TICK_IN  = 0.15   # ticker bars start sliding
    T_DAY5     = 0.60   # DAY 5 text pops
    T_SUB      = 1.10   # subtitle appears
    T_FADE_OUT = dur - 0.40

    for i in range(n):
        t = i / FPS
        cv = new_frame()
        d  = ImageDraw.Draw(cv)

        # global alpha
        if t < 0.30:
            ga = eo(t / 0.30)
        elif t > T_FADE_OUT:
            ga = eo((dur - t) / 0.40)
        else:
            ga = 1.0

        # card background
        bg_a = int(ga * 215)
        rrect(d, (x0, y0, x1, y1), 22,
              fill=(*PANEL, bg_a),
              outline=(*RED_LIVE, int(ga * 100)), width=2)

        # left ticker "BREAKING" slides in from left
        p_tick = eo((t - T_TICK_IN) / 0.45) if t > T_TICK_IN else 0.0
        if p_tick > 0:
            # bar slides right from off-screen left
            bar_w  = (cx - x0) - 10
            bar_x0 = cx - 10 - bar_w
            bar_x1 = cx - 10
            slide_x = int(lerp(x0 - bar_w - 20, bar_x0, p_tick))
            ta = int(ga * 240 * p_tick)
            # red filled bar
            d.rectangle((slide_x, TICKER_Y, slide_x + bar_w, TICKER_Y + TICKER_H),
                        fill=(*RED_LIVE, ta))
            lbl = "BREAKING"
            lw = tw(d, lbl, ftick)
            tx = slide_x + (bar_w - lw) // 2
            d.text((tx, TICKER_Y + (TICKER_H - th(d, lbl, ftick)) // 2),
                   lbl, font=ftick, fill=(*WHITE, ta))

        # right ticker "NEWS" slides in from right
        if p_tick > 0:
            bar_w2 = (x1 - cx) - 10
            bar_x0b = cx + 10
            slide_x2 = int(lerp(x1 + 20, bar_x0b, p_tick))
            ta = int(ga * 240 * p_tick)
            d.rectangle((slide_x2, TICKER_Y, slide_x2 + bar_w2, TICKER_Y + TICKER_H),
                        fill=(*NAVY, ta))
            d.rectangle((slide_x2, TICKER_Y, slide_x2 + 6, TICKER_Y + TICKER_H),
                        fill=(*RED_LIVE, ta))
            lbl2 = "NEWS"
            lw2 = tw(d, lbl2, ftick)
            tx2 = slide_x2 + (bar_w2 - lw2) // 2
            d.text((tx2, TICKER_Y + (TICKER_H - th(d, lbl2, ftick)) // 2),
                   lbl2, font=ftick, fill=(*WHITE, ta))

        # "DAY 5" pops in center with overshoot scale
        p_day5 = eo_back((t - T_DAY5) / 0.50) if t > T_DAY5 else 0.0
        if p_day5 > 0:
            txt = "DAY 5"
            # render at target size then composite (no PIL scale trick needed —
            # font size is fixed; we simulate scale with alpha only for simplicity)
            a5 = int(ga * 255 * min(1.0, p_day5))
            # glow behind text
            for gox in range(-4, 5, 2):
                for goy in range(-4, 5, 2):
                    d.text((cx - tw(d, txt, fday) // 2 + gox,
                            DAY5_Y - th(d, txt, fday) // 2 + goy),
                           txt, font=fday, fill=(*GREEN, int(a5 * 0.15)))
            d.text((cx - tw(d, txt, fday) // 2,
                    DAY5_Y - th(d, txt, fday) // 2),
                   txt, font=fday, fill=(*WHITE, a5))

        # subtitle "AI NEWS TRADING"
        p_sub = eo((t - T_SUB) / 0.35) if t > T_SUB else 0.0
        if p_sub > 0:
            sa = int(ga * 200 * p_sub)
            sub = "AI NEWS TRADING"
            d.text((cx - tw(d, sub, fsub) // 2, SUB_Y), sub,
                   font=fsub, fill=(*GREEN, sa))

        # pulsing LIVE badge (top-right of card)
        live_pulse = 0.5 + 0.5 * math.sin(t * math.pi * 3)
        if p_tick > 0:
            la = int(ga * (180 + 60 * live_pulse) * min(1.0, p_tick * 2))
            dot_x, dot_y = x1 - 120, y0 + 22
            d.ellipse((dot_x, dot_y, dot_x + 16, dot_y + 16),
                      fill=(*RED_LIVE, la))
            d.text((dot_x + 22, dot_y - 2), "LIVE", font=flive,
                   fill=(*RED_LIVE, la))

        # global alpha pass
        if ga < 1.0:
            r_ch, g_ch, b_ch, a_ch = cv.split()
            a_ch = a_ch.point(lambda v: int(v * ga))
            cv = Image.merge("RGBA", (r_ch, g_ch, b_ch, a_ch))

        cv.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)


# ─────────────────────────────────────────── EARNINGS SURPRISE BAR CHART
def render_gfx_expect(slot, dur):
    """Animated bar chart: FORECAST (gray) vs ACTUAL (red), gap arrow with label."""
    out_dir = os.path.join(ANIM, slot, "frames")
    os.makedirs(out_dir, exist_ok=True)

    x0, y0, x1, y1 = CARD
    n = int(round(dur * FPS))
    fhdr = font(28); fsub = font(20, False)
    fnum = font(48); flbl = font(22, False); fgap = font(26)

    bar_y0, bar_y1 = y0 + 130, y1 - 70
    bar_h = bar_y1 - bar_y0
    cx = (x0 + x1) // 2
    bar_w = 220
    gap_x = 80

    left_x  = cx - gap_x // 2 - bar_w   # FORECAST bar left edge
    right_x = cx + gap_x // 2            # ACTUAL bar left edge

    DRAW_T, DRAW_D = 0.50, 1.60
    GAP_T = 1.80

    for i in range(n):
        t = i / FPS
        layer = new_frame()
        d = ImageDraw.Draw(layer)

        rrect(d, (x0, y0, x1, y1), 24, fill=PANEL + (238,),
              outline=(40, 54, 80, 255), width=2)
        d.text((x0 + 34, y0 + 22), "EARNINGS SURPRISE", font=fhdr, fill=WHITE)
        d.text((x0 + 34, y0 + 60),
               "prices move on the GAP, not the number itself",
               font=fsub, fill=DIM)

        p = eio((t - DRAW_T) / DRAW_D) if t > DRAW_T else 0.0

        # baseline
        d.line((left_x - 20, bar_y1, right_x + bar_w + 20, bar_y1),
               fill=(*DIM, 80), width=2)

        # FORECAST bar (gray/dim — full height anchor)
        fh = int(bar_h * 0.80 * p)
        if fh > 0:
            rrect(d, (left_x, bar_y1 - fh, left_x + bar_w, bar_y1),
                  8, fill=(*DIM, 160))
        pa = int(255 * min(1.0, (t - DRAW_T) / DRAW_D)) if t > DRAW_T else 0
        d.text((left_x + bar_w // 2 - tw(d, "250,000", fnum) // 2,
                bar_y1 - fh - 60),
               "250,000", font=fnum, fill=(*DIM, pa))
        d.text((left_x + bar_w // 2 - tw(d, "FORECAST", flbl) // 2, bar_y1 + 8),
               "FORECAST", font=flbl, fill=(*DIM, pa))

        # ACTUAL bar (red — shorter, shows miss)
        ah = int(bar_h * 0.64 * p)   # 200/250 = 0.64× of forecast bar
        if ah > 0:
            rrect(d, (right_x, bar_y1 - ah, right_x + bar_w, bar_y1),
                  8, fill=(*RED, 200))
        ra = int(255 * min(1.0, max(0.0, (t - DRAW_T - 0.30) / DRAW_D))) if t > DRAW_T else 0
        d.text((right_x + bar_w // 2 - tw(d, "200,000", fnum) // 2,
                bar_y1 - ah - 60),
               "200,000", font=fnum, fill=(*RED, ra))
        d.text((right_x + bar_w // 2 - tw(d, "ACTUAL", flbl) // 2, bar_y1 + 8),
               "ACTUAL", font=flbl, fill=(*RED, ra))

        # GAP bracket + label
        p_gap = eo((t - GAP_T) / 0.50) if t > GAP_T else 0.0
        if p_gap > 0 and fh > 0 and ah > 0:
            ga2 = int(255 * p_gap)
            bracket_x = right_x + bar_w + 18
            top_y = bar_y1 - fh
            bot_y = bar_y1 - ah
            d.line((bracket_x, top_y, bracket_x + 16, top_y), fill=(*GOLD, ga2), width=3)
            d.line((bracket_x + 8, top_y, bracket_x + 8, bot_y), fill=(*GOLD, ga2), width=3)
            d.line((bracket_x, bot_y, bracket_x + 16, bot_y), fill=(*GOLD, ga2), width=3)
            mid_y = (top_y + bot_y) // 2
            lbl = "GAP = −50k"
            d.text((bracket_x + 22, mid_y - th(d, lbl, fgap) // 2),
                   lbl, font=fgap, fill=(*GOLD, ga2))

        layer = card_fade(layer, t, dur)
        layer.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)


# ─────────────────────────────────────────── NLP SIGNAL FLOW DIAGRAM
def render_gfx_nlp(slot, dur):
    """Flow: [POWELL SPEECH] -> NLP PARSER -> [TRADE SIGNAL ▲/▼].

    Three boxes appear left-to-right in sequence, connected by arrows.
    Word-synced to IMG_1014 (linguistic trading beat).
    """
    out_dir = os.path.join(ANIM, slot, "frames")
    os.makedirs(out_dir, exist_ok=True)

    x0, y0, x1, y1 = CARD
    n = int(round(dur * FPS))
    fhdr  = font(28); fsub = font(20, False)
    fbox  = font(22); fbig = font(38)

    cy = (y0 + y1) // 2 + 10
    BOX_W, BOX_H = 230, 84
    GAP = 56

    # Three box centres
    total_w = 3 * BOX_W + 2 * GAP
    bx1 = x0 + (x1 - x0 - total_w) // 2
    bx2 = bx1 + BOX_W + GAP
    bx3 = bx2 + BOX_W + GAP

    BOXES = [
        (bx1, "POWELL\nSPEECH",    DIM,   0.30),
        (bx2, "NLP\nPARSER",       GREEN, 0.90),
        (bx3, "TRADE\nSIGNAL",     GOLD,  1.60),
    ]

    def draw_box(d, bx, label, color, alpha):
        box = (bx, cy - BOX_H // 2, bx + BOX_W, cy + BOX_H // 2)
        rrect(d, box, 14,
              fill=(color[0] // 5, color[1] // 5, color[2] // 5, alpha),
              outline=(*color, alpha), width=3)
        lines = label.split("\n")
        total_h = sum(th(d, l, fbox) for l in lines) + 4 * (len(lines) - 1)
        ty = cy - total_h // 2
        for line in lines:
            lw = tw(d, line, fbox)
            d.text((bx + (BOX_W - lw) // 2, ty), line, font=fbox, fill=(*color, alpha))
            ty += th(d, line, fbox) + 4

    def draw_arrow(d, x_from, x_to, color, alpha):
        ax1, ax2 = x_from + BOX_W, x_to
        d.line((ax1, cy, ax2, cy), fill=(*color, alpha), width=4)
        d.polygon([(ax2, cy), (ax2 - 14, cy - 7), (ax2 - 14, cy + 7)],
                  fill=(*color, alpha))

    # ▲▼ signal icons for box 3
    T_ICONS = 2.20

    for i in range(n):
        t = i / FPS
        layer = new_frame()
        d = ImageDraw.Draw(layer)

        rrect(d, (x0, y0, x1, y1), 24, fill=PANEL + (238,),
              outline=(40, 54, 80, 255), width=2)
        d.text((x0 + 34, y0 + 22), "LINGUISTIC SIGNAL TRADING", font=fhdr, fill=WHITE)
        d.text((x0 + 34, y0 + 60),
               "markets now price the WORDS, not the rate decision",
               font=fsub, fill=DIM)

        prev_bx = None
        prev_col = None
        for bx, label, color, t_on in BOXES:
            p = pop(t, t_on, 0.45)
            if p > 0:
                a = int(255 * p)
                if prev_bx is not None:
                    da = int(255 * min(p, pop(t, t_on - 0.30, 0.45)))
                    draw_arrow(d, prev_bx, bx, DIM, da)
                draw_box(d, bx, label, color, a)
            prev_bx = bx
            prev_col = color

        # ▲ BUY / ▼ SELL icons inside box 3 once it appears
        p3 = pop(t, T_ICONS, 0.40)
        if p3 > 0:
            a3 = int(255 * p3)
            # ▲ buy above centre
            d.text((bx3 + BOX_W // 2 - tw(d, "▲ BUY", fbig) // 2, cy - BOX_H // 2 - 52),
                   "▲ BUY", font=fbig, fill=(*GREEN, a3))
            # ▼ sell below centre
            d.text((bx3 + BOX_W // 2 - tw(d, "▼ SELL", fbig) // 2, cy + BOX_H // 2 + 10),
                   "▼ SELL", font=fbig, fill=(*RED, a3))

        layer = card_fade(layer, t, dur)
        layer.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)


# ─────────────────────────────────────────── SHARPE 3.8 -> CROWDED FLIP
def render_gfx_sharpe(slot, dur):
    """Result badge: Sharpe 3.8 (green) holds, then 'CROWDED' stamp overlays in red.

    Synced to IMG_1019: badge appears on 'three point eight', red stamp on 'mati'.
    Output-timeline offsets:
      start_in_output = 82.0 (seg 9 offset=79.31, src_start=1.20)
      'three point eight' at src ~5.0 -> out = 5.0 - 1.20 + 79.31 = 83.11
      badge reveal_d = 1.2s, so badge starts at out 83.11 - 1.2 = 81.91 ≈ 82.0  ✓
      'sudah mati' at src ~8.5  -> out = 8.5 - 1.20 + 79.31 = 86.61
      stamp appears at local t = 86.61 - 82.0 = 4.61s
    """
    out_dir = os.path.join(ANIM, slot, "frames")
    os.makedirs(out_dir, exist_ok=True)

    x0, y0, x1, y1 = CARD
    n = int(round(dur * FPS))
    fhdr = font(28); flbl = font(22, False); fbig = font(80); fstamp = font(72)

    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2 + 10

    T_BADGE  = 0.30    # green badge pops
    T_STAMP  = 4.61    # red CROWDED stamp

    for i in range(n):
        t = i / FPS
        layer = new_frame()
        d = ImageDraw.Draw(layer)

        rrect(d, (x0, y0, x1, y1), 24, fill=PANEL + (238,),
              outline=(40, 54, 80, 255), width=2)
        d.text((x0 + 34, y0 + 22), "CHATGPT FOR TRADING — RESULTS", font=fhdr, fill=WHITE)

        # green badge
        p_b = pop(t, T_BADGE, 0.55)
        if p_b > 0:
            ba = int(255 * p_b)
            bw, bh = 580, 160
            bx, by = cx - bw // 2, cy - bh // 2
            rrect(d, (bx, by, bx + bw, by + bh), 20,
                  fill=(10, 60, 35, ba), outline=(*GREEN, ba), width=4)
            lbl = "SHARPE RATIO"
            d.text((cx - tw(d, lbl, flbl) // 2, by + 14),
                   lbl, font=flbl, fill=(*DIM, ba))
            val = "3.8"
            d.text((cx - tw(d, val, fbig) // 2, by + 46),
                   val, font=fbig, fill=(*GREEN, ba))
            src_lbl = "Lopez-Lira & Tang (2023)  •  GPT-4 strategy"
            d.text((cx - tw(d, src_lbl, flbl) // 2, by + bh - 30),
                   src_lbl, font=flbl, fill=(*DIM, ba))

        # red CROWDED stamp (rotated feel via manual diagonal — PIL has no rotate per-text)
        p_s = pop(t, T_STAMP, 0.40)
        if p_s > 0:
            # draw on a tmp layer so we can rotate it
            stamp_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            sd = ImageDraw.Draw(stamp_layer)
            stamp = "CROWDED"
            sw = tw(sd, stamp, fstamp)
            sh = th(sd, stamp, fstamp)
            # draw with thick red border
            for ox in range(-3, 4, 1):
                for oy in range(-3, 4, 1):
                    sd.text((cx - sw // 2 + ox, cy - sh // 2 + oy),
                            stamp, font=fstamp, fill=(*RED, 0))
            sd.text((cx - sw // 2, cy - sh // 2), stamp, font=fstamp,
                    fill=(*RED, int(220 * p_s)))
            # draw a red box outline around it
            pad = 12
            sd.rectangle((cx - sw // 2 - pad, cy - sh // 2 - pad,
                           cx + sw // 2 + pad, cy + sh // 2 + pad),
                          outline=(*RED, int(200 * p_s)), width=5)
            # rotate -18 degrees
            rotated = stamp_layer.rotate(-18, expand=False, center=(cx, cy))
            layer = Image.alpha_composite(layer, rotated)

        layer = card_fade(layer, t, dur)
        layer.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)


# ─────────────────────────────────────────── MULTI-AGENT DEBATE DIAGRAM
def render_gfx_agents(slot, dur):
    """Multi-agent LLM trading diagram: N analysts -> TRADER -> RETURN: +26%.

    Left column: 4 analyst boxes fitted within the card's box area.
    Center: TRADER box.
    Right: RETURN +26% badge — appears at t=4.5s (mid-overlay) so it holds
    for ~5s before the overlay fades, giving the viewer time to read it.

    Box positions are computed explicitly to avoid overflow past y1=455.
    Box area: y=210 to y=445 (235px). 4 boxes of AH=46 + gap=10.
    """
    out_dir = os.path.join(ANIM, slot, "frames")
    os.makedirs(out_dir, exist_ok=True)

    x0, y0, x1, y1 = CARD
    n = int(round(dur * FPS))
    fhdr = font(26); fsub = font(19, False); fbox = font(19); fbig = font(52); flbl = font(21, False)

    cy = (y0 + y1) // 2 + 5

    # Analyst boxes (left column)
    AGENTS = [
        ("FUNDAMENTALS\nANALYST", DIM,   0.30),
        ("SENTIMENT\nANALYST",    GREEN, 0.60),
        ("NEWS\nANALYST",         GOLD,  0.90),
        ("TECHNICAL\nANALYST",    DIM,   1.20),
    ]
    AW, AH = 215, 46   # reduced height so 4 boxes fit within card
    AGENT_X = x0 + 32

    # Explicit positions fitted within box area y=210..445 (235px available)
    # 4 * 46 = 184px boxes + 51px for 5 gaps → gap=10px each
    _BOX_AREA_Y0 = y0 + 90   # 210
    _BOX_AREA_Y1 = y1 - 10   # 445
    _GAP = (_BOX_AREA_Y1 - _BOX_AREA_Y0 - len(AGENTS) * AH) // (len(AGENTS) + 1)

    def agent_y(idx):
        return _BOX_AREA_Y0 + _GAP + idx * (AH + _GAP)

    # Trader box (centre-left of right half)
    TW2, TH2 = 180, 80
    TRADER_X = x0 + 305
    TRADER_Y = cy - TH2 // 2

    # Return badge (right side of card)
    RET_X = x0 + 550
    # Badge appears at t=4.5s so it holds ~5s before overlay fades out
    T_RETURN = 4.50

    def draw_agent_box(d, idx, color, alpha):
        ay = agent_y(idx)
        box = (AGENT_X, ay, AGENT_X + AW, ay + AH)
        rrect(d, box, 10,
              fill=(color[0] // 6, color[1] // 6, color[2] // 6, alpha),
              outline=(*color, alpha), width=2)
        lines = AGENTS[idx][0].split("\n")
        total_h = sum(th(d, l, fbox) for l in lines) + 3 * (len(lines) - 1)
        ty = ay + (AH - total_h) // 2
        for line in lines:
            lw = tw(d, line, fbox)
            d.text((AGENT_X + (AW - lw) // 2, ty), line, font=fbox, fill=(*color, alpha))
            ty += th(d, line, fbox) + 3

    def draw_arrow_to_trader(d, idx, alpha):
        ay = agent_y(idx) + AH // 2
        d.line((AGENT_X + AW, ay, TRADER_X, TRADER_Y + TH2 // 2),
               fill=(*DIM, alpha // 2), width=2)

    for i in range(n):
        t = i / FPS
        layer = new_frame()
        d = ImageDraw.Draw(layer)

        rrect(d, (x0, y0, x1, y1), 24, fill=PANEL + (238,),
              outline=(40, 54, 80, 255), width=2)
        d.text((x0 + 34, y0 + 22), "AGENT TEAMS — MULTI-LLM DEBATE", font=fhdr, fill=WHITE)
        d.text((x0 + 34, y0 + 56),
               "agents debate each data dimension, then trade",
               font=fsub, fill=DIM)

        # Analyst agents appear in sequence
        p_trader = 0.0
        for idx, (label, color, t_on) in enumerate(AGENTS):
            p = pop(t, t_on, 0.40)
            if p > 0:
                a = int(255 * p)
                draw_agent_box(d, idx, color, a)
                draw_arrow_to_trader(d, idx, a)
                p_trader = max(p_trader, p)

        # TRADER box appears after first agent
        p_trad = pop(t, 1.50, 0.45)
        if p_trad > 0:
            ta = int(255 * p_trad)
            rrect(d, (TRADER_X, TRADER_Y, TRADER_X + TW2, TRADER_Y + TH2), 14,
                  fill=(22 // 5, 199 // 5, 132 // 5, ta),
                  outline=(*GREEN, ta), width=3)
            lbl = "TRADER"
            d.text((TRADER_X + (TW2 - tw(d, lbl, fbox)) // 2,
                    TRADER_Y + (TH2 - th(d, lbl, fbox)) // 2),
                   lbl, font=fbox, fill=(*GREEN, ta))

        # Return badge pops on '26%'
        p_ret = pop(t, T_RETURN, 0.45)
        if p_ret > 0:
            ra = int(255 * p_ret)
            # arrow from trader to return
            d.line((TRADER_X + TW2, cy, RET_X, cy), fill=(*GREEN, ra // 2), width=3)
            d.polygon([(RET_X, cy), (RET_X - 12, cy - 6), (RET_X - 12, cy + 6)],
                      fill=(*GREEN, ra))
            # badge
            RBW, RBH = 380, 155
            rx = RET_X + 10
            ry = cy - RBH // 2
            rrect(d, (rx, ry, rx + RBW, ry + RBH), 18,
                  fill=(10, 60, 35, ra), outline=(*GREEN, ra), width=4)
            hdr_r = "ANNUAL RETURN"
            d.text((rx + (RBW - tw(d, hdr_r, flbl)) // 2, ry + 12),
                   hdr_r, font=flbl, fill=(*DIM, ra))
            val_r = "+26%"
            d.text((rx + (RBW - tw(d, val_r, fbig)) // 2, ry + 46),
                   val_r, font=fbig, fill=(*GREEN, ra))
            src_r = "Xiao et al. (2024)  •  TradingAgents"
            d.text((rx + (RBW - tw(d, src_r, flbl)) // 2, ry + RBH - 28),
                   src_r, font=flbl, fill=(*DIM, ra))

        layer = card_fade(layer, t, dur)
        layer.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)


# ══════════════════════════════════════════════════════════════════ MAIN
if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"

    SRCS = [
        ("slot_src_powell",
         f"{SRC}/powell.png",
         "Jerome Powell, Chair  •  Federal Reserve  —  FOMC Press Conference",
         6.0),
        ("slot_src_bloomberg",
         f"{SRC}/bloomberg.png",
         "Wu et al. / Bloomberg LP (2023)  —  BloombergGPT  •  arXiv:2303.17564",
         5.5),
        ("slot_src_chatgpt",
         f"{SRC}/chatgpt.png",
         "Lopez-Lira & Tang (2023)  —  Can ChatGPT Forecast Stock Movements?  •  arXiv:2304.07619",
         5.0),
    ]

    if which in ("all", "hook"):   render_gfx_hook("slot_gfx_hook", 12.0)
    if which in ("all", "day5"):   render_news_day5("slot_news_day5", 2.9)
    if which in ("all", "expect"): render_gfx_expect("slot_gfx_expect", 9.0)
    if which in ("all", "nlp"):    render_gfx_nlp("slot_gfx_nlp", 7.5)
    if which in ("all", "sharpe"): render_gfx_sharpe("slot_gfx_sharpe", 6.0)
    if which in ("all", "agents"): render_gfx_agents("slot_gfx_agents", 10.5)
    if which in ("all", "src"):
        for slot, img, cap, dur in SRCS:
            if os.path.exists(img):
                render_src(slot, img, cap, dur)
            else:
                print(f"  SKIP {slot} — screenshot not found: {img}")

    print("DONE", which)
