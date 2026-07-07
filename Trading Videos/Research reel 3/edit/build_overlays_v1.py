"""Build overlays for Research reel 3 — ML & Neural Networks (Day 4).

Slots:
  slot_pvz_day4       PvZ wooden sign "DAY 4", drops on "four"
  slot_gfx_zoo        Factor Zoo bar chart: 452 anomalies, 65% fail replication
  slot_src_hou2020    Citation: Hou, Xue & Zhang (2020) Replicating Anomalies
  slot_gfx_nn         Neural network node diagram (animated)
  slot_src_gu2020     Citation: Gu, Kelly & Xiu (2020) Empirical Asset Pricing via ML
  slot_gfx_result_nn  Result badge: ~2x Sharpe + R²
  slot_gfx_rl         Reinforcement learning reward/punishment loop diagram
  slot_src_alphaport  Citation: Cong et al. (2021) AlphaPortfolio
  slot_gfx_result_rl  Result badge: Sharpe 2.0 · α 13%
  slot_gfx_decay      Alpha decay graphic: fee + crowding kills edge

Encode each slot after running this script:
  for s in edit/animations/slot_*; do
    ffmpeg -y -framerate 30 -i "$s/frames/f_%05d.png" \
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

GREEN  = (22, 199, 132)
GREEN_D= (10, 150, 98)
NAVY   = (11, 31, 58)
PANEL  = (12, 22, 40)
WHITE  = (255, 255, 255)
DIM    = (158, 168, 184)
RED    = (235, 90, 95)
GOLD   = (245, 196, 90)

def font(sz, bold=True):
    return ImageFont.truetype(ARIALBD if bold else ARIAL, sz)

def eo(t):
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3

def eio(t):
    t = max(0.0, min(1.0, t))
    return 4*t**3 if t < 0.5 else 1 - (-2*t+2)**3/2

def lerp(a, b, p): return a + (b - a) * p

def tw(d, s, f): b = d.textbbox((0,0), s, font=f); return b[2]-b[0]
def th(d, s, f): b = d.textbbox((0,0), s, font=f); return b[3]-b[1]

def rrect(draw, box, r, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

def pop(t, t0, d=0.5):
    if t < t0: return 0.0
    return eo((t - t0) / d)

def note(slot, n): print(f"  {slot}: {n} frames")

def new_frame(): return Image.new("RGBA", (W, H), (0, 0, 0, 0))

def card_fade(layer, t, dur, t_in=0.4, t_out=0.4):
    """Apply global alpha fade-in / fade-out to a layer."""
    if t < t_in:
        ga = eo(t / t_in)
    elif t > dur - t_out:
        ga = eo((dur - t) / t_out)
    else:
        return layer
    a = layer.split()[3].point(lambda v: int(v * ga))
    layer.putalpha(a)
    return layer

# Top-band card bounds (same as reel 1 — proven position)
CARD = (80, 120, 1000, 455)

# ─────────────────────────────────────────── FULL-BLEED CITATION PANEL
SHOT_H = 700
CAP_H  = 56
PANEL_H = SHOT_H + CAP_H

def render_src(slot, img_path, caption, dur):
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
    d.text((30, SHOT_H + (CAP_H - th(d, caption, fc)) // 2 - 4), caption, font=fc, fill=(225, 232, 242))
    d.line((0, SHOT_H, W, SHOT_H), fill=(255, 255, 255, 60), width=2)

    shadow = Image.new("RGBA", (W, 60), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rectangle((0, 0, W, 60), fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))

    n = int(round(dur * FPS))
    t_in, t_out = 0.5, 0.42
    for i in range(n):
        t = i / FPS
        if t < t_in:   y = lerp(-(PANEL_H + 50), 0, eo(t / t_in))
        elif t > dur - t_out: y = lerp(-(PANEL_H + 50), 0, eo((dur - t) / t_out))
        else: y = 0
        cv = new_frame()
        yy = int(round(y))
        cv.paste(shadow, (0, yy + PANEL_H - 20), shadow)
        cv.paste(panel,  (0, yy), panel)
        cv.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)

# ─────────────────────────────────────────── ML / NEURAL-NETWORK "DAY 4" INTRO
# Each episode has a distinct themed intro sign:
#   Reel 1 / DAY 2 → PvZ wooden lawn sign
#   Reel 2 / DAY 3 → Satellite/spy HUD with target-lock
#   Reel 3 / DAY 4 → Neural network predicting "DAY 4" (this function)

def _draw_node_glow(d, cx, cy, r, color, alpha):
    """Concentric halo rings for a glowing node."""
    for ring in range(3, 0, -1):
        ra = r + ring * 8
        ga = int(alpha * (0.12 * ring))
        d.ellipse((cx-ra, cy-ra, cx+ra, cy+ra),
                  fill=(color[0], color[1], color[2], ga))
    d.ellipse((cx-r, cy-r, cx+r, cy+r),
              fill=(color[0]//4, color[1]//4, color[2]//4, alpha),
              outline=(color[0], color[1], color[2], alpha), width=3)

def render_ml_intro(slot, dur):
    """Futuristic ML-themed intro: a neural network activates left-to-right,
    then 'DAY 4' materialises as the predicted output — scan-reveal effect.

    Layout (top-band, fits y=90–455):
      Left (x=90–480):  3-layer neural net (input → hidden → output node)
      Right (x=490–990): 'DAY 4' as the network's prediction output
    """
    import random
    rng = random.Random(42)   # deterministic

    out_dir = os.path.join(ANIM, slot, "frames")
    os.makedirs(out_dir, exist_ok=True)

    n = int(round(dur * FPS))
    fday  = font(148)
    flbl  = font(22, False)
    fmono = font(18, False)

    # Neural-net geometry
    LAYER_X  = [120, 265, 420]          # x centres: input, hidden, output
    LAYER_N  = [4,   6,   1]            # node counts per layer
    NET_Y0, NET_Y1 = 135, 445           # vertical span
    net_cy = (NET_Y0 + NET_Y1) // 2

    def node_ys(count):
        span = (NET_Y1 - NET_Y0) * 0.82
        top  = net_cy - span / 2
        if count == 1:
            return [net_cy]
        return [int(top + i * span / (count - 1)) for i in range(count)]

    layers = [(LAYER_X[i], node_ys(LAYER_N[i])) for i in range(3)]

    # Pre-generate matrix rain columns (faint binary chars, top strip only)
    RAIN_COLS = [(rng.randint(80, 990), rng.uniform(0, 2.9)) for _ in range(28)]

    # Timing anchors (seconds, local to this overlay)
    T_INPUT_ON  = 0.30   # input nodes appear
    T_CONN1     = 0.55   # input→hidden connections draw
    T_HIDDEN_ON = 0.65   # hidden nodes appear
    T_CONN2     = 0.90   # hidden→output connections draw
    T_OUT_ON    = 1.10   # output node pops
    T_SCAN      = 1.35   # scan-line reveal of "DAY 4" begins
    T_SCAN_END  = 2.10   # scan line finishes (DAY 4 fully revealed)
    T_FADE_OUT  = dur - 0.4

    for i in range(n):
        t = i / FPS
        cv = new_frame()
        d  = ImageDraw.Draw(cv)

        # ── global alpha envelope
        if t < 0.35:
            ga = eo(t / 0.35)
        elif t > T_FADE_OUT:
            ga = eo((dur - t) / 0.4)
        else:
            ga = 1.0

        # ── faint matrix rain (binary digits, top 90px only)
        for rx, rdelay in RAIN_COLS:
            rt = (t - rdelay) % 2.9
            if rt < 0:
                continue
            ry = int(lerp(60, 110, min(1.0, rt / 1.2)))
            char = rng.choice(["0", "1"])
            ca   = int(ga * 55)
            d.text((rx, ry), char, font=fmono, fill=(*GREEN, ca))

        # ── panel background (left half covering the neural net)
        bg_a = int(ga * 210)
        rrect(d, (82, 100, 1000, 458), 22, fill=(*PANEL, bg_a),
              outline=(*GREEN, int(ga * 80)), width=2)

        # ── connections input→hidden
        p_c1 = eo((t - T_CONN1) / 0.40) if t > T_CONN1 else 0.0
        if p_c1 > 0:
            lx, lys = layers[0]
            rx, rys = layers[1]
            for ly_y in lys:
                for ry_y in rys:
                    ca = int(ga * 50 * p_c1)
                    d.line((lx, ly_y, rx, ry_y), fill=(*GREEN, ca), width=1)

        # ── connections hidden→output
        p_c2 = eo((t - T_CONN2) / 0.35) if t > T_CONN2 else 0.0
        if p_c2 > 0:
            lx, lys = layers[1]
            rx, rys = layers[2]
            for ly_y in lys:
                for ry_y in rys:
                    ca = int(ga * 70 * p_c2)
                    d.line((lx, ly_y, rx, ry_y), fill=(*GREEN, ca), width=2)

        # ── input nodes
        p_inp = eo((t - T_INPUT_ON) / 0.35) if t > T_INPUT_ON else 0.0
        if p_inp > 0:
            lx, lys = layers[0]
            for j, ny in enumerate(lys):
                delay_p = eo(max(0.0, (t - T_INPUT_ON - j*0.06) / 0.30))
                a = int(ga * 200 * delay_p)
                if a > 0:
                    _draw_node_glow(d, lx, ny, 13, DIM, a)

        # ── hidden nodes
        p_hid = eo((t - T_HIDDEN_ON) / 0.40) if t > T_HIDDEN_ON else 0.0
        if p_hid > 0:
            lx, lys = layers[1]
            for j, ny in enumerate(lys):
                delay_p = eo(max(0.0, (t - T_HIDDEN_ON - j*0.05) / 0.28))
                a = int(ga * 220 * delay_p)
                if a > 0:
                    _draw_node_glow(d, lx, ny, 14, GREEN, a)

        # ── output node (large, strong glow)
        p_out = eo((t - T_OUT_ON) / 0.35) if t > T_OUT_ON else 0.0
        if p_out > 0:
            ox, (oy,) = layers[2]
            a = int(ga * 255 * p_out)
            # outer glow rings
            for ring in range(5, 0, -1):
                ra  = 20 + ring * 12
                rga = int(a * 0.07 * ring)
                d.ellipse((ox-ra, oy-ra, ox+ra, oy+ra), fill=(*GREEN, rga))
            d.ellipse((ox-20, oy-20, ox+20, oy+20),
                      fill=(*GREEN, a),
                      outline=(*WHITE, int(a*0.8)), width=3)

        # ── "OUTPUT →" label connecting network to text
        if p_out > 0:
            la = int(ga * 160 * p_out)
            lbl = "OUTPUT →"
            d.text((440, net_cy - th(d, lbl, flbl)//2), lbl, font=flbl, fill=(*GREEN, la))

        # ── "DAY 4" scan-reveal
        # Drawn to a scratch image then alpha_composited onto cv so the panel
        # background (and node network) behind the text are never erased.
        if t > T_SCAN:
            scan_p = min(1.0, (t - T_SCAN) / (T_SCAN_END - T_SCAN))
            txt    = "DAY 4"
            text_x = 506
            text_y = net_cy - th(d, txt, fday) // 2 - 8
            txt_w  = tw(d, txt, fday)

            # Build full text on a scratch layer
            txt_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            td = ImageDraw.Draw(txt_img)
            for gox in range(-5, 6, 2):
                for goy in range(-5, 6, 2):
                    td.text((text_x+gox, text_y+goy), txt, font=fday,
                            fill=(*GREEN, int(ga * 70)))
            td.text((text_x, text_y), txt, font=fday,
                    fill=(*WHITE, int(ga * 250)))

            # Reveal only the left strip up to the scan front — crop, re-paste
            # into a blank layer, then alpha_composite so underlying pixels survive
            reveal_x = max(0, int(text_x + txt_w * scan_p))
            if reveal_x > 0:
                revealed = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                revealed.paste(txt_img.crop((0, 0, reveal_x, H)), (0, 0))
                cv = Image.alpha_composite(cv, revealed)

            # Bright scan-edge line drawn directly (fine since it's on top)
            if scan_p < 1.0:
                d = ImageDraw.Draw(cv)   # refresh draw context after composite
                d.line((reveal_x, text_y - 6,
                        reveal_x, text_y + th(d, txt, fday) + 6),
                       fill=(*WHITE, int(ga * 220)), width=4)

        # ── "MACHINE LEARNING" label below "DAY 4" (appears once scan done)
        if t > T_SCAN_END:
            la   = int(ga * 200 * eo((t - T_SCAN_END) / 0.35))
            sub  = "MACHINE LEARNING"
            sx   = 506
            sy   = net_cy + th(d, "DAY 4", fday)//2 + 4
            d.text((sx, sy), sub, font=flbl, fill=(*GREEN, la))

        # ── apply global alpha to whole canvas
        if ga < 1.0:
            r_ch, g_ch, b_ch, a_ch = cv.split()
            a_ch = a_ch.point(lambda v: int(v * ga))
            cv = Image.merge("RGBA", (r_ch, g_ch, b_ch, a_ch))

        cv.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)

# ─────────────────────────────────────────── FACTOR ZOO BAR CHART
def render_gfx_zoo(slot, dur):
    """452 anomalies tested — 65% failed replication. Animated bar reveal."""
    out_dir = os.path.join(ANIM, slot, "frames")
    os.makedirs(out_dir, exist_ok=True)
    x0, y0, x1, y1 = CARD
    n = int(round(dur * FPS))
    fhdr = font(30); fsub = font(22, False); fnum = font(52); flbl = font(24, False)

    # Two bars: 35% real (green) and 65% noise (red)
    bar_y0, bar_y1 = y0 + 120, y1 - 60
    bar_h = bar_y1 - bar_y0
    cx = (x0 + x1) // 2
    bar_w = 200
    gap = 80
    bar_ax = cx - gap // 2 - bar_w   # real bar left
    bar_bx = cx + gap // 2            # noise bar left

    draw_t = 0.5   # bars start drawing at 0.5s
    draw_d = 1.8   # draw duration

    for i in range(n):
        t = i / FPS
        layer = new_frame()
        d = ImageDraw.Draw(layer)
        rrect(d, (x0, y0, x1, y1), 24, fill=PANEL+(238,), outline=(40,54,80,255), width=2)
        d.text((x0+34, y0+22), "THE FACTOR ZOO", font=fhdr, fill=WHITE)
        d.text((x0+34, y0+62), "452 anomalies tested by Hou, Xue & Zhang (2020)", font=fsub, fill=DIM)

        p = eio((t - draw_t) / draw_d) if t > draw_t else 0.0

        # green bar — 35% real
        gh = int(bar_h * 0.35 * p)
        if gh > 0:
            rrect(d, (bar_ax, bar_y1 - gh, bar_ax + bar_w, bar_y1), 8, fill=GREEN+(220,))
        pa = int(255 * min(1.0, (t - draw_t) / draw_d)) if t > draw_t else 0
        d.text((bar_ax + bar_w//2 - tw(d, "35%", fnum)//2, bar_y1 - gh - 64),
               "35%", font=fnum, fill=(GREEN[0], GREEN[1], GREEN[2], pa))
        d.text((bar_ax + bar_w//2 - tw(d, "REAL", flbl)//2, bar_y1 + 8),
               "REAL", font=flbl, fill=(GREEN[0], GREEN[1], GREEN[2], pa))

        # red bar — 65% noise
        rh = int(bar_h * 0.65 * p)
        if rh > 0:
            rrect(d, (bar_bx, bar_y1 - rh, bar_bx + bar_w, bar_y1), 8, fill=RED+(220,))
        rb = int(255 * min(1.0, max(0.0, (t - draw_t - 0.4) / draw_d))) if t > draw_t else 0
        d.text((bar_bx + bar_w//2 - tw(d, "65%", fnum)//2, bar_y1 - rh - 64),
               "65%", font=fnum, fill=(RED[0], RED[1], RED[2], rb))
        d.text((bar_bx + bar_w//2 - tw(d, "NOISE", flbl)//2, bar_y1 + 8),
               "NOISE", font=flbl, fill=(RED[0], RED[1], RED[2], rb))

        layer = card_fade(layer, t, dur)
        layer.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)

# ─────────────────────────────────────────── NEURAL NET DIAGRAM
def render_gfx_nn(slot, dur):
    """Animated layered node diagram: input → hidden → output."""
    out_dir = os.path.join(ANIM, slot, "frames")
    os.makedirs(out_dir, exist_ok=True)
    x0, y0, x1, y1 = CARD
    n = int(round(dur * FPS))
    fhdr = font(30); fsub = font(22, False); flbl = font(20, False)

    # Layer positions
    layers = [
        {"label": "INPUT\nFACTORS", "nodes": 4, "x": x0 + 110},
        {"label": "HIDDEN\nLAYER 1", "nodes": 5, "x": x0 + 310},
        {"label": "HIDDEN\nLAYER 2", "nodes": 5, "x": x0 + 510},
        {"label": "OUTPUT\nRETURN", "nodes": 2, "x": x0 + 710},
    ]
    cy_center = (y0 + y1) // 2 + 20
    node_r = 18
    node_spacing = 72

    def node_ys(count):
        total = (count - 1) * node_spacing
        top = cy_center - total // 2
        return [top + i * node_spacing for i in range(count)]

    all_layers = [(l["x"], node_ys(l["nodes"])) for l in layers]

    reveal_d = 1.5    # connections draw over 1.5s
    reveal_t = 0.5

    for i in range(n):
        t = i / FPS
        layer = new_frame()
        d = ImageDraw.Draw(layer)
        rrect(d, (x0, y0, x1, y1), 24, fill=PANEL+(238,), outline=(40,54,80,255), width=2)
        d.text((x0+34, y0+22), "NEURAL NETWORK", font=fhdr, fill=WHITE)
        d.text((x0+34, y0+62), "layers of nodes learn factor interactions automatically", font=fsub, fill=DIM)

        p_conn = eio((t - reveal_t) / reveal_d) if t > reveal_t else 0.0

        # draw connections between consecutive layers
        for li in range(len(all_layers) - 1):
            lx, lys = all_layers[li]
            rx, rys = all_layers[li + 1]
            conn_count = len(lys) * len(rys)
            shown = int(p_conn * conn_count)
            k = 0
            for ly_y in lys:
                for ry_y in rys:
                    if k < shown:
                        alpha = int(60 * min(1.0, (shown - k) / max(1, conn_count * 0.3)))
                        d.line((lx, ly_y, rx, ry_y), fill=(GREEN[0], GREEN[1], GREEN[2], alpha), width=1)
                    k += 1

        # draw nodes
        p_nodes = eo((t - 0.2) / 0.6) if t > 0.2 else 0.0
        for li, (lx, lys) in enumerate(all_layers):
            col = GREEN if li == len(all_layers) - 1 else WHITE
            for ny in lys:
                a = int(220 * p_nodes)
                d.ellipse((lx-node_r, ny-node_r, lx+node_r, ny+node_r),
                          fill=(col[0], col[1], col[2], a),
                          outline=(NAVY[0], NAVY[1], NAVY[2], a), width=3)
            # layer label below
            lbl = layers[li]["label"]
            for line_i, lline in enumerate(lbl.split("\n")):
                lw = tw(d, lline, flbl)
                la = int(180 * p_nodes)
                d.text((lx - lw//2, y1 - 50 + line_i * 22), lline, font=flbl,
                       fill=(DIM[0], DIM[1], DIM[2], la))

        layer = card_fade(layer, t, dur)
        layer.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)

# ─────────────────────────────────────────── RESULT BADGE: ~2x Sharpe + R²
def render_gfx_result_nn(slot, dur):
    """Pop-in badge: Sharpe & R² ~ doubled."""
    out_dir = os.path.join(ANIM, slot, "frames")
    os.makedirs(out_dir, exist_ok=True)
    x0, y0, x1, y1 = CARD
    n = int(round(dur * FPS))
    fhdr = font(30); fbig = font(70); fsub = font(26, False); flbl = font(22, False)

    for i in range(n):
        t = i / FPS
        layer = new_frame()
        d = ImageDraw.Draw(layer)
        rrect(d, (x0, y0, x1, y1), 24, fill=PANEL+(238,), outline=(40,54,80,255), width=2)
        d.text((x0+34, y0+22), "ML OUTPERFORMS CLASSICAL MODELS", font=fhdr, fill=WHITE)

        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2 + 10

        # left badge: Sharpe
        p1 = pop(t, 0.3, 0.5)
        if p1 > 0:
            a = int(255 * p1)
            bw, bh = 360, 130
            bx, by = cx - bw - 20, cy - bh // 2
            rrect(d, (bx, by, bx+bw, by+bh), 16, fill=(20, 50, 30, a), outline=(GREEN[0],GREEN[1],GREEN[2],a), width=3)
            label = "SHARPE RATIO"
            d.text((bx + bw//2 - tw(d,label,flbl)//2, by+12), label, font=flbl, fill=(DIM[0],DIM[1],DIM[2],a))
            val = "~2×"
            d.text((bx + bw//2 - tw(d,val,fbig)//2, by+38), val, font=fbig, fill=(GREEN[0],GREEN[1],GREEN[2],a))

        # right badge: R²
        p2 = pop(t, 0.8, 0.5)
        if p2 > 0:
            a = int(255 * p2)
            bw, bh = 360, 130
            bx, by = cx + 20, cy - bh // 2
            rrect(d, (bx, by, bx+bw, by+bh), 16, fill=(20, 50, 30, a), outline=(GREEN[0],GREEN[1],GREEN[2],a), width=3)
            label = "R² (FIT)"
            d.text((bx + bw//2 - tw(d,label,flbl)//2, by+12), label, font=flbl, fill=(DIM[0],DIM[1],DIM[2],a))
            val = "~2×"
            d.text((bx + bw//2 - tw(d,val,fbig)//2, by+38), val, font=fbig, fill=(GREEN[0],GREEN[1],GREEN[2],a))

        p3 = pop(t, 1.4, 0.4)
        if p3 > 0:
            a = int(255 * p3)
            sub = "vs. classical linear regression   •   Gu, Kelly & Xiu (2020)"
            d.text((cx - tw(d,sub,fsub)//2, y1 - 52), sub, font=fsub, fill=(DIM[0],DIM[1],DIM[2],a))

        layer = card_fade(layer, t, dur)
        layer.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)

# ─────────────────────────────────────────── RL REWARD/PUNISHMENT DIAGRAM
def render_gfx_rl(slot, dur):
    """RL flow diagram — elements are word-synced to the voiceover.

    Layout (3 non-overlapping zones, left→right):
      Zone A (x≈220): [AGENT]
      Zone B (x≈530): [MARKET]
      Zone C (x≈685–965): [✓ REWARD] top / [✗ PENALTY] bottom

    Word-sync (local overlay seconds, derived from transcript):
      t=0.30 → AGENT + MARKET appear
      t=0.90 → AGENT→MARKET trade arrow draws
      t=2.00 → fork arrow from MARKET toward outcomes
      t=3.12 → "rewards" → REWARD box fades in
      t=4.14 → "cuan"    → REWARD box pulses bright green
      t=4.92 → "hukum"   → PENALTY box fades in
      t=6.06 → "rugi"    → PENALTY box pulses bright red
    """
    out_dir = os.path.join(ANIM, slot, "frames")
    os.makedirs(out_dir, exist_ok=True)
    x0, y0, x1, y1 = CARD
    n = int(round(dur * FPS))
    fhdr  = font(28)
    fsub  = font(21, False)
    fbox  = font(25)
    fsmall = font(20, False)

    # Zone geometry — nothing overlaps
    A_CX, A_CY = 220, 288      # AGENT center
    M_CX, M_CY = 530, 288      # MARKET center
    BW, BH     = 180, 66       # main box size

    R_BOX = (685, 212, 962, 277)   # REWARD box  (top of zone C)
    P_BOX = (685, 300, 962, 365)   # PENALTY box (bottom of zone C)
    R_CY  = (R_BOX[1] + R_BOX[3]) // 2
    P_CY  = (P_BOX[1] + P_BOX[3]) // 2
    FORK_X = 638                   # x where the arrow forks

    def draw_main_box(d, cx, cy, label, color, a):
        rrect(d, (cx-BW//2, cy-BH//2, cx+BW//2, cy+BH//2), 14,
              fill=(color[0]//5, color[1]//5, color[2]//5, a),
              outline=(*color, a), width=3)
        d.text((cx - tw(d, label, fbox)//2, cy - th(d, label, fbox)//2),
               label, font=fbox, fill=(*color, a))

    def draw_outcome_box(d, box, label, color, a, pulse=0.0):
        """Outcome box with optional pulse highlight (0–1 extra brightness)."""
        glow = min(255, int(a + pulse * (255 - a)))
        fill_a = min(255, int(a * 0.25 + pulse * 80))
        rrect(d, box, 12,
              fill=(color[0]//4, color[1]//4, color[2]//4, fill_a),
              outline=(*color, glow), width=4 if pulse > 0 else 3)
        cx_ = (box[0] + box[2]) // 2
        cy_ = (box[1] + box[3]) // 2
        d.text((cx_ - tw(d, label, fbox)//2, cy_ - th(d, label, fbox)//2),
               label, font=fbox, fill=(*color, glow))

    def harrow(d, x1_, y_, x2_, color, a, label=None):
        d.line((x1_, y_, x2_, y_), fill=(*color, a), width=4)
        d.polygon([(x2_, y_), (x2_-14, y_-7), (x2_-14, y_+7)], fill=(*color, a))
        if label:
            mid = (x1_ + x2_) // 2
            d.text((mid - tw(d, label, fsmall)//2, y_ - 22),
                   label, font=fsmall, fill=(*color, a))

    def fork_arrow(d, from_x, from_y, fork_x, to_y_top, to_y_bot, box_x, color, a):
        """Horizontal stem → vertical split → two horizontal branches to outcome boxes."""
        # stem
        d.line((from_x, from_y, fork_x, from_y), fill=(*color, a), width=3)
        # vertical spine
        d.line((fork_x, to_y_top, fork_x, to_y_bot), fill=(*color, a), width=3)
        # top branch
        d.line((fork_x, to_y_top, box_x, to_y_top), fill=(*color, a), width=3)
        d.polygon([(box_x, to_y_top), (box_x-12, to_y_top-6), (box_x-12, to_y_top+6)],
                  fill=(*color, a))
        # bottom branch
        d.line((fork_x, to_y_bot, box_x, to_y_bot), fill=(*color, a), width=3)
        d.polygon([(box_x, to_y_bot), (box_x-12, to_y_bot-6), (box_x-12, to_y_bot+6)],
                  fill=(*color, a))

    # Word-synced timing constants (local overlay seconds)
    T_BOXES   = 0.30
    T_ARROW   = 0.90
    T_FORK    = 2.00
    T_REWARD  = 3.12   # "rewards"
    T_CUAN    = 4.14   # "cuan" → pulse
    T_HUKUM   = 4.92   # "hukum"
    T_RUGI    = 6.06   # "rugi"  → pulse

    for i in range(n):
        t = i / FPS
        layer = new_frame()
        d = ImageDraw.Draw(layer)

        rrect(d, (x0, y0, x1, y1), 24, fill=(*PANEL, 238), outline=(40, 54, 80, 255), width=2)
        d.text((x0+34, y0+22), "REINFORCEMENT LEARNING", font=fhdr, fill=WHITE)
        d.text((x0+34, y0+60),
               "sistem yang belajar dari reward dan punishment",
               font=fsub, fill=DIM)

        # AGENT + MARKET boxes
        p_boxes = pop(t, T_BOXES, 0.45)
        if p_boxes > 0:
            draw_main_box(d, A_CX, A_CY, "AGENT",  GREEN, int(255*p_boxes))
            draw_main_box(d, M_CX, M_CY, "MARKET", WHITE, int(255*p_boxes))

        # AGENT→MARKET trade arrow
        p_arrow = pop(t, T_ARROW, 0.45)
        if p_arrow > 0:
            harrow(d, A_CX+BW//2, A_CY, M_CX-BW//2, WHITE, int(255*p_arrow), label="TRADE")

        # fork arrow from MARKET right → outcome boxes
        p_fork = pop(t, T_FORK, 0.50)
        if p_fork > 0:
            fork_arrow(d, M_CX+BW//2, M_CY, FORK_X, R_CY, P_CY, R_BOX[0], DIM, int(180*p_fork))

        # REWARD box (appears on "rewards", pulses on "cuan")
        p_reward = pop(t, T_REWARD, 0.45)
        if p_reward > 0:
            pulse_r = eo(max(0.0, (t - T_CUAN) / 0.30)) * max(0.0, 1.0 - (t - T_CUAN) / 0.80) \
                      if t > T_CUAN else 0.0
            draw_outcome_box(d, R_BOX, "✓  REWARD  (cuan)", GREEN, int(255*p_reward), pulse_r)

        # PENALTY box (appears on "hukum", pulses on "rugi")
        p_penalty = pop(t, T_HUKUM, 0.45)
        if p_penalty > 0:
            pulse_p = eo(max(0.0, (t - T_RUGI) / 0.30)) * max(0.0, 1.0 - (t - T_RUGI) / 0.80) \
                      if t > T_RUGI else 0.0
            draw_outcome_box(d, P_BOX, "✗  PENALTY  (rugi)", RED, int(255*p_penalty), pulse_p)

        layer = card_fade(layer, t, dur)
        layer.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)

# ─────────────────────────────────────────── RESULT BADGE: Sharpe 2.0 · α 13%
def render_gfx_result_rl(slot, dur):
    """Pop-in result badges for AlphaPortfolio: Sharpe 2.0 and out-of-sample α 13%."""
    out_dir = os.path.join(ANIM, slot, "frames")
    os.makedirs(out_dir, exist_ok=True)
    x0, y0, x1, y1 = CARD
    n = int(round(dur * FPS))
    fhdr = font(30); fbig = font(66); fsub = font(24, False); flbl = font(22, False)

    for i in range(n):
        t = i / FPS
        layer = new_frame()
        d = ImageDraw.Draw(layer)
        rrect(d, (x0, y0, x1, y1), 24, fill=PANEL+(238,), outline=(40,54,80,255), width=2)
        d.text((x0+34, y0+22), "ALPHAPORTOLIO — OUT-OF-SAMPLE", font=fhdr, fill=WHITE)

        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2 + 10

        p1 = pop(t, 0.3, 0.5)
        if p1 > 0:
            a = int(255 * p1)
            bw, bh = 360, 130
            bx, by = cx - bw - 20, cy - bh // 2
            rrect(d, (bx, by, bx+bw, by+bh), 16, fill=(20,50,30,a), outline=(GREEN[0],GREEN[1],GREEN[2],a), width=3)
            lbl = "SHARPE RATIO"
            d.text((bx+bw//2-tw(d,lbl,flbl)//2, by+12), lbl, font=flbl, fill=(DIM[0],DIM[1],DIM[2],a))
            val = "2.0"
            d.text((bx+bw//2-tw(d,val,fbig)//2, by+38), val, font=fbig, fill=(GREEN[0],GREEN[1],GREEN[2],a))

        p2 = pop(t, 0.8, 0.5)
        if p2 > 0:
            a = int(255 * p2)
            bw, bh = 360, 130
            bx, by = cx + 20, cy - bh // 2
            rrect(d, (bx, by, bx+bw, by+bh), 16, fill=(20,50,30,a), outline=(GREEN[0],GREEN[1],GREEN[2],a), width=3)
            lbl = "OOS ALPHA"
            d.text((bx+bw//2-tw(d,lbl,flbl)//2, by+12), lbl, font=flbl, fill=(DIM[0],DIM[1],DIM[2],a))
            val = "13%"
            d.text((bx+bw//2-tw(d,val,fbig)//2, by+38), val, font=fbig, fill=(GREEN[0],GREEN[1],GREEN[2],a))

        p3 = pop(t, 1.4, 0.4)
        if p3 > 0:
            a = int(255 * p3)
            sub = "Cong, Tang, Wang & Zhang (2021)  •  AlphaPortfolio"
            d.text((cx-tw(d,sub,fsub)//2, y1-52), sub, font=fsub, fill=(DIM[0],DIM[1],DIM[2],a))

        layer = card_fade(layer, t, dur)
        layer.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)

# ─────────────────────────────────────────── ALPHA DECAY TABLE
def render_gfx_decay(slot, dur):
    """Table showing how gross alpha erodes to ~0 after real-world costs.

    Rows appear one-by-one so the viewer can follow the subtraction:
      GROSS ALPHA  →  − Fees  →  − Crowding  →  = ~0% edge
    """
    out_dir = os.path.join(ANIM, slot, "frames")
    os.makedirs(out_dir, exist_ok=True)
    x0, y0, x1, y1 = CARD
    n = int(round(dur * FPS))
    fhdr = font(28); fsub = font(20, False); flbl = font(24); fval = font(28)

    # Table geometry — left description col, right value col
    TBL_X0, TBL_X1 = x0 + 36, x1 - 36
    COL_SPLIT = TBL_X0 + 580          # divider between description and value
    ROW_H = 52
    ROW_Y0 = y0 + 108                 # first row top

    ROWS = [
        ("GROSS ALPHA  (backtest)",     "+HIGH",  GREEN),
        ("  −  Transaction Fees",       "−MED",   GOLD),
        ("  −  Crowding / Alpha Decay", "−HIGH",  RED),
        ("  =  Real Edge (live)",       "~ 0%",   RED),
    ]
    # Each row appears at these times
    ROW_T = [0.5, 1.5, 2.5, 3.5]

    for i in range(n):
        t = i / FPS
        layer = new_frame()
        d = ImageDraw.Draw(layer)
        rrect(d, (x0, y0, x1, y1), 24, fill=PANEL+(238,), outline=(40,54,80,255), width=2)
        d.text((x0+34, y0+22), "WHY EDGE VANISHES IN PRACTICE", font=fhdr, fill=WHITE)
        d.text((x0+34, y0+62), "backtest results vs. live trading reality", font=fsub, fill=DIM)

        # column header rule
        d.line((TBL_X0, ROW_Y0, TBL_X1, ROW_Y0), fill=(*DIM, 80), width=1)

        for ri, (desc, val, color) in enumerate(ROWS):
            p = pop(t, ROW_T[ri], 0.4)
            if p <= 0:
                continue
            a = int(255 * p)
            ry = ROW_Y0 + ri * ROW_H

            # subtle row tint for last row (= result)
            if ri == len(ROWS) - 1:
                rrect(d, (TBL_X0, ry + 2, TBL_X1, ry + ROW_H - 2), 6,
                      fill=(color[0]//6, color[1]//6, color[2]//6, a))

            # description text
            d.text((TBL_X0 + 8, ry + (ROW_H - th(d, desc, flbl))//2),
                   desc, font=flbl, fill=(*WHITE, a) if ri == 0 else (*color, a))

            # value text — right-aligned in value column
            vw = tw(d, val, fval)
            d.text((TBL_X1 - vw - 8, ry + (ROW_H - th(d, val, fval))//2),
                   val, font=fval, fill=(*color, a))

            # row separator
            d.line((TBL_X0, ry + ROW_H, TBL_X1, ry + ROW_H), fill=(*DIM, 40), width=1)

        # column divider
        total_rows = sum(1 for rt in ROW_T if t > rt)
        if total_rows > 0:
            div_bottom = ROW_Y0 + min(total_rows, len(ROWS)) * ROW_H
            d.line((COL_SPLIT, ROW_Y0, COL_SPLIT, div_bottom), fill=(*DIM, 50), width=1)

        layer = card_fade(layer, t, dur)
        layer.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)

# ══════════════════════════════════════════════════════════════════ MAIN
if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"

    # Citation panels — require source screenshots to exist first
    SRCS = [
        ("slot_src_hou2020",   f"{SRC}/hou2020.png",     "Hou, Xue & Zhang (2020), Review of Financial Studies  —  Replicating Anomalies", 5.0),
        ("slot_src_gu2020",    f"{SRC}/gu2020.png",      "Gu, Kelly & Xiu (2020), Review of Financial Studies  —  Empirical Asset Pricing via ML", 5.5),
        ("slot_src_alphaport", f"{SRC}/alphaport.png",   "Liu et al. (2020)  —  FinRL: Deep Reinforcement Learning Library for Automated Stock Trading", 4.5),
    ]

    if which in ("all", "pvz"):    render_ml_intro("slot_pvz_day4", 2.9)
    if which in ("all", "zoo"):    render_gfx_zoo("slot_gfx_zoo", 5.2)
    if which in ("all", "nn"):     render_gfx_nn("slot_gfx_nn", 6.0)
    if which in ("all", "rnn"):    render_gfx_result_nn("slot_gfx_result_nn", 4.2)
    if which in ("all", "rl"):     render_gfx_rl("slot_gfx_rl", 6.2)
    if which in ("all", "rrl"):    render_gfx_result_rl("slot_gfx_result_rl", 5.3)
    if which in ("all", "decay"):  render_gfx_decay("slot_gfx_decay", 8.0)
    if which in ("all", "src"):
        for slot, img, cap, dur in SRCS:
            if os.path.exists(img):
                render_src(slot, img, cap, dur)
            else:
                print(f"  SKIP {slot} — screenshot not found: {img}")

    print("DONE", which)
