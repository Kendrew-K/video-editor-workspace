"""Build overlays for Research reel 2 (Day 3 — Alternative Data).

Top-band design system inherited from Reel 1 (build_overlays_v6.py):
  - graph cards live in the box x0,y0,x1,y1 = 80,120,1000,455 (top band)
  - full-bleed citation panels = top 700px screenshot + navy caption bar
  - intro sign drops in, lands on the spoken episode number

Slots:
  spy_day3        -> satellite/spy HUD "DAY 3" sign (lands on "three")
  gfx_satellite   -> parking-lot fill + 67,120-store counter
  src_satellite   -> Katona/Painter/Patatoukas/Zeng citation panel (eScholarship)
  gfx_webscrape   -> 3 scraped-data counters feeding a growth signal
  gfx_gtrends     -> search-volume spike for 'utang' -> market-move signal
  src_gtrends     -> Preis/Moat/Stanley (2013) Nature citation panel

PNG frame sequences -> each slot's frames/; encode to ProRes 4444 in the shell
(alpha MUST be ProRes 4444 on this machine — libvpx-vp9 silently drops alpha).
"""
import os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
ANIM = os.path.join(HERE, "animations")
SRC = os.path.join(HERE, "sources")
ARIALBD = "C:/Windows/Fonts/arialbd.ttf"
ARIAL = "C:/Windows/Fonts/arial.ttf"

GREEN = (22, 199, 132)
GREEN_D = (10, 150, 98)
HUDG = (46, 232, 150)
NAVY = (11, 31, 58)
PANEL = (12, 22, 40)
WHITE = (255, 255, 255)
DIM = (158, 168, 184)
RED = (235, 90, 95)
GOLD = (245, 196, 90)

def font(sz, bold=True):
    return ImageFont.truetype(ARIALBD if bold else ARIAL, sz)

def eo(t):
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3
def eio(t):
    t = max(0.0, min(1.0, t))
    return 4*t**3 if t < 0.5 else 1 - (-2*t+2)**3/2
def lerp(a, b, p): return a + (b - a) * p
def pop(t, t0, d=0.6):
    if t < t0: return 0.0
    return eo((t-t0)/d)

def text_w(d, s, f):
    b = d.textbbox((0,0), s, font=f); return b[2]-b[0]
def text_h(d, s, f):
    b = d.textbbox((0,0), s, font=f); return b[3]-b[1]
def rrect(draw, box, r, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)
def note(slot, n): print(f"{slot}: {n} frames")

CARD = (80, 120, 1000, 455)   # top-band graph box

def card_bg(d):
    rrect(d, CARD, 24, fill=PANEL+(238,), outline=(40,54,80,255), width=2)

def fade_alpha(layer, ga):
    if ga < 1.0:
        a = layer.split()[3].point(lambda v: int(v*ga))
        layer.putalpha(a)
    return layer

# ============================================================ FULL-BLEED SOURCE
SHOT_H = 700
CAP_H = 56
PANEL_H = SHOT_H + CAP_H

