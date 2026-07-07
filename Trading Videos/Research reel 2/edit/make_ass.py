"""Generate master_v1.ass for Research reel 2 (Day 3 — Alternative Data).

Bilingual: Indonesian (white, top) + English (yellow/gold, bottom).
Output-timeline offsets derived from edl_v1.json (Hard Rule 5).
MarginV tuned for the reframed layout (head sits low-center; subs go below chin).
"""

import json, os

EDIT = os.path.dirname(__file__)
EDL = json.load(open(os.path.join(EDIT, "edl_v1.json"), encoding="utf-8"))

# Build per-source segment offset + src_start from the EDL ranges (in order).
offsets = {}      # source -> output offset (s)
src_starts = {}   # source -> EDL range start (s)
acc = 0.0
for r in EDL["ranges"]:
    s, e = float(r["start"]), float(r["end"])
    offsets[r["source"]] = acc
    src_starts[r["source"]] = s
    acc += (e - s)
TOTAL = acc


def ts(sec: float) -> str:
    h = int(sec // 3600); m = int((sec % 3600) // 60); s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def out_t(source: str, src_time: float) -> float:
    return src_time - src_starts[source] + offsets[source]


# Cues: (source, src_start, src_end, id_text, en_text)
# Times are seconds into the raw clip (from the cached transcripts / takes_packed).
CUES = [
    # INTRO
    ("IMG_0938", 2.26, 5.16,
     "Selamat datang di hari ketiga dari series gua.",
     "Welcome to day three of my series."),

    ("IMG_0947", 1.76, 6.20,
     "Pernahkah kau penasaran gimana perusahaan besar bisa memprediksi harga saham sebelum berita keluar?",
     "Ever wondered how big firms predict stock prices before the news drops?"),
    ("IMG_0947", 6.20, 10.46,
     "Jawabannya ada di video ini.",
     "The answer is in this video."),

    # TECH A — SATELLITE
    ("IMG_0949", 2.16, 6.20,
     "Lu pikir ke supermarket gak ada yang lacak? Mana ada, bos!",
     "Think nobody tracks you at the supermarket? No chance, boss!"),

    ("IMG_0951", 1.92, 6.60,
     "Hedge fund pakai satelit buat melacak kondisi parkiran di lebih dari 67 ribu toko,",
     "Hedge funds use satellites to track parking lots at 67,000+ stores,"),
    ("IMG_0951", 6.60, 11.24,
     "biar mereka tahu seberapa laku toko-toko ini.",
     "so they know how well these stores are selling."),

    ("IMG_0952", 1.48, 7.76,
     "Mereka juga beli data transaksi buat merekonstruksi omzet perusahaan sebelum datanya keluar.",
     "They also buy transaction data to rebuild a firm's revenue before it's released."),

    ("IMG_0955", 1.96, 7.94,
     "Menurut laporan, fund yang pakai cara ini bisa menaikkan akurasi mereka sampai 10%.",
     "Reportedly, funds using this lift their accuracy by up to 10%."),

    # TECH B — WEB SCRAPING
    ("IMG_0956", 1.74, 6.94,
     "Kalau online gimana? Perusahaan pakai sesuatu yang disebut web scraping.",
     "What about online? Companies deploy something called web scraping."),

    ("IMG_0957", 1.94, 8.78,
     "Alat yang bisa mengeruk jutaan halaman web: lowongan kerja, harga produk, sampai jumlah download.",
     "A tool that scrapes millions of pages: job listings, prices, even download counts."),

    ("IMG_0960", 1.62, 5.40,
     "Semua ini adalah faktor pertumbuhan sebuah perusahaan atau ekonomi.",
     "All of these are factors of growth in a company or the economy."),
    ("IMG_0960", 5.40, 9.96,
     "Contohnya, naiknya lowongan kerja bisa menandakan industri yang sedang tumbuh.",
     "For example, more job listings can signal a growing industry."),

    # TECH C — GOOGLE TRENDS
    ("IMG_0962", 1.98, 6.26,
     "Nah, yang ini mungkin paling relevan buat kita: Google Trends.",
     "Now this may be the most applicable to us: Google Trends."),

    ("IMG_0964", 2.32, 6.40,
     "Volume orang yang mencari kata kunci seperti ‘tarif’ atau ‘utang’",
     "The volume of people searching keywords like ‘tariff’ or ‘debt’"),
    ("IMG_0964", 6.40, 10.04,
     "bisa jadi peringatan kalau ada gerakan besar di bawah pasar.",
     "can warn us a big move is brewing under the market."),

    ("IMG_0965", 1.64, 5.88,
     "Masalahnya, informasi ini terlalu publik sampai hampir bukan keunggulan.",
     "The problem is, this info is so public it's barely an edge."),

    # RECAP / TEASE
    ("IMG_0967", 1.48, 5.34,
     "Ya, pada akhirnya, semua teknik ini cuma soal data mentah.",
     "Yeah, at the end of the day, these are all just raw data."),

    ("IMG_0970", 2.22, 6.14,
     "Buat benar-benar memakai data ini, kita perlu yang namanya machine learning,",
     "To actually use this data, we need something called machine learning,"),
    ("IMG_0970", 6.14, 10.72,
     "di video selanjutnya. Peace.",
     "in the next video. Peace."),
]

# One Dialogue event per cue (ID white line + EN gold line via inline color).
# A single event avoids libass collision-avoidance reordering the two language
# lines when both wrap to 2 lines (observed swapping in v1). Block is bottom-
# anchored (Alignment 2) so it grows upward and always clears the chin.
WHITE_TAG = r"{\c&HFFFFFF&}"
GOLD_TAG  = r"{\c&H50C8F5&}"   # ASS BGR -> R245 G200 B80 gold

HEADER = """\
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: BL,Arial,32,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,3,1,2,36,36,200,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

lines = [HEADER]
for source, s, e, id_, en in CUES:
    o_s, o_e = out_t(source, s), out_t(source, e)
    text = f"{WHITE_TAG}{id_}\\N{GOLD_TAG}{en}"
    lines.append(f"Dialogue: 0,{ts(o_s)},{ts(o_e)},BL,,0,0,0,,{text}")
    lines.append("")

out_path = os.path.join(EDIT, "master_v1.ass")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"Written: {out_path}  ({len(CUES)} cues, total {TOTAL:.1f}s)")
