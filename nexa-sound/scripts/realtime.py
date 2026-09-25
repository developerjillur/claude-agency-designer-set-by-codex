"""nexa-sound: record an exact-length bed from Lyria RealTime (lyria-realtime-exp, experimental, instrumental only).

Runs inside ~/.nexa-sound/venv (uv, Python 3.12, google-genai>=2.9), which `sound.py generate --realtime` creates on
first use after saying so. sound.py writes the config and reads the one JSON line this prints.

    python realtime.py --config CONFIG.json --out OUT.wav [--json]

CONFIG.json:
  {"weighted_prompts": [["Uplifting corporate pop", 1.0], ["soft piano", 0.5]],
   "config": {"bpm": 104, "scale": "C_MAJOR_A_MINOR", "density": 0.45, "brightness": 0.6, "guidance": 4.0},
   "automation": [{"t": 14.0, "density": 0.61, "brightness": 0.64, "mute_drums": false}],
   "seconds": 48.0, "preroll": 8.0, "api_version": "v1beta"}

How it records (Google's RealTime guide and the SDK source; untested against the live service here):
- the stream is 48 kHz, 16-bit, stereo PCM in chunks of about 2 s, paced in real time;
- it records preroll + seconds and drops the preroll, because the first 5 to 10 s after start are unsettled;
- the whole config is sent every time (fields left out fall back to defaults); an automation event is sent about
  2 s before its time, since changes take about 2 s to land; BPM and scale cannot change mid-stream (that needs
  reset_context, a hard cut), so automation may not touch them;
- an unknown scale, mode or field is an error, never dropped silently;
- a prompt the service filters is reported by name; the key is read by gemini_api and never printed;
- v1beta first, v1alpha when the service refuses v1beta; sessions stop at about 10 minutes.

Test hook: NEXA_REALTIME_FAKE=1 swaps the service for a local fake stream (NEXA_REALTIME_FAKE_LOG=FILE records the
calls it received).
"""
import argparse
import asyncio
import json
import math
import os
import sys
import wave
from array import array

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gemini_api  # noqa: E402

SR, CH, SW = 48000, 2, 2
BYTES_PER_S = SR * CH * SW
MODEL = "models/lyria-realtime-exp"
SCALES = ["C_MAJOR_A_MINOR", "D_FLAT_MAJOR_B_FLAT_MINOR", "D_MAJOR_B_MINOR", "E_FLAT_MAJOR_C_MINOR",
          "E_MAJOR_D_FLAT_MINOR", "F_MAJOR_D_MINOR", "G_FLAT_MAJOR_E_FLAT_MINOR", "G_MAJOR_E_MINOR",
          "A_FLAT_MAJOR_F_MINOR", "A_MAJOR_G_FLAT_MINOR", "B_FLAT_MAJOR_G_MINOR", "B_MAJOR_A_FLAT_MINOR",
          "SCALE_UNSPECIFIED"]
MODES = ["QUALITY", "DIVERSITY", "VOCALIZATION"]
RANGES = {"guidance": (0.0, 6.0), "bpm": (60, 200), "density": (0.0, 1.0), "brightness": (0.0, 1.0),
          "temperature": (0.0, 3.0), "top_k": (1, 1000), "seed": (0, 2147483647)}
BOOLS = ("mute_bass", "mute_drums", "only_bass_and_drums")
MAX_SECONDS = 540.0
EDGE_S = 0.005


class ConfigError(ValueError):
    pass


def validate_config(cfg, where="config"):
    """The config as the SDK wants it; any unknown field or bad value is an error (never dropped)."""
    out = {}
    for k, v in cfg.items():
        if k in RANGES:
            lo, hi = RANGES[k]
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not lo <= v <= hi:
                raise ConfigError("%s.%s must be a number from %s to %s (got %r)" % (where, k, lo, hi, v))
            out[k] = int(v) if k in ("bpm", "top_k", "seed") else float(v)
        elif k in BOOLS:
            if not isinstance(v, bool):
                raise ConfigError("%s.%s must be true or false (got %r)" % (where, k, v))
            out[k] = v
        elif k == "scale":
            if v not in SCALES:
                raise ConfigError("%s.scale %r is not a Lyria RealTime scale; use one of: %s" % (
                    where, v, ", ".join(SCALES)))
            out[k] = v
        elif k == "music_generation_mode":
            if v not in MODES:
                raise ConfigError("%s.music_generation_mode must be one of %s (got %r)" % (where, ", ".join(MODES), v))
            out[k] = v
        else:
            raise ConfigError("%s has an unknown field %r" % (where, k))
    return out