def build_src_static(img_path, caption, crop_y=0, masks=None):
    shot = Image.open(img_path).convert("RGBA")
    sw = W
    sh = int(shot.height * sw / shot.width)
    shot = shot.resize((sw, sh), Image.LANCZOS)
    shot = shot.crop((0, crop_y, W, crop_y + SHOT_H))
    if masks:
        md = ImageDraw.Draw(shot)
        for box in masks:
            md.rectangle(box, fill=(255, 255, 255, 255))
    panel = Image.new("RGBA", (W, PANEL_H), (0, 0, 0, 0))
    panel.paste(shot, (0, 0))
    d = ImageDraw.Draw(panel)
    d.rectangle((0, SHOT_H, W, PANEL_H), fill=NAVY + (255,))
    d.rectangle((0, SHOT_H, 12, PANEL_H), fill=GREEN + (255,))
    fc = font(24, True)
    d.text((30, SHOT_H + (CAP_H - text_h(d, caption, fc)) // 2 - 4),
           caption, font=fc, fill=(225, 232, 242))
    d.line((0, SHOT_H, W, SHOT_H), fill=(255, 255, 255, 60), width=2)
    return panel

def render_src(slot, img_path, caption, dur, crop_y=0, masks=None):
    out_dir = os.path.join(ANIM, slot, "frames")
    os.makedirs(out_dir, exist_ok=True)
    panel = build_src_static(img_path, caption, crop_y, masks)
    n = int(round(dur * FPS))
    y_hidden = -(PANEL_H + 50); y_shown = 0
    t_in, t_out = 0.5, 0.42
    shadow = Image.new("RGBA", (W, 60), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow); sd.rectangle((0, 0, W, 60), fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    for i in range(n):
        t = i / FPS
        if t < t_in:           y = lerp(y_hidden, y_shown, eo(t / t_in))
        elif t > dur - t_out:  y = lerp(y_hidden, y_shown, eo((dur - t) / t_out))
        else:                  y = y_shown
        cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        yy = int(round(y))
        cv.paste(shadow, (0, yy + PANEL_H - 20), shadow)
        cv.paste(panel, (0, yy), panel)
        cv.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)

# ============================================================ SATELLITE GRAPH
def render_satellite(slot, dur):
    out_dir = os.path.join(ANIM, slot, "frames"); os.makedirs(out_dir, exist_ok=True)
    x0, y0, x1, y1 = CARD
    n = int(round(dur*FPS))
    ft = font(30, True); fs = font(22, False); fnum = font(58, True); flab = font(23, False); fbadge = font(26, True)
    # parking lot grid (left)
    gx0, gy0 = x0+40, y0+112
    cols, rows = 8, 4
    cw, ch, gap = 38, 30, 8
    slots = [(gx0 + c*(cw+gap), gy0 + r*(ch+gap)) for r in range(rows) for c in range(cols)]
    total = len(slots)
    # fill order: pseudo-random but deterministic
    order = sorted(range(total), key=lambda k: (k*37) % total)
    t0, t1 = 0.8, 4.0
    badge_t = 4.2
    for i in range(n):
        t = i/FPS
        ga = eo(t/0.4) if t < 0.4 else (eo((dur-t)/0.4) if t > dur-0.4 else 1.0)
        layer = Image.new("RGBA", (W,H), (0,0,0,0)); d = ImageDraw.Draw(layer)
        card_bg(d)
        d.text((x0+34, y0+20), "SATELIT PANTAU PARKIRAN", font=ft, fill=WHITE)
        d.text((x0+34, y0+58), "lacak keramaian toko dari luar angkasa", font=fs, fill=DIM)
        # lot outline
        d.rounded_rectangle((gx0-12, gy0-12, gx0+cols*(cw+gap)-gap+12, gy0+rows*(ch+gap)-gap+12),
                            radius=10, outline=(90,104,128), width=2)
        p = eio((t-t0)/(t1-t0)) if t > t0 else 0.0
        nfill = int(round(p*total))
        fillset = set(order[:nfill])
        for k,(sx,sy) in enumerate(slots):
            if k in fillset:
                d.rounded_rectangle((sx, sy, sx+cw, sy+ch), radius=5, fill=GREEN, outline=GREEN_D, width=1)
            else:
                d.rounded_rectangle((sx, sy, sx+cw, sy+ch), radius=5, outline=(60,74,100), width=2)
        # store counter (right)
        rx = x0+560
        cnt = int(round(p*67120))
        d.text((rx, y0+96), f"{cnt:,}", font=fnum, fill=GREEN)
        d.text((rx+4, y0+162), "toko dipantau", font=flab, fill=DIM)
        # NOTE: +10% AKURASI badge moved out of this slot -> render_akurasi (lands on
        # the spoken "sepuluh persen" payoff at ~out 37.55s, not on the 67k-stores line).
        fade_alpha(layer, ga)
        layer.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)

