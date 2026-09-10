"""Generate master_v3.ass for Build reel 1 v3 (cold-open hook + jump-cut timeline).

White line ALWAYS Indonesian, yellow ALWAYS English (creator rule, Session 2).
Segments are now per-RANGE (jump cuts split clips into many ranges) — each cue
must reference the range that contains it, offsets per Hard Rule 5.
Final "See you next time. Peace." uncaptioned (series convention).
"""

import os

def ts(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"

# (source, range_src_start, output_offset) — must match edl_v3.json ranges, in order
SEGMENTS = [
    ("IMG_1051", 14.14,  0.00),  # 0  HOOK
    ("IMG_1045",  1.22,  3.96),  # 1  INTRO a
    ("IMG_1045",  3.94,  6.44),  # 2  INTRO b
    ("IMG_1047",  1.36, 12.57),  # 3  DEC a
    ("IMG_1047",  7.18, 18.05),  # 4  DEC b (Kenapa?)
    ("IMG_1047",  8.26, 18.63),  # 5  DEC c
    ("IMG_1047", 11.50, 21.61),  # 6  DEC d
    ("IMG_1047", 13.84, 23.55),  # 7  DEC e
    ("IMG_1050",  1.60, 25.61),  # 8  T1 a
    ("IMG_1050",  3.06, 26.69),  # 9  T1 b
    ("IMG_1050",  5.98, 29.11),  # 10 T1 c (Why?)
    ("IMG_1050",  6.82, 29.59),  # 11 T1 d
    ("IMG_1051",  0.62, 40.39),  # 12 T2 a
    ("IMG_1051",  3.06, 42.55),  # 13 T2 b
    ("IMG_1052",  0.98, 52.59),  # 14 REJECT
    ("IMG_1053",  0.90, 63.77),  # 15 STEPS
    ("IMG_1054",  0.82, 74.63),  # 16 OUT a
    ("IMG_1054",  1.58, 75.01),  # 17 OUT b
    ("IMG_1054",  5.88, 78.99),  # 18 OUT c
    ("IMG_1054",  8.02, 80.79),  # 19 OUT d (uncaptioned)
]

def out(src_time, seg_idx):
    _, seg_start, offset = SEGMENTS[seg_idx]
    return src_time - seg_start + offset

# (range_idx, src_start, src_end, id_text, en_text)
PHRASES = [
    # HOOK (cold open — was the TECH2 closing line)
    (0, 14.22, 16.84,
     "Gua bisa lacak dan pantau banyak korporasi",
     "I can track and oversee multiple corporations"),
    (0, 16.88, 18.00,
     "tanpa keluar uang sepeser pun.",
     "without spending a dime."),

    # INTRO
    (1, 1.30, 3.60,
     "Selamat datang di day 6 trading series gua,",
     "Welcome to day six of my trading series,"),
    (2, 4.02, 6.50,
     "dan hari ini kita akan bahas",
     "and today we are going to talk about"),
    (2, 6.50, 10.02,
     "teknik-teknik yang gua pakai untuk trading bot gua.",
     "the techniques I'll use for my own trading bot."),

    # DECISION
    (3, 1.44, 4.48,
     "Setelah research, gue memutuskan untuk menggunakan",
     "After research, I decided to use"),
    (3, 4.52, 6.74,
     "dua teknik yang gua bahas dalam video sebelumnya.",
     "two techniques I covered in my last video."),
    (4, 7.26, 7.66,
     "Kenapa?",
     "Why?"),
    (5, 8.34, 11.14,
     "Dengan teknologi Wall Street Trader sekarang ini,",
     "With the tech Wall Street traders have today,"),
    (6, 11.58, 13.34,
     "nggak bijak untuk bersaing dengan mereka,",
     "it is unwise to compete with them,"),
    (7, 13.92, 15.80,
     "jadi gua akan hindari mereka sepenuhnya.",
     "so I will avoid them entirely."),

    # TECH1 — PEAD
    (8, 1.68, 2.58,
     "Teknik satu,",
     "Technique one,"),
    (9, 3.14, 5.38,
     "PEAD, price drift.",
     "PEAD, price drift."),
    (10, 6.06, 6.36,
     "Kenapa?",
     "Why?"),
    (11, 6.90, 9.90,
     "Andalannya: stok yang ngalahin ekspektasinya sendiri,",
     "It relies on a stock beating its own expectations,"),
    (11, 10.26, 12.42,
     "artinya kita nggak bersaing dengan siapa pun,",
     "meaning we're not competing with anyone,"),
    (11, 12.78, 15.56,
     "cuma ngikutin harga stok selama beberapa minggu,",
     "just following stock prices for several weeks,"),
    (11, 15.94, 17.52,
     "jadi sangat gampang untuk di-backtest.",
     "making it very easy to backtest."),

    # TECH2 — SEC FILINGS (ends at "files." — closing line moved to HOOK)
    (12, 0.78, 2.68,
     "Teknik dua adalah SEC filings.",
     "Technique two is SEC filings."),
    (13, 3.14, 3.38,
     "Kenapa?",
     "Why?"),
    (13, 3.70, 6.12,
     "Karena semua korporasi wajib menyerahkan",
     "Because all corporations need to submit"),
    (13, 6.16, 8.28,
     "SEC filing mereka sendiri.",
     "their own SEC filing."),
    (13, 8.34, 10.18,
     "Ini resource gratis dan publik",
     "It is a free and public resource"),
    (13, 10.20, 13.00,
     "langsung dari file-nya SEC sendiri.",
     "coming from the SEC's own files."),

    # REJECT
    (14, 1.06, 2.58,
     "Teknik-teknik yang lain menurut gua",
     "The other techniques, in my opinion,"),
    (14, 2.62, 5.06,
     "nggak cocok untuk solo builder seperti gua",
     "don't fit a solo builder like me"),
    (14, 5.42, 7.44,
     "karena butuh uang terlalu banyak",
     "because they either need too much money"),
    (14, 7.48, 10.06,
     "atau kita semua harus bersaing dengan korporasi besar",
     "or we all have to compete with big corporations"),
    (14, 10.10, 12.06,
     "dan itu ide yang sangat buruk.",
     "which is a terrible idea."),

    # STEPS
    (15, 0.98, 4.74,
     "Step dua: ubah semua teknik ini jadi kode",
     "Now step two is to turn all these techniques into code"),
    (15, 4.78, 8.18,
     "dan step tiga: backtest dan paper trade.",
     "and step three is to backtest and paper trade."),
    (15, 8.24, 11.66,
     "Dengan itu, KTrade bot versi satu selesai.",
     "With that, KTrade bot version one should be done."),

    # OUTRO
    (16, 0.90, 1.10,
     "Nah,",
     "Now,"),
    (17, 1.66, 3.54,
     "kalau lo tertarik nonton gua",
     "if you're interested in watching me"),
    (17, 4.04, 5.46,
     "ngoding algoritma untuk bot ini,",
     "code the algorithm for this bot,"),
    (18, 5.96, 7.58,
     "langsung aja like dan follow akun ini.",
     "just like and follow this account."),
]

ASS_HEADER = """\
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: BL,Arial,34,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,3,1,2,36,36,200,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

lines = [ASS_HEADER]
for seg_idx, src_s, src_e, id_text, en_text in PHRASES:
    o_s = out(src_s, seg_idx)
    o_e = out(src_e, seg_idx)
    cue = f"{{\\c&HFFFFFF&}}{id_text}\\N{{\\c&H00FFFF&}}{en_text}"
    lines.append(f"Dialogue: 0,{ts(o_s)},{ts(o_e)},BL,,0,0,0,,{cue}")
    lines.append("")

out_path = os.path.join(os.path.dirname(__file__), "master_v3.ass")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"Written: {out_path}")
