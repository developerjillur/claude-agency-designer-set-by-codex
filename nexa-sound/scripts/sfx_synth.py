"""nexa-sound synthesiser: clean motion-graphics sound effects built from scratch in plain Python.

Every sound here is made from sine and FM partials, filtered noise, pitch sweeps and exponential envelopes, so the
skill owns it outright: no samples and no third-party licence. The same preset, parameters and seed give the same
file, byte for byte.

Output: 48 kHz, stereo, 24-bit WAV, sample peak at -1 dBFS, DC removed, both ends faded to exactly zero, and a tail
that has decayed well below -60 dBFS in its last 20 ms.

Craft notes (why the code does what it does):
- Swept filters use the two-pole state-variable filter in its topology-preserving form (a biquad whose state is kept
  as integrator values). A direct-form biquad clicks and can go unstable when its cutoff moves quickly; this form
  stays clean when the cutoff changes every few samples, which is what whooshes and risers need.
- Tones are sums of sine partials, each with its own decay (higher partials die faster, as on a struck bar), or FM
  with a decaying index. Every partial above 18 kHz is dropped, so nothing folds back as aliasing.
- Every sound starts from zero through a raised-cosine attack (0.25 ms for the sharpest clicks) and ends through a
  raised-cosine fade after its natural decay, so neither end can click.
- Stereo movement is an equal-power pan of a mono source plus, for wide sounds, a partly decorrelated side layer kept
  small enough that a mono fold-down loses under 1 dB.

    python3 sfx_synth.py NAME OUT.wav [--dur S] [--seed N] [--pitch HZ] [--brightness 0-1]
"""
import argparse
import json
import math
import operator
import random
import sys
import wave
from array import array

SR = 48000
PEAK_DBFS = -1.0
SYNTH_VERSION = "1"
NYQ_SAFE = 18000.0
TWO_PI = 2.0 * math.pi

LP, BP, HP = 0, 1, 2


# ---------------------------------------------------------------- small helpers

def _n(seconds):
    return max(1, int(round(seconds * SR)))


def _clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def _rng(seed):
    return random.Random(int(seed) * 7919 + 104729)


def _white(n, rng):
    r = rng.random
    return [2.0 * r() - 1.0 for _ in range(n)]


def _pink(n, rng):
    """Pink noise (Paul Kellet's three-pole filter on white noise): more low-mid body than white, like real air."""
    r = rng.random
    out = [0.0] * n
    b0 = b1 = b2 = 0.0
    for i in range(n):
        w = 2.0 * r() - 1.0
        b0 = 0.99765 * b0 + w * 0.0990460
        b1 = 0.96300 * b1 + w * 0.2965164
        b2 = 0.57000 * b2 + w * 1.0526913
        out[i] = (b0 + b1 + b2 + w * 0.1848) * 0.2
    return out


