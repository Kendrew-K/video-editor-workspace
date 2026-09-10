"""Build v5 overlays for Research reel 1.

Design change from v4: animation and source are NEVER shown in the same frame.
For each technique: the graph/animation plays first (lower band, face visible),
then it slides away and a FULL-BLEED screenshot of the source slides down from
the top to cover the shelf above the head (like Final Vids/Intro Video.mp4).

Slots produced:
  src_pead, src_analyst, src_merger, src_fda  -> full-bleed top source panels
  gfx_pead   -> climbing 60-day drift graph (re-timed to 4.1s)
  gfx_merger -> merger arbitrage boxes + equation (re-timed to 17.6s)
  gfx_fda    -> NEW: +20% pre-announcement rise with BUY/SELL markers (14.0s)

Outputs PNG frame sequences into each slot's frames/ dir; encode to ProRes 4444
.mov happens in the shell afterwards (alpha MUST be ProRes 4444 on this machine —
libvpx-vp9 silently drops alpha, see project.md).
"""
import os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Resolve fonts through the repo-root helper so these render off Windows too.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")))
from fonts import font_path

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
ANIM = os.path.join(HERE, "animations")
SRC = os.path.join(HERE, "sources")
ARIALBD = font_path("arialbd")
ARIAL = font_path("arial")

GREEN = (22, 199, 132)
GREEN_D = (10, 150, 98)
NAVY = (11, 31, 58)
PANEL = (12, 22, 40)
WHITE = (255, 255, 255)
DIM = (158, 168, 184)
RED = (235, 90, 95)
GOLD = (245, 196, 90)
CARD_BG = (251, 251, 253)

def font(sz, bold=True):
    return ImageFont.truetype(ARIALBD if bold else ARIAL, sz)

def eo(t):
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3
def eio(t):
    t = max(0.0, min(1.0, t))
    return 4*t**3 if t < 0.5 else 1 - (-2*t+2)**3/2
def lerp(a, b, p): return a + (b - a) * p

def text_w(d, s, f):
    b = d.textbbox((0,0), s, font=f); return b[2]-b[0]
def text_h(d, s, f):
    b = d.textbbox((0,0), s, font=f); return b[3]-b[1]