def validate_prompts(prompts):
    out = []
    for p in prompts or []:
        if not (isinstance(p, (list, tuple)) and len(p) == 2 and isinstance(p[0], str) and p[0].strip()
                and isinstance(p[1], (int, float)) and not isinstance(p[1], bool) and p[1] != 0):
            raise ConfigError("each weighted prompt is [text, weight] with a weight that is not 0 (got %r)" % (p,))
        out.append((p[0].strip(), float(p[1])))
    if not out:
        raise ConfigError("at least one weighted prompt is needed")
    return out


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        spec = json.load(fh)
    seconds = float(spec.get("seconds") or 0)
    if not 1.0 <= seconds <= MAX_SECONDS:
        raise ConfigError("seconds must be 1 to %d (a session stops at about 10 minutes)" % MAX_SECONDS)
    preroll = float(spec.get("preroll", 8.0))
    if not 0.0 <= preroll <= 20.0:
        raise ConfigError("preroll must be 0 to 20 s")
    config = validate_config(spec.get("config") or {})
    autos = []
    for i, ev in enumerate(spec.get("automation") or []):
        ev = dict(ev)
        t = float(ev.pop("t"))
        prompts = ev.pop("prompts", None)
        if "bpm" in ev or "scale" in ev:
            raise ConfigError("automation %d changes bpm or scale; that needs reset_context (a hard cut), so it is "
                              "not allowed mid-stream" % i)
        autos.append({"t": t, "config": validate_config(ev, "automation[%d]" % i),
                      "prompts": validate_prompts(prompts) if prompts else None})
    autos.sort(key=lambda a: a["t"])
    return {"prompts": validate_prompts(spec.get("weighted_prompts")), "config": config, "automation": autos,
            "seconds": seconds, "preroll": preroll, "api_version": spec.get("api_version") or "v1beta"}


# ---------------------------------------------------------------- the real service (google-genai in the venv)

class Sdk(object):
    def __init__(self):
        from google import genai
        from google.genai import types
        self.genai, self.types = genai, types
        for name in SCALES:
            if not hasattr(types.Scale, name):
                raise ConfigError("this google-genai has no Scale.%s; update it in the venv" % name)

    def prompts(self, items):
        return [self.types.WeightedPrompt(text=t, weight=w) for t, w in items]

    def config(self, cfg):
        c = dict(cfg)
        if "scale" in c:
            c["scale"] = getattr(self.types.Scale, c["scale"])
        if "music_generation_mode" in c:
            c["music_generation_mode"] = getattr(self.types.MusicGenerationMode, c["music_generation_mode"])
        return self.types.LiveMusicGenerationConfig(**c)

    def connect(self, key, api_version):
        client = self.genai.Client(api_key=key, http_options={"api_version": api_version})
        return client.aio.live.music.connect(model=MODEL)


# ---------------------------------------------------------------- a fake stream for tests

class _Chunk(object):
    def __init__(self, data):
        self.data = data


class _Content(object):
    def __init__(self, chunks):
        self.audio_chunks = chunks


class _Msg(object):
    def __init__(self, content=None, filtered=None):
        self.server_content = content
        self.filtered_prompt = filtered


class FakeSession(object):
    """Stands in for the SDK session: a steady synthetic groove at the configured BPM, in 2 s chunks."""

    def __init__(self, log_path=None):
        self.log_path = log_path
        self.calls = []
        self.bpm = 120
        self.t = 0
        self.filtered = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        if self.log_path:
            with open(self.log_path, "w", encoding="utf-8") as fh:
                json.dump(self.calls, fh)
        return False

    async def set_weighted_prompts(self, prompts):
        self.calls.append({"call": "set_weighted_prompts", "prompts": prompts})
        self.filtered += [t for t, _ in prompts if "fake:filtered" in t]

    async def set_music_generation_config(self, config):
        self.calls.append({"call": "set_music_generation_config", "config": dict(config)})
        self.bpm = config.get("bpm", self.bpm)

    async def play(self):
        self.calls.append({"call": "play"})

    async def stop(self):
        self.calls.append({"call": "stop"})

    async def reset_context(self):
        self.calls.append({"call": "reset_context"})

    def _bar(self):
        """One bar (4 beats) of a steady groove at the current BPM, interleaved 16-bit stereo."""
        period = 60.0 / self.bpm
        n = int(round(4 * period * SR))
        out = array("h", [0]) * (2 * n)
        sin, exp = math.sin, math.exp
        for i in range(n):
            t = i / float(SR)
            u = t % period
            kick = (1.0 if int(t / period) == 0 else 0.5) * sin(2 * math.pi * 55 * u) * exp(-u * 12)
            pad = 0.08 * (sin(2 * math.pi * 220 * t) + sin(2 * math.pi * 277.5 * t))
            v = int(9000 * (kick + pad))
            out[2 * i] = v
            out[2 * i + 1] = v
        return out

    def _chunk(self, seconds=2.0):
        if getattr(self, "_loop", None) is None or self._loop_bpm != self.bpm:
            self._loop, self._loop_bpm = self._bar(), self.bpm
        loop = self._loop
        n = 2 * int(SR * seconds)
        start = (2 * self.t) % len(loop)
        reps = (start + n) // len(loop) + 1
        chunk = (loop * (reps + 1))[start:start + n]
        self.t += n // 2
        return chunk.tobytes()

    async def receive(self):
        if self.filtered:
            yield _Msg(filtered=self.filtered.pop(0))
        for _ in range(3):
            yield _Msg(_Content([_Chunk(self._chunk())]))


