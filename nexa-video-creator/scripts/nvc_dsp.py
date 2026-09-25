#!/usr/bin/env python3
"""Speech activity, word snapping and mic levels for nexa-video-creator (runs in the skill venv, needs numpy).

    python nvc_dsp.py activity AUDIO            -> [[start, end], ...] speech runs in seconds
    python nvc_dsp.py snap AUDIO WORDS.json     -> the words with their pause edges measured
    python nvc_dsp.py levels AUDIO              -> speech and noise level, SNR, high-frequency share, clipped samples

Snapping (measured on a synthetic 28-phrase test in the research, 2026-09-25): whisper.cpp word edges were 170 to 263 ms
off (median); letting every measured pause claim the nearest word boundary brought them to 2 to 4 ms (p90 7 to 9 ms).
"""
import json
import subprocess
import sys

import numpy as np

SR, HOP = 16000, 160   # 10 ms frames


def decode(path, sr=SR, extra_filter="highpass=f=80"):
    cmd = ["ffmpeg", "-v", "error", "-nostdin", "-i", path, "-map", "0:a:0", "-ac", "1", "-ar", str(sr)]
    if extra_filter:
        cmd += ["-af", extra_filter]
    raw = subprocess.run(cmd + ["-f", "f32le", "-"], stdout=subprocess.PIPE, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def frame_db(x):
    n = len(x) // HOP
    if n == 0:
        return np.zeros(0)
    return 10 * np.log10(1e-12 + np.mean(x[: n * HOP].reshape(n, HOP) ** 2, axis=1))


def activity(path, over_floor_db=15.0):
    """Speech runs from frame energy: 15 dB over the noise floor (and no lower than 45 dB under the loud frames),
    gaps under 80 ms closed, blips under 40 ms dropped. Clean voice works well; very noisy rooms need a VAD model."""
    db = frame_db(decode(path))
    if len(db) == 0:
        return []
    on = db > max(np.percentile(db, 10) + over_floor_db, np.percentile(db, 95) - 45)
    edges = np.flatnonzero(np.diff(np.concatenate([[0], on.astype(int), [0]])))
    runs = [[int(a), int(b)] for a, b in zip(edges[::2], edges[1::2])]
    merged = []
    for a, b in runs:
        if merged and a - merged[-1][1] < 8:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    return [[round(a * HOP / SR, 3), round(b * HOP / SR, 3)] for a, b in merged if b - a >= 4]


def snap(words, runs, min_gap=0.12, reach=0.6):
    """words: [{"start", "end", ...}] in time order. Each measured pause (a gap between runs of at least min_gap)
    claims the closest word boundary within `reach` seconds, and that boundary takes the pause edges. The first and
    last words take the outer activity edges when they are within a second of them."""
    w = [dict(x) for x in words]
    gaps = [(runs[k][1], runs[k + 1][0]) for k in range(len(runs) - 1) if runs[k + 1][0] - runs[k][1] >= min_gap]
    used = set()
    for g0, g1 in gaps:
        centre = (g0 + g1) / 2
        best, best_d = None, reach
        for b in range(len(w) - 1):
            d = abs((w[b]["end"] + w[b + 1]["start"]) / 2 - centre)
            if d < best_d and b not in used:
                best, best_d = b, d
        if best is not None:
            used.add(best)
            w[best]["end"], w[best + 1]["start"] = round(g0, 3), round(g1, 3)
            w[best]["pause_after"] = round(g1 - g0, 3)
    if runs and w:
        if abs(w[0]["start"] - runs[0][0]) < 1.0:
            w[0]["start"] = round(runs[0][0], 3)
        if abs(w[-1]["end"] - runs[-1][1]) < 1.0:
            w[-1]["end"] = round(runs[-1][1], 3)
    for item in w:                       # keep every word at least 20 ms long and in order
        if item["end"] < item["start"] + 0.02:
            item["end"] = round(item["start"] + 0.02, 3)
    return w


def levels(path):
    """Numbers for picking the best microphone among recordings of the same talk."""
    full = decode(path)
    db = frame_db(full)
    if len(db) == 0:
        return {"speech_db": None, "noise_db": None, "snr_db": None, "hf_share": 0.0, "clipped": 0,
                "speech_share": 0.0}
    speech_db, noise_db = float(np.percentile(db, 90)), float(np.percentile(db, 10))
    runs = activity(path)
    speech_s = sum(b - a for a, b in runs)
    duration = len(full) / SR
    high = decode(path, extra_filter="highpass=f=5000")
    n = min(len(high), len(full)) // HOP
    on = np.zeros(n, bool)
    for a, b in runs:
        on[int(a * 100): int(b * 100)] = True
    p_full = np.mean(full[: n * HOP].reshape(n, HOP) ** 2, axis=1)
    p_high = np.mean(high[: n * HOP].reshape(n, HOP) ** 2, axis=1)
    hf = float(np.sum(p_high[on]) / max(np.sum(p_full[on]), 1e-12)) if on.any() else 0.0
    native = decode(path, sr=48000, extra_filter=None)
    clipped = int(np.sum(np.abs(native) >= 0.999))
    return {"speech_db": round(speech_db, 1), "noise_db": round(noise_db, 1), "snr_db": round(speech_db - noise_db, 1),
            "hf_share": round(hf, 4), "clipped": clipped, "speech_share": round(speech_s / max(duration, 1e-9), 3),
            "duration_s": round(duration, 3)}


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, path = sys.argv[1], sys.argv[2]
    if cmd == "activity":
        out = activity(path)
    elif cmd == "snap":
        with open(sys.argv[3], encoding="utf-8") as handle:
            words = json.load(handle)
        out = snap(words, activity(path))
    elif cmd == "levels":
        out = levels(path)
    else:
        sys.exit("unknown command: " + cmd)
    json.dump(out, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
