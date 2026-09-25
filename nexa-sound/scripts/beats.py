"""nexa-sound beat grid: tempo, beats and downbeats in plain Python on envelopes that ffmpeg decodes (no numpy).

1. ffmpeg decodes the track to mono 16-bit at 8 kHz twice: the full band, and low-passed at 150 Hz (the kick).
2. Log energy every 10 ms (each 10 ms mean square smoothed over its neighbours, a 30 ms window, so bass notes and
   beating chords do not ripple into false onsets); onset strength is the positive part of its first difference.
3. Tempo: autocorrelation of the onset strength over 60 to 200 BPM, weighted by a Gaussian (in octaves) around the
   BPM the brief asked for (Lyria follows the requested tempo closely), so half and double tempo resolve toward the
   request. Without a request the weight is a wide one around 120 BPM.
4. Beat phase: a comb sum of onset strength at phase + k x period over the whole track (2 frames either side), the
   best phase wins; the period is refined on the same comb, then by a least-squares line through the matched onsets.
5. Downbeat: of the 4 possible bar phases, the one with the most low-band (kick) onset on its beats.
6. The whole grid is nudged by the median offset of 1 ms onset estimates around the beats (a 10 ms frame alone
   leaves up to 10 ms of bias).

The grid is steady (one tempo for the whole track), which suits generated music; `confidence` (the share of beats
with a real onset near them) says when it does not fit. 4/4 is assumed: one bar lasts 240 / BPM seconds.

    python3 beats.py TRACK [--bpm 104] [--json]
"""
import argparse
import json
import math
import operator
import shutil
import subprocess
import sys
from array import array

RATE = 8000
HOP = 80                 # 10 ms frames
FPS = RATE // HOP        # 100 frames a second
BPM_MIN, BPM_MAX = 60.0, 200.0


class BeatError(Exception):
    pass


