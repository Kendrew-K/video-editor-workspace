"""Synthesize the small UI sound effects for Build reel 1 v3 into edit/sfx/*.wav.

numpy-only (no scipy dependency on this machine). All mono 48 kHz 16-bit,
peak-normalized to 0.9 — final loudness set per-event by the `gain` field
in edl_v3.json's `sfx` list, mixed by render_v3.py AFTER loudnorm so the
speech normalization can't squash them.
"""

import os
import wave

import numpy as np

SR = 48000
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfx")
os.makedirs(OUT, exist_ok=True)


def write_wav(name, x):
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.9
    pcm = (x * 32767).astype(np.int16)
    with wave.open(os.path.join(OUT, name), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("sfx:", name)


def t_axis(dur):
    return np.linspace(0, dur, int(SR * dur), endpoint=False)


# whoosh: noise burst, brightness swept by a moving 1-pole filter, up-down env
t = t_axis(0.35)
noise = np.random.default_rng(42).standard_normal(len(t))
# one-pole lowpass with time-varying coefficient (dark -> bright -> dark)
sweep = 0.25 + 0.65 * np.sin(np.pi * t / t[-1])
y = np.zeros_like(noise)
acc = 0.0
for i in range(len(noise)):
    acc += sweep[i] * (noise[i] - acc)
    y[i] = acc
env = np.clip(np.sin(np.pi * t / t[-1]), 0, None) ** 1.5
write_wav("whoosh.wav", y * env)

# pop: sine pitch-drop 620->170 Hz, sharp exponential decay
t = t_axis(0.16)
freq = 620 * (170 / 620) ** (t / t[-1])
phase = 2 * np.pi * np.cumsum(freq) / SR
write_wav("pop.wav", np.sin(phase) * np.exp(-22 * t))

# error: two short low square-ish buzzes (minor-second drop reads as "wrong")
t = t_axis(0.09)
n1 = np.tanh(3 * np.sin(2 * np.pi * 220 * t)) * np.exp(-8 * t)
n2 = np.tanh(3 * np.sin(2 * np.pi * 185 * t)) * np.exp(-8 * t)
gap = np.zeros(int(SR * 0.03))
write_wav("error.wav", np.concatenate([n1, gap, n2]))

# thud: 85 Hz sine body + click transient, fast decay (stamp impact)
t = t_axis(0.30)
body = np.sin(2 * np.pi * 85 * t * (1 - 0.25 * t)) * np.exp(-14 * t)
click = np.random.default_rng(7).standard_normal(int(SR * 0.012)) * 0.5
body[: len(click)] += click
write_wav("thud.wav", body)

# ding: 880 + 1320 Hz (fifth) with slow decay (success check)
t = t_axis(0.6)
ding = (np.sin(2 * np.pi * 880 * t) + 0.5 * np.sin(2 * np.pi * 1320 * t)) * np.exp(-6 * t)
write_wav("ding.wav", ding)
