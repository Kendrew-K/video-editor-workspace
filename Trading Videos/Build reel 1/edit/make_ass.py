"""Generate master_v1.ass for Build reel 1 — Trading Bot Techniques (Day 6).

Dual bilingual subtitles: ID (white, top) + EN (yellow, bottom) per cue via \\N.
White line is ALWAYS Indonesian, yellow ALWAYS English — English-spoken lines get
an ID translation on top (creator feedback, Session 2), never duplicated EN/EN.
<=55 chars per language line. Output-timeline offsets per Hard Rule 5.
Outro "See you next time. Peace." left uncaptioned (series convention).
"""

import os

def ts(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"

# (source, clip_src_start, output_offset) — must match edl_v1.json ranges
SEGMENTS = [
    ("IMG_1045", 1.20,  0.00),   # 0 INTRO  (end trimmed to 10.07, Session 2)
    ("IMG_1047", 1.34,  8.87),   # 1 DECISION
    ("IMG_1050", 1.58, 23.58),   # 2 TECH1
    ("IMG_1051", 0.70, 39.77),   # 3 TECH2
    ("IMG_1052", 0.96, 57.32),   # 4 REJECT
    ("IMG_1053", 0.88, 68.67),   # 5 STEPS
    ("IMG_1054", 0.80, 79.70),   # 6 OUTRO  (end trimmed to 11.12, Session 2)
]

def out(src_time, seg_idx):
    _, seg_start, offset = SEGMENTS[seg_idx]
    return src_time - seg_start + offset

# (seg_idx, src_start, src_end, id_text, en_text)
# NOTE: IMG_1045 word timestamps collapse after "techniques" (Scribe glitch) —
# cue splits there are estimated against the audio, not word-exact.
PHRASES = [
    # INTRO
    (0, 1.30, 3.60,
     "Selamat datang di day 6 trading series gua,",
     "Welcome to day six of my trading series,"),
    (0, 4.02, 6.50,
     "dan hari ini kita akan bahas",
     "and today we are going to talk about"),
    (0, 6.50, 10.02,
     "teknik-teknik yang gua pakai untuk trading bot gua.",
     "the techniques I'll use for my own trading bot."),

    # DECISION
    (1, 1.44, 4.48,
     "Setelah research, gue memutuskan untuk menggunakan",
     "After research, I decided to use"),
    (1, 4.52, 6.74,
     "dua teknik yang gua bahas dalam video sebelumnya.",
     "two techniques I covered in my last video."),
    (1, 7.26, 7.66,
     "Kenapa?",
     "Why?"),
    (1, 8.34, 11.14,
     "Dengan teknologi Wall Street Trader sekarang ini,",
     "With the tech Wall Street traders have today,"),
    (1, 11.58, 13.34,
     "nggak bijak untuk bersaing dengan mereka,",
     "it is unwise to compete with them,"),
    (1, 13.92, 15.80,
     "jadi gua akan hindari mereka sepenuhnya.",
     "so I will avoid them entirely."),

    # TECH1 — PEAD
    (2, 1.68, 5.38,
     "Teknik satu: PEAD, price drift.",
     "Technique one: PEAD, price drift."),
    (2, 6.06, 6.36,
     "Kenapa?",
     "Why?"),
    (2, 6.90, 9.90,
     "Andalannya: stok yang ngalahin ekspektasinya sendiri,",
     "It relies on a stock beating its own expectations,"),
    (2, 10.26, 12.42,
     "artinya kita nggak bersaing dengan siapa pun,",
     "meaning we're not competing with anyone,"),
    (2, 12.78, 15.56,
     "cuma ngikutin harga stok selama beberapa minggu,",
     "just following stock prices for several weeks,"),
    (2, 15.94, 17.52,
     "jadi sangat gampang untuk di-backtest.",
     "making it very easy to backtest."),

    # TECH2 — SEC FILINGS
    (3, 0.78, 2.68,
     "Teknik dua adalah SEC filings.",
     "Technique two is SEC filings."),
    (3, 3.14, 3.38,
     "Kenapa?",
     "Why?"),
    (3, 3.70, 6.12,
     "Karena semua korporasi wajib menyerahkan",
     "Because all corporations need to submit"),
    (3, 6.16, 8.28,
     "SEC filing mereka sendiri.",
     "their own SEC filing."),
    (3, 8.34, 10.18,
     "Ini resource gratis dan publik",
     "It is a free and public resource"),
    (3, 10.20, 13.00,
     "langsung dari file-nya SEC sendiri.",
     "coming from the SEC's own files."),
    (3, 13.64, 15.84,
     "Artinya gua bisa lacak dan pantau",
     "This means I can track and oversee"),
    (3, 15.88, 18.00,
     "banyak korporasi tanpa keluar uang sepeser pun.",
     "multiple corporations without spending a dime."),

    # REJECT
    (4, 1.06, 2.58,
     "Teknik-teknik yang lain menurut gua",
     "The other techniques, in my opinion,"),
    (4, 2.62, 5.06,
     "nggak cocok untuk solo builder seperti gua",
     "don't fit a solo builder like me"),
    (4, 5.42, 7.44,
     "karena butuh uang terlalu banyak",
     "because they either need too much money"),
    (4, 7.48, 10.06,
     "atau kita semua harus bersaing dengan korporasi besar",
     "or we all have to compete with big corporations"),
    (4, 10.10, 12.06,
     "dan itu ide yang sangat buruk.",
     "which is a terrible idea."),

    # STEPS
    (5, 0.98, 4.74,
     "Step dua: ubah semua teknik ini jadi kode",
     "Now step two is to turn all these techniques into code"),
    (5, 4.78, 8.18,
     "dan step tiga: backtest dan paper trade.",
     "and step three is to backtest and paper trade."),
    (5, 8.24, 11.66,
     "Dengan itu, KTrade bot versi satu selesai.",
     "With that, KTrade bot version one should be done."),

    # OUTRO (cut before "See you next time. Peace." — uncaptioned)
    (6, 0.90, 3.54,
     "Nah, kalau lo tertarik nonton gua",
     "Now, if you're interested in watching me"),
    (6, 4.04, 5.46,
     "ngoding algoritma untuk bot ini,",
     "code the algorithm for this bot,"),
    (6, 5.96, 7.58,
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

out_path = os.path.join(os.path.dirname(__file__), "master_v1.ass")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"Written: {out_path}")