def decode(path, lowpass=None, ffmpeg=None):
    """Mono signed 16-bit samples at 8 kHz, optionally low-passed (4 poles) first."""
    ff = ffmpeg or shutil.which("ffmpeg")
    if not ff:
        raise BeatError("ffmpeg was not found")
    cmd = [ff, "-v", "error", "-nostdin", "-i", str(path), "-map", "0:a:0", "-ac", "1"]
    if lowpass:
        cmd += ["-af", "lowpass=f=%g,lowpass=f=%g" % (lowpass, lowpass)]
    cmd += ["-ar", str(RATE), "-f", "s16le", "-"]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        raise BeatError("ffmpeg could not decode %s: %s" % (path, r.stderr.decode("utf-8", "replace")[-300:]))
    x = array("h")
    x.frombytes(r.stdout[: len(r.stdout) // 2 * 2])
    if sys.byteorder == "big":
        x.byteswap()
    return x


def frame_log_energy(x, hop=HOP, floor_db=-60.0):
    """Natural-log energy every 10 ms, floored 60 dB under the loudest frame (so silence makes no onsets).

    Each 10 ms mean square is smoothed with the centred kernel [1, 2, 1] / 4 (a 30 ms window). Without it, bass notes
    and beating chords make the frame energy ripple (a 60 Hz sine ripples at 120 Hz, two close partials beat at 50 Hz
    or so) and every ripple reads as an onset; the kernel's zero sits exactly at 50 Hz in the frame domain."""
    mul = operator.mul
    n = len(x) // hop
    ms = []
    for i in range(n):
        seg = x[i * hop:(i + 1) * hop]
        ms.append(sum(map(mul, seg, seg)) / float(hop))
    if n >= 3:
        ms = [ms[0]] + [0.25 * ms[i - 1] + 0.5 * ms[i] + 0.25 * ms[i + 1] for i in range(1, n - 1)] + [ms[-1]]
    top = max(ms) if ms else 0.0
    eps = max(top * 10 ** (floor_db / 10.0), 1e-9)
    return [math.log(v + eps) for v in ms]


def onset_strength(e):
    return [0.0] + [max(0.0, e[i] - e[i - 1]) for i in range(1, len(e))]


def _maxfilter(o, r=2):
    n = len(o)
    return [max(o[max(0, i - r):min(n, i + r + 1)]) for i in range(n)]


def _parabolic(y, i):
    if 0 < i < len(y) - 1:
        den = y[i - 1] - 2.0 * y[i] + y[i + 1]
        if den != 0:
            return i + 0.5 * (y[i - 1] - y[i + 1]) / den
    return float(i)


def tempo(onset, bpm_hint=None):
    """(period in frames, raw autocorrelation dict) for the most likely beat period."""
    mean = sum(onset) / max(1, len(onset))
    oc = [v - mean for v in onset]
    lo = int(math.floor(60.0 * FPS / BPM_MAX))
    hi = int(math.ceil(60.0 * FPS / BPM_MIN))
    mul = operator.mul
    ac = {}
    for lag in range(lo - 1, hi + 2):
        if lag < 1 or lag >= len(oc):
            continue
        ac[lag] = sum(map(mul, oc[:-lag], oc[lag:])) / float(len(oc) - lag)
    if not ac:
        raise BeatError("the track is too short for a tempo")
    prior, sigma = (float(bpm_hint), 0.3) if bpm_hint else (120.0, 1.0)

    def weight(lag):
        return math.exp(-0.5 * (math.log2(60.0 * FPS / lag / prior) / sigma) ** 2)

    best = max((lag for lag in ac if lo <= lag <= hi), key=lambda lag: max(ac[lag], 0.0) * weight(lag))
    lags = sorted(ac)
    ys = [ac[k] for k in lags]
    return _parabolic(ys, lags.index(best)) + lags[0], ac


def _comb(omax, period, phase):
    n = len(omax)
    total = 0.0
    t = phase
    while t < n - 0.5:
        total += omax[int(t + 0.5)]
        t += period
    return total


def grid(onset, period):
    """(phase, period) of the beat grid: comb search over phase and a narrow band of periods, then a least-squares
    fit through the onsets found near the predicted beats."""
    omax = _maxfilter(onset, 2)
    best = (-1.0, 0.0, period)
    steps = 31
    for s in range(steps):
        p = period * (0.985 + 0.03 * s / (steps - 1))
        ph = 0.0
        while ph < p:
            c = _comb(omax, p, ph)
            if c > best[0]:
                best = (c, ph, p)
            ph += 1.0
    _, phase, period = best
    peaks = sorted(v for v in onset if v > 0)
    thr = peaks[int(len(peaks) * 0.5)] if peaks else 0.0
    n = len(onset)
    for _ in range(3):
        ks, ts = [], []
        k0 = -int(phase // period)
        k = k0
        while phase + k * period < n - 1:
            b = phase + k * period
            i0, i1 = max(0, int(b) - 3), min(n, int(b) + 4)
            if i1 - i0 >= 3:
                j = max(range(i0, i1), key=onset.__getitem__)
                if onset[j] > thr:
                    ks.append(k)
                    ts.append(_parabolic(onset, j))
            k += 1
        if len(ks) < 4:
            break
        for _trim in range(2):
            m = len(ks)
            mk, mt = sum(ks) / m, sum(ts) / m
            sxx = sum((a - mk) ** 2 for a in ks)
            if sxx == 0:
                break
            slope = sum((a - mk) * (b - mt) for a, b in zip(ks, ts)) / sxx
            icpt = mt - slope * mk
            keep = [(a, b) for a, b in zip(ks, ts) if abs(b - (icpt + slope * a)) <= 2.0]
            if len(keep) < 4 or len(keep) == m:
                break
            ks, ts = [a for a, _ in keep], [b for _, b in keep]
        if not (0.9 * period < slope < 1.1 * period):
            break
        period, phase = slope, icpt % slope
    return phase, period


def fine_offset(x, beat_times, rate=RATE, window=0.04):
    """Median distance (s) from each beat to the steepest 1 ms energy rise within +-40 ms of it."""
    blk = rate // 1000
    mul = operator.mul
    offs = []
    for t in beat_times:
        c = int(t * rate)
        a, b = c - int(window * rate) - 4 * blk, c + int(window * rate) + 4 * blk
        if a < 0 or b > len(x):
            continue
        seg = x[a:b]
        e = []
        for i in range(0, len(seg) - blk + 1, blk):
            s = seg[i:i + blk]
            e.append(math.log(sum(map(mul, s, s)) / blk + 1.0))
        best, rise = None, 0.0
        for j in range(4, len(e) - 4):
            r = sum(e[j:j + 4]) / 4.0 - sum(e[j - 4:j]) / 4.0
            if r > rise:
                best, rise = j, r
        if best is not None and rise > 0.7:        # about 3 dB of rise
            offs.append((a + best * blk) / float(rate) - t)
    if len(offs) < 4:
        return 0.0, len(offs)
    offs.sort()
    return offs[len(offs) // 2], len(offs)


def analyze(path, bpm_hint=None, ffmpeg=None, beats_per_bar=4):
    """The beat grid of a track: {"bpm", "beats", "downbeats", "confidence", ...} with times in seconds."""
    full = decode(path, ffmpeg=ffmpeg)
    low = decode(path, lowpass=150, ffmpeg=ffmpeg)
    duration = len(full) / float(RATE)
    if duration < 3.0:
        raise BeatError("the track is %.1f s long; a beat grid needs at least 3 s" % duration)
    onset = onset_strength(frame_log_energy(full))
    lag, _ = tempo(onset, bpm_hint)
    phase, period = grid(onset, lag)
    # frame index -> seconds: a frame's onset sits somewhere inside it; its centre is the unbiased guess
    to_s = 1.0 / FPS
    first = phase % period
    beats_f = []
    b = first
    while b * to_s + 0.5 * to_s < duration:
        beats_f.append(b)
        b += period
    times = [(f + 0.5) * to_s for f in beats_f]
    shift, used = fine_offset(full, times)
    if abs(shift) <= 0.02:
        times = [t + shift for t in times]
    # a phase a hair before frame 0 wraps to the next beat: put back any beat that falls at the very start
    step = period * to_s
    while times and times[0] - step > -0.03:
        times.insert(0, times[0] - step)
    times = [max(0.0, t) for t in times if -0.03 < t < duration]
    if len(times) < beats_per_bar:
        raise BeatError("too few beats for a bar grid")
    # downbeat phase: most low-band onset on its beats
    onset_low = onset_strength(frame_log_energy(low))
    olow = _maxfilter(onset_low, 2)
    scores = [0.0] * beats_per_bar
    counts = [0] * beats_per_bar
    for k, t in enumerate(times):
        i = int(t * FPS)
        if 0 <= i < len(olow):
            scores[k % beats_per_bar] += olow[i]
            counts[k % beats_per_bar] += 1
    means = [s / c if c else 0.0 for s, c in zip(scores, counts)]
    down = max(range(beats_per_bar), key=means.__getitem__)
    others = [m for i, m in enumerate(means) if i != down]
    down_conf = (means[down] - sum(others) / len(others)) / means[down] if means[down] > 0 else 0.0
    # confidence: share of beats with a real onset within 2 frames
    omax = _maxfilter(onset, 2)
    peaks = sorted(v for v in onset if v > 0)
    thr = peaks[int(len(peaks) * 0.5)] if peaks else 0.0
    hits = sum(1 for t in times if omax[min(len(omax) - 1, int(t * FPS))] > thr)
    bpm = 60.0 * FPS / period
    return {
        "bpm": round(bpm, 2),
        "period_s": round(period / FPS, 5),
        "bar_s": round(beats_per_bar * period / FPS, 5),
        "beats_per_bar": beats_per_bar,
        "beats": [round(t, 4) for t in times],
        "downbeats": [round(t, 4) for t in times[down::beats_per_bar]],
        "first_downbeat_s": round(times[down], 4),
        "confidence": round(hits / float(len(times)), 3),
        "downbeat_confidence": round(max(0.0, down_conf), 3),
        "fine_shift_ms": round(shift * 1000, 2) if abs(shift) <= 0.02 else 0.0,
        "duration_s": round(duration, 3),
        "bpm_hint": bpm_hint,
        "method": "onset autocorrelation + comb + least squares (10 ms frames, 1 ms refinement), 4/4 assumed",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Tempo, beats and downbeats of a music track (4/4).")
    ap.add_argument("track")
    ap.add_argument("--bpm", type=float, help="the tempo the brief asked for (resolves half and double tempo)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        r = analyze(a.track, a.bpm)
    except BeatError as err:
        print("beats: %s" % err, file=sys.stderr)
        sys.exit(1)
    if a.json:
        print(json.dumps(r))
    else:
        print("%.2f BPM, bar %.3f s, first downbeat %.3f s, %d beats, confidence %.2f" % (
            r["bpm"], r["bar_s"], r["first_downbeat_s"], len(r["beats"]), r["confidence"]))


if __name__ == "__main__":
    main()
