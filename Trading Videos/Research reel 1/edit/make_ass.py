"""Generate master.ass for Research reel 1 — dual EN/ID tracks, matching first reel style."""

import os

def ts(sec: float) -> str:
    """Seconds -> ASS timestamp H:MM:SS.CC"""
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"


# EDL segments: (clip, src_start, src_end, output_offset)
# IMG_0927 is split to remove 0.15s gap; all segments after shift by -0.15s.
# IMG_0933 extended to 10.25 to include hand-cover outro.
SEGMENTS = [
    ("IMG_0909", 1.93,  5.14,  0.00),   # 0
    ("IMG_0911", 1.75, 11.58,  3.21),   # 1
    ("IMG_0914", 1.61,  6.68, 13.04),   # 2
    ("IMG_0915", 1.11,  8.66, 18.11),   # 3
    ("IMG_0920", 1.31, 11.66, 25.66),   # 4
    ("IMG_0921", 1.23, 12.02, 36.01),   # 5
    ("IMG_0922", 1.53, 10.72, 46.80),   # 6
    ("IMG_0925", 1.71,  8.06, 55.99),   # 7
    ("IMG_0927", 1.05,  8.71, 62.34),   # 8a — part A (ends at output 70.00)
    ("IMG_0927", 8.86,  9.94, 70.00),   # 8b — part B (skip 0.15s gap; ends at 71.08)
    ("IMG_0929", 1.69,  7.68, 71.08),   # 9  (-0.15s shift)
    ("IMG_0932", 1.79, 10.06, 77.07),   # 10 (-0.15s shift)
    ("IMG_0933", 1.39, 10.25, 85.34),   # 11 (-0.15s shift, extended outro to 10.25)
]

def out(src_time: float, seg_idx: int) -> float:
    _, seg_start, _, offset = SEGMENTS[seg_idx]
    return src_time - seg_start + offset

# Phrases: (seg_idx, src_phrase_start, src_phrase_end, en_text, id_text)
# For English-only lines, id_text is a translation; for ID-only lines, en_text is a translation.
PHRASES = [
    # INTRO
    (0, 1.979, 5.059,
     "Welcome everyone to day two of my series.",
     "Selamat datang semua di hari kedua dari series gua."),

    # PEAD — phrase 1 (English)
    (1, 1.799, 5.980,
     "Did you know that prices tend to drift for up to sixty days after news?",
     "Tahukah kamu bahwa harga bisa drift sampai enam puluh hari setelah news?"),

    # PEAD — phrase 2 (Indonesian)
    (1, 6.519, 11.500,
     "This is what's called PEAD — Post Earnings Announcement Drift.",
     "Inilah apa yang disebut sebagai PEAD atau Post Earning Announcement Drift."),

    # ANALYST_A (Indonesian)
    (2, 1.659, 6.599,
     "Not only that — if analysts upgrade their sentiment on this stock,",
     "Bukan hanya itu, jika para analis mengupgrade sentimen stok ini,"),

    # ANALYST_B (Indonesian)
    (3, 1.159, 8.579,
     "the stock price can rise or fall for weeks. This is called analyst-driven momentum.",
     "harga stok ini bisa naik atau turun selama beberapa minggu. Inilah analyst driven momentum."),

    # MERGER_A (Indonesian)
    (4, 1.360, 11.579,
     "Now imagine this: Company A announces they'll buy Company B shares for $30 per share.",
     "Nah, bayangin perusahaan A mau beli share perusahaan B dengan harga tiga puluh dolar per share."),

    # MERGER_B (Indonesian)
    (5, 1.279, 11.939,
     "If we buy those shares at $28 now, we're guaranteed $2 profit. This is merger arbitrage.",
     "Jika kita beli dengan harga dua puluh delapan dolar, kita garanti dua dolar profit. Ini merger arbitrage."),

    # FDA_A (Indonesian)
    (6, 1.579, 10.639,
     "Biotech companies in the US need FDA approval, with a PDUFA date published months in advance.",
     "Perusahaan bioteknologi di Amerika butuh persetujuan FDA dan PDUFA yang dipublisikan beberapa bulan sebelumnya."),

    # FDA_B (Indonesian)
    (7, 1.759, 7.979,
     "In that window, the stock can rise 20% — four to eight weeks before the announcement.",
     "Dalam jangka waktu itu, stok bisa naik dua puluh persen, empat sampai delapan minggu sebelum announcement."),

    # FDA_C — phrase start is in seg 8a, phrase end ("aman.") is in seg 8b after the gap cut
    # Output start: 1.100 - 1.05 + 62.34 = 62.39  (from seg 8a)
    # Output end:   9.859 - 8.86 + 70.00 = 70.999  (from seg 8b) — hardcoded below as sentinel -1
    (8, 1.100, -1,
     "As traders, we just buy when the date is published and sell before the announcement — to stay safe.",
     "Kita sebagai trader tinggal beli waktu baru dipublikasikan dan jual sebelum announcement itu keluar."),

    # RECAP (Indonesian) — seg index 10
    (10, 1.740, 7.599,
     "In this video we covered four trading techniques used after news drops.",
     "Dalam video ini kita sudah bahas empat trading teknik yang dipakai setelah news keluar."),

    # TEASE (Indonesian) — seg index 11
    (11, 1.839, 9.979,
     "In the next video, we'll find out if there are techniques to predict the outcome before news comes out.",
     "Di video selanjutnya, kita akan cari tahu teknik-teknik untuk mengetahui hasilnya sebelum news keluar."),

    # OUTRO phrase 1 (mixed) — seg index 12
    (12, 1.439, 7.659,
     "Once again, if you're into algorithmic trading, like, follow, and comment on my IG.",
     "Once again, jika tertarik dengan algorithmic trading, tinggal like, follow, dan comment di IG gua."),

    # OUTRO phrase 2 (English) — seg index 12
    (12, 8.199, 9.179,
     "See you next time!",
     "Sampai jumpa lagi!"),

    # OUTRO phrase 3 — Peace + hand cover
    (12, 9.699, 10.25,
     "Peace!",
     "Peace!"),
]

ASS_HEADER = """\
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: EN,Arial,34,&H0000FFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,2,0,2,10,10,490,1
Style: ID,Arial,34,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,2,0,2,10,10,555,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

FDA_C_END_OUTPUT = 9.859 - 8.86 + 70.00  # "aman." end in seg 8b output timeline

lines = [ASS_HEADER]
for seg_idx, src_s, src_e, en, id_ in PHRASES:
    o_s = out(src_s, seg_idx)
    o_e = FDA_C_END_OUTPUT if src_e == -1 else out(src_e, seg_idx)
    lines.append(f"Dialogue: 0,{ts(o_s)},{ts(o_e)},EN,,0,0,0,,{en}")
    lines.append(f"Dialogue: 0,{ts(o_s)},{ts(o_e)},ID,,0,0,0,,{id_}")
    lines.append("")

out_path = os.path.join(os.path.dirname(__file__), "master_v2.ass")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"Written: {out_path}")