# ============================================================ WEB SCRAPING GRAPH
def render_webscrape(slot, dur):
    out_dir = os.path.join(ANIM, slot, "frames"); os.makedirs(out_dir, exist_ok=True)
    x0, y0, x1, y1 = CARD
    n = int(round(dur*FPS))
    ft = font(30, True); fs = font(22, False); fr = font(26, True); fnum = font(28, True); ftag = font(25, True)
    rows = [
        ("LOWONGAN KERJA", 1_240_000, 0.6),
        ("HARGA PRODUK",     845_000, 1.0),
        ("DOWNLOADS",      3_410_000, 1.4),
    ]
    ry0 = y0+104; rgap = 70
    barx0 = x0+470; barw = 300
    tag_t = dur - 2.6
    for i in range(n):
        t = i/FPS
        ga = eo(t/0.4) if t < 0.4 else (eo((dur-t)/0.4) if t > dur-0.4 else 1.0)
        layer = Image.new("RGBA", (W,H), (0,0,0,0)); d = ImageDraw.Draw(layer)
        card_bg(d)
        d.text((x0+34, y0+20), "WEB SCRAPING", font=ft, fill=WHITE)
        d.text((x0+34, y0+58), "mengeruk jutaan halaman web jadi data", font=fs, fill=DIM)
        for idx,(lab, target, t_app) in enumerate(rows):
            ry = ry0 + idx*rgap
            p = eio(min(1.0, (t-t_app)/3.4)) if t > t_app else 0.0
            d.text((x0+40, ry), lab, font=fr, fill=(210,222,238))
            # bar track + fill
            d.rounded_rectangle((barx0, ry+2, barx0+barw, ry+26), radius=8, fill=(28,40,62,255))
            if p > 0:
                d.rounded_rectangle((barx0, ry+2, barx0+int(barw*p), ry+26), radius=8, fill=GREEN)
            cnt = int(round(p*target))
            d.text((barx0+barw+18, ry), f"{cnt:,}", font=fnum, fill=GREEN)
        # growth signal tag
        if t > tag_t:
            a = int(255*pop(t, tag_t, 0.4))
            txt = "→ SINYAL PERTUMBUHAN"
            tw = text_w(d, txt, ftag)
            tx = (x0+x1)//2 - tw//2
            d.text((tx, y1-46), txt, font=ftag, fill=(GREEN[0],GREEN[1],GREEN[2],a))
        fade_alpha(layer, ga)
        layer.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)

# ============================================================ GOOGLE TRENDS GRAPH
def render_gtrends(slot, dur):
    out_dir = os.path.join(ANIM, slot, "frames"); os.makedirs(out_dir, exist_ok=True)
    x0, y0, x1, y1 = CARD
    n = int(round(dur*FPS))
    ft = font(30, True); fs = font(22, False); fmk = font(23, True)
    cx0, cx1 = x0+50, x1-44
    cyB, cyT = y1-44, y0+112
    # search-volume curve: low noise, sharp spike at ~0.80, slight relax
    N = 100
    def vol(fx):
        base = 0.12 + 0.06*math.sin(fx*23) + 0.05*math.sin(fx*7+1)
        spike = 0.0
        if fx > 0.62:
            s = (fx-0.62)/0.18
            spike = 0.92*math.exp(-((s-1.0)**2)*3.2) if s < 1.2 else 0.92*math.exp(-((fx-0.80)/0.10)**2)
        return max(0.04, min(1.0, base*0.5 + spike))
    pts = []
    for k in range(N+1):
        fx = k/N
        xx = cx0 + (cx1-cx0)*fx
        yy = cyB - (cyB-cyT)*vol(fx)
        pts.append((xx, yy))
    spike_idx = max(range(N+1), key=lambda k: -pts[k][1])  # highest point (min y)
    spike_pt = pts[spike_idx]
    t0, t1 = 0.7, dur-2.2     # draw spans most of the card life; spike lands late
    mark_t = (t0 + (t1-t0)*(spike_idx/N))
    for i in range(n):
        t = i/FPS
        ga = eo(t/0.4) if t < 0.4 else (eo((dur-t)/0.4) if t > dur-0.4 else 1.0)
        layer = Image.new("RGBA", (W,H), (0,0,0,0)); d = ImageDraw.Draw(layer)
        card_bg(d)
        d.text((x0+34, y0+20), "GOOGLE TRENDS:  ‘UTANG’ / ‘TARIF’", font=ft, fill=WHITE)
        d.text((x0+34, y0+58), "lonjakan pencarian mendahului gerakan pasar", font=fs, fill=DIM)
        # axes
        d.line((cx0, cyT-6, cx0, cyB), fill=(90,104,128), width=2)
        d.line((cx0, cyB, cx1+6, cyB), fill=(90,104,128), width=2)
        p = eio((t-t0)/(t1-t0)) if t > t0 else 0.0
        ncut = max(1, int(p*N))
        seg = pts[:ncut+1]
        if len(seg) >= 2:
            # filled area under the curve
            poly = seg + [(seg[-1][0], cyB), (cx0, cyB)]
            d.polygon(poly, fill=(GREEN[0],GREEN[1],GREEN[2],60))
            d.line(seg, fill=GREEN, width=6, joint="curve")
        lead = seg[-1]
        d.ellipse((lead[0]-7, lead[1]-7, lead[0]+7, lead[1]+7), fill=GREEN, outline=WHITE, width=2)
        # spike marker + label once the draw passes the spike
        if t > mark_t:
            a = int(255*pop(t, mark_t, 0.4))
            sx, sy = spike_pt
            for yy in range(int(cyT), int(cyB), 12):
                d.line((sx, yy, sx, yy+7), fill=(GOLD[0],GOLD[1],GOLD[2],int(a*0.8)), width=2)
            lab = "lonjakan pencarian"
            d.text((sx - text_w(d,lab,fmk) - 12, cyT-6), lab, font=fmk, fill=(GOLD[0],GOLD[1],GOLD[2],a))
            # market-move arrow to the right of the spike
            mx = sx + 40
            d.text((mx, cyB-54), "→ gerakan pasar", font=fmk, fill=(RED[0],RED[1],RED[2],a))
        fade_alpha(layer, ga)
        layer.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)

