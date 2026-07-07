"""Generate master_v1.ass for Research reel 4 — AI News Trading (Day 5).

Dual bilingual subtitles: ID (white, top) + EN (yellow, bottom) per cue via \\N.
≤55 chars per language line. Output-timeline offsets per Hard Rule 5.
Outro 'See you next time! Peace! Pshew!' left uncaptioned.
"""

import os

def ts(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"

# (seg_idx, clip_src_start, output_offset)
SEGMENTS = [
    ("IMG_0999", 1.28,  0.00),   # 0  HOOK
    ("IMG_1002", 1.70, 13.92),   # 1  DAY5
    ("IMG_1004", 1.60, 18.67),   # 2  SETUP
    ("IMG_1009", 1.38, 26.89),   # 3  EXAMPLE
    ("IMG_1011", 1.46, 37.73),   # 4  POWELL_A
    ("IMG_1013", 1.60, 44.09),   # 5  POWELL_B
    ("IMG_1014", 1.24, 50.11),   # 6  LING_TRADE
    ("IMG_1016", 2.04, 58.31),   # 7  BLOOMBERG
    ("IMG_1018", 1.84, 70.47),   # 8  CHATGPT
    ("IMG_1019", 1.20, 79.31),   # 9  RESULTS
    ("IMG_1020", 1.26, 92.43),   # 10 AGENTS
    ("IMG_1026", 1.98,102.39),   # 11 OUTRO
]

def out(src_time, seg_idx):
    _, seg_start, offset = SEGMENTS[seg_idx]
    return src_time - seg_start + offset

# (seg_idx, src_start, src_end, id_text, en_text)
# Each line ≤55 chars. 'Kendrew' override where Scribe says 'Ken Drew' (none in this reel).
# Seg 11 outro: "See you next time! Peace! Pshew!" is intentionally uncaptioned.
PHRASES = [
    # HOOK
    (0, 1.32, 3.80,
     "In 2024, kebanyakan Wall Street Trader",
     "In 2024, most Wall Street traders"),
    (0, 3.80, 6.20,
     "pakai AI Agents untuk baca berita",
     "used AI Agents to read news"),
    (0, 6.20, 8.62,
     "& buat keputusan trading dalam detik.",
     "& trade in seconds."),
    (0, 9.18, 10.80,
     "Tapi, kenapa di tahun ini",
     "But why, today,"),
    (0, 10.80, 12.28,
     "kebanyakan itu sudah mati?",
     "have most of them died out?"),
    (0, 13.10, 13.30,
     "Well,",
     "Well,"),
    (0, 13.86, 15.08,
     "let's rewind first.",
     "let's rewind first."),

    # DAY 5
    (1, 1.74, 4.26,
     "Before we begin, welcome everyone to",
     "Before we begin, welcome everyone to"),
    (1, 4.90, 6.42,
     "Day 5 of my trading series.",
     "Day 5 of my trading series."),

    # SETUP
    (2, 1.64, 4.20,
     "Dari dulu, harga stok bukan dari data,",
     "Stock prices have never been about data,"),
    (2, 4.20, 6.60,
     "tetapi dari gap antara realita",
     "but from the gap between reality"),
    (2, 6.60, 9.78,
     "dan ekspektasi di dalam data itu.",
     "and expectations within that data."),

    # EXAMPLE
    (3, 1.42, 4.50,
     "Misalnya, forecast bilang 250.000",
     "Say the forecast predicts 250,000"),
    (3, 4.50, 9.42,
     "lowongan kerja baru... tapi realitanya",
     "new jobs... but reality shows only"),
    (3, 9.92, 12.18,
     "200.000 lowongan kerja yang baru.",
     "200,000 new jobs."),

    # POWELL A
    (4, 1.50, 3.50,
     "Kalian pasti pernah lihat video",
     "You've definitely seen the video"),
    (4, 3.50, 5.80,
     "of Jerome Powell, Kepala Fed of America,",
     "of Jerome Powell, head of the Fed,"),
    (4, 5.80, 7.82,
     "ketika dia memberi pidato.",
     "when he gives his speech."),

    # POWELL B
    (5, 1.64, 3.60,
     "Satu kata dari dia",
     "One word from him"),
    (5, 3.60, 5.66,
     "bisa merubah harga stok secara drastis.",
     "can change stock prices drastically."),
    (5, 6.32, 7.62,
     "Inilah poin kedua gua.",
     "This is my second point."),

    # LING TRADE
    (6, 1.28, 4.20,
     "Orang tidak lagi trade dari rate-nya,",
     "People no longer trade the actual rate,"),
    (6, 4.20, 7.20,
     "melainkan dari kata-kata pemimpin",
     "but from the words leaders use"),
    (6, 7.20, 9.44,
     "saat announcement.",
     "during the announcement."),

    # BLOOMBERG
    (7, 2.08, 4.80,
     "Makanya Bloomberg punya sistem",
     "So Bloomberg built a system"),
    (7, 4.80, 7.80,
     "yang bisa nge-skor semua headline",
     "that scores every headline instantly"),
    (7, 7.80, 11.20,
     "yang dijual ke hedge fund-hedge fund besar",
     "sold to the world's biggest hedge funds"),
    (7, 11.20, 14.16,
     "seharga ribuan sampai ratusan US dollar.",
     "for thousands to hundreds of USD."),

    # CHATGPT
    (8, 1.88, 4.20,
     "Nah, balik lagi ke 2023.",
     "Now, let's go back to 2023."),
    (8, 4.20, 6.60,
     "waktu ChatGPT baru mulai mainstream.",
     "when ChatGPT just went mainstream."),
    (8, 6.60, 10.64,
     "Orang pakai ChatGPT buat prediksi harga.",
     "People used ChatGPT to predict stock prices."),

    # RESULTS
    (9, 1.24, 2.28,
     "Hasilnya,",
     "The result:"),
    (9, 2.28, 4.20,
     "bagusnya minta ampun,",
     "Incredibly good,"),
    (9, 4.20, 5.80,
     "Sharpe Ratio of 3.8.",
     "a Sharpe Ratio of 3.8."),
    (9, 6.36, 8.60,
     "Tapi, pada tahun 2024,",
     "But by 2024,"),
    (9, 8.60, 10.20,
     "ini semua sudah mati. Kenapa?",
     "all of this died. Why?"),
    (9, 10.80, 12.60,
     "Terlalu banyak orang",
     "Too many people"),
    (9, 12.60, 14.32,
     "memakai metode yang sama.",
     "used the exact same method."),

    # AGENTS
    (10, 1.30, 3.80,
     "Mereka mulai pakai Agent Teams,",
     "They started using Agent Teams,"),
    (10, 3.80, 7.00,
     "sekelompok agent yang debat",
     "a group of agents that debate"),
    (10, 7.00, 9.60,
     "berbagai aspek data dan berita,",
     "different aspects of data and news,"),
    (10, 9.60, 11.18,
     "dan hasilnya: return 26%!",
     "which reported a 26% return!"),

    # OUTRO (cut before "See you next time! Peace! Pshew!" — uncaptioned)
    (11, 2.02, 5.10,
     "In reality, banyak trik yang",
     "In reality, many tricks that"),
    (11, 5.10, 8.88,
     "bagus di kertas & backtest, gagal live.",
     "look good on paper & in backtest, fail live."),
    (11, 9.92, 11.60,
     "Di video selanjutnya,",
     "In the next video,"),
    (11, 11.60, 13.34,
     "gua bahas actual game plan trading bot gua.",
     "I'll cover my actual trading bot game plan."),
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

