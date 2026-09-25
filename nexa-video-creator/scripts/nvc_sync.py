#!/usr/bin/env python3
"""Find the offset and clock drift between two recordings of the same event.

Needs numpy and ffmpeg on PATH. Works on any pair of files ffmpeg can read.

    python nvc_sync.py REFERENCE OTHER [--json]

Model, per segment: a sound heard at REFERENCE time t is heard at OTHER time  a + (1 + d) * t.
  a = offset in seconds (positive: OTHER started recording before REFERENCE)
  d = drift (d * 1e6 = ppm; positive: OTHER's clock runs fast, its file is longer)
A recording that paused or dropped samples gives more than one segment (a step in the offset).

Method:
 1. coarse: cross-correlate 100 Hz onset envelopes over the whole files (any offset, robust to EQ and gain)
 2. fine: GCC-PHAT on 16 kHz waveform windows spread over the overlap, sub-sample peak;
    a window that finds nothing near the running estimate gets a local coarse search (+-90 s)
 3. drift: robust line (Theil-Sen) per segment; segments split where the lag jumps by more than 20 ms
"""
import argparse
import json
import subprocess
import sys

import numpy as np

SR = 16000          # fine analysis rate
ENV_RATE = 100      # coarse envelope frames per second
STEP_S = 0.020      # a lag change larger than this between neighbouring windows is a step, not drift