# ============================================================ SPY / SAT-HUD "DAY 3"
def _ease_out_back(t, s=1.7):
    t = max(0.0, min(1.0, t)); t -= 1
    return 1 + (s + 1) * t**3 + s * t**2

def render_spy(slot, dur):
    """Satellite/spy HUD that frames the subject and locks on, landing 'DAY 3'
    + a TARGET LOCKED stamp on the spoken word 'three' (~overlay-local 1.0s)."""
    out_dir = os.path.join(ANIM, slot, "frames"); os.makedirs(out_dir, exist_ok=True)
    n = int(round(dur*FPS))
    fbig = font(150, True); fsub = font(30, True); ftag = font(34, True); fmono = font(26, True)
    # reticle target box framing the upper body (face sits ~y740-1450 after reframe)
    bx0, by0, bx1, by1 = 250, 560, 830, 1140
    cx, cy = (bx0+bx1)//2, (by0+by1)//2
    t_lock = 1.0
    for i in range(n):
        t = i/FPS
        ga = eo(t/0.3) if t < 0.3 else (eo((dur-t)/0.4) if t > dur-0.4 else 1.0)
        layer = Image.new("RGBA", (W,H), (0,0,0,0)); d = ImageDraw.Draw(layer)
        # converging corner brackets (wide -> locked)
        conv = eo(min(1.0, t/t_lock))
        spread = lerp(150, 0, conv)
        L = 70
        col = HUDG + (235,)
        for (ox, oy, dx, dy) in [(bx0,by0,1,1),(bx1,by0,-1,1),(bx0,by1,1,-1),(bx1,by1,-1,-1)]:
            px = ox - dx*spread; py = oy - dy*spread
            d.line((px, py, px+dx*L, py), fill=col, width=5)
            d.line((px, py, px, py+dy*L), fill=col, width=5)
        # crosshair center
        d.line((cx-26, cy, cx+26, cy), fill=HUDG+(180,), width=3)
        d.line((cx, cy-26, cx, cy+26), fill=HUDG+(180,), width=3)
        d.ellipse((cx-46, cy-46, cx+46, cy+46), outline=HUDG+(150,), width=2)
        # sweeping scanline (loops)
        sweep = (t*0.65) % 1.0
        sy = int(lerp(by0, by1, sweep))
        d.line((bx0, sy, bx1, sy), fill=HUDG+(90,), width=3)
        # top HUD label band
        d.text((bx0, by0-150), "▸ SAT-LINK ESTABLISHED", font=fsub, fill=HUDG+(230,))
        # REC blinker + timecode (top right of reticle)
        if int(t*2) % 2 == 0:
            d.ellipse((bx1-150, by0-150, bx1-128, by0-128), fill=RED+(255,))
        d.text((bx1-118, by0-150), "REC", font=fmono, fill=(235,235,235,230))
        d.text((bx0, by1+18), f"LAT -6.21  LON 106.84   ALT 705km", font=fmono, fill=HUDG+(170,))
        # DAY 3 title (top band)
        txt = "DAY 3"
        tw = text_w(d, txt, fbig)
        tx = W//2 - tw//2; ty = 150
        for ox in range(-4,5,2):
            for oy in range(-4,5,2):
                d.text((tx+ox, ty+oy), txt, font=fbig, fill=(8,30,20,200))
        d.text((tx, ty), txt, font=fbig, fill=HUDG)
        # TARGET LOCKED stamp pops on lock
        if t > t_lock:
            a = int(255*pop(t, t_lock, 0.35))
            sc = 1.0 + 0.18*(1-eo(min(1.0,(t-t_lock)/0.4)))
            stamp = "● TARGET LOCKED"
            sw = text_w(d, stamp, ftag)
            sxp = cx - sw//2
            syp = by1 - 64
            rrect(d, (sxp-18, syp-8, sxp+sw+18, syp+44), 8, fill=(8,30,20,int(a*0.85)),
                  outline=(HUDG[0],HUDG[1],HUDG[2],a), width=3)
            d.text((sxp, syp), stamp, font=ftag, fill=(HUDG[0],HUDG[1],HUDG[2],a))
        fade_alpha(layer, ga)
        layer.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)