def rrect(draw, box, r, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

def note(slot, n): print(f"{slot}: {n} frames")

# ============================================================ FULL-BLEED SOURCE
SHOT_H = 700          # height of the screenshot strip
CAP_H = 56            # caption bar under it
PANEL_H = SHOT_H + CAP_H

def build_src_static(img_path, caption, masks=None):
    """Full-width (1080) source panel: top screenshot strip + citation bar.

    `masks` is a list of (x0,y0,x1,y1) boxes painted white to hide cookie/consent
    banners that some sites overlay in a corner.
    """
    shot = Image.open(img_path).convert("RGBA")
    sw = W
    sh = int(shot.height * sw / shot.width)
    shot = shot.resize((sw, sh), Image.LANCZOS)
    shot = shot.crop((0, 0, W, SHOT_H))   # top portion only
    if masks:
        md = ImageDraw.Draw(shot)
        for box in masks:
            md.rectangle(box, fill=(255, 255, 255, 255))

    panel = Image.new("RGBA", (W, PANEL_H), (0, 0, 0, 0))
    panel.paste(shot, (0, 0))
    d = ImageDraw.Draw(panel)
    # caption bar
    d.rectangle((0, SHOT_H, W, PANEL_H), fill=NAVY + (255,))
    d.rectangle((0, SHOT_H, 12, PANEL_H), fill=GREEN + (255,))   # accent
    fc = font(24, True)
    d.text((30, SHOT_H + (CAP_H - text_h(d, caption, fc)) // 2 - 4),
           caption, font=fc, fill=(225, 232, 242))
    # thin separators
    d.line((0, SHOT_H, W, SHOT_H), fill=(255, 255, 255, 60), width=2)
    return panel

def render_src(slot, img_path, caption, dur, masks=None):
    out_dir = os.path.join(ANIM, slot, "frames")
    os.makedirs(out_dir, exist_ok=True)
    panel = build_src_static(img_path, caption, masks)
    n = int(round(dur * FPS))
    y_hidden = -(PANEL_H + 50)
    y_shown = 0
    t_in, t_out = 0.5, 0.42
    # soft drop shadow baked under the panel bottom edge
    shadow = Image.new("RGBA", (W, 60), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rectangle((0, 0, W, 60), fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    for i in range(n):
        t = i / FPS
        if t < t_in:
            y = lerp(y_hidden, y_shown, eo(t / t_in))
        elif t > dur - t_out:
            y = lerp(y_hidden, y_shown, eo((dur - t) / t_out))
        else:
            y = y_shown
        cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        yy = int(round(y))
        cv.paste(shadow, (0, yy + PANEL_H - 20), shadow)
        cv.paste(panel, (0, yy), panel)
        cv.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)

# ============================================================ PEAD CLIMB GRAPH
def render_pead(slot, dur):
    out_dir = os.path.join(ANIM, slot, "frames")
    os.makedirs(out_dir, exist_ok=True)
    x0, y0, x1, y1 = 80, 120, 1000, 455   # v6: moved to TOP band (was 955-1290, over face)
    n = int(round(dur * FPS))
    ft = font(31, True); fs = font(24, False); fa = font(34, True)
    cx0, cx1 = x0+48, x1-150
    cyB, cyT = y1-46, y0+118
    N = 80
    pts = []
    for i in range(N+1):
        fx = i/N
        fy = fx**0.72
        wob = 0.02*math.sin(fx*22)
        yy = cyB - (cyB-cyT)*(fy+wob)
        pts.append((cx0 + (cx1-cx0)*fx, yy))
    t_in, t_out = 0.4, 0.4
    draw_t0, draw_t1 = 0.4, 2.0       # payoff lands ~2.0s (out ~5.9 = "sixty days")
    for i in range(n):
        t = i/FPS
        if t < t_in: ga = eo(t/t_in)
        elif t > dur - t_out: ga = eo((dur-t)/t_out)
        else: ga = 1.0
        layer = Image.new("RGBA", (W,H), (0,0,0,0))
        d = ImageDraw.Draw(layer)
        rrect(d, (x0,y0,x1,y1), 24, fill=PANEL+(238,), outline=(40,54,80,255), width=2)
        d.text((x0+34, y0+22), "HARGA NAIK  ~60 HARI", font=ft, fill=WHITE)
        d.text((x0+34, y0+62), "prices drift up after good news", font=fs, fill=DIM)
        d.line((cx0, cyT-6, cx0, cyB), fill=(90,104,128), width=2)
        d.line((cx0, cyB, cx1+8, cyB), fill=(90,104,128), width=2)
        for yy in range(int(cyT), int(cyB), 12):
            d.line((cx0+4, yy, cx0+4, yy+6), fill=(120,135,160), width=2)
        d.text((cx0+10, cyT-8), "NEWS", font=fs, fill=(150,165,190))
        p = eio((t-draw_t0)/(draw_t1-draw_t0)) if t>draw_t0 else 0.0
        if p > 0:
            ncut = max(1, int(p*N))
            seg = pts[:ncut+1]
            if len(seg) >= 2:
                d.line(seg, fill=GREEN, width=7, joint="curve")
            lead = seg[-1]
            d.ellipse((lead[0]-9, lead[1]-9, lead[0]+9, lead[1]+9), fill=GREEN, outline=WHITE, width=2)
        if p > 0.96:
            ex, ey = pts[-1]
            d.text((ex+14, ey-26), "↑", font=fa, fill=GREEN)
            d.text((cx1-30, cyB+8), "~60 hari drift", font=fs, fill=(150,165,190))
        if ga < 1.0:
            a = layer.split()[3].point(lambda v: int(v*ga))
            layer.putalpha(a)
        layer.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)

# ============================================================ MERGER GRAPH
def pop(t, t0, d=0.6):
    if t < t0: return 0.0
    return eo((t-t0)/d)

def render_merger(slot, dur):
    out_dir = os.path.join(ANIM, slot, "frames")
    os.makedirs(out_dir, exist_ok=True)
    x0, y0, x1, y1 = 80, 120, 1000, 455   # v6: moved to TOP band (was 955-1290, over face)
    n = int(round(dur*FPS))
    fhdr = font(30, True); fbox = font(30, True); fsub = font(23, False)
    fbig = font(66, True); fmid = font(34, True); fglow = font(74, True)
    t_in, t_out = 0.4, 0.4
    bw, bh = 332, 150
    ax, ay = x0+34, y0+96
    bx, by = x1-34-bw, y0+96
    cx_center = (x0+x1)//2
    for i in range(n):
        t = i/FPS
        if t < t_in: ga = eo(t/t_in)
        elif t > dur - t_out: ga = eo((dur-t)/t_out)
        else: ga = 1.0
        layer = Image.new("RGBA", (W,H), (0,0,0,0))
        d = ImageDraw.Draw(layer)
        rrect(d, (x0,y0,x1,y1), 24, fill=PANEL+(238,), outline=(40,54,80,255), width=2)
        d.text((x0+34, y0+22), "MERGER ARBITRAGE", font=fhdr, fill=WHITE)
        phase2 = t > 10.5
        grp_a = 1.0
        if phase2:
            grp_a = max(0.0, 1 - (t-10.5)/0.6)
        if grp_a > 0:
            pa = pop(t, 0.3)
            if pa > 0:
                aa = int(255*pa*grp_a)
                rrect(d, (ax, ay, ax+bw, ay+bh), 16, fill=(22,34,58,aa), outline=(70,120,200,aa), width=3)
                d.text((ax+bw//2 - text_w(d,"PERUSAHAAN A",fbox)//2, ay+bh//2-18), "PERUSAHAAN A", font=fbox, fill=(220,230,245,aa))
            pb = pop(t, 1.0)
            if pb > 0:
                ab = int(255*pb*grp_a)
                rrect(d, (bx, by, bx+bw, by+bh), 16, fill=(22,34,58,ab), outline=(70,120,200,ab), width=3)
                d.text((bx+bw//2 - text_w(d,"PERUSAHAAN B",fbox)//2, by+bh//2-18), "PERUSAHAAN B", font=fbox, fill=(220,230,245,ab))
            par = pop(t, 2.0, 1.0)
            if par > 0:
                ar_y = ay+bh//2
                axs = ax+bw+8; axe = bx-8
                cur = axs + (axe-axs)*par
                col = (GREEN[0],GREEN[1],GREEN[2], int(255*grp_a))
                d.line((axs, ar_y, cur, ar_y), fill=col, width=6)
                if par > 0.5:
                    d.polygon([(axe, ar_y),(axe-22, ar_y-13),(axe-22, ar_y+13)], fill=col)
                if par > 0.4:
                    lab="AKUISISI"; d.text(((axs+axe)//2 - text_w(d,lab,fsub)//2, ar_y-40), lab, font=fsub, fill=(GREEN[0],GREEN[1],GREEN[2],int(255*grp_a)))
            pt = pop(t, 7.0, 0.5)
            if pt > 0:
                tag = "$30 / lembar"
                tw = text_w(d, tag, fmid)
                tgw, tgh = tw+34, 56
                tgx = bx+bw//2 - tgw//2
                tgy = by - 34
                at = int(255*pt*grp_a)
                rrect(d, (tgx, tgy, tgx+tgw, tgy+tgh), 12, fill=(255,255,255,at), outline=(GREEN[0],GREEN[1],GREEN[2],at), width=3)
                d.text((tgx+17, tgy+11), tag, font=fmid, fill=(NAVY[0],NAVY[1],NAVY[2],at))
                d.text((bx+bw//2 - text_w(d,"harga deal",fsub)//2, by+bh+6), "harga deal", font=fsub, fill=(150,165,190,int(255*grp_a)))
        if phase2:
            ey = y0+150
            def el(txt, tx, t_app, color, big=fbig):
                p = pop(t, t_app, 0.45)
                if p<=0: return
                a=int(255*p)
                d.text((tx, ey - text_h(d,txt,big)//2), txt, font=big, fill=(color[0],color[1],color[2],a))
            s30, sminus, s28, seq, s2 = "$30","−","$28","=","$2"
            g=26
            w30=text_w(d,s30,fbig); wm=text_w(d,sminus,fbig); w28=text_w(d,s28,fbig)
            we=text_w(d,seq,fbig); w2=text_w(d,s2,fglow)
            tot=w30+wm+w28+we+w2+4*g
            sx=cx_center-tot//2
            x=sx
            el(s30,x,11.0,WHITE)
            d.text((x, ey+44), "harga deal", font=fsub, fill=(150,165,190,int(255*pop(t,11.0)))); x+=w30+g
            el(sminus,x,12.3,DIM); x+=wm+g
            el(s28,x,12.6,(255,210,120))
            d.text((x, ey+44), "lo beli skrg", font=fsub, fill=(150,165,190,int(255*pop(t,12.6)))); x+=w28+g
            el(seq,x,14.2,DIM); x+=we+g
            p2=pop(t,15.8,0.5)
            if p2>0:
                a=int(255*p2)
                gl=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(gl)
                gd.text((x, ey - text_h(gd,s2,fglow)//2), s2, font=fglow, fill=(GREEN[0],GREEN[1],GREEN[2],a))
                gl=gl.filter(ImageFilter.GaussianBlur(12))
                layer=Image.alpha_composite(layer,gl)
                d=ImageDraw.Draw(layer)
                d.text((x, ey - text_h(d,s2,fglow)//2), s2, font=fglow, fill=(GREEN[0],GREEN[1],GREEN[2],a))
                d.text((x-6, ey+48), "PROFIT/lembar", font=fsub, fill=(GREEN[0],GREEN[1],GREEN[2],a))
        if ga < 1.0:
            aa = layer.split()[3].point(lambda v: int(v*ga))
            layer.putalpha(aa)
        layer.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)

# ============================================================ FDA +20% / BUY-SELL
def render_fda(slot, dur):
    out_dir = os.path.join(ANIM, slot, "frames")
    os.makedirs(out_dir, exist_ok=True)
    x0, y0, x1, y1 = 80, 120, 1000, 455   # v6: moved to TOP band (was 955-1290, over face)
    n = int(round(dur*FPS))
    ft = font(30, True); fs = font(22, False); ftag = font(27, True); fmk = font(25, True)
    cx0, cx1 = x0+58, x1-70
    cyB, cyT = y1-58, y0+120
    WEEKS = 12.0
    ann_w = 12.0       # announcement at week 12
    def X(wk): return cx0 + (cx1-cx0) * (wk/WEEKS)
    # price path normalized 1.0 -> 1.20 (rise mostly weeks 4..8), plateau 8..12
    def price(wk):
        if wk <= 4:   base = 1.0 + 0.02*(wk/4)
        elif wk <= 8: base = 1.02 + 0.18*((wk-4)/4)
        else:         base = 1.20 + 0.01*((wk-8)/4)
        return base
    pmin, pmax = 0.98, 1.23
    def Y(p): return cyB - (cyB-cyT) * ((p-pmin)/(pmax-pmin))
    N = 96
    pts = [(X(WEEKS*i/N), Y(price(WEEKS*i/N))) for i in range(N+1)]
    buy_pt = (X(0.0), Y(price(0.0)))
    sell_pt = (X(8.0), Y(price(8.0)))
    t_in, t_out = 0.4, 0.4
    draw_t0, draw_t1 = 0.5, 5.0     # rise drawn during FDA_B ("20%, 4-8 minggu")
    buy_t = 8.49                    # out 64.49 = "beli"
    sell_t = 11.35                  # out 67.35 = "jual"
    pct_t = 5.2                     # "+20%" bracket after rise drawn (out ~61)
    for i in range(n):
        t = i/FPS
        if t < t_in: ga = eo(t/t_in)
        elif t > dur - t_out: ga = eo((dur-t)/t_out)
        else: ga = 1.0
        layer = Image.new("RGBA", (W,H), (0,0,0,0))
        d = ImageDraw.Draw(layer)
        rrect(d, (x0,y0,x1,y1), 24, fill=PANEL+(238,), outline=(40,54,80,255), width=2)
        d.text((x0+34, y0+22), "NAIK ~20% SEBELUM PENGUMUMAN", font=ft, fill=WHITE)
        d.text((x0+34, y0+60), "biotech: harga naik 4-8 minggu sblm FDA", font=fs, fill=DIM)
        # axes
        d.line((cx0, cyT-6, cx0, cyB), fill=(90,104,128), width=2)
        d.line((cx0, cyB, cx1+8, cyB), fill=(90,104,128), width=2)
        # week ticks (skip the last so it doesn't collide with the "minggu" label)
        for wk in range(0, 11, 2):
            xx = X(wk)
            d.line((xx, cyB, xx, cyB+7), fill=(90,104,128), width=2)
            d.text((xx-8, cyB+10), f"{wk}", font=fs, fill=(120,135,160))
        d.text((cx1-58, cyB+10), "minggu", font=fs, fill=(120,135,160))
        # announcement marker (dashed vertical) — always visible faintly
        axx = X(ann_w)
        for yy in range(int(cyT), int(cyB), 14):
            d.line((axx, yy, axx, yy+8), fill=(150,120,120), width=2)
        plab = "PENGUMUMAN"
        d.text((axx-text_w(d,plab,fs)-12, cyT-36), plab, font=fs, fill=(210,150,150))
        # animated rising line
        p = eio((t-draw_t0)/(draw_t1-draw_t0)) if t>draw_t0 else 0.0
        if p > 0:
            ncut = max(1, int(p*N))
            seg = pts[:ncut+1]
            if len(seg) >= 2:
                d.line(seg, fill=GREEN, width=7, joint="curve")
            lead = seg[-1]
            d.ellipse((lead[0]-8, lead[1]-8, lead[0]+8, lead[1]+8), fill=GREEN, outline=WHITE, width=2)
        # +20% bracket between buy level and sell level
        if t > pct_t:
            pa = int(255*pop(t, pct_t, 0.4))
            bx = sell_pt[0] + 22
            d.line((bx, buy_pt[1], bx, sell_pt[1]), fill=(GREEN[0],GREEN[1],GREEN[2],pa), width=3)
            d.line((bx-8, buy_pt[1], bx+8, buy_pt[1]), fill=(GREEN[0],GREEN[1],GREEN[2],pa), width=3)
            d.line((bx-8, sell_pt[1], bx+8, sell_pt[1]), fill=(GREEN[0],GREEN[1],GREEN[2],pa), width=3)
            d.text((bx+12, (buy_pt[1]+sell_pt[1])//2-16), "+20%", font=ftag, fill=(GREEN[0],GREEN[1],GREEN[2],pa))
        # BUY marker (week 0)
        if t > buy_t:
            a = int(255*pop(t, buy_t, 0.4))
            sc = 1.0 + 0.3*(1-eo(min(1.0,(t-buy_t)/0.5)))
            r = int(11*sc)
            d.ellipse((buy_pt[0]-r, buy_pt[1]-r, buy_pt[0]+r, buy_pt[1]+r), fill=(GREEN[0],GREEN[1],GREEN[2],a), outline=(255,255,255,a), width=3)
            lab = "BELI"
            lw = text_w(d, lab, fmk)
            lx = buy_pt[0]-lw//2; ly = buy_pt[1]+20
            rrect(d, (lx-12, ly-4, lx+lw+12, ly+34), 8, fill=(GREEN_D[0],GREEN_D[1],GREEN_D[2],a))
            d.text((lx, ly), lab, font=fmk, fill=(255,255,255,a))
        # SELL marker (week 8)
        if t > sell_t:
            a = int(255*pop(t, sell_t, 0.4))
            sc = 1.0 + 0.3*(1-eo(min(1.0,(t-sell_t)/0.5)))
            r = int(11*sc)
            d.ellipse((sell_pt[0]-r, sell_pt[1]-r, sell_pt[0]+r, sell_pt[1]+r), fill=(GOLD[0],GOLD[1],GOLD[2],a), outline=(255,255,255,a), width=3)
            lab = "JUAL"
            lw = text_w(d, lab, fmk)
            lx = sell_pt[0]-lw//2; ly = sell_pt[1]-46
            rrect(d, (lx-12, ly-4, lx+lw+12, ly+34), 8, fill=(180,140,40,a))
            d.text((lx, ly), lab, font=fmk, fill=(255,255,255,a))
        if ga < 1.0:
            aa = layer.split()[3].point(lambda v: int(v*ga))
            layer.putalpha(aa)
        layer.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)

# ============================================================ PvZ "DAY 2" SIGN
# Plants vs. Zombies themed wooden lawn sign that drops in over the head during
# the intro ("Welcome everyone to day two..."). Lands on the word "day" (~1.0s
# into the overlay window) with an overshoot bounce, then a gentle hanging sway.
def _fit_font(path, text, max_w, start=170):
    sz = start
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    while sz > 40:
        f = ImageFont.truetype(path, sz)
        if text_w(tmp, text, f) <= max_w:
            return f, sz
        sz -= 4
    return ImageFont.truetype(path, sz), sz

def _ease_out_back(t, s=1.9):
    t = max(0.0, min(1.0, t)); t -= 1
    return 1 + (s + 1) * t**3 + s * t**2

def _sunflower(d, cx, cy, r):
    pet = (252, 200, 64); pet_e = (224, 158, 32); ctr = (120, 74, 30); ctr_e = (86, 50, 18)
    for k in range(12):
        a = math.radians(k * 30)
        px, py = cx + math.cos(a) * r, cy + math.sin(a) * r
        pr = r * 0.46
        d.ellipse((px - pr, py - pr, px + pr, py + pr), fill=pet, outline=pet_e, width=3)
    d.ellipse((cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62), fill=ctr, outline=ctr_e, width=4)
    # seeds
    for k in range(8):
        a = math.radians(k * 45)
        sx, sy = cx + math.cos(a) * r * 0.32, cy + math.sin(a) * r * 0.32
        d.ellipse((sx - 4, sy - 4, sx + 4, sy + 4), fill=ctr_e)

def _leaf(d, cx, cy, w, h, ang=0):
    lf = (96, 176, 74); lf_e = (52, 120, 48)
    box = (cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2)
    d.ellipse(box, fill=lf, outline=lf_e, width=4)
    d.line((cx - w // 2 + 8, cy, cx + w // 2 - 8, cy), fill=lf_e, width=3)

def _build_sign():
    SW, SH = 760, 660
    s = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    WOOD_L = (172, 118, 70); WOOD_M = (146, 96, 54); WOOD_D = (104, 66, 36)
    EDGE = (66, 40, 20); POST = (124, 80, 44); POST_D = (88, 54, 28)
    cx = SW // 2
    # ---- posts (behind board)
    for px in (cx - 168, cx + 168):
        d.rounded_rectangle((px - 26, 40, px + 26, 360), radius=18, fill=POST, outline=EDGE, width=5)
        d.line((px, 60, px, 350), fill=POST_D, width=4)
        d.ellipse((px - 10, 90, px + 10, 110), fill=POST_D)   # nail
    # ---- board
    bx0, by0, bx1, by1 = 36, 250, SW - 36, 512
    d.rounded_rectangle((bx0 + 6, by0 + 10, bx1 + 6, by1 + 14), radius=26, fill=(0, 0, 0, 90))  # shadow
    d.rounded_rectangle((bx0, by0, bx1, by1), radius=26, fill=WOOD_M, outline=EDGE, width=8)
    # plank grain
    for gy in range(by0 + 26, by1 - 10, 30):
        d.line((bx0 + 14, gy, bx1 - 14, gy), fill=(WOOD_D[0], WOOD_D[1], WOOD_D[2], 90), width=2)
    d.line((bx0 + 10, by0 + 14, bx1 - 10, by0 + 14), fill=(WOOD_L[0], WOOD_L[1], WOOD_L[2], 200), width=4)  # top hilite
    # bolts
    for bxp in (bx0 + 30, bx1 - 30):
        for byp in (by0 + 28, by1 - 28):
            d.ellipse((bxp - 9, byp - 9, bxp + 9, byp + 9), fill=(212, 198, 170), outline=EDGE, width=3)
    # ---- text "DAY 2" — cartoon lawn-green with thick dark outline
    txt = "DAY 2"
    f, _sz = _fit_font(ARIALBD, txt, (bx1 - bx0) - 120, start=190)
    tw = text_w(d, txt, f); th = text_h(d, txt, f)
    tx = cx - tw // 2; ty = (by0 + by1) // 2 - th // 2 - 8
    OUT = (38, 84, 28); GRN = (128, 202, 74); HI = (196, 240, 150)
    for ox in range(-7, 8, 2):
        for oy in range(-7, 8, 2):
            d.text((tx + ox, ty + oy), txt, font=f, fill=OUT)
    d.text((tx, ty - 4), txt, font=f, fill=HI)   # highlight pop
    d.text((tx, ty), txt, font=f, fill=GRN)
    # ---- PvZ accents
    _sunflower(d, bx0 + 6, by0 + 4, 44)
    _leaf(d, bx1 - 6, by1 - 2, 96, 60)
    _leaf(d, bx1 - 44, by1 + 6, 70, 44)
    return s, (cx, (by0 + by1) // 2)

def render_pvz(slot, dur):
    out_dir = os.path.join(ANIM, slot, "frames")
    os.makedirs(out_dir, exist_ok=True)
    sign, (scx, scy) = _build_sign()
    SW, SH = sign.size
    n = int(round(dur * FPS))
    # board center should land near canvas y = 360 (upper, above the head)
    land_x = W // 2 - scx
    land_y = 300 - scy
    start_y = -SH - 40                  # fully above the frame
    t_drop = 1.0                        # lands on "day" (overlay starts at out 0.4)
    for i in range(n):
        t = i / FPS
        if t < t_drop:
            p = _ease_out_back(t / t_drop)
            y = lerp(start_y, land_y, p)
            ang = 0.0
        else:
            y = land_y
            # damped pendulum sway after landing
            te = t - t_drop
            ang = 5.0 * math.exp(-1.6 * te) * math.sin(te * 6.5)
        frame = sign
        if abs(ang) > 0.05:
            frame = sign.rotate(ang, resample=Image.BICUBIC, expand=True)
        fw, fh = frame.size
        ox = land_x - (fw - SW) // 2
        oy = int(round(y)) - (fh - SH) // 2
        cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cv.paste(frame, (ox, oy), frame)
        cv.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)

# ==================================================================== MAIN
if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    srcs = [
        # v6: PEAD + Merger now point at single-paper IDEAS pages (was Semantic Scholar
        # search-results lists). IDEAS pages have no cookie banner -> masks=None.
        ("slot_src_pead",    f"{SRC}/1d_pead_ideas.png",  "Bernard & Thomas (1989), Journal of Accounting Research", 4.9, None),
        ("slot_src_analyst", f"{SRC}/2_analyst_womack.png",   "Womack (1996), Journal of Finance  -  504 sitasi", 12.1, None),
        ("slot_src_merger",  f"{SRC}/3f_merger_ideas.png","Mitchell & Pulvino (2001), Journal of Finance", 3.1, None),
        ("slot_src_fda",     f"{SRC}/4c_fda_gov2.png",        "U.S. Food & Drug Administration  -  PDUFA  -  fda.gov", 8.9, None),
    ]
    if which in ("all", "src"):
        for slot, img, cap, dur, masks in srcs:
            render_src(slot, img, cap, dur, masks)
    if which in ("all", "pead"):
        render_pead("slot_gfx_pead", 4.1)
    if which in ("all", "merger"):
        render_merger("slot_gfx_merger", 17.6)
    if which in ("all", "fda"):
        render_fda("slot_gfx_fda", 14.0)
    if which in ("all", "pvz"):
        render_pvz("slot_pvz_day2", 2.9)
    print("DONE", which)
