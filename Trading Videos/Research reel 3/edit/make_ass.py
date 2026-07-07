"""Generate master_v1.ass for Research reel 3 — dual EN/ID bilingual subtitles.

Single-cue approach (matches Reel 2): one Dialogue line per phrase, ID+EN
separated by \\N with inline color overrides. Guarantees exactly 2 lines on
screen — never 4.
"""

import os

def ts(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"

# (clip, src_start, src_end, output_offset)
SEGMENTS = [
    ("IMG_0982", 1.92,  6.98,  0.00),   # 0  INTRO
    ("IMG_0983", 1.88,  8.40,  5.06),   # 1  FACTOR_ZOO
    ("IMG_0984", 1.66,  9.64, 11.58),   # 2  REPLICATION
    ("IMG_0985", 1.60, 10.08, 19.56),   # 3  NEURAL_NET
    ("IMG_0988", 1.96,  7.90, 28.04),   # 4  RESULT_NN
    ("IMG_0989", 1.78,  8.34, 33.98),   # 5  RL_INTRO
    ("IMG_0991", 1.82,  7.00, 40.54),   # 6  RL_MECHANISM
    ("IMG_0992", 1.10,  6.92, 45.72),   # 7  RESULT_RL
    ("IMG_0993", 1.48,  8.88, 51.54),   # 8  WHY_NOT
    ("IMG_0996", 2.36,  8.50, 58.94),   # 9  CAVEAT_1
    ("IMG_0997", 1.84,  7.64, 65.08),   # 10 CAVEAT_2
    ("IMG_0998", 1.68, 17.54, 70.88),   # 11 TEASE_OUTRO
]

def out(src_time, seg_idx):
    _, seg_start, _, offset = SEGMENTS[seg_idx]
    return src_time - seg_start + offset

# (seg_idx, src_start, src_end, id_text, en_text)
# ID line first (top), EN line second (bottom) — separated by \N in output.
# Each line ≤55 chars so it never wraps.
# Cues must NOT overlap within the same segment (fixed RL_INTRO overlap).
PHRASES = [
    # INTRO
    (0, 1.92, 4.20,
     "Hari ke-4 sudah tiba —",
     "Day 4 is here —"),
    (0, 4.20, 6.98,
     "kita masuk ke ML dan neural network.",
     "diving into ML and neural networks."),

    # FACTOR ZOO
    (1, 1.88, 3.22,
     "Dalam 50 tahun terakhir,",
     "In the last 50 years,"),
    (1, 3.70, 6.52,
     "ilmuwan menemukan ratusan faktor",
     "scientists discovered hundreds of factors"),
    (1, 6.60, 8.40,
     "yang mempengaruhi pasar saham.",
     "that affect the stock market."),

    # REPLICATION
    (2, 1.66, 4.42,
     "Namun, 65% dari faktor itu",
     "However, 65% of those factors"),
    (2, 4.46, 6.42,
     "hanyalah noise yang tak bisa direplikasi.",
     "are just noise — can't be replicated."),
    (2, 7.06, 9.64,
     "Seperti ditunjukkan paper 2020 ini.",
     "As shown by this 2020 research paper."),

    # NEURAL NET
    (3, 1.60, 3.54,
     "Daripada menebak tiap faktor,",
     "So instead of guessing each factor,"),
    (3, 3.90, 5.42,
     "ilmuwan pakai neural network —",
     "scientists used a neural network —"),
    (3, 5.78, 7.98,
     "sistem yang meniru otak manusia,",
     "a system replicating the human brain,"),
    (3, 8.06, 10.08,
     "menggunakan lapisan node, atau neuron.",
     "using layers of nodes, or neurons."),

    # RESULT NN
    (4, 1.96, 3.34,
     "Mereka menemukan bahwa",
     "They found that"),
    (4, 3.68, 6.08,
     "sistem ini menaikkan Sharpe Ratio",
     "this system raised the Sharpe Ratio"),
    (4, 6.06, 7.90,
     "dan R² hampir dua kali lipat!",
     "and R² by almost double!"),

    # RL INTRO — fixed: first phrase ends at 2.58 (where second starts)
    (5, 1.78, 2.58,
     "Mereka pun mencoba",
     "They also tried"),
    (5, 2.58, 3.76,
     "sistem reinforcement learning —",
     "reinforcement learning —"),
    (5, 4.26, 6.14,
     "memberi reward kalau cuan,",
     "rewards agents for profit,"),
    (5, 6.74, 8.34,
     "menghukum kalau rugi.",
     "penalizes them for losses."),

    # RL MECHANISM
    (6, 1.82, 4.06,
     "Dengan sistem ini, agen belajar",
     "With this system, agents learn"),
    (6, 4.16, 7.00,
     "pola-pola agar cuan sesering mungkin.",
     "patterns to profit as often as possible."),

    # RESULT RL
    (7, 1.10, 2.90,
     "Sistem ini mencapai",
     "This system secured"),
    (7, 2.96, 6.92,
     "Sharpe 2.0  ·  alpha 13% out-of-sample.",
     "Sharpe 2.0  ·  out-of-sample alpha 13%."),

    # WHY NOT
    (8, 1.48, 3.52,
     "Kita sudah bahas dua sistem —",
     "We've discussed two systems —"),
    (8, 3.82, 6.86,
     "keduanya punya Sharpe dan R² tinggi.",
     "both show high Sharpe and R²."),
    (8, 7.34, 8.88,
     "Jadi kenapa tidak semua orang pakai?",
     "So why doesn't everyone use them?"),

    # CAVEAT 1
    (9, 2.36, 4.90,
     "Masalahnya, riset ini masih mentah.",
     "The problem: results are still raw."),
    (9, 5.34, 8.50,
     "Belum ada biaya transaksi & crowding.",
     "No transaction costs or crowding factored in."),

    # CAVEAT 2
    (10, 1.84, 2.92,
     "Strategi memang penting,",
     "Strategy is important,"),
    (10, 3.28, 5.90,
     "tapi kalau semua pakai strategi yang sama,",
     "but if everyone uses the same strategy,"),
    (10, 6.42, 7.64,
     "hilang sudah edge-mu.",
     "there goes your edge."),

    # TEASE / OUTRO
    (11, 1.68, 3.36,
     "Tapi ini semua hanya angka.",
     "But these are all just numbers."),
    (11, 3.86, 4.74,
     "Di video selanjutnya,",
     "In the next video,"),
    (11, 4.96, 8.26,
     "gua akan bahas gimana AI Agent",
     "I'll cover how AI Agents work"),
    (11, 8.40, 10.48,
     "bisa membaca berita otomatis",
     "to read news automatically"),
    (11, 10.60, 12.86,
     "dan buat keputusan seperti hedge fund.",
     "and make decisions like a real hedge fund."),
    (11, 13.70, 14.32,
     "This is Kendrew,",
     "This is Kendrew,"),
    (11, 15.10, 16.00,
     "sampai jumpa di video selanjutnya!",
     "see you on the next video!"),
]

# Single BL style — ID (white) + EN (yellow) on one cue via \N.
# MarginV=200 positions the block low (below chin). Matches Reel 2 layout.
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
    # ID white (top line) \N EN yellow (bottom line) — inline color tags
    cue = f"{{\\c&HFFFFFF&}}{id_text}\\N{{\\c&H00FFFF&}}{en_text}"
    lines.append(f"Dialogue: 0,{ts(o_s)},{ts(o_e)},BL,,0,0,0,,{cue}")
    lines.append("")

out_path = os.path.join(os.path.dirname(__file__), "master_v1.ass")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"Written: {out_path}")