# ============================================================ +10% AKURASI BADGE
def render_akurasi(slot, dur):
    """Standalone hero badge. Pops on the spoken 'sepuluh persen' payoff.
    Overlay window starts ~out 35.3; badge_t=1.85 lands the pop at ~out 37.55."""
    out_dir = os.path.join(ANIM, slot, "frames"); os.makedirs(out_dir, exist_ok=True)
    n = int(round(dur*FPS))
    flab = font(26, False); fbadge = font(56, True)
    badge_t = 1.85
    cx = W//2
    for i in range(n):
        t = i/FPS
        ga = eo(t/0.4) if t < 0.4 else (eo((dur-t)/0.4) if t > dur-0.4 else 1.0)
        layer = Image.new("RGBA", (W,H), (0,0,0,0)); d = ImageDraw.Draw(layer)
        lab = "MENURUT REPORT"
        lw = text_w(d, lab, flab)
        d.text((cx-lw//2, 252), lab, font=flab, fill=DIM)
        if t > badge_t:
            a = int(255*pop(t, badge_t, 0.4))
            txt = "+10% AKURASI"
            tw = text_w(d, txt, fbadge); th = text_h(d, txt, fbadge)
            bw = tw+72; bh = 96
            bx0 = cx-bw//2; by0 = 300
            rrect(d, (bx0, by0, bx0+bw, by0+bh), 18,
                  fill=(GREEN_D[0],GREEN_D[1],GREEN_D[2],a), outline=(GREEN[0],GREEN[1],GREEN[2],a), width=3)
            d.text((cx-tw//2, by0+(bh-th)//2-8), txt, font=fbadge, fill=(255,255,255,a))
        fade_alpha(layer, ga)
        layer.save(os.path.join(out_dir, f"f_{i:05d}.png"))
    note(slot, n)

# ==================================================================== MAIN
if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "spy"):       render_spy("slot_spy_day3", 2.9)
    if which in ("all", "satellite"): render_satellite("slot_gfx_satellite", 8.0)
    if which in ("all", "akurasi"):   render_akurasi("slot_gfx_akurasi", 3.8)
    if which in ("all", "webscrape"): render_webscrape("slot_gfx_webscrape", 11.0)
    if which in ("all", "gtrends"):   render_gtrends("slot_gfx_gtrends", 9.5)
    if which in ("all", "src"):
        render_src("slot_src_satellite", f"{SRC}/satellite_escholar.png",
                   "Katona, Painter, Patatoukas & Zeng (2024), J. of Financial & Quantitative Analysis",
                   7.0, crop_y=0)
        render_src("slot_src_gtrends", f"{SRC}/gtrends_nature.png",
                   "Preis, Moat & Stanley (2013), Scientific Reports (Nature)",
                   6.0, crop_y=95)
        render_src("slot_src_transaction", f"{SRC}/transaction_paragon.png",
                   "Data transaksi konsumen — penyedia alternative data (Paragon Intel / Daloopa)",
                   5.0, crop_y=0)
    print("DONE", which)
