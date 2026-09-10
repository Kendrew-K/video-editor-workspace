"""Generate master_v1.ass for Build reel 3 (Day 8) — jump-cut timeline.

Series rules enforced here (EDITING_GUIDE §4):
  - White line is ALWAYS Indonesian (top), yellow ALWAYS English (bottom), even
    when the creator speaks English. English-spoken lines get an ID translation
    in his colloquial register (gua/lo/nggak/udah).
  - Exactly two lines on screen; every cue split to <= 55 chars per language.
  - "Kendrew", never Scribe's "Ken Drew". No em dashes.
  - Output-timeline offsets per Hard Rule 5:
        out = src_time - range_src_start + range_output_offset
  - The final "Peace!" range is left uncaptioned (series button convention).

SEGMENTS must stay in sync with edl_v1.json "ranges" (same order, same
start/offset). Re-check both together whenever a cut moves.
"""

import os

MAX_LINE = 55


def ts(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"


# (source, range_src_start, output_offset) — mirrors edl_v1.json ranges, in order
SEGMENTS = [
    ("IMG_1110",  8.20,  0.00),  # 0  HOOK (B&W flash-forward)
    ("IMG_1106",  2.00,  2.65),  # 1  INTRO
    ("IMG_1106",  6.46,  6.75),  # 2  SOURCES a
    ("IMG_1106",  9.16,  9.21),  # 3  SOURCES b
    ("IMG_1106", 13.54, 13.39),  # 4  SOURCES c
    ("IMG_1108",  2.20, 15.89),  # 5  WHY a
    ("IMG_1108",  3.64, 16.95),  # 6  WHY b
    ("IMG_1108", 10.44, 23.39),  # 7  WHY c
    ("IMG_1108", 11.24, 23.99),  # 8  WHY d
    ("IMG_1110",  2.24, 31.43),  # 9  PROBLEM a
    ("IMG_1110",  3.46, 32.43),  # 10 PROBLEM b
    ("IMG_1111",  0.88, 36.23),  # 11 SOLUTION a
    ("IMG_1111",  2.42, 37.61),  # 12 SOLUTION b
    ("IMG_1111",  4.88, 39.73),  # 13 SOLUTION c
    ("IMG_1111",  9.94, 44.63),  # 14 SOLUTION d
    ("IMG_1116",  1.00, 46.45),  # 15 WEBHOOK a
    ("IMG_1116",  4.54, 49.69),  # 16 WEBHOOK b
    ("IMG_1116", 10.40, 54.79),  # 17 WEBHOOK c
    ("IMG_1120",  1.82, 60.37),  # 18 STORE a
    ("IMG_1120",  3.36, 61.67),  # 19 STORE b
    ("IMG_1120",  6.98, 65.01),  # 20 STORE c
    ("IMG_1120",  9.48, 67.31),  # 21 STORE d
    ("IMG_1121",  0.76, 75.17),  # 22 OUTRO a
    ("IMG_1121",  6.62, 80.77),  # 23 OUTRO b
    ("IMG_1121", 11.26, 85.25),  # 24 OUTRO c
    ("IMG_1121", 13.16, 86.73),  # 25 OUTRO d
    ("IMG_1121", 14.72, 87.97),  # 26 BUTTON (uncaptioned)
]


def out(src_time: float, seg_idx: int) -> float:
    _, seg_start, offset = SEGMENTS[seg_idx]
    return src_time - seg_start + offset


# (range_idx, src_start, src_end, indonesian, english)
PHRASES = [
    # HOOK — spoken in English, so the white line carries the ID translation
    (0, 8.28, 10.60, "Guys, gua nggak tahu ini bisa apa nggak.",
     "Guys, I don't know if this is possible."),

    # INTRO
    (1, 2.08, 3.40, "Day 8 telah hadir,", "Day 8 is here,"),
    (1, 3.44, 6.00, "dan gua mau share rencana gua buat ambil berita.",
     "and I'll share my plan on getting news."),

    # SOURCES
    (2, 6.54, 8.86, "Karena Bloomberg sekarang mahal banget,",
     "Since Bloomberg now costs way too much,"),
    (3, 9.24, 10.90, "gua bakal pakai Alpaca News API", "I plan to use the Alpaca News API"),
    (3, 11.16, 13.30, "dan juga SEC EDGAR API", "and also the SEC EDGAR API"),
    (4, 13.62, 16.00, "buat semua financial news bot gua ini.",
     "for all the financial news for this bot."),

    # WHY
    (5, 2.28, 3.20, "Nah, kenapa dua ini?", "So, why these two?"),
    (6, 3.72, 6.50, "Karena Alpaca punya broker API", "Because Alpaca has a broker API"),
    (6, 6.56, 9.98, "yang udah kepasang otomatis di aplikasi mereka.",
     "that's already built into their app."),
    (7, 10.52, 11.00, "Dan juga,", "And also,"),
    (8, 11.32, 13.50, "di video sebelumnya gua udah bilang",
     "in the previous video I already said"),
    (8, 13.54, 15.30, "bahwa gua bakal pakai SEC filing",
     "that I'd be using SEC filings"),
    (8, 15.32, 18.58, "sebagai salah satu teknik bot gua ini.",
     "as one of the techniques for this bot."),

    # PROBLEM
    (9, 2.32, 3.20, "Sebelum gua lanjut,", "Before I go on,"),
    (10, 3.54, 4.46, "gua baru sadar,", "I just realised,"),
    (10, 4.48, 7.20, "apa API-nya bisa diakses di Indonesia?",
     "can these APIs even be accessed from Indonesia?"),

    # SOLUTION
    (11, 0.96, 2.20, "Nah, setelah research,", "So, after some research,"),
    (12, 2.50, 4.48, "gua nemu alternatif buat Alpaca,", "I found an alternative to Alpaca,"),
    (13, 4.96, 6.80, "yaitu Finnhub API.", "which is the Finnhub API."),
    (13, 6.86, 9.70, "Meskipun Finnhub cuma news provider,",
     "Even though Finnhub is only a news provider,"),
    (14, 10.02, 11.70, "buat sementara ini cukuplah ya.", "for now it's good enough."),

    # WEBHOOK
    (15, 1.08, 2.98, "Jadi dengan dua API ini,", "So with these two APIs,"),
    (15, 3.04, 4.20, "gua bakal set up webhook,", "I'm going to set up a webhook,"),
    (16, 4.62, 6.08, "yaitu sebuah sistem", "which is a system"),
    (16, 6.12, 7.80, "biar semua berita baru", "so that every new piece of news"),
    (16, 7.84, 9.60, "langsung kekirim ke bot gua.", "gets pushed straight to my bot."),
    (17, 10.48, 12.46, "Jadi bot ini bisa jalan", "That way this bot can run"),
    (17, 12.48, 14.34, "pakai informasi terbaru tiap hari,", "on the latest info every day,"),
    (17, 14.36, 15.94, "tanpa gua sentuh sama sekali.", "without any intervention."),

    # STORE
    (18, 1.90, 3.08, "Dari dua news source ini,", "From these two news sources,"),
    (19, 3.44, 4.40, "gua bakal normalize,", "I'm going to normalize,"),
    (19, 4.52, 6.66, "yaitu ubah semua data ke format yang sama.",
     "meaning turn all the data into one format."),
    (20, 7.06, 9.22, "Terus semua data ini gua simpan di database,",
     "And I will store all of this data in a database,"),
    (21, 9.56, 11.70, "yang dalam hal ini pakai SQLite.", "which in this case will be SQLite."),
    (21, 11.74, 13.46, "Setup simpel buat proyek lokal.", "Simple setup for local projects."),
    (21, 13.50, 15.44, "Nah, data inilah yang bakal gua pakai",
     "And this is the data I'll be using"),
    (21, 15.48, 17.30, "buat backtesting nanti.", "for backtesting later on."),

    # OUTRO
    (22, 0.84, 3.72, "Dan segitu aja episode hari ini.",
     "And that pretty much wraps up today's episode."),
    (22, 3.76, 6.30, "Walaupun ada halangan yang hampir ngebunuh proyek ini,",
     "Even though blockades nearly killed this project,"),
    (23, 6.70, 8.62, "pada akhirnya semuanya lancar.", "in the end it went well."),
    (23, 8.66, 11.02, "Kalau kalian masih tertarik sama perjalanan gua,",
     "If you're still interested in this journey of mine,"),
    (24, 11.34, 12.70, "tinggal like dan follow aja ya.", "just like and follow."),
    (25, 13.24, 14.34, "Sampai jumpa lain waktu.", "I'll see you next time."),
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


def check_lengths() -> list[str]:
    """Guard the two-line rule: a line over MAX_LINE wraps into a third row."""
    problems = []
    for i, (_, _, _, id_text, en_text) in enumerate(PHRASES):
        for lang, text in (("ID", id_text), ("EN", en_text)):
            if len(text) > MAX_LINE:
                problems.append(f"cue {i} {lang} is {len(text)} chars: {text}")
    return problems


def main() -> None:
    problems = check_lengths()
    for p in problems:
        print(f"  WARN over {MAX_LINE} chars -> {p}")

    lines = [ASS_HEADER]
    prev_end = -1.0
    for seg_idx, src_s, src_e, id_text, en_text in PHRASES:
        o_s, o_e = out(src_s, seg_idx), out(src_e, seg_idx)
        if o_s < prev_end - 0.001:
            print(f"  WARN overlapping cue at {o_s:.2f} (prev ended {prev_end:.2f})")
        prev_end = o_e
        cue = f"{{\\c&HFFFFFF&}}{id_text}\\N{{\\c&H00FFFF&}}{en_text}"
        lines.append(f"Dialogue: 0,{ts(o_s)},{ts(o_e)},BL,,0,0,0,,{cue}")
        lines.append("")

    out_path = os.path.join(os.path.dirname(__file__), "master_v1.ass")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Written: {out_path} ({len(PHRASES)} cues, {len(problems)} warnings)")


if __name__ == "__main__":
    main()