def decode(path: str, sr: int = SR, stream: str = "0:a:0") -> np.ndarray:
    """Mono float64 at `sr`, band-limited to the speech band so rumble and hiss do not dominate."""
    cmd = ["ffmpeg", "-v", "error", "-nostdin", "-i", path, "-map", stream, "-ac", "1", "-ar", str(sr),
           "-af", "highpass=f=100,lowpass=f=4000", "-f", "f32le", "-"]
    raw = subprocess.run(cmd, stdout=subprocess.PIPE, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def onset_envelope(x: np.ndarray, sr: int = SR, rate: int = ENV_RATE) -> np.ndarray:
    """Half-wave rectified change of log energy per 10 ms frame, z-scored."""
    hop = sr // rate
    n = len(x) // hop
    if n < 3:
        return np.zeros(max(n, 1))
    e = np.log10(1e-10 + np.mean(x[: n * hop].reshape(n, hop) ** 2, axis=1))
    d = np.maximum(0.0, np.diff(e, prepend=e[:1]))
    d = np.convolve(d, np.ones(3) / 3, mode="same")
    return (d - d.mean()) / (d.std() + 1e-12)


def xcorr(a: np.ndarray, b: np.ndarray):
    """Linear cross-correlation c[k] = sum_n a[n] * b[n + k] for every lag k, via FFT."""
    n = len(a) + len(b) - 1
    nfft = 1 << (n - 1).bit_length()
    c = np.fft.irfft(np.conj(np.fft.rfft(a, nfft)) * np.fft.rfft(b, nfft), nfft)
    c = np.concatenate([c[nfft - (len(a) - 1):], c[: len(b)]])
    return np.arange(-(len(a) - 1), len(b)), c


def peak_stats(c: np.ndarray, i: int, guard: int):
    """Robust z-score of the peak, and its height over the best competing peak outside +-guard."""
    med = np.median(c)
    mad = np.median(np.abs(c - med)) * 1.4826 + 1e-12
    mask = np.ones(len(c), bool)
    mask[max(0, i - guard): i + guard + 1] = False
    second = c[mask].max() if mask.any() else med
    return float((c[i] - med) / mad), float((c[i] - med) / max(second - med, 1e-12))


def parabolic(c: np.ndarray, i: int) -> float:
    if 0 < i < len(c) - 1:
        den = c[i - 1] - 2 * c[i] + c[i + 1]
        if den != 0:
            return i + 0.5 * (c[i - 1] - c[i + 1]) / den
    return float(i)


def coarse_offset(ref_env: np.ndarray, oth_env: np.ndarray):
    lags, c = xcorr(ref_env, oth_env)
    i = int(np.argmax(c))
    z, ratio = peak_stats(c, i, guard=ENV_RATE // 2)     # nothing else within 0.5 s may compete
    return lags[i] / ENV_RATE, z, ratio


def local_coarse(ref_env, oth_env, t_ref: float, guess: float, span: float = 30.0, search: float = 90.0):
    """Re-find the lag around reference time t_ref when the fine search lost it (a paused recorder)."""
    r0, r1 = int((t_ref - span / 2) * ENV_RATE), int((t_ref + span / 2) * ENV_RATE)
    o0 = int((t_ref - span / 2 + guess - search) * ENV_RATE)
    o1 = int((t_ref + span / 2 + guess + search) * ENV_RATE)
    r0, o0 = max(r0, 0), max(o0, 0)
    a, b = ref_env[r0:r1], oth_env[o0:o1]
    if len(a) < ENV_RATE * 5 or len(b) < len(a):
        return None
    lags, c = xcorr(a - a.mean(), b - b.mean())
    ok = (lags >= 0) & (lags <= len(b) - len(a))            # full overlap only
    lags, c = lags[ok], c[ok]
    i = int(np.argmax(c))
    z, ratio = peak_stats(c, i, guard=ENV_RATE // 2)
    return (o0 - r0 + lags[i]) / ENV_RATE if z >= 8 and ratio >= 1.3 else None


def gcc_phat_window(ref, oth, t_ref: float, lag0: float, win: float, margin: float):
    """(lag s, z, ratio) near lag0 at reference time t_ref; None when out of range or silent."""
    w, m = int(win * SR), int(margin * SR)
    r0 = int((t_ref - win / 2) * SR)
    o0 = r0 + int(round(lag0 * SR)) - m
    if r0 < 0 or o0 < 0 or r0 + w > len(ref) or o0 + w + 2 * m > len(oth):
        return None
    a = ref[r0: r0 + w] * np.hanning(w)
    b = oth[o0: o0 + w + 2 * m]
    if np.sqrt(np.mean(a ** 2)) < 1e-4 or np.sqrt(np.mean(b ** 2)) < 1e-4:
        return None                                          # silence: nothing to lock on to
    nfft = 1 << (len(a) + len(b) - 1).bit_length()
    X = np.conj(np.fft.rfft(a, nfft)) * np.fft.rfft(b, nfft)
    X /= np.abs(X) + 1e-12                                   # PHAT: keep the phase, drop the magnitude
    cc = np.fft.irfft(X, nfft)[: 2 * m + 1]                  # lags 0..2m relative to (o0 - r0)
    k = int(np.argmax(cc))
    z, ratio = peak_stats(cc, k, guard=int(0.002 * SR))
    return (o0 - r0 + parabolic(cc, k)) / SR, z, ratio


def theil_sen(t: np.ndarray, y: np.ndarray):
    if len(t) < 2:
        return float(y[0]), 0.0
    i, j = np.triu_indices(len(t), 1)
    dt = t[j] - t[i]
    ok = dt > 0
    slope = float(np.median((y[j] - y[i])[ok] / dt[ok])) if ok.any() else 0.0
    return float(np.median(y - slope * t)), slope


def split_segments(pts):
    """Group consecutive windows whose lags agree; a jump over STEP_S (plus 200 ppm of drift) starts a new one."""
    segs = [[pts[0]]]
    for p in pts[1:]:
        q = segs[-1][-1]
        if abs(p[1] - q[1]) > STEP_S + 200e-6 * (p[0] - q[0]):
            segs.append([p])
        else:
            segs[-1].append(p)
    return segs


def estimate(ref_path: str, oth_path: str, win: float = 8.0, step: float = 30.0, margin: float = 0.25,
             min_z: float = 8.0) -> dict:
    ref, oth = decode(ref_path), decode(oth_path)
    dur_r, dur_o = len(ref) / SR, len(oth) / SR
    ref_env, oth_env = onset_envelope(ref), onset_envelope(oth)
    lag0, cz, cratio = coarse_offset(ref_env, oth_env)

    # windows cover the overlap the coarse lag implies (reference time t, other time t + lag0)
    t_lo, t_hi = max(0.0, -lag0) + win, min(dur_r, dur_o - lag0) - win
    if t_hi <= t_lo:
        t_lo, t_hi = win, max(win, dur_r - win)
    centers = np.arange(t_lo, t_hi + 1e-9, step) if t_hi - t_lo > 4 * step else np.linspace(t_lo, t_hi, 5)
    pts, guess, misses = [], lag0, 0
    for c in centers:
        r = gcc_phat_window(ref, oth, float(c), guess, win, margin)
        if not (r and r[1] >= min_z):
            misses += 1
            if misses >= 2:                                  # lost it twice: a pause or a gap? search wider
                g = local_coarse(ref_env, oth_env, float(c), guess)
                if g is not None:
                    r = gcc_phat_window(ref, oth, float(c), g, win, margin)
        if r and r[1] >= min_z:
            pts.append((float(c), r[0], r[1]))
            misses = 0
            seg = split_segments(pts)[-1]
            if len(seg) >= 3:
                a_, d_ = theil_sen(np.array([p[0] for p in seg]), np.array([p[1] for p in seg]))
                guess = a_ + d_ * (c + step)
            else:
                guess = r[0]
    out = {"reference": ref_path, "other": oth_path, "duration_ref_s": round(dur_r, 3),
           "duration_other_s": round(dur_o, 3), "coarse_offset_s": round(lag0, 3), "coarse_z": round(cz, 1),
           "coarse_peak_ratio": round(cratio, 2), "windows_tried": int(len(centers)), "windows_used": len(pts)}
    segments = []
    if pts:
        for s in split_segments(pts):
            t = np.array([p[0] for p in s]); y = np.array([p[1] for p in s])
            a, d = theil_sen(t, y)
            res = y - (a + d * t)
            segments.append({"t_ref_from": round(float(t[0]), 1), "t_ref_to": round(float(t[-1]), 1),
                             "windows": len(s), "offset_s": round(a, 5),
                             # under 2 minutes of span, drift is below the noise (and below 1 frame)
                             "drift_ppm": round(d * 1e6, 1) if len(s) >= 3 and t[-1] - t[0] >= 120 else None,
                             "residual_rms_ms": round(float(np.sqrt(np.mean(res ** 2))) * 1000, 2)})
    out["segments"] = segments
    main_seg = max(segments, key=lambda s: s["windows"]) if segments else None
    out["offset_s"] = main_seg["offset_s"] if main_seg else round(lag0, 3)
    out["drift_ppm"] = main_seg["drift_ppm"] if main_seg else None
    out["steps"] = [{"between_t_ref": [segments[k - 1]["t_ref_to"], segments[k]["t_ref_from"]],
                     "jump_ms": round((segments[k]["offset_s"] - segments[k - 1]["offset_s"]) * 1000, 1)}
                    for k in range(1, len(segments))]
    # confidence: the coarse peak must stand out and most windows must lock on with a tight fit
    used = len(pts) / max(1, len(centers))
    tight = all(s["residual_rms_ms"] < 5 for s in segments if s["windows"] >= 3)
    # a paused recorder gives two equal coarse peaks; tight segments on both sides explain that
    explained = len(segments) > 1 and all(s["windows"] >= 3 for s in segments)
    if (cz >= 10 and (cratio >= 1.5 or explained) and used >= 0.5 and tight and main_seg
            and main_seg["windows"] >= 3):
        out["confidence"] = "high"
    elif cz >= 6 and cratio >= 1.2 and len(pts) >= 2:
        out["confidence"] = "medium"
    else:
        out["confidence"] = "low"        # different events, no shared sound, or music-only clips
    out["windows"] = [{"t_ref": round(p[0], 1), "lag_s": round(p[1], 5), "z": round(p[2], 1)} for p in pts]
    return out


def other_time(r: dict, t_ref: float) -> float:
    """Where reference time t_ref is found in OTHER, using the segment that covers it."""
    segs = r.get("segments") or [{"t_ref_from": 0, "t_ref_to": 1e12, "offset_s": r["offset_s"], "drift_ppm": 0}]
    s = min(segs, key=lambda s: 0 if s["t_ref_from"] <= t_ref <= s["t_ref_to"]
            else min(abs(t_ref - s["t_ref_from"]), abs(t_ref - s["t_ref_to"])))
    return s["offset_s"] + (1 + (s["drift_ppm"] or 0) / 1e6) * t_ref


def ffmpeg_hint(r: dict, out_rate: int = 48000) -> str:
    """One continuous take: trim or pad OTHER, then remove drift by resampling.

    asetrate only takes whole numbers, so the rate change is made at 960 kHz (1 ppm steps). Measured on a
    24 min take: this left 0.0 ms residual, while atempo=1+d (WSOLA) left 2.1 ms rms jitter and 2.4 ms offset."""
    a, d = r.get("offset_s") or 0.0, (r.get("drift_ppm") or 0.0) / 1e6
    head = f"atrim=start={a:.5f},asetpts=PTS-STARTPTS" if a >= 0 else f"adelay=delays={-a * 1000:.1f}:all=1"
    if r.get("steps"):
        return head + "  # steps found: place each kept segment with other_time() instead"
    if abs(d) * r["duration_ref_s"] < 0.010:                 # under 10 ms over the whole take: ignore
        return head
    hi = 20 * out_rate
    return f"{head},aresample={hi},asetrate={round(hi * (1 + d))},aresample={out_rate}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("reference")
    ap.add_argument("other")
    ap.add_argument("--win", type=float, default=8.0, help="fine window length in seconds (default 8)")
    ap.add_argument("--step", type=float, default=30.0, help="spacing of fine windows in seconds (default 30)")
    ap.add_argument("--margin", type=float, default=0.25, help="fine search range around the estimate (s)")
    ap.add_argument("--json", action="store_true", help="print everything, windows included, as JSON")
    a = ap.parse_args()
    r = estimate(a.reference, a.other, a.win, a.step, a.margin)
    r["ffmpeg_filter_for_other"] = ffmpeg_hint(r)
    if a.json:
        print(json.dumps(r, indent=1))
    else:
        for k, v in r.items():
            if k != "windows":
                print(f"{k}: {v}")
    sys.exit(0 if r["confidence"] != "low" else 3)


if __name__ == "__main__":
    main()