def _smoothstep(x):
    x = _clamp(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def _mul(a, b):
    return list(map(operator.mul, a, b))


def _scale(a, g):
    return [v * g for v in a]


def _add_into(dst, src, start=0, gain=1.0):
    """dst[start + i] += gain * src[i], clipped to dst's length."""
    if start < 0:
        src = src[-start:]
        start = 0
    end = min(len(dst), start + len(src))
    for i in range(start, end):
        dst[i] += gain * src[i - start]


def _peak(x):
    return max(max(x), -min(x)) if x else 0.0


# ---------------------------------------------------------------- filters

def _svf(x, fc, q, mode):
    """Two-pole state-variable filter, topology-preserving form (Zavalishin; Simper's formulation).

    `fc` (Hz) and `q` are numbers or per-sample lists. Coefficients are recomputed every 8 samples (6 kHz control
    rate), which is smooth for any sweep in this module and saves most of the tan() calls.
    """
    n = len(x)
    y = [0.0] * n
    tan = math.tan
    w = math.pi / SR
    fc_list = isinstance(fc, list)
    q_list = isinstance(q, list)
    ic1 = ic2 = 0.0
    a1 = a2 = a3 = k = 0.0
    for i in range(n):
        if (i & 7) == 0:
            f = fc[i] if fc_list else fc
            f = 20.0 if f < 20.0 else (0.45 * SR if f > 0.45 * SR else f)
            qq = q[i] if q_list else q
            k = 1.0 / (qq if qq > 0.05 else 0.05)
            g = tan(w * f)
            a1 = 1.0 / (1.0 + g * (g + k))
            a2 = g * a1
            a3 = g * a2
        v0 = x[i]
        v3 = v0 - ic2
        v1 = a1 * ic1 + a2 * v3
        v2 = ic2 + a2 * ic1 + a3 * v3
        ic1 = 2.0 * v1 - ic1
        ic2 = 2.0 * v2 - ic2
        if mode == LP:
            y[i] = v2
        elif mode == BP:
            y[i] = k * v1          # unity gain at the centre frequency
        else:
            y[i] = v0 - k * v1 - v2
    return y


def _biquad_coeffs(kind, f, q=0.7071, gain_db=0.0):
    """RBJ audio-EQ-cookbook coefficients, normalised (b0, b1, b2, a1, a2)."""
    w0 = TWO_PI * f / SR
    cw, sw = math.cos(w0), math.sin(w0)
    alpha = sw / (2.0 * q)
    if kind == "hp":
        b0, b1, b2 = (1 + cw) / 2, -(1 + cw), (1 + cw) / 2
        a0, a1, a2 = 1 + alpha, -2 * cw, 1 - alpha
    elif kind == "lp":
        b0, b1, b2 = (1 - cw) / 2, 1 - cw, (1 - cw) / 2
        a0, a1, a2 = 1 + alpha, -2 * cw, 1 - alpha
    elif kind == "peak":
        a = 10 ** (gain_db / 40.0)
        b0, b1, b2 = 1 + alpha * a, -2 * cw, 1 - alpha * a
        a0, a1, a2 = 1 + alpha / a, -2 * cw, 1 - alpha / a
    else:
        raise ValueError(kind)
    return (b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)


def _biquad(x, coeffs):
    """Static biquad, transposed direct form II."""
    b0, b1, b2, a1, a2 = coeffs
    y = [0.0] * len(x)
    z1 = z2 = 0.0
    for i, v in enumerate(x):
        o = b0 * v + z1
        z1 = b1 * v - a1 * o + z2
        z2 = b2 * v - a2 * o
        y[i] = o
    return y


# ---------------------------------------------------------------- envelopes and oscillators

def _perc(n, attack, tau, start=0):
    """0 until `start` (samples), a raised-cosine rise over `attack` seconds, then exp(-t / tau)."""
    out = [0.0] * n
    na = max(1, int(attack * SR))
    cos = math.cos
    for i in range(na):
        j = start + i
        if 0 <= j < n:
            out[j] = 0.5 - 0.5 * cos(math.pi * (i + 1) / na)
    d = math.exp(-1.0 / (max(tau, 1e-4) * SR))
    e = 1.0
    for j in range(start + na, n):
        if j >= 0:
            out[j] = e
        e *= d
    return out


def _swell(n, t_peak, rise_pow, tau):
    """A swell to 1 at `t_peak` seconds (raised cosine to a power: slow start, quick arrival), then exp decay."""
    npk = _clamp(int(t_peak * SR), 1, n)
    out = [0.0] * n
    cos = math.cos
    for i in range(npk):
        out[i] = (0.5 - 0.5 * cos(math.pi * (i + 1) / npk)) ** rise_pow
    d = math.exp(-1.0 / (max(tau, 1e-4) * SR))
    e = 1.0
    for i in range(npk, n):
        out[i] = e
        e *= d
    return out


def _exp_sweep(n, f0, f1, curve=1.0):
    """Frequency list from f0 to f1 on a log scale; curve > 1 moves late, < 1 moves early."""
    r = math.log(f1 / f0)
    inv = 1.0 / max(1, n - 1)
    return [f0 * math.exp(r * ((i * inv) ** curve)) for i in range(n)]


def _sine(freqs, phase=0.0):
    """Sine from a per-sample frequency list (phase accumulator, so sweeps are continuous)."""
    out = [0.0] * len(freqs)
    inc = TWO_PI / SR
    sin = math.sin
    p = phase
    for i, f in enumerate(freqs):
        out[i] = sin(p)
        p += inc * f
    return out


def _saw_bl(freqs, harmonics=6, fade_from=14000.0):
    """Band-limited sawtooth: the first harmonics summed, each faded out as it nears 18 kHz (no aliasing)."""
    n = len(freqs)
    out = [0.0] * n
    inc = TWO_PI / SR
    sin = math.sin
    for h in range(1, harmonics + 1):
        p = 0.0
        amp = 1.0 / h
        for i in range(n):
            fh = freqs[i] * h
            if fh < NYQ_SAFE:
                g = amp if fh <= fade_from else amp * (NYQ_SAFE - fh) / (NYQ_SAFE - fade_from)
                out[i] += g * sin(p)
            p += inc * fh
    return out


def _flutter(n, rng, depth, lo=9.0, hi=31.0):
    """Slow random wobble around 1.0: the turbulence that makes a whoosh sound like moving air."""
    if depth <= 0:
        return [1.0] * n
    comps = [(rng.uniform(lo, hi), rng.uniform(0, TWO_PI)) for _ in range(3)]
    sin = math.sin
    out = [1.0] * n
    for f, ph in comps:
        w = TWO_PI * f / SR
        for i in range(n):
            out[i] += depth / 3.0 * sin(w * i + ph)
    return out


def _pan(x, pan):
    """Equal-power pan of a mono list; `pan` is -1 (left) to 1 (right), a number or a per-sample list."""
    cos, sin = math.cos, math.sin
    q = math.pi / 4.0
    if isinstance(pan, list):
        L = [v * cos(q * (p + 1.0)) for v, p in zip(x, pan)]
        R = [v * sin(q * (p + 1.0)) for v, p in zip(x, pan)]
    else:
        gl, gr = cos(q * (pan + 1.0)), sin(q * (pan + 1.0))
        L = [v * gl for v in x]
        R = [v * gr for v in x]
    return L, R


def _partials_note(n, f0, parts, attack, tau, start=0, fm=None, bright=0.5):
    """One struck or plucked note as a mono list of length n.

    parts: [(ratio, amp, tau_scale)]: each partial decays with tau * tau_scale. fm: (ratio, index, index_tau) adds a
    short FM brightening of the fundamental's attack (the 'tink' of a mallet). Partials above 18 kHz are skipped.
    """
    out = [0.0] * n
    na = max(1, int(attack * SR))
    sin, cos = math.sin, math.cos
    inc = TWO_PI / SR
    for ratio, amp, ts in parts:
        f = f0 * ratio
        if f >= NYQ_SAFE or amp <= 0:
            continue
        d = math.exp(-1.0 / (max(tau * ts, 1e-4) * SR))
        e = 1.0
        w = inc * f
        use_fm = fm is not None and ratio == 1.0
        if use_fm:
            fr, idx0, itau = fm
            if f * fr * (idx0 + 2.0) + f >= NYQ_SAFE:        # Carson's rule: keep every sideband under 18 kHz
                idx0 = max(0.0, (NYQ_SAFE - f) / (f * fr) - 2.0)
            wm = inc * f * fr
            di = math.exp(-1.0 / (max(itau, 1e-4) * SR))
            idx = idx0
        for i in range(n - start):
            if i < na:
                a = amp * (0.5 - 0.5 * cos(math.pi * (i + 1) / na))
            else:
                a = amp * e
                e *= d
                if a < 1e-7:
                    break
            if use_fm:
                out[start + i] += a * sin(w * i + idx * sin(wm * i))
                idx *= di
            else:
                out[start + i] += a * sin(w * i)
    return out


def _noise_hit(n, rng, start, fc, q, attack, tau, mode=BP, length=None, white=True):
    """A short burst of filtered noise placed at `start` (samples) in a list of n."""
    out = [0.0] * n
    if start >= n:
        return out
    m = n - start if length is None else min(n - start, _n(length))
    src = _white(m, rng) if white else _pink(m, rng)
    env = _perc(m, attack, tau)
    filt = _svf(src, fc, q, mode)
    for i in range(m):
        out[start + i] = filt[i] * env[i]
    return out


# ---------------------------------------------------------------- presets

def _whoosh_core(n, dur, pitch, bright, rng, peak_frac, lo_ratio, hi_ratio, flutter, pan_width, doppler, air):
    """Air rushing past: a band of pink noise whose centre follows the loudness (dull when far, bright when near),
    shifting a little lower after the peak (Doppler), with a turbulent wobble and a pan that crosses the centre at the
    peak."""
    tp = peak_frac * dur
    env = _swell(n, tp, 1.6, (dur - tp) / 8.5)
    f_lo, f_hi = pitch * lo_ratio, pitch * hi_ratio
    ratio = f_hi / f_lo
    npk = int(tp * SR)
    span = max(1, n - npk)
    fc = [f_lo * ratio ** (e ** 0.7) * (1.0 - doppler * max(0, i - npk) / span) for i, e in enumerate(env)]
    band = _svf(_svf(_pink(n, rng), fc, 0.9, LP), fc, 0.6, LP)          # 24 dB per octave above the band
    band = _svf(band, [f * 0.32 for f in fc], 0.7, HP)
    if air > 0:
        sheen = _svf(_white(n, rng), [min(f * 1.5, 9000.0) for f in fc], 0.7, HP)
        sheen = _svf(_svf(sheen, [min(f * 5.0, 12000.0) for f in fc], 0.7, LP), 12000.0, 0.7, LP)
        band = [b + air * s for b, s in zip(band, sheen)]
    mod = _flutter(n, rng, flutter)
    mono = [b * e * m for b, e, m in zip(band, env, mod)]
    width = 0.22 * dur
    pan = [pan_width * math.tanh((i / SR - tp) / width) for i in range(n)]
    return _pan(mono, pan)


def p_whoosh(n, dur, pitch, bright, rng):
    return _whoosh_core(n, dur, pitch, bright, rng, peak_frac=0.58, lo_ratio=0.35, hi_ratio=2.2 + 3.5 * bright,
                        flutter=0.12, pan_width=0.45, doppler=0.25, air=0.25 * bright)


def p_whoosh_short(n, dur, pitch, bright, rng):
    return _whoosh_core(n, dur, pitch, bright, rng, peak_frac=0.62, lo_ratio=0.4, hi_ratio=2.6 + 3.8 * bright,
                        flutter=0.06, pan_width=0.3, doppler=0.2, air=0.35 * bright)


def p_swipe(n, dur, pitch, bright, rng):
    """A quick airy flick: a band of noise sweeping upward (you hear the direction), a softer air layer above it and
    a faint rising 'zip' tone underneath, moving a little left to right."""
    tp = 0.35 * dur
    env = _swell(n, tp, 1.2, (dur - tp) / 8.0)
    fc = _exp_sweep(n, pitch * 0.6, pitch * (2.2 + 1.2 * bright))
    src = _white(n, rng)
    band = _svf(_svf(src, fc, 1.1, BP), fc, 1.1, BP)
    air = _svf(_svf(_white(n, rng), [f * 1.6 for f in fc], 0.7, HP), 12000.0, 0.7, LP)
    zip_ = _sine(_exp_sweep(n, pitch * 0.25, pitch * 0.6))
    mono = [(b + 0.25 * a + 0.08 * z) * e for b, a, z, e in zip(band, air, zip_, env)]
    pan = [-0.3 + 0.6 * _smoothstep(i / n) for i in range(n)]
    return _pan(mono, pan)


def p_swoosh_down(n, dur, pitch, bright, rng):
    """Something falling past: a noise band sweeping down across the whole sound, a sinking tonal body, and a pan
    that settles in the centre."""
    tp = 0.4 * dur
    env = _swell(n, tp, 1.4, (dur - tp) / 7.5)
    fc = _exp_sweep(n, pitch * (3.0 + 3.0 * bright), pitch * 0.25, curve=0.8)
    band = _svf(_pink(n, rng), fc, 1.0, LP)
    band = _svf(band, [f * 0.3 for f in fc], 0.7, HP)
    body = _sine(_exp_sweep(n, pitch * 0.3, pitch * 0.08))
    body_env = _swell(n, tp * 1.1, 2.0, (dur - tp) / 6.5)
    mod = _flutter(n, rng, 0.08)
    mono = [(b * e + 0.12 * s * be) * m for b, e, s, be, m in zip(band, env, body, body_env, mod)]
    pan = [0.35 * (1.0 - _smoothstep(i / (0.85 * n))) for i in range(n)]
    return _pan(mono, pan)


def p_pop(n, dur, pitch, bright, rng):
    """A round pop: a sine whose pitch drops from about an octave above in 30 ms, a hint of second harmonic from
    FM, and a tiny noise transient for the consonant."""
    tau = dur / 9.0
    inc = TWO_PI / SR
    sin, exp = math.sin, math.exp
    env = _perc(n, 0.0008, tau)
    out = [0.0] * n
    p = 0.0
    fm_idx = 0.6 * bright
    for i in range(n):
        t = i / SR
        f = pitch * (1.0 + 1.0 * exp(-t / 0.010))
        out[i] = sin(p + fm_idx * exp(-t / 0.012) * sin(2.0 * p)) * env[i]
        p += inc * f
    click = _noise_hit(n, rng, 0, 3200.0, 1.5, 0.0002, 0.0012)
    mono = [a + 0.25 * c for a, c in zip(out, click)]
    return _pan(mono, 0.0)


def p_bubble(n, dur, pitch, bright, rng):
    """A water 'bloop': a nearly pure sine whose pitch rises as the bubble shrinks, with a quick decay."""
    tau = dur / 8.0
    rise = math.log(2.6)
    freqs = [pitch * math.exp(rise * min(i / (0.11 * SR), 1.0)) for i in range(n)]
    base = _sine(freqs)
    third = _sine([f * 3.0 for f in freqs])
    env = _perc(n, 0.003, tau)
    mono = [(b + 0.06 * bright * t) * e for b, t, e in zip(base, third, env)]
    return _pan(mono, 0.0)


def p_click(n, dur, pitch, bright, rng):
    """A crisp interface click: a 2 ms band of noise and a 5 ms tonal tock, high-passed so it stays light."""
    fc = pitch * (0.8 + 0.4 * bright)
    tick = _noise_hit(n, rng, 0, fc, 2.5, 0.00025, min(0.0022, dur / 15))
    tone = _partials_note(n, pitch * 0.62, [(1.0, 1.0, 1.0)], 0.00025, min(0.005, dur / 12))
    mono = _biquad([a + 0.5 * b for a, b in zip(tick, tone)], _biquad_coeffs("hp", 400.0))
    return _pan(mono, 0.0)


def p_tick(n, dur, pitch, bright, rng):
    """A small dry tick, higher and shorter than a click (a clock, a counter step)."""
    tone = _partials_note(n, pitch, [(1.0, 1.0, 1.0)], 0.00025, min(0.0025, dur / 12))
    hiss = _noise_hit(n, rng, 0, pitch * (1.1 + 0.4 * bright), 3.0, 0.0002, min(0.001, dur / 20))
    mono = _biquad([a + 0.6 * b for a, b in zip(tone, hiss)], _biquad_coeffs("hp", 800.0))
    return _pan(mono, 0.0)


def _key_voice(pitch, level, rng, space=False):
    """One keyboard key, 120 ms: the key-down clack (bright click, resonant plastic 'thock', low knock) and a softer
    release click 30 to 45 ms later."""
    seg = _n(0.12)
    body_ratio, body_tau, body_lvl = (0.2, 0.020, 0.8) if space else (0.28, 0.012, 0.55)
    parts = [
        _noise_hit(seg, rng, 0, pitch, 1.4, 0.0002, 0.004),
        _scale(_noise_hit(seg, rng, 0, pitch * body_ratio, 4.0, 0.0004, body_tau), body_lvl),
        _scale(_partials_note(seg, pitch * 0.16, [(1.0, 1.0, 1.0)], 0.0005, 0.010), 0.25),
    ]
    rel = _n(rng.uniform(0.030, 0.045))
    parts.append(_scale(_noise_hit(seg, rng, rel, pitch * 1.12, 1.6, 0.0002, 0.003), 0.35))
    parts.append(_scale(_noise_hit(seg, rng, rel, pitch * body_ratio * 1.1, 4.0, 0.0004, body_tau * 0.7), 0.2))
    return [level * sum(vals) for vals in zip(*parts)]


def p_key(n, dur, pitch, bright, rng):
    """A single keyboard key press."""
    mono = [0.0] * n
    _add_into(mono, _key_voice(pitch * (0.9 + 0.2 * bright), 1.0, rng), _n(0.002))
    return _pan(mono, 0.0)


def p_typing(n, dur, pitch, bright, rng):
    """A burst of typing: keys about 8 to 10 a second with human timing, the odd pause, a lower spacebar now and
    then, each key a little different in pitch, level and position."""
    L, R = [0.0] * n, [0.0] * n
    t = 0.004
    count = 0
    while t < dur - 0.16:
        space = count > 2 and rng.random() < 0.15
        f = pitch * (0.9 + 0.2 * bright) * rng.uniform(0.93, 1.07) * (0.72 if space else 1.0)
        lvl = 10 ** (rng.uniform(-2.0, 1.0) / 20.0) * (1.12 if space else 1.0)
        l, r = _pan(_key_voice(f, lvl, rng, space), rng.uniform(-0.22, 0.22))
        _add_into(L, l, _n(t))
        _add_into(R, r, _n(t))
        count += 1
        gap = rng.uniform(0.07, 0.16)
        if rng.random() < 0.08:
            gap += rng.uniform(0.18, 0.3)
        t += gap
    return L, R


def p_ding(n, dur, pitch, bright, rng):
    """A clean glassy ding: a sine fundamental with bell partials (2, 2.76, 5.4) that die faster than it, and a
    short FM 'tink' on the strike."""
    tau = dur / 7.5
    parts = [(1.0, 1.0, 1.0), (2.0, 0.28 * bright + 0.05, 0.45), (2.76, 0.22 * bright + 0.03, 0.3),
             (5.4, 0.1 * bright, 0.12)]
    core = _partials_note(n, pitch, parts[:1], 0.0012, tau, fm=(3.5, 0.5 * bright, 0.03))
    upper_l = _partials_note(n, pitch, [parts[1], parts[3]], 0.0012, tau)
    upper_r = _partials_note(n, pitch, [parts[2]], 0.0012, tau)
    L = [c * 0.7071 + a * 0.83 + b * 0.55 for c, a, b in zip(core, upper_l, upper_r)]
    R = [c * 0.7071 + a * 0.55 + b * 0.83 for c, a, b in zip(core, upper_l, upper_r)]
    return L, R


def _arpeggio(n, dur, f0, ratios, spacing, parts, attack, tau_first, tau_last, pans, rng, fm=None, jitter=0.0):
    L, R = [0.0] * n, [0.0] * n
    for k, ratio in enumerate(ratios):
        start = _n(k * spacing + (rng.uniform(-jitter, jitter) if jitter and k else 0.0))
        if start >= n:
            break
        tau = tau_last if k == len(ratios) - 1 else tau_first
        tau = min(tau, (n - start) / float(SR) / 7.5)   # every note has died away by the end, however short
        note = _partials_note(n - start, f0 * ratio, parts, attack, tau, fm=fm)
        l, r = _pan(note, pans[k])
        for i in range(len(note)):
            L[start + i] += l[i]
            R[start + i] += r[i]
    return L, R


def p_chime(n, dur, pitch, bright, rng):
    """A soft three-note chime (a rising major triad, 70 ms apart), celesta-like, spread gently left to right."""
    ratios = [1.0, 2 ** (4 / 12.0), 2 ** (7 / 12.0)]
    tau = (dur - 0.14) / 8.0
    parts = [(1.0, 1.0, 1.0), (3.0, 0.07 + 0.08 * bright, 0.35), (4.2, 0.04 * bright + 0.01, 0.2)]
    return _arpeggio(n, dur, pitch, ratios, 0.07, parts, 0.0015, tau, tau, [-0.25, 0.0, 0.25], rng,
                     fm=(2.0, 0.35 * bright, 0.02))


def p_notify(n, dur, pitch, bright, rng):
    """A friendly two-note notification (up a fourth, 105 ms apart) with a marimba-like tone and a soft mallet."""
    parts = [(1.0, 1.0, 1.0), (3.93, 0.2 * bright + 0.05, 0.25), (9.2, 0.05 * bright, 0.1)]
    L, R = _arpeggio(n, dur, pitch, [1.0, 2 ** (5 / 12.0)], 0.105, parts, 0.001, dur / 8.5, (dur - 0.105) / 7.5,
                     [-0.12, 0.12], rng)
    mallet = _noise_hit(n, rng, 0, 3000.0, 1.2, 0.0002, 0.0015)
    mallet2 = _noise_hit(n, rng, _n(0.105), 3400.0, 1.2, 0.0002, 0.0015)
    for i in range(n):
        m = 0.08 * (mallet[i] + mallet2[i])
        L[i] += m
        R[i] += m
    return L, R


def p_success(n, dur, pitch, bright, rng):
    """A bright rising arpeggio (root, third, fifth, octave, 70 ms apart), plucked, the last note left to ring."""
    ratios = [1.0, 2 ** (4 / 12.0), 2 ** (7 / 12.0), 2.0]
    parts = [(1.0, 1.0, 1.0), (2.0, 0.18 * bright + 0.04, 0.4), (3.0, 0.06 * bright, 0.25)]
    return _arpeggio(n, dur, pitch, ratios, 0.07, parts, 0.001, 0.07, (dur - 0.21) / 7.5,
                     [-0.2, -0.07, 0.07, 0.2], rng, fm=(1.0, 1.2 * bright, 0.03))


def p_error(n, dur, pitch, bright, rng):
    """A soft 'uh-oh': two short descending notes of a warm square-ish tone (odd harmonics, low-passed) with a
    slightly detuned second voice."""
    L, R = [0.0] * n, [0.0] * n
    note_len = min(0.2, dur / 2.6)
    for k, (t0, ratio) in enumerate(((0.0, 1.0), (note_len * 1.25, 2 ** (-2 / 12.0)))):
        start = _n(t0)
        m = n - start
        f = pitch * ratio
        tone = [0.0] * m
        for det, lvl in ((1.0, 1.0), (1.0035, 0.5)):
            freqs = [f * det] * m
            for h in (1, 3, 5, 7, 9):
                if f * det * h >= 10000:
                    break
                s = _sine([x * h for x in freqs])
                for i in range(m):
                    tone[i] += lvl * s[i] / h
        tone = _svf(tone, 2200.0 + 2000.0 * bright, 0.7, LP)
        env = _perc(m, 0.004, (dur - t0) / 7.5 if k else min(note_len / 2.2, dur / 8.0))
        mono = _mul(tone, env)
        l, r = _pan(mono, -0.05 if k == 0 else 0.05)
        for i in range(m):
            L[start + i] += l[i]
            R[start + i] += r[i]
    return L, R


def p_riser(n, dur, pitch, bright, rng):
    """A build-up: a resonant noise sweep (250 Hz to about 9 kHz), a band-limited saw rising an octave and a fifth,
    a tremolo that speeds up, and a stereo image that widens. It peaks 0.25 s before the end (a fifth of its length
    before the end when it is shorter than 1.25 s): the moment to put on the cut. Then it releases fast."""
    release = min(0.25, dur * 0.2)
    tc = dur - release
    nc = _n(tc)
    p = [min(1.0, i / nc) for i in range(n)]
    env = [0.0] * n
    d = math.exp(-1.0 / (0.028 * SR))
    e = 1.0
    for i in range(n):
        if i < nc:
            env[i] = p[i] ** 2.2
        else:
            env[i] = e
            e *= d
    top = min(16000.0, 5000.0 + 8000.0 * bright)
    fc = [250.0 * (top / 250.0) ** (x ** 1.6) for x in p]
    hp = [80.0 * (1200.0 / 80.0) ** (x ** 1.6) for x in p]
    q = [0.7 + 1.8 * x ** 2 for x in p]
    common = _svf(_svf(_pink(n, rng), fc, q, LP), hp, 0.7, HP)
    side = _svf(_svf(_pink(n, rng), fc, q, LP), hp, 0.7, HP)
    freqs = [pitch * 2 ** ((19 / 12.0) * (x ** 1.5)) for x in p]
    saw = _saw_bl(freqs, 6)
    saw2 = _saw_bl([f * 1.004 for f in freqs], 6)
    inc = TWO_PI / SR
    trem_p = 0.0
    L, R = [0.0] * n, [0.0] * n
    sin = math.sin
    for i in range(n):
        x = p[i]
        trem = 1.0 - 0.35 * x * (0.5 + 0.5 * sin(trem_p))
        trem_p += inc * (3.0 + 11.0 * x * x)
        w = 0.15 + 0.3 * x
        tone = 0.22 * (0.6 + 0.4 * x)
        a = env[i] * trem
        mid = common[i] + tone * 0.5 * (saw[i] + saw2[i])
        sid = w * side[i] + tone * 0.3 * (saw[i] - saw2[i])
        L[i] = a * (mid + sid)
        R[i] = a * (mid - sid)
    return L, R


def p_downlifter(n, dur, pitch, bright, rng):
    """The reverse of a riser: bright and wide on the hit, then the noise band, a saw and a soft sub all fall away
    and the image narrows to the centre."""
    p = [i / n for i in range(n)]
    atk = _n(0.008)
    env = [((1.0 - x) ** 2.6) * (0.5 - 0.5 * math.cos(math.pi * min(1.0, (i + 1) / atk))) for i, x in enumerate(p)]
    top = min(15000.0, 5000.0 + 8000.0 * bright)
    fc = [top * (180.0 / top) ** (x ** 0.6) for x in p]
    hp = [1500.0 * (40.0 / 1500.0) ** (x ** 0.6) for x in p]
    q = [2.0 - 1.3 * x for x in p]
    common = _svf(_svf(_pink(n, rng), fc, q, LP), hp, 0.7, HP)
    side = _svf(_svf(_pink(n, rng), fc, q, LP), hp, 0.7, HP)
    saw = _saw_bl([pitch * 0.25 ** (x ** 0.7) for x in p], 4)
    sub = _sine([110.0 * (45.0 / 110.0) ** (x ** 0.8) for x in p])
    L, R = [0.0] * n, [0.0] * n
    for i in range(n):
        x = p[i]
        w = 0.5 - 0.4 * x
        mono = common[i] + 0.2 * (1.0 - 0.3 * x) * saw[i] + 0.25 * sub[i]
        L[i] = env[i] * (mono + w * side[i])
        R[i] = env[i] * (mono - w * side[i])
    return L, R


def _saturate(x, drive):
    """Soft saturation (tanh): adds the harmonics that let a sub be heard on phone speakers."""
    t = math.tanh
    k = 1.0 / t(drive)
    return [t(drive * v) * k for v in x]


def p_impact(n, dur, pitch, bright, rng):
    """A cinematic hit: a kick-like body (pitch falling from about three times the fundamental), a bright crack, a
    low-mid thump and a wide rumbling tail, softly saturated together."""
    tau = dur / 7.5
    inc = TWO_PI / SR
    sin, exp = math.sin, math.exp
    body = [0.0] * n
    ph = 0.0
    env = _perc(n, 0.0006, tau)
    for i in range(n):
        body[i] = sin(ph) * env[i]
        ph += inc * pitch * (1.0 + 2.2 * exp(-(i / SR) / 0.028))
    crack = _noise_hit(n, rng, 0, 1800.0 + 1200.0 * bright, 0.8, 0.0003, 0.006, length=0.09)
    thump = _noise_hit(n, rng, 0, 350.0, 0.7, 0.001, 0.045, mode=LP, length=0.5)
    center = [b + (0.25 + 0.5 * bright) * c + 0.5 * t for b, c, t in zip(body, crack, thump)]
    center = _saturate(center, 1.8)
    tail_env = _perc(n, 0.005, tau * 1.05)
    tail_f = _exp_sweep(n, 900.0, 300.0)
    tc = _svf(_pink(n, rng), tail_f, 0.7, LP)
    ts = _svf(_pink(n, rng), tail_f, 0.7, LP)
    L = [c * 0.7071 + 0.3 * e * (t + 0.5 * a) for c, e, t, a in zip(center, tail_env, tc, ts)]
    R = [c * 0.7071 + 0.3 * e * (t - 0.5 * a) for c, e, t, a in zip(center, tail_env, tc, ts)]
    return L, R


def p_boom(n, dur, pitch, bright, rng):
    """A deep, long boom: a sub sine settling from about 2.2 times its pitch, a soft transient and a wide low
    rumble, saturated so the low end still reads on small speakers."""
    tau = dur / 7.2
    inc = TWO_PI / SR
    sin, exp = math.sin, math.exp
    env = _perc(n, 0.002, tau)
    sub = [0.0] * n
    ph = 0.0
    for i in range(n):
        sub[i] = sin(ph) * env[i]
        ph += inc * pitch * (1.0 + 1.2 * exp(-(i / SR) / 0.05))
    trans = _noise_hit(n, rng, 0, 900.0, 0.9, 0.0005, 0.010, length=0.12)
    center = _saturate([s + (0.15 + 0.2 * bright) * t for s, t in zip(sub, trans)], 2.2)
    r_env = _perc(n, 0.01, dur / 7.5)
    rc = _svf(_pink(n, rng), 180.0, 0.7, LP)
    rs = _svf(_pink(n, rng), 180.0, 0.7, LP)
    L = [c * 0.7071 + 0.9 * e * (a + 0.4 * b) for c, e, a, b in zip(center, r_env, rc, rs)]
    R = [c * 0.7071 + 0.9 * e * (a - 0.4 * b) for c, e, a, b in zip(center, r_env, rc, rs)]
    return L, R


def p_sub_drop(n, dur, pitch, bright, rng):
    """A trailer sub drop: a sine gliding down from about four times its pitch, with a quiet second harmonic and
    gentle saturation so it survives small speakers. Mono, centred."""
    tau = dur / 7.0
    glide = 0.22 * dur
    inc = TWO_PI / SR
    sin, exp = math.sin, math.exp
    env = _perc(n, 0.004, tau)
    out = [0.0] * n
    ph = 0.0
    h2 = 0.12 + 0.15 * bright
    for i in range(n):
        out[i] = (sin(ph) + h2 * sin(2.0 * ph)) * env[i]
        ph += inc * pitch * (1.0 + 3.2 * exp(-(i / SR) / glide))
    return _pan(_saturate(out, 1.6), 0.0)


def _fm_blip(m, f, ratio, index, lp=9000.0):
    """A short FM tone, its index capped so Carson's bandwidth stays under 12 kHz, then low-passed (4 poles)."""
    if f + (index + 1.0) * f * ratio > 12000.0:
        index = max(0.0, (12000.0 - f) / (f * ratio) - 1.0)
    inc = TWO_PI / SR
    sin = math.sin
    tone = [sin(inc * f * i + index * sin(inc * f * ratio * i)) for i in range(m)]
    return _svf(_svf(tone, lp, 0.7, LP), lp, 0.7, LP)


def p_glitch(n, dur, pitch, bright, rng):
    """A digital stutter: short grains of FM blips, band-passed noise and sample-and-hold tones, one of them
    repeated, each with 1.5 ms edges, scattered across the stereo field. FM blips are low-passed at 9 kHz and held
    tones at 7 kHz (4 poles each) so the stair-steps do not ring up to the top of the band."""
    L, R = [0.0] * n, [0.0] * n
    t = 0.002
    last = None
    grains = 0
    edge = _n(0.0015)
    while t < dur - 0.08 and grains < 12:
        glen = rng.uniform(0.012, 0.045)
        m = _n(glen)
        kind = rng.random()
        if last is not None and rng.random() < 0.3:
            g = list(last)
            m = len(g)
        elif kind < 0.4:
            ratio = (0.5, 1.5, 2.1, 3.7)[int(rng.random() * 4)]
            g = _fm_blip(m, pitch * rng.uniform(0.5, 3.0), ratio, rng.uniform(1.5, 3.5))
        elif kind < 0.75:
            g = _svf(_white(m, rng), rng.uniform(1000.0, 6000.0), 3.0, BP)
            pk = _peak(g) or 1.0
            g = _scale(g, 1.0 / pk)
        else:
            src = _fm_blip(m, pitch * rng.uniform(0.7, 2.0), 2.0, rng.uniform(1.0, 2.5))
            hold = int(rng.uniform(3, 7))
            g = [src[i - i % hold] for i in range(m)]
            g = _svf(_svf(g, 7000.0, 0.7, LP), 7000.0, 0.7, LP)
        for i in range(min(edge, len(g) // 2)):
            w = 0.5 - 0.5 * math.cos(math.pi * (i + 1) / (edge + 1))
            g[i] *= w
            g[-1 - i] *= w
        lvl = 10 ** (rng.uniform(-3.0, 0.0) / 20.0) * (0.55 + 0.45 * bright)
        l, r = _pan(_scale(g, lvl), rng.uniform(-0.45, 0.45))
        s = _n(t)
        _add_into(L, l, s)
        _add_into(R, r, s)
        last = g
        grains += 1
        t += len(g) / SR + rng.uniform(0.004, 0.03)
    L = _svf(_svf(_biquad(L, _biquad_coeffs("hp", 150.0)), 12000.0, 0.7, LP), 12000.0, 0.7, LP)
    R = _svf(_svf(_biquad(R, _biquad_coeffs("hp", 150.0)), 12000.0, 0.7, LP), 12000.0, 0.7, LP)
    return L, R


def p_shutter(n, dur, pitch, bright, rng):
    """A camera shutter: the opening click, the curtain's swish, and a slightly lower closing click 80 ms later,
    each with a small mechanical body resonance."""
    def click(start, f, body_f, lvl):
        c = _noise_hit(n, rng, start, f, 2.0, 0.0002, 0.0018)
        b = _noise_hit(n, rng, start, body_f, 6.0, 0.0003, 0.009)
        k = _partials_note(n - start, 180.0, [(1.0, 1.0, 1.0)], 0.0005, 0.008)
        out = [lvl * (x + 0.6 * y) for x, y in zip(c, b)]
        _add_into(out, _scale(k, 0.25 * lvl), start)
        return out
    f = pitch * (0.9 + 0.2 * bright)
    c1 = click(_n(0.005), f, f * 0.36, 0.9)
    c2 = click(_n(0.085), f * 0.85, f * 0.31, 1.0)
    sw_len = _n(0.04)
    swish = _svf(_svf(_white(sw_len, rng), 5000.0, 0.8, BP), 10000.0, 0.7, LP)
    swish = [v * 0.05 * (0.5 - 0.5 * math.cos(TWO_PI * i / sw_len)) for i, v in enumerate(swish)]
    room_env = _perc(n, 0.002, 0.025, start=_n(0.085))
    room_l = _mul(_svf(_white(n, rng), 2000.0, 0.7, LP), room_env)
    room_r = _mul(_svf(_white(n, rng), 2000.0, 0.7, LP), room_env)
    mono1 = list(c1)
    _add_into(mono1, swish, _n(0.02))
    l1, r1 = _pan(mono1, -0.05)
    l2, r2 = _pan(c2, 0.05)
    L = [a + b + 0.05 * c for a, b, c in zip(l1, l2, room_l)]
    R = [a + b + 0.05 * c for a, b, c in zip(r1, r2, room_r)]
    return L, R


def p_sparkle(n, dur, pitch, bright, rng):
    """A magic shimmer: dozens of tiny glassy grains on a major pentatonic scale, densest a third of the way in,
    scattered across the stereo field over a faint airy hiss."""
    scale = [1.0, 9 / 8.0, 5 / 4.0, 3 / 2.0, 5 / 3.0, 2.0, 9 / 4.0, 5 / 2.0, 3.0, 10 / 3.0]
    L, R = [0.0] * n, [0.0] * n
    count = max(6, int(28 * dur))
    last_start = max(0.01, dur - 0.3)
    for _ in range(count):
        t = last_start * (rng.random() ** 1.3)
        f = pitch * scale[int(rng.random() * len(scale))]
        tau = min(rng.uniform(0.035, 0.09), (dur - t) / 7.5)
        m = min(n - _n(t), _n(tau * 8))
        second = 2.76 if f * 2.76 < 16000.0 else 0.0
        parts = [(1.0, 1.0, 1.0)] + ([(second, 0.2, 0.5)] if second else [])
        g = _partials_note(m, f, parts, 0.0015, tau)
        swell = math.sin(math.pi * min(1.0, t / max(last_start, 1e-3))) ** 0.6 + 0.15
        l, r = _pan(_scale(g, rng.uniform(0.5, 1.0) * swell), rng.uniform(-0.6, 0.6))
        _add_into(L, l, _n(t))
        _add_into(R, r, _n(t))
    hiss_env = _swell(n, 0.35 * dur, 1.5, (dur * 0.65) / 7.5)
    hl = _svf(_svf(_svf(_white(n, rng), 6000.0, 0.7, HP), 13000.0, 0.7, LP), 13000.0, 0.7, LP)
    hr = _svf(_svf(_svf(_white(n, rng), 6000.0, 0.7, HP), 13000.0, 0.7, LP), 13000.0, 0.7, LP)
    lvl = 0.03 + 0.05 * bright
    L = [a + lvl * e * h for a, e, h in zip(L, hiss_env, hl)]
    R = [a + lvl * e * h for a, e, h in zip(R, hiss_env, hr)]
    return L, R


# name: (function, default duration, (min, max) duration, default pitch Hz, (min, max) pitch, default brightness,
#        placement: align, default gain_db against the dialogue anchor, category, one-line description)
PRESETS = {
    "whoosh": (p_whoosh, 0.9, (0.3, 4.0), 900.0, (200.0, 4000.0), 0.5, "peak", -9.0, "transition",
               "Air rushing past: a swept pink-noise band, peak at 58 %, moving left to right."),
    "whoosh-short": (p_whoosh_short, 0.45, (0.15, 1.5), 1300.0, (300.0, 5000.0), 0.65, "peak", -10.0, "transition",
                     "A quick bright whoosh for fast moves and snappy transitions."),
    "swipe": (p_swipe, 0.28, (0.1, 1.0), 2500.0, (600.0, 6000.0), 0.6, "peak", -12.0, "transition",
              "An airy upward flick for a swipe or a slide-in."),
    "swoosh-down": (p_swoosh_down, 0.8, (0.3, 3.0), 1200.0, (300.0, 4000.0), 0.5, "peak", -9.0, "transition",
                    "Something falling past: a band sweeping down with a sinking body, settling in the centre."),
    "pop": (p_pop, 0.16, (0.06, 0.6), 520.0, (150.0, 2000.0), 0.5, "attack", -14.0, "ui",
            "A round pop for an element, chip or badge appearing."),
    "bubble": (p_bubble, 0.3, (0.1, 1.0), 380.0, (150.0, 1500.0), 0.4, "attack", -14.0, "ui",
               "A soft water bloop with a rising pitch."),
    "click": (p_click, 0.05, (0.04, 0.3), 2600.0, (800.0, 6000.0), 0.6, "attack", -20.0, "ui",
              "A crisp interface click: button, toggle, selection."),
    "tick": (p_tick, 0.045, (0.04, 0.2), 4200.0, (1500.0, 8000.0), 0.7, "attack", -22.0, "ui",
             "A small dry tick for counters, clocks and steppers."),
    "key": (p_key, 0.14, (0.12, 0.5), 1900.0, (800.0, 4000.0), 0.5, "attack", -20.0, "ui",
            "One keyboard key press with its release."),
    "typing": (p_typing, 1.6, (0.4, 10.0), 1900.0, (800.0, 4000.0), 0.5, "attack", -20.0, "ui",
               "A burst of typing, about 8 to 10 keys a second with human timing."),
    "ding": (p_ding, 1.3, (0.3, 4.0), 1318.5, (300.0, 4000.0), 0.5, "attack", -12.0, "tone",
             "A clean glassy ding for a highlight or a point made."),
    "chime": (p_chime, 2.2, (0.6, 6.0), 1046.5, (300.0, 3000.0), 0.5, "attack", -12.0, "tone",
              "A soft rising three-note chime: success, welcome, a gentle transition."),
    "notify": (p_notify, 0.8, (0.3, 3.0), 880.0, (300.0, 2500.0), 0.5, "attack", -12.0, "tone",
               "A friendly two-note notification: a message, a toast, a badge."),
    "success": (p_success, 0.95, (0.4, 3.0), 784.0, (300.0, 2500.0), 0.55, "attack", -12.0, "tone",
                "A bright rising four-note arpeggio: done, saved, unlocked."),
    "error": (p_error, 0.55, (0.3, 2.0), 311.0, (120.0, 1000.0), 0.4, "attack", -12.0, "tone",
              "A soft descending two-note 'uh-oh' for a wrong step or a failure state."),
    "riser": (p_riser, 3.0, (0.8, 12.0), 220.0, (60.0, 800.0), 0.6, "end", -8.0, "build",
              "A build-up that peaks 0.25 s before its end (sooner when short): put that moment on the cut."),
    "downlifter": (p_downlifter, 2.2, (0.6, 8.0), 660.0, (150.0, 2000.0), 0.6, "attack", -9.0, "build",
                   "The reverse of a riser: bright on the hit, then falling and narrowing."),
    "impact": (p_impact, 1.6, (0.4, 5.0), 55.0, (30.0, 120.0), 0.5, "attack", -3.0, "hit",
               "A cinematic hit: kick-like body, bright crack, low thump and a wide tail."),
    "boom": (p_boom, 2.6, (0.8, 6.0), 42.0, (25.0, 90.0), 0.35, "attack", -4.0, "hit",
             "A deep long boom with a wide low rumble."),
    "sub-drop": (p_sub_drop, 2.0, (0.6, 6.0), 34.0, (22.0, 80.0), 0.3, "attack", -6.0, "hit",
                 "A trailer sub drop gliding down about two octaves."),
    "glitch": (p_glitch, 0.5, (0.15, 2.0), 900.0, (200.0, 3000.0), 0.6, "attack", -10.0, "digital",
               "A short digital stutter of blips, noise and held tones."),
    "shutter": (p_shutter, 0.32, (0.2, 1.0), 2800.0, (1000.0, 6000.0), 0.55, "attack", -14.0, "ui",
                "A camera shutter: open click, curtain swish, close click."),
    "sparkle": (p_sparkle, 1.5, (0.5, 5.0), 2093.0, (600.0, 4000.0), 0.6, "attack", -12.0, "tone",
                "A magic shimmer of tiny glassy grains across the stereo field."),
}

ALIASES = {
    "swoosh": "whoosh", "woosh": "whoosh", "whoosh-fast": "whoosh-short", "short-whoosh": "whoosh-short",
    "swish": "swipe", "slide": "swipe", "swoosh-downward": "swoosh-down", "fall": "swoosh-down",
    "ui-click": "click", "button": "click", "tap": "click", "toggle": "click", "select": "click",
    "keypress": "key", "key-press": "key", "keystroke": "key", "keyboard": "typing", "type": "typing",
    "bell": "ding", "ping": "ding", "chime-up": "chime", "notification": "notify", "message": "notify",
    "done": "success", "complete": "success", "win": "success", "fail": "error", "wrong": "error",
    "build": "riser", "rise": "riser", "uplifter": "riser", "downer": "downlifter", "hit": "impact",
    "slam": "impact", "impact-bass": "impact", "thud": "impact", "sub": "sub-drop", "subdrop": "sub-drop",
    "bass-drop": "sub-drop", "stutter": "glitch", "camera": "shutter", "snapshot": "shutter",
    "shimmer": "sparkle", "twinkle": "sparkle", "magic": "sparkle", "bloop": "bubble", "blip": "pop",
    "appear": "pop", "clock": "tick",
}


def slug(name):
    return "-".join("".join(c if c.isalnum() else " " for c in str(name).lower()).split())


def resolve_name(name):
    """A preset name for a cue name (exact, alias or slug), or None."""
    s = slug(name)
    if s in PRESETS:
        return s
    return ALIASES.get(s)


def info(name):
    fn, dur, dr, pitch, pr, bright, align, gain, cat, desc = PRESETS[name]
    return {"name": name, "dur": dur, "dur_range": list(dr), "pitch": pitch, "pitch_range": list(pr),
            "brightness": bright, "align": align, "gain_db": gain, "category": cat, "description": desc}


# ---------------------------------------------------------------- finishing, measuring, files

def _finish(L, R, hp_hz=20.0, lp_hz=16000.0, fade_in=0.00025, fade_out=0.02):
    """High-pass (DC and subsonic rumble out), a gentle 2-pole ceiling (the fizz above 16 kHz that makes noise sound
    digital), raised-cosine edges to exactly zero, then peak to -1 dBFS."""
    c = _biquad_coeffs("hp", hp_hz, 0.7071)
    L, R = _biquad(L, c), _biquad(R, c)
    if lp_hz:
        c = _biquad_coeffs("lp", lp_hz, 0.7071)
        L, R = _biquad(L, c), _biquad(R, c)
    n = len(L)
    ni = min(n // 4, max(1, int(fade_in * SR)))
    no = min(n // 3, max(1, int(fade_out * SR)))
    cos = math.cos
    for i in range(ni):
        w = 0.5 - 0.5 * cos(math.pi * i / ni)
        L[i] *= w
        R[i] *= w
    for i in range(no):
        w = 0.5 - 0.5 * cos(math.pi * i / no)
        L[n - 1 - i] *= w
        R[n - 1 - i] *= w
    pk = max(_peak(L), _peak(R))
    if pk > 0:
        g = 10 ** (PEAK_DBFS / 20.0) / pk
        L = [v * g for v in L]
        R = [v * g for v in R]
    return L, R


HP_BY_CATEGORY = {"hit": 18.0}


def render(name, dur=None, seed=1, pitch=None, brightness=None):
    """(left, right, params) for a preset: finished, normalised, deterministic for the same inputs."""
    key = resolve_name(name)
    if key is None:
        raise KeyError("no preset called %r (sfx list shows them)" % name)
    fn, d0, dr, p0, pr, b0, align, gain, cat, desc = PRESETS[key]
    dur = float(d0 if dur is None else dur)
    if not dr[0] <= dur <= dr[1]:
        raise ValueError("%s: duration %.3f s is outside %.2f to %.2f s" % (key, dur, dr[0], dr[1]))
    pitch = float(p0 if pitch is None else pitch)
    if not pr[0] <= pitch <= pr[1]:
        raise ValueError("%s: pitch %.1f Hz is outside %.0f to %.0f Hz" % (key, pitch, pr[0], pr[1]))
    bright = float(b0 if brightness is None else brightness)
    if not 0.0 <= bright <= 1.0:
        raise ValueError("brightness must be between 0 and 1")
    rng = _rng(seed)
    n = _n(dur)
    L, R = fn(n, dur, pitch, bright, rng)
    L, R = list(L[:n]) + [0.0] * (n - len(L)), list(R[:n]) + [0.0] * (n - len(R))
    L, R = _finish(L, R, hp_hz=16.0 if key == "sub-drop" else HP_BY_CATEGORY.get(cat, 20.0),
                   lp_hz=18000.0 if cat == "tone" else 16000.0)
    params = {"preset": key, "dur": round(dur, 4), "seed": int(seed), "pitch": round(pitch, 2),
              "brightness": round(bright, 3)}
    if key == "riser":
        params["climax_s"] = round(dur - min(0.25, dur * 0.2), 4)
    return L, R, params


def measure(L, R, rate=SR, rel_db=-30.0):
    """Placement and QC numbers from the samples themselves (no ffmpeg needed).

    attack_s: the first sample within `rel_db` of the peak (04 section 7.1: land it on the frame it should hit);
    peak_s: the centre of the loudest 10 ms (placement of whooshes); end_s: the last moment the 10 ms level is within
    40 dB of its loudest; dc: mean of all samples; tail: the last 20 ms."""
    n = len(L)
    pk = max(_peak(L), _peak(R)) or 1e-12
    thr = pk * 10 ** (rel_db / 20.0)
    attack = 0
    for i in range(n):
        if abs(L[i]) >= thr or abs(R[i]) >= thr:
            attack = i
            break
    blk = max(1, rate // 1000)
    mul = operator.mul
    energy = []
    for b in range(0, n, blk):
        sl, sr = L[b:b + blk], R[b:b + blk]
        energy.append(sum(map(mul, sl, sl)) + sum(map(mul, sr, sr)))
    win = 10
    run = [sum(energy[max(0, i - win + 1):i + 1]) for i in range(len(energy))]
    best = max(range(len(run)), key=run.__getitem__) if run else 0
    peak_s = max(0.0, (best + 1 - win / 2.0) * blk / rate)
    top = run[best] if run else 0.0
    end_i = best
    lim = top * 1e-4
    for i in range(len(run) - 1, best - 1, -1):
        if run[i] >= lim:
            end_i = i
            break
    ai = max(range(n), key=lambda i: max(abs(L[i]), abs(R[i]))) if n else 0
    tn = min(n, int(0.02 * rate))
    tail = L[n - tn:] + R[n - tn:]
    tail_rms = math.sqrt(sum(v * v for v in tail) / max(1, len(tail))) if tail else 0.0
    dc = (sum(L) + sum(R)) / max(1, 2 * n)
    return {"duration_s": round(n / rate, 4), "peak_dbfs": round(20 * math.log10(pk), 2),
            "attack_s": round(attack / rate, 5), "peak_s": round(peak_s, 4), "sample_peak_s": round(ai / rate, 5),
            "end_s": round(min(n, (end_i + 1) * blk) / rate, 4), "dc_offset": round(dc, 7),
            "tail_rms_dbfs": round(20 * math.log10(tail_rms), 1) if tail_rms > 0 else -200.0,
            "tail_peak_dbfs": round(20 * math.log10(max(max(map(abs, tail)), 1e-12)), 1) if tail else -200.0}


def write_wav(path, L, R, rate=SR):
    """24-bit stereo WAV with the standard library: ints packed through array('i'), low three bytes kept."""
    full = 8388607.0
    li = [int(round(_clamp(v, -1.0, 1.0) * full)) for v in L]
    ri = [int(round(_clamp(v, -1.0, 1.0) * full)) for v in R]
    inter = [0] * (2 * len(li))
    inter[0::2] = li
    inter[1::2] = ri
    arr = array("i", inter)
    if sys.byteorder == "big":
        arr.byteswap()
    raw = arr.tobytes()
    out = bytearray(len(raw) // 4 * 3)
    out[0::3] = raw[0::4]
    out[1::3] = raw[1::4]
    out[2::3] = raw[2::4]
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(3)
        w.setframerate(rate)
        w.writeframes(bytes(out))


def read_wav(path):
    """(channels as lists of floats, rate) for 16-, 24- or 32-bit PCM WAV."""
    with wave.open(path, "rb") as w:
        ch, width, rate, frames = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(frames)
    if width == 3:
        b4 = bytearray(len(raw) // 3 * 4)
        b4[1::4] = raw[0::3]
        b4[2::4] = raw[1::3]
        b4[3::4] = raw[2::3]
        arr = array("i")
        arr.frombytes(bytes(b4))
        scale = 1.0 / 2147483648.0
    elif width == 2:
        arr = array("h")
        arr.frombytes(raw)
        scale = 1.0 / 32768.0
    elif width == 4:
        arr = array("i")
        arr.frombytes(raw)
        scale = 1.0 / 2147483648.0
    else:
        raise ValueError("unsupported sample width %d" % width)
    if sys.byteorder == "big":
        arr.byteswap()
    chans = [[v * scale for v in arr[c::ch]] for c in range(ch)]
    return chans, rate


def make(name, path, dur=None, seed=1, pitch=None, brightness=None):
    """Render a preset to `path` and return its manifest entry (parameters plus measured placement numbers)."""
    L, R, params = render(name, dur, seed, pitch, brightness)
    write_wav(path, L, R)
    m = measure(L, R)
    entry = dict(info(params["preset"]))
    entry.update({"params": params, "measured": m, "format": {"sample_rate": SR, "channels": 2, "bits": 24},
                  "synth_version": SYNTH_VERSION})
    if "climax_s" in params:
        entry["measured"]["climax_s"] = params["climax_s"]
    return entry


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render one nexa-sound synthesiser preset to a WAV file.")
    ap.add_argument("name")
    ap.add_argument("out")
    ap.add_argument("--dur", type=float)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--pitch", type=float)
    ap.add_argument("--brightness", type=float)
    a = ap.parse_args(argv)
    print(json.dumps(make(a.name, a.out, a.dur, a.seed, a.pitch, a.brightness), indent=1))


if __name__ == "__main__":
    main()