class FakeSdk(object):
    def __init__(self):
        self.session = FakeSession(os.environ.get("NEXA_REALTIME_FAKE_LOG"))

    def prompts(self, items):
        return [[t, w] for t, w in items]

    def config(self, cfg):
        return dict(cfg)

    def connect(self, key, api_version):
        return self.session


# ---------------------------------------------------------------- recording

def _filtered_text(value):
    for name in ("text", "filtered_reason"):
        if getattr(value, name, None):
            return str(getattr(value, name))
    return str(value)


async def record(session, sdk, spec):
    """The PCM of preroll + seconds, the filtered prompts and the chunk count."""
    need = int(round((spec["seconds"] + spec["preroll"]) * SR)) * CH * SW
    buf = bytearray()
    filtered, chunks = [], 0
    current = dict(spec["config"])
    pending = [dict(a, send_at=max(0.0, a["t"] + spec["preroll"] - 2.0)) for a in spec["automation"]]
    await session.set_weighted_prompts(prompts=sdk.prompts(spec["prompts"]))
    await session.set_music_generation_config(config=sdk.config(current))
    await session.play()

    async def pull():
        nonlocal chunks
        while len(buf) < need:
            async for msg in session.receive():
                f = getattr(msg, "filtered_prompt", None)
                if f:
                    filtered.append(_filtered_text(f))
                sc = getattr(msg, "server_content", None)
                for c in (getattr(sc, "audio_chunks", None) or []) if sc else []:
                    buf.extend(c.data)
                    chunks += 1
                recorded = len(buf) / float(BYTES_PER_S)
                while pending and recorded >= pending[0]["send_at"]:
                    ev = pending.pop(0)
                    current.update(ev["config"])
                    if ev["prompts"]:
                        await session.set_weighted_prompts(prompts=sdk.prompts(ev["prompts"]))
                    await session.set_music_generation_config(config=sdk.config(current))
                if len(buf) >= need:
                    return
            await asyncio.sleep(0)

    await asyncio.wait_for(pull(), timeout=(spec["seconds"] + spec["preroll"]) * 1.5 + 60)
    await session.stop()
    return bytes(buf[:need]), filtered, chunks


def fade_edges(pcm):
    """5 ms raised-cosine fades at both cut points: a cut in the middle of a continuous stream would click."""
    a = array("h")
    a.frombytes(pcm)
    if sys.byteorder == "big":
        a.byteswap()
    n = len(a) // CH
    m = min(int(EDGE_S * SR), n // 2)
    for i in range(m):
        w = 0.5 - 0.5 * math.cos(math.pi * i / m)
        for c in range(CH):
            a[i * CH + c] = int(a[i * CH + c] * w)
            j = (n - 1 - i) * CH + c
            a[j] = int(a[j] * w)
    if sys.byteorder == "big":
        a.byteswap()
    return a.tobytes()


def _refused(err):
    text = str(err).lower()
    return any(k in text for k in ("api key", "api_key", "permission", "unauthenticated", "401", "403"))


def _version_refused(err):
    text = str(err).lower()
    return any(k in text for k in ("404", "not found", "not supported", "unimplemented"))


async def run(spec, out):
    fake = bool(os.environ.get("NEXA_REALTIME_FAKE"))
    sdk = FakeSdk() if fake else Sdk()
    pairs = [("fake", "fake")] if fake else gemini_api.keys()
    if not pairs:
        raise RuntimeError(gemini_api.MISSING_KEY_HELP)
    versions = [spec["api_version"]] + (["v1alpha"] if spec["api_version"] != "v1alpha" else [])
    last = None
    for source, key in pairs:
        for version in versions:
            try:
                async with sdk.connect(key, version) as session:
                    pcm, filtered, chunks = await record(session, sdk, spec)
                start = int(round(spec["preroll"] * SR)) * CH * SW
                kept = fade_edges(pcm[start:])
                with wave.open(out, "wb") as w:
                    w.setnchannels(CH)
                    w.setsampwidth(SW)
                    w.setframerate(SR)
                    w.writeframes(kept)
                return {"ok": True, "file": os.path.abspath(out),
                        "recorded_s": round(len(kept) / float(BYTES_PER_S), 3),
                        "preroll_s": spec["preroll"], "chunks": chunks, "filtered_prompts": filtered,
                        "api_version": version, "key_source": source if not fake else None,
                        "edges": "5 ms fades at both cut points", "fake": fake or None}
            except ConfigError:
                raise
            except Exception as err:  # the SDK raises many kinds; decide by what it says
                last = err
                if _version_refused(err) and version != versions[-1]:
                    continue
                if _refused(err):
                    break
                raise
    raise RuntimeError("Lyria RealTime refused every key: %s" % gemini_api.scrub(str(last)))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Record an exact-length Lyria RealTime bed.")
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        spec = load(a.config)
        result = asyncio.run(run(spec, a.out))
    except ConfigError as err:
        print("realtime: %s" % err, file=sys.stderr)
        sys.exit(2)
    except Exception as err:
        print("realtime: %s" % gemini_api.scrub(str(err)), file=sys.stderr)
        sys.exit(1)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
