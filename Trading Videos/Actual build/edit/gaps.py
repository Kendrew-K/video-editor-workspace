"""Dump word-level timeline + silence gaps per source. Read-only diagnostic."""
import json, sys, pathlib

TDIR = pathlib.Path(__file__).parent / "transcripts"
MIN_GAP = float(sys.argv[1]) if len(sys.argv) > 1 else 0.30
only = sys.argv[2] if len(sys.argv) > 2 else None

for jf in sorted(TDIR.glob("*.json")):
    if only and only not in jf.stem:
        continue
    d = json.loads(jf.read_text(encoding="utf-8"))
    words = [w for w in d["words"] if w.get("type") == "word"]
    print(f"\n=== {jf.stem} ({len(words)} words) ===")
    prev_end = None
    line = []
    for w in words:
        gap = None if prev_end is None else w["start"] - prev_end
        if gap is not None and gap >= MIN_GAP:
            print("  " + " ".join(line))
            print(f"  --- GAP {gap:.2f}s  [{prev_end:.2f} -> {w['start']:.2f}] ---")
            line = []
        line.append(f"{w['text']}({w['start']:.2f}-{w['end']:.2f})")
        prev_end = w["end"]
    if line:
        print("  " + " ".join(line))
