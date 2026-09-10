"""Generate master_v1.ass for Build Reel 2 (Day 7) — jump-cut timeline.

White line ALWAYS Indonesian (top), yellow ALWAYS English (bottom) — series rule.
Segments are per-RANGE (jump cuts). Each cue references the range that contains
it; output offset per Hard Rule 5: out = src_time - range_src_start + offset.
Final "Peace. (gunshot)" range left uncaptioned (series button convention).
Colloquial ID register: gua/lo/nggak/udah/kalau.
No em dashes (series rule).
"""

import os


def ts(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"


# (source, range_src_start, output_offset) — must match edl_v1.json ranges, in order
SEGMENTS = [
    ("IMG_1065",  1.06,  0.00),  # 0  HOOK a
    ("IMG_1065",  3.70,  2.20),  # 1  HOOK b
    ("IMG_1066",  0.92,  4.22),  # 2  INTRO
    ("IMG_1067",  1.08,  8.70),  # 3  OVERVIEW a
    ("IMG_1067",  7.52, 14.88),  # 4  OVERVIEW b
    ("IMG_1068",  2.54, 20.02),  # 5  DEDUP a
    ("IMG_1068",  4.34, 21.40),  # 6  DEDUP b (Why)
    ("IMG_1068",  5.12, 21.84),  # 7  DEDUP c
    ("IMG_1068",  7.28, 23.72),  # 8  DEDUP d
    ("IMG_1070",  1.46, 34.38),  # 9  RULES a
    ("IMG_1070",  3.14, 35.80),  # 10 RULES b
    ("IMG_1070",  7.06, 39.48),  # 11 RULES c
    ("IMG_1070", 10.38, 42.32),  # 12 RULES d
    ("IMG_1071",  0.54, 45.68),  # 13 SAFETY
    ("IMG_1073",  1.02, 58.08),  # 14 ROADMAP a (start pulled back to include "Jadi")
    ("IMG_1073", 10.30, 67.06),  # 15 ROADMAP b (+0.78 from R14 lengthening)
    ("IMG_1074",  1.04, 74.84),  # 16 OUTRO a
    ("IMG_1074",  3.26, 76.72),  # 17 OUTRO b
    ("IMG_1074",  6.40, 79.58),  # 18 OUTRO c
    ("IMG_1074",  8.34, 81.14),  # 19 OUTRO d (uncaptioned)
]


def out(src_time, seg_idx):
    _, seg_start, offset = SEGMENTS[seg_idx]
    return src_time - seg_start + offset


# (range_idx, src_start, src_end, id_text, en_text)
PHRASES = [
    # HOOK ("shit" beeped in audio; caption censored to match)
    (0, 1.14, 3.16, "Trading itu susah banget,", "Trading is hard as sh*t,"),
    (1, 3.78, 5.62, "jadi ini bakal jadi perjalanan panjang.", "so this will be a long journey."),

    # INTRO
    (2, 1.00, 2.52, "Selamat datang di day tujuh,", "Welcome guys to day seven,"),
    (2, 2.58, 5.30, "dan gua punya banyak info buat kalian.", "and boy, do I have info for you all."),

    # OVERVIEW — 5 stages
    (3, 1.16, 2.36, "Implementasi bot ini", "The implementation of this bot"),
    (3, 2.44, 3.68, "akan datang dalam lima tahap:", "will come in five stages:"),
    (3, 4.08, 5.86, "baca berita, filter duplikat,", "read news, filter duplicates,"),
    (3, 6.24, 7.16, "cari stok yang kena,", "find the affected stock,"),
    (4, 7.60, 9.12, "buat keputusan buy atau sell,", "make a buy or sell decision,"),
    (4, 9.14, 12.56, "dan terakhir cek kalau trade-nya aman.", "and finally check if the trade is safe."),

    # DEDUP
    (5, 2.62, 3.82, "Duplikat itu bahaya.", "Duplicates are dangerous."),
    (6, 4.42, 4.68, "Kenapa?", "Why?"),
    (7, 5.20, 6.90, "Berita di-post ulang berkali-kali.", "News gets republished over and over."),
    (8, 7.36, 9.18, "Kalau bot kita ngira beritanya baru,", "If our bot thinks the news is new,"),
    (8, 9.56, 11.98, "dia bakal trade terus pakai info itu.", "it keeps trading on that same info."),
    (8, 12.04, 13.78, "Dan kalau semua orang udah tahu,", "And once everyone already knows,"),
    (8, 13.84, 15.28, "itu bukan edge lagi.", "it's no longer an edge."),
    (8, 15.34, 17.84, "Jadi kita fokus ke berita baru aja.", "So we'll focus only on fresh news."),

    # RULES
    (9, 1.54, 2.78, "Sebelum implementasi algoritmanya,", "Before implementing the algorithm,"),
    (10, 3.22, 6.26, "kita harus bikin aturan dasar dulu buat botnya.", "we first set some basic rules for the bot."),
    (10, 6.30, 6.72, "Misalnya,", "For example,"),
    (11, 7.14, 9.80, "kalau ada merger di perusahaan, kita buy.", "if there's a merger at a company, we buy."),
    (12, 10.46, 13.64, "Jadi tiap trade bisa dijelasin pakai logika.", "So every trade can be explained with logic."),

    # SAFETY
    (13, 0.62, 2.76, "Dan yang terakhir, cek keamanan.", "And last, the safety check."),
    (13, 2.80, 6.72, "Misalnya posisi kita di suatu saham kegedean,", "Like if our position in a stock is too big,"),
    (13, 6.76, 9.36, "atau daily loss limit kita udah kena,", "or our daily loss limit is already hit,"),
    (13, 9.42, 10.50, "maka akan ada kill switch", "then a kill switch kicks in"),
    (13, 10.52, 12.84, "yang matiin program itu buat hari itu.", "that shuts the program down for the day."),

    # ROADMAP ("Jadi" kept per creator note — natural beat before the plan)
    (14, 1.10, 1.40, "Jadi,", "So,"),
    (14, 1.88, 4.12, "bulan pertama kita kumpulin berita.", "month one we're gonna collect news."),
    (14, 4.18, 6.30, "Bulan kedua kita implement semua aturannya", "Month two we implement all the rules"),
    (14, 6.34, 7.86, "yang udah kita bahas tadi.", "that we discussed earlier."),
    (14, 7.90, 9.90, "Bulan tiga dan empat kita mulai", "Months three and four we start"),
    (15, 10.38, 12.84, "backtesting sama paper trading.", "backtesting and paper trading."),
    (15, 12.86, 14.94, "Dan kalau nggak ada perubahan lain,", "And if nothing else changes,"),
    (15, 15.28, 17.98, "bulan kelima kita mulai live trading.", "month five we start live trading."),

    # OUTRO
    (16, 1.12, 2.82, "Jadi itu seluruh pipeline-nya.", "So that's the entire pipeline."),
    (17, 3.34, 4.36, "Follow kalau lo tertarik", "Follow if you're interested"),
    (17, 4.38, 6.02, "buat tahu gimana gua bikin bot ini.", "in how I built this bot."),
    (18, 6.48, 7.86, "Sampai jumpa di video berikutnya.", "See you in the next video."),
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
print(f"Written: {out_path} ({len(PHRASES)} cues)")
