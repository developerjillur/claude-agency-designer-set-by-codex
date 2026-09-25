"""Offline tests for nexa-sound: no network and no real keys. A local fake server stands in for the Gemini API (Lyria
3.5, Lyria 3 Clip, the listening judge, the models list), Freesound and ElevenLabs; a fake stream stands in for Lyria
RealTime. Synthetic sound comes from ffmpeg's aevalsrc and the skill's own synthesiser. Tests that need ffmpeg skip
when it is missing.

Run: python3 -m unittest discover -s ~/.claude/skills/nexa-sound/tests
"""
import base64
import hashlib
import http.server
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.parse
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
SCRIPTS = KIT / "scripts"
sys.path.insert(0, str(SCRIPTS))
import beats  # noqa: E402
import sfx_synth  # noqa: E402
import sound  # noqa: E402

HAVE_FF = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
HAVE_MP3 = HAVE_FF and " libmp3lame " in subprocess.run(["ffmpeg", "-hide_banner", "-encoders"],
                                                        capture_output=True, text=True).stdout
NEED_FF = unittest.skipUnless(HAVE_FF, "needs ffmpeg and ffprobe")
FAKE_KEY = "test-key-0000"
FS_KEY = "fs-test-key-1111"
EL_KEY = "el-test-key-2222"
ROOT = None            # the module's temporary folder
OUTPUTS = []           # every stdout and stderr the CLI printed, checked for keys at the end
SAVED_ENV = {}
SERVER = None


# ================================================================ synthetic sound

def ff(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y"] + [str(a) for a in args], check=True)


def groove_expr(bpm, dur, ring=2.0, idx=0):
    """Kick on 1 and 3 (1 accented), snare on 2 and 4, eighth-note hats, a bass changing every bar, a pad, and a
    ring-out after the drums stop."""
    p = 60.0 / bpm
    t1 = dur - ring
    u = "mod(t,%.9f)" % p
    k = "floor(t/%.9f)" % p
    m = "mod(%s,4)" % k
    kick = "(eq(%s,0)*1.0+eq(%s,2)*0.55)*sin(2*PI*55*%s+30*(1-exp(-%s*35)))*exp(-%s*9)" % (m, m, u, u, u)
    snare = "(eq(%s,1)+eq(%s,3))*0.3*(2*random(%d)-1)*exp(-%s*28)" % (m, m, idx, u)
    hat = "0.07*(2*random(%d)-1)*exp(-mod(t,%.9f)*90)" % (idx + 1, p / 2)
    bass = "0.18*sin(2*PI*if(mod(floor(%s/4),2),73.42,55)*t)*(0.6+0.4*exp(-%s*4))" % (k, u)
    pad = "0.05*(sin(2*PI*220*t)+sin(2*PI*277.18*t)+sin(2*PI*329.63*t))"
    body = "(%s+%s+%s)*lt(t,%.3f)" % (kick, snare, hat, t1)
    tail = "if(gt(t,%.3f),exp(-(t-%.3f)*3.5),1)" % (t1, t1)
    return "0.6*((%s)+(%s+%s)*%s)" % (body, bass, pad, tail)


def groove(path, bpm, dur, rate=44100, codec=None, dc=0.0):
    expr = groove_expr(bpm, dur) + ("+%g" % dc if dc else "")
    args = ["-f", "lavfi", "-i", "aevalsrc='%s':s=%d:d=%.3f" % (expr, rate, dur),
            "-af", "pan=stereo|c0=c0|c1=c0"]
    if codec:
        args += ["-c:a", codec]
    ff(*(args + [path]))


def dotted(path, bpm, dur):
    """Kick and pluck on sixteenths 0, 3, 6, 9 and 12 of every bar (dotted eighths, then a quarter), soft eighth-note
    hats and a pad: the syncopation that made a real Lyria take at 110 BPM read as 146.7 (4/3 of it)."""
    s = 60.0 / bpm / 4
    pos = "floor(mod(t,%.9f)/%.9f)" % (16 * s, s)
    u = "mod(t,%.9f)" % s
    trig = "+".join("eq(%s,%d)" % (pos, k) for k in (0, 3, 6, 9, 12))
    kick = "(%s)*sin(2*PI*55*%s+30*(1-exp(-%s*35)))*exp(-%s*30)" % (trig, u, u, u)
    pluck = "(%s)*0.35*sin(2*PI*880*t)*exp(-%s*40)" % (trig, u)
    hat = "0.05*(2*random(1)-1)*exp(-mod(t,%.9f)*90)" % (2 * s)
    pad = "0.05*(sin(2*PI*220*t)+sin(2*PI*261.63*t)+sin(2*PI*329.63*t))"
    ff("-f", "lavfi", "-i", "aevalsrc='0.6*(%s+%s+%s+%s)':s=44100:d=%g" % (kick, pluck, hat, pad, dur),
       "-af", "pan=stereo|c0=c0|c1=c0", path)


def clicks(path, bpm, t0, dur):
    """A click on every beat, a low thump on each downbeat, and a pad under it."""
    p = 60.0 / bpm
    expr = ("gte(t,{t0})*(0.35*sin(2*PI*2000*t)*exp(-mod(t-{t0},{p})*300)+lt(mod(t-{t0},4*{p}),{p})*0.8*"
            "sin(2*PI*60*mod(t-{t0},{p}))*exp(-mod(t-{t0},{p})*25))+0.06*(sin(2*PI*220*t)+sin(2*PI*277.18*t)+"
            "sin(2*PI*329.63*t))").format(t0=t0, p="%.9f" % p)
    ff("-f", "lavfi", "-i", "aevalsrc='%s':s=44100:d=%g" % (expr, dur), "-af", "pan=stereo|c0=c0|c1=c0", path)


SENTENCES = [(0.3, 2.1), (2.6, 4.7), (5.2, 6.9), (7.6, 9.7), (10.0, 11.6)]


def voice(path, noise_db=None, hum_db=None, level=0.35, stereo=False):
    """Fake speech: a 180 Hz carrier with 8 harmonics, 4.5 syllables a second, 250 to 700 ms between sentences."""
    gate = "+".join("between(t,%.3f,%.3f)" % s for s in SENTENCES)
    syl = "(0.5-0.5*cos(2*PI*mod(t,0.22)/0.22))"
    f0 = "(180+12*sin(2*PI*0.7*t))"
    carrier = "+".join("%.3f*sin(2*PI*%d*%s*t)" % (1.0 / h, h, f0) for h in range(1, 9))
    expr = "%g*(%s)*%s*(%s)/2.2" % (level, gate, syl, carrier)
    if noise_db is not None:
        expr += "+%g*(2*random(0)-1)" % (10 ** (noise_db / 20.0) * 1.73)
    if hum_db is not None:
        expr += "+%g*sin(2*PI*50*t)" % (10 ** (hum_db / 20.0) * 1.414)
    args = ["-f", "lavfi", "-i", "aevalsrc='%s':s=48000:d=12" % expr]
    if stereo:
        args += ["-af", "pan=stereo|c0=c0|c1=c0"]
    ff(*(args + [path]))


def read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def read_text(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_jsonl(path):
    return [json.loads(x) for x in read_text(path).splitlines() if x.strip()]


def decode(path, channels=2):
    return sound.decode_f32(str(path), channels=channels)


def rms_db(samples):
    return 10 * math.log10(sum(v * v for v in samples) / max(1, len(samples)) + 1e-20)


_CACHE = {}


def shared(name):
    """Inputs made once per run."""
    if name in _CACHE:
        return _CACHE[name]
    p = os.path.join(ROOT, "inputs", name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if name == "groove.wav":
        groove(p, 104, 26.0)
    elif name == "clicks104.wav":
        clicks(p, 104, 0.3, 20.0)
    elif name == "dotted110.wav":
        dotted(p, 110, 24.0)
    elif name == "voice_noisy.wav":
        voice(p, noise_db=-42, hum_db=-38)
    elif name == "voice.wav":
        voice(p)
    elif name == "bed.wav":
        ff("-f", "lavfi", "-i", "aevalsrc='0.1*(sin(2*PI*220*t)+sin(2*PI*277.18*t)+sin(2*PI*329.63*t))|"
               "0.1*(sin(2*PI*221*t)+sin(2*PI*277.18*t)+sin(2*PI*330.63*t))':s=48000:d=16", "-c:a", "pcm_s24le", p)
    _CACHE[name] = p
    return p


# ================================================================ the fake server

def id3_c2pa():
    """A minimal ID3v2.3 tag with a GEOB frame of type application/c2pa, as Google's Lyria MP3s carry."""
    data = b"\x00" + b"application/c2pa\x00" + b"c2pa.json\x00" + b"c2pa manifest store\x00" + b'{"fake": true}'
    frame = b"GEOB" + len(data).to_bytes(4, "big") + b"\x00\x00" + data
    size = len(frame)
    syncsafe = bytes([(size >> 21) & 0x7F, (size >> 14) & 0x7F, (size >> 7) & 0x7F, size & 0x7F])
    return b"ID3\x03\x00\x00" + syncsafe + frame


class Fake(object):
    lock = threading.Lock()
    log = []
    active = 0
    max_active = 0
    el_tier = "creator"
    audio = {}
    blocks = {}

    @classmethod
    def track(cls, bpm, seconds, fmt, dc=0.0):
        key = (round(bpm, 2), int(seconds), fmt, dc)
        with cls.lock:
            if key in cls.audio:
                return cls.audio[key]
        path = os.path.join(ROOT, "fake", "track_%s_%d_%g.%s" % (key[0], key[1], dc, fmt))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if fmt == "mp3" and not HAVE_MP3:     # the spec's fallback: a WAV when this ffmpeg cannot write MP3
            fmt, path = "wav", path[:-4] + ".wav"
        if fmt == "wav":
            groove(path, bpm, seconds, rate=44100, codec="pcm_s16le", dc=dc)
            data = read_bytes(path)
        else:
            groove(path, bpm, seconds, rate=44100, codec="libmp3lame")
            data = id3_c2pa() + read_bytes(path)
        with cls.lock:
            cls.audio[key] = data
        return data


def prompt_text(body):
    inp = body.get("input")
    if isinstance(inp, str):
        return inp
    return " ".join(b.get("text", "") for b in inp or [] if isinstance(b, dict) and b.get("type") == "text")


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _record(self, body=None):
        with Fake.lock:
            Fake.log.append({"method": self.command, "path": self.path, "headers": dict(self.headers.items()),
                             "body": body})

    def do_GET(self):
        self._record()
        url = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(url.query)
        if url.path == "/v1beta/models":
            if self.headers.get("x-goog-api-key") != FAKE_KEY:
                return self._send(401, {"error": {"code": 401, "message": "API key not valid"}})
            return self._send(200, {"models": [{"name": "models/" + m} for m in
                                               ("lyria-3.5", "lyria-3-clip-preview", "lyria-realtime-exp",
                                                "gemini-3.8-flash")]})
        if url.path == "/apiv2/search/text/":
            if self.headers.get("Authorization") != "Token " + FS_KEY:
                return self._send(401, {"detail": "Invalid token"})
            flt = (q.get("filter") or [""])[0]
            if 'license:"Creative Commons 0"' not in flt:
                return self._send(400, {"detail": "the test expects the CC0 filter"})
            base = "http://127.0.0.1:%d" % SERVER.server_address[1]
            return self._send(200, {"count": 2, "results": [
                {"id": 111, "name": "Glass NC", "username": "someone", "duration": 1.2,
                 "license": "http://creativecommons.org/licenses/by-nc/4.0/",
                 "previews": {"preview-hq-mp3": base + "/previews/111.mp3"}},
                {"id": 222, "name": "Glass break", "username": "maker", "duration": 1.1,
                 "license": "http://creativecommons.org/publicdomain/zero/1.0/",
                 "url": "https://freesound.org/people/maker/sounds/222/",
                 "previews": {"preview-hq-mp3": base + "/previews/222.mp3"}}]})
        if url.path.startswith("/previews/"):
            return self._send(200, Fake.audio_sfx(), "audio/mpeg")
        if url.path == "/v1/user/subscription":
            if self.headers.get("xi-api-key") != EL_KEY:
                return self._send(401, {"detail": "invalid key"})
            return self._send(200, {"tier": Fake.el_tier})
        return self._send(404, {"error": "no route %s" % url.path})

    def do_POST(self):
        raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        url = urllib.parse.urlparse(self.path)
        if url.path == "/v1/sound-generation":
            body = json.loads(raw.decode("utf-8"))
            self._record(body)
            if self.headers.get("xi-api-key") != EL_KEY:
                return self._send(401, {"detail": "invalid key"})
            return self._send(200, Fake.audio_sfx(), "audio/mpeg")
        body = json.loads(raw.decode("utf-8")) if raw else {}
        rec = {k: (v if k != "input" else prompt_text(body)) for k, v in body.items()}
        if isinstance(body.get("input"), list):
            rec["images"] = [b.get("mime_type") for b in body["input"] if b.get("type") == "image" and b.get("data")]
        self._record(rec)
        if url.path != "/v1beta/interactions":
            return self._send(404, {"error": "no route"})
        if self.headers.get("x-goog-api-key") != FAKE_KEY:
            return self._send(401, {"error": {"code": 401, "message": "API key not valid. Please pass a valid key."}})
        with Fake.lock:
            Fake.active += 1
            Fake.max_active = max(Fake.max_active, Fake.active)
        try:
            time.sleep(0.15)
            return self._interaction(body)
        finally:
            with Fake.lock:
                Fake.active -= 1

    def _interaction(self, body):
        model = body.get("model")
        text = prompt_text(body)
        if body.get("response_format") and model in ("lyria-3.5", "lyria-3-clip-preview"):   # as the live API
            mime = str(body["response_format"].get("mime_type", "")).upper().replace("/", "_")
            return self._send(400, {"error": {"message": "Audio MIME type %s is not supported for models/%s" % (
                mime, model), "code": "invalid_request"}})
        for tag, times in (("fake:outblock1", 1), ("fake:outblock2", 2)):   # blocked after generation
            if tag in text:
                with Fake.lock:
                    Fake.blocks[tag] = Fake.blocks.get(tag, 0) + 1
                    n = Fake.blocks[tag]
                if n <= times:
                    return self._send(400, {"error": {"message": "Request blocked for an unspecified policy reason. "
                                                      "Please modify your input and retry.",
                                           "code": "content_blocked"}})
        if "fake:slow" in text:
            time.sleep(1.5)
        if "fake:blocked" in text:
            return self._send(400, {"error": {"code": 400, "status": "INVALID_ARGUMENT",
                                              "message": "The prompt was blocked for safety reasons."}})
        if model == "gemini-3.8-flash":
            verdict = {"genre": "corporate pop", "mood": "optimistic", "tempo_feel": "mid", "instruments": ["piano"],
                       "vocals_present": "mood suspense" in text, "vocal_spans": [], "sections": [],
                       "ending": "ring_out", "fit_to_brief_1_10": 8, "problems": []}
            return self._send(200, {"id": "interactions/judge", "status": "completed", "steps": [
                {"type": "model_output", "content": [{"type": "text", "text": json.dumps(verdict)}]}]})
        bpm = float((re.search(r"(\d+(?:\.\d+)?) BPM", text) or re.search("(120)", "120")).group(1))
        texts = [{"type": "text", "text": "[[A0]] [[B1]] [[C2]]"}]
        if "fake:timed-lyrics" in text:
            texts.append({"type": "text", "text": "[0.0:4.5] We rise together\n[4.5:9.0] (oh oh)"})
        if model == "lyria-3.5":             # MP3, as the live API answers (a WAV for the DC test)
            secs = int((re.search(r"Create a (\d+)-second", text) or re.search("(14)", "14")).group(1))
            dc = 0.006 if "fake:dc" in text else 0.0
            data = Fake.track(bpm, secs, "wav" if dc else "mp3", dc=dc)
            mime = "audio/wav" if data[:4] == b"RIFF" else "audio/mpeg"
        elif model == "lyria-3-clip-preview":
            data, mime = Fake.track(bpm, 30, "mp3"), "audio/mpeg"
        else:
            return self._send(404, {"error": {"code": 404, "message": "model %s not found" % model}})
        content = texts + [{"type": "audio", "mime_type": mime, "data": base64.b64encode(data).decode("ascii")}]
        return self._send(200, {"id": "interactions/fake-%d" % len(Fake.log), "status": "completed",
                                "steps": [{"type": "user_input"}, {"type": "model_output", "content": content}]})


def _audio_sfx():
    path = os.path.join(ROOT, "fake", "sfx.mp3")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        ff("-f", "lavfi", "-i", "aevalsrc='(2*random(0)-1)*exp(-t*9)*lt(t,0.9)':s=44100:d=1", "-c:a",
           "libmp3lame" if HAVE_MP3 else "pcm_s16le", "-f", "mp3" if HAVE_MP3 else "wav", path)
    return read_bytes(path)


Fake.audio_sfx = staticmethod(_audio_sfx)


# ================================================================ module set-up

def setUpModule():
    global ROOT, SERVER
    ROOT = tempfile.mkdtemp(prefix="nexa-sound-test-")
    SERVER = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=SERVER.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % SERVER.server_address[1]
    mu = os.path.join(ROOT, "media-use-sfx")
    os.makedirs(mu)
    env = {"NEXA_SOUND_HOME": os.path.join(ROOT, "home"), "NEXA_GEMINI_BASE_URL": base,
           "NEXA_GEMINI_SLEEP_SCALE": "0", "NEXA_NO_KEYCHAIN": "1", "GEMINI_API_KEY": FAKE_KEY,
           "NEXA_FREESOUND_BASE_URL": base, "NEXA_ELEVENLABS_BASE_URL": base, "NEXA_MEDIA_USE_SFX": mu}
    for k in list(os.environ):
        if k.startswith("GEMINI_API_KEY_") or k in ("GOOGLE_API_KEY", "FREESOUND_API_KEY", "ELEVENLABS_API_KEY",
                                                  "NEXA_SFX_DIRS", "NEXA_SOUND_VENV_PYTHON",
                                                  "NEXA_SOUND_ISOLATE_BIN", "NEXA_REALTIME_FAKE"):
            SAVED_ENV[k] = os.environ.pop(k)
    for k, v in env.items():
        SAVED_ENV.setdefault(k, os.environ.get(k))
        os.environ[k] = v


def tearDownModule():
    if SERVER:
        SERVER.shutdown()
        SERVER.server_close()
    for k, v in SAVED_ENV.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    if ROOT:
        shutil.rmtree(ROOT, ignore_errors=True)


def cli(*args, expect=0, env=None):
    e = dict(os.environ)
    e.update(env or {})
    r = subprocess.run([sys.executable, str(SCRIPTS / "sound.py")] + [str(a) for a in args],
                       capture_output=True, text=True, env=e, timeout=600)
    OUTPUTS.append(r.stdout + r.stderr)
    if expect is not None and r.returncode != expect:
        raise AssertionError("sound.py %s exited %d (wanted %d):\n%s\n%s" % (
            " ".join(map(str, args)), r.returncode, expect, r.stdout[-1500:], r.stderr[-1500:]))
    return r


def cli_json(*args, expect=0, env=None):
    r = cli(*(list(args) + ["--json"]), expect=expect, env=env)
    return json.loads(r.stdout)


def tmp(*parts):
    p = os.path.join(ROOT, *parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def make_brief(name, duration=20.0, mood="corporate", notes=None, extra=()):
    out = tmp("briefs", name + ".json")
    args = ["brief", "--duration", duration, "--mood", mood, "--out", out] + list(extra)
    if notes:
        args += ["--notes", notes]
    cli(*args)
    return out


# ================================================================ tests

class A_BriefTests(unittest.TestCase):
    def cuts_file(self):
        p = tmp("brief_cuts.json")
        with open(p, "w") as fh:
            json.dump({"duration_s": 45, "cuts": [
                {"t": 6.2, "weight": 1, "label": "problem"}, {"t": 14.0, "weight": 2.5, "label": "Acme product reveal"},
                {"t": 15.1, "weight": 0.5, "label": "tiny"}, {"t": 27.5, "weight": 1.2, "label": "features demo"},
                {"t": 38.0, "weight": 1.5, "label": "CTA: buy now"}],
                "speech": [{"start": 0.5, "end": 5.8}, {"start": 6.5, "end": 13.2}, {"start": 16.0, "end": 26.0},
                           {"start": 28.0, "end": 37.0}]}, fh)
        return p

    def test_like_a_name_is_refused_behind_small_words(self):
        for phrase in ("make it sound like a Rihanna song", "like the Beatles but modern", "sung like a young Adele",
                       "production like an early Kanye West track"):
            r = cli("brief", "--duration", 20, "--mood", "corporate", "--notes", phrase, "--out",
                    tmp("refused.json"), expect=1)
            self.assertIn("brief refused", r.stderr, phrase)
        ok = cli_json("brief", "--duration", 20, "--mood", "corporate", "--notes", "soft like rain on a roof",
                      "--out", tmp("rain.json"))
        self.assertIn("like rain", ok["prompt"])

    def test_lyrics_need_vocals_and_are_checked(self):
        r = cli("brief", "--duration", 20, "--mood", "corporate", "--notes", "Lyrics: we walk the river road",
                "--out", tmp("lyr1.json"), expect=1)
        self.assertIn("needs --vocals", r.stderr)
        r = cli("brief", "--duration", 20, "--mood", "corporate", "--vocals", "--notes",
                "Lyrics: it sounds just like Rihanna", "--out", tmp("lyr2.json"), expect=1)
        self.assertIn("like Rihanna", r.stderr)
        ok = cli_json("brief", "--duration", 20, "--mood", "corporate", "--vocals", "--notes",
                      "Lyrics: we walk the river road", "--out", tmp("lyr3.json"))
        self.assertIn("river road", ok["prompt"])

    def test_sections_come_from_the_cuts(self):
        b = cli_json("brief", "--duration", 45, "--mood", "corporate", "--cuts", self.cuts_file(), "--out",
                     tmp("b1.json"))
        prompt = b["prompt"]
        self.assertIn("Create a 47-second instrumental", prompt)          # {DUR} is the length plus 2 s
        self.assertTrue(prompt.endswith("Instrumental."))
        lines = [ln for ln in prompt.splitlines() if ln.startswith("[")]
        self.assertEqual(len(lines), 5, lines)                            # the 1.1 s section was merged away
        for ln in lines:
            self.assertRegex(ln, r"^\[\d:\d\d - \d:\d\d\] [A-Z][A-Za-z ]+: .+\. Intensity: \d+/10$")
        self.assertIn("[0:14 - 0:28] Reveal: Lift", prompt)
        self.assertIn("Call to action", prompt)
        self.assertNotIn("Acme", prompt)                                  # edit-list words never reach Lyria
        by_label = {s["label"]: s for s in b["sections"]}
        self.assertIn(by_label["Intro"]["intensity"], (2, 3, 4))          # narrated: 2 to 4
        self.assertIn(by_label["Reveal"]["intensity"], (6, 7, 8))         # reveals and calls to action: 6 to 8
        self.assertIn(by_label["Call to action"]["intensity"], (6, 7, 8))
        brief = load_json(tmp("b1.json"))
        self.assertEqual(brief["drop_s"], 14.0)                           # {DROP}: the heaviest cut
        self.assertEqual(brief["scale"], "C_MAJOR_A_MINOR")

    def test_names_and_quoted_titles_are_refused(self):
        for bad in ("in the style of Daft Punk", "a vibe like Coldplay", 'the hook from "Blinding Lights"',
                    "cover of Yesterday", "Rabindra Sangeet feel", "feat. a rapper", "a la Hans Zimmer"):
            r = cli("brief", "--duration", 30, "--mood", "ad", "--notes", bad, "--out", tmp("bad.json"), expect=1)
            self.assertIn("brief refused", r.stderr, bad)
        for ok in ("sounds like rain on a window", "a relaxed style of drumming", "like a heartbeat",
                   "don't rush the ending"):
            cli("brief", "--duration", 30, "--mood", "lofi", "--notes", ok, "--out", tmp("ok.json"))

    def test_every_template_passes_and_vocals_drop_instrumental(self):
        moods = sound.load_moods()
        self.assertEqual(len(moods), 12)
        for mid, m in moods.items():
            self.assertEqual(sound.name_problems(m["template"]), [], mid)
            for ph in ("{DUR}", "{SECTIONS}", "{BPM}", "{KEY}"):
                self.assertIn(ph, m["template"], (mid, ph))
            self.assertTrue(m["template"].endswith("Instrumental."), mid)
            self.assertIn(sound.scale_for_key(m["key"]), sound.SCALES)
        b = cli_json("brief", "--duration", 30, "--mood", "bangla-folk", "--variant", "calm", "--vocals", "--notes",
                     "Lyrics: amar sonar desh", "--out", tmp("v.json"))
        self.assertNotIn("instrumental", b["prompt"].lower())
        self.assertIn("With lead vocals.", b["prompt"])

    def test_lyrics_get_only_the_strong_checks(self):
        cli("brief", "--duration", 30, "--mood", "vlog", "--vocals", "--notes", "Lyrics: Like Summer rain we run",
            "--out", tmp("lyr.json"))
        r = cli("brief", "--duration", 30, "--mood", "vlog", "--vocals", "--notes", "Lyrics: a cover of Yesterday",
                "--out", tmp("lyr.json"), expect=1)
        self.assertIn("cover of", r.stderr)
        r = cli("brief", "--duration", 30, "--mood", "vlog", "--vocals", "--notes", "sing like Adele. Lyrics: hi",
                "--out", tmp("lyr.json"), expect=1)
        self.assertIn("like Adele", r.stderr)

    def test_c2pa_is_looked_for_where_google_puts_it(self):
        self.assertTrue(sound.has_c2pa(id3_c2pa() + b"\xff\xfb" + b"\x00" * 64))
        self.assertFalse(sound.has_c2pa(b"ID3\x03\x00\x00\x00\x00\x00\x00" + b"c2pa in the audio" * 4))
        riff = b"RIFF" + (36).to_bytes(4, "little") + b"WAVEfmt " + (16).to_bytes(4, "little") + b"\x00" * 16
        self.assertFalse(sound.has_c2pa(riff + b"data" + (8).to_bytes(4, "little") + b"c2pa1234"))
        self.assertTrue(sound.has_c2pa(riff + b"C2PA" + (4).to_bytes(4, "little") + b"abcd"))

    def test_keys_map_to_realtime_scales(self):
        self.assertEqual(sound.scale_for_key("A minor"), "C_MAJOR_A_MINOR")
        self.assertEqual(sound.scale_for_key("D minor"), "F_MAJOR_D_MINOR")
        self.assertEqual(sound.scale_for_key("F# minor"), "A_MAJOR_G_FLAT_MINOR")
        self.assertEqual(sound.scale_for_key("Bb major"), "B_FLAT_MAJOR_G_MINOR")
        with self.assertRaises(ValueError):
            sound.parse_key("H dorian")


class B_SynthTests(unittest.TestCase):
    """Every preset, rendered in-process: plain Python, no ffmpeg needed."""

    @classmethod
    def setUpClass(cls):
        cls.rendered = {}
        for name in sfx_synth.PRESETS:
            L, R, params = sfx_synth.render(name, seed=1)
            cls.rendered[name] = (L, R, params, sfx_synth.measure(L, R))

    def test_there_are_at_least_the_presets_the_spec_names(self):
        for n in ("whoosh", "whoosh-short", "swipe", "swoosh-down", "pop", "bubble", "click", "tick", "key", "typing",
                  "ding", "chime", "notify", "success", "error", "riser", "downlifter", "impact", "boom", "sub-drop",
                  "glitch", "shutter", "sparkle"):
            self.assertIn(n, sfx_synth.PRESETS)
            self.assertTrue(sfx_synth.info(n)["description"])

    def test_every_preset_is_clean(self):
        for name, (L, R, params, m) in self.rendered.items():
            with self.subTest(preset=name):
                self.assertAlmostEqual(len(L) / 48000.0, params["dur"], delta=1.0 / 48000)
                self.assertAlmostEqual(m["peak_dbfs"], -1.0, delta=0.2)
                self.assertLess(abs(m["dc_offset"]), 0.001)
                self.assertLess(m["tail_rms_dbfs"], -60.0)                # the last 20 ms are near silence
                self.assertEqual((L[0], R[0], L[-1], R[-1]), (0.0, 0.0, 0.0, 0.0))
                self.assertLess(m["attack_s"], m["duration_s"])
                self.assertLessEqual(m["attack_s"], m["peak_s"] + 0.005)

    def test_attack_is_the_first_sample_within_30_db_of_the_peak(self):
        for name in ("impact", "click", "pop", "ding", "whoosh"):
            L, R, _, m = self.rendered[name]
            pk = max(max(map(abs, L)), max(map(abs, R)))
            i = int(round(m["attack_s"] * 48000))
            self.assertGreaterEqual(max(abs(L[i]), abs(R[i])), pk * 10 ** (-30 / 20.0) * 0.999, name)
            self.assertTrue(all(max(abs(L[j]), abs(R[j])) < pk * 10 ** (-30 / 20.0) for j in range(i)), name)
        for name in ("impact", "click", "tick", "pop", "key", "boom", "sub-drop"):
            self.assertLess(self.rendered[name][3]["attack_s"], 0.01, name)   # hits start at once

    def test_the_shortest_lengths_still_end_in_silence(self):
        for name in sfx_synth.PRESETS:
            d0 = sfx_synth.info(name)["dur_range"][0]
            L, R, _ = sfx_synth.render(name, dur=d0, seed=5)
            m = sfx_synth.measure(L, R)
            self.assertLess(m["tail_rms_dbfs"], -58.0, (name, d0))
            self.assertAlmostEqual(m["peak_dbfs"], -1.0, delta=0.2)

    def test_same_seed_same_sound_other_seed_other_sound(self):
        a = sfx_synth.render("whoosh", seed=7)
        b = sfx_synth.render("whoosh", seed=7)
        c = sfx_synth.render("whoosh", seed=8)
        self.assertEqual(a[0], b[0])
        self.assertNotEqual(a[0], c[0])

    def test_wide_presets_survive_a_mono_fold_down(self):
        for name in ("riser", "downlifter", "whoosh", "sparkle", "impact", "typing"):
            L, R = self.rendered[name][:2]
            stereo = (sum(v * v for v in L) + sum(v * v for v in R)) / 2.0
            mono = sum(((a + b) / 2.0) ** 2 for a, b in zip(L, R))
            self.assertLess(10 * math.log10(stereo / mono), 1.5, name)

    def test_parameters_are_checked(self):
        with self.assertRaises(ValueError):
            sfx_synth.render("click", dur=9.0)
        with self.assertRaises(KeyError):
            sfx_synth.render("no-such-sound")
        self.assertEqual(sfx_synth.resolve_name("UI Click"), "click")
        self.assertEqual(sfx_synth.resolve_name("swoosh"), "whoosh")

    def test_written_file_is_24_bit_48k_stereo(self):
        p = tmp("synth", "pop.wav")
        entry = sfx_synth.make("pop", p)
        (L, R), rate = sfx_synth.read_wav(p)
        self.assertEqual(rate, 48000)
        self.assertEqual(entry["format"], {"sample_rate": 48000, "channels": 2, "bits": 24})
        self.assertAlmostEqual(20 * math.log10(max(map(abs, L + R))), -1.0, delta=0.05)


@NEED_FF
class C_BeatTests(unittest.TestCase):
    def check(self, grid, bpm, t0):
        self.assertLess(abs(grid["bpm"] - bpm) / bpm, 0.01)
        period = 240.0 / bpm
        for d in grid["downbeats"]:
            k = round((d - t0) / period)
            self.assertLess(abs(d - (t0 + k * period)), 0.020, d)

    def test_click_track_with_an_accented_downbeat(self):
        path = shared("clicks104.wav")
        for hint in (104, None, 120):
            g = beats.analyze(path, hint)
            self.check(g, 104.0, 0.3)
            self.assertAlmostEqual(g["first_downbeat_s"], 0.3, delta=0.02)

    def test_a_groove_with_kick_on_one_and_three(self):
        g = beats.analyze(shared("groove.wav"), 104)
        self.check(g, 104.0, 0.0)
        self.assertEqual(g["downbeats"][0], 0.0)
        self.assertGreater(g["confidence"], 0.8)

    def test_dotted_eighths_do_not_read_as_four_thirds_of_the_tempo(self):
        path = shared("dotted110.wav")
        for hint in (112, 110, 104):
            self.assertAlmostEqual(beats.analyze(path, hint)["bpm"], 110.0, delta=0.6)


@NEED_FF
class D_FitLoopTests(unittest.TestCase):
    def test_fit_takes_out_dc_and_keeps_the_peaks_under_full_scale(self):
        src = tmp("fit", "hot_dc.wav")       # a float source over full scale with a 1 % DC offset
        ff("-f", "lavfi", "-i", "aevalsrc='(%s)*2.2+0.01':s=44100:d=20" % groove_expr(104, 20.0),
           "-af", "pan=stereo|c0=c0|c1=c0", "-c:a", "pcm_f32le", src)
        self.assertGreater(sound.astats(src)["peak_db"], 0.5)
        out = tmp("fit", "hot_dc_fit.wav")
        r = cli_json("fit", src, "--target", 12.0, "--bpm", 104, "--out", out)
        ops = dict((op["op"], op) for op in r["ops"])
        self.assertIn("dc_block", ops)
        self.assertLess(ops["gain"]["db"], -1.0)
        st = sound.astats(out)
        self.assertLess(st["peak_db"], -0.1)
        self.assertLess(abs(st["dc_offset"]), 0.0005)

    def test_shorter_lands_on_the_target_with_crossfades_on_bar_lines(self):
        src = shared("groove.wav")
        before = hashlib.sha256(read_bytes(src)).hexdigest()
        out = tmp("fit", "short.wav")
        r = cli_json("fit", src, "--target", 15.3, "--bpm", 104, "--out", out)
        self.assertLessEqual(abs(sound.probe(out)["duration_s"] - 15.3), 0.05)
        self.assertEqual(sound.probe(out)["sample_rate"], 48000)
        grid = beats.analyze(src, 104)
        cuts = [op for op in r["ops"] if op["op"] == "cut_middle"]
        self.assertTrue(cuts, r["ops"])
        for op in cuts:
            for t in (op["from_s"], op["to_s"]):
                self.assertLess(min(abs(t - d) for d in grid["downbeats"]), 0.002)
            self.assertAlmostEqual(op["xfade_s"], 60.0 / 104, delta=0.01)
        self.assertTrue(os.path.exists(r["report"]))
        self.assertEqual(hashlib.sha256(read_bytes(src)).hexdigest(), before)
        # the edit keeps one continuous bar grid
        g2 = beats.analyze(out, 104 * r["tempo_factor"])
        d = g2["downbeats"]
        step = 240.0 / (104 * r["tempo_factor"])
        self.assertLess(max(abs((x - d[0]) - round((x - d[0]) / step) * step) for x in d), 0.02)

    def test_longer_loops_whole_bars(self):
        out = tmp("fit", "long.wav")
        r = cli_json("fit", shared("groove.wav"), "--target", 41.0, "--bpm", 104, "--out", out)
        self.assertLessEqual(abs(sound.probe(out)["duration_s"] - 41.0), 0.05)
        loops = [op for op in r["ops"] if op["op"] == "loop"]
        self.assertTrue(loops, r["ops"])
        grid = beats.analyze(shared("groove.wav"), 104)
        for t in (loops[0]["from_s"], loops[0]["to_s"]):
            self.assertLess(min(abs(t - d) for d in grid["downbeats"]), 0.002)
        self.assertLessEqual(abs(r["tempo_factor"] - 1.0), 0.03)          # atempo only within 3 %

    def test_hits_on_cuts_move_the_start(self):
        cuts = tmp("fit", "cuts.json")
        bar = 240.0 / 104
        with open(cuts, "w") as fh:
            json.dump([{"t": 1.0 + 2 * bar, "weight": 2.0}, {"t": 1.0 + 4 * bar, "weight": 1.0}], fh)
        out = tmp("fit", "cuts.wav")
        r = cli_json("fit", shared("groove.wav"), "--target", 18.0, "--bpm", 104, "--cuts", cuts, "--out", out)
        h = r["hits_on_cuts"]
        self.assertLessEqual(abs(h["offset_s"]), 2.0)
        self.assertGreaterEqual(h["weighted_hits_after"], h["weighted_hits_before"])
        self.assertEqual(h["weighted_hits_after"], 3.0)
        self.assertLessEqual(abs(sound.probe(out)["duration_s"] - 18.0), 0.05)

    def test_fade_fallbacks(self):
        grid = {"bar_s": 2.0, "period_s": 0.5, "downbeats": [2.0 * k for k in range(12)], "first_downbeat_s": 0.0}
        bars = [[0.0] * 12 for _ in range(11)]
        tail = {"abrupt": True, "ring_room_s": 0.0, "ends_quiet": False}
        plan = sound.plan_fit(22.0, 15.5, grid, bars, [], tail, 0.0, "final_hit")
        self.assertEqual(plan["residual"]["kind"], "fade_end")
        self.assertEqual((plan["residual"]["fade_from_s"], plan["residual"]["fade_s"]), (14.0, 0.3))
        plan = sound.plan_fit(22.0, 15.5, grid, bars, [], tail, 0.0, "ring_out")
        self.assertEqual((plan["residual"]["fade_from_s"], plan["residual"]["fade_s"]), (14.0, 1.5))

    def test_an_abrupt_source_is_lengthened_into_a_fade_and_weak_grids_get_long_crossfades(self):
        grid = {"bar_s": 2.0, "period_s": 0.5, "downbeats": [2.0 * k for k in range(15)], "first_downbeat_s": 0.0,
                "confidence": 0.9}
        bars = [[0.0] * 12 for _ in range(14)]
        tail = {"abrupt": True, "ring_room_s": 0.0, "ends_quiet": False}
        plan = sound.plan_fit(30.0, 41.0, grid, bars, [], tail, 0.0, "ring_out")
        self.assertEqual(plan["residual"]["kind"], "fade_end")
        self.assertEqual(plan["edits"][0]["op"], "loop")
        self.assertGreaterEqual(sum(b - a for a, b in plan["segments"]), 42.0)
        self.assertLessEqual(plan["residual"]["fade_from_s"] + plan["residual"]["fade_s"], 41.0 + 1e-6)
        self.assertEqual(plan["xfade_s"], 0.5)
        weak = dict(grid, confidence=0.3)
        plan = sound.plan_fit(30.0, 25.0, weak, bars, [], {"abrupt": False, "ring_room_s": 3.0, "ends_quiet": True},
                              0.0)
        self.assertEqual(plan["xfade_s"], 2.0)
        self.assertTrue(any("weak" in n for n in plan["notes"]))

    def test_loop_is_seamless_whole_bars(self):
        out = tmp("loop", "loop4.wav")
        r = cli_json("loop", shared("groove.wav"), "--bars", 4, "--bpm", 104, "--out", out, "--preview")
        self.assertAlmostEqual(sound.probe(out)["duration_s"], 4 * 240.0 / 104, delta=0.002)
        self.assertAlmostEqual(sound.probe(r["preview"])["duration_s"], 3 * sound.probe(out)["duration_s"],
                               delta=0.002)
        self.assertLess(abs(r["join"]["continuation_db"]), 1.5)
        self.assertLess(r["join"]["sample_step_vs_source"], 3.0)


@NEED_FF
class E_SfxPlaceTests(unittest.TestCase):
    def test_list_names_every_preset(self):
        r = cli_json("sfx", "list")
        self.assertEqual([p["name"] for p in r["presets"]], list(sfx_synth.PRESETS))
        self.assertEqual(r["sources"]["media_use"], os.environ["NEXA_MEDIA_USE_SFX"])

    def test_make_writes_the_file_and_its_numbers(self):
        out = tmp("sfx", "impact.wav")
        r = cli_json("sfx", "make", "impact", "--out", out)
        q = cli_json("qc", out)
        self.assertEqual(q["kind"], "sfx")
        self.assertTrue(q["passed"], q["checks"])
        pr = sound.probe(out)
        self.assertEqual((pr["sample_rate"], pr["channels"], pr["bits"]), (48000, 2, 24))
        self.assertAlmostEqual(r["measured"]["peak_dbfs"], -1.0, delta=0.2)
        self.assertIsNotNone(r["measured"]["m_max_lufs"])
        self.assertEqual(r["placement"]["align"], "attack")

    def test_an_impact_lands_on_its_cue_and_a_whoosh_peaks_before_it(self):
        cues = tmp("place", "cues.json")
        with open(cues, "w") as fh:
            json.dump([{"t": 1.0, "name": "impact"}, {"t": 3.0, "name": "whoosh"}, {"t": 5.5, "name": "riser"},
                       {"t": 6.0, "name": "glass shatter"}], fh)
        out = tmp("place", "sfx.wav")
        r = cli_json("sfx", "place", cues, "--duration", 8, "--out", out, "--offline")
        self.assertEqual(len(r["cues"]), 3)
        self.assertEqual([s["name"] for s in r["skipped"]], ["glass shatter"])
        self.assertAlmostEqual(sound.probe(out)["duration_s"], 8.0, delta=0.001)
        a = decode(out)
        L, R = a[0::2], a[1::2]
        lo, hi = int(0.95 * 48000), int(1.3 * 48000)
        pk = max(max(abs(v) for v in L[lo:hi]), max(abs(v) for v in R[lo:hi]))
        thr = pk * 10 ** (-30 / 20.0)
        attack = next(i for i in range(lo, hi) if abs(L[i]) >= thr or abs(R[i]) >= thr) / 48000.0
        self.assertLess(abs(attack - 1.0), 0.002)                         # within 2 ms of t
        whoosh = [c for c in r["cues"] if c["name"] == "whoosh"][0]
        self.assertAlmostEqual(whoosh["start_s"] + whoosh["ref_s"], 3.0 - 0.05, delta=0.001)
        riser = [c for c in r["cues"] if c["name"] == "riser"][0]
        self.assertAlmostEqual(riser["start_s"] + riser["ref_s"], 5.5, delta=0.001)
        self.assertTrue(os.path.exists(r["cues_file"]))
        self.assertEqual(r["reference_dialogue_lufs"], -20.0)

    def test_media_use_files_are_used_in_place_with_their_licence(self):
        mu = os.environ["NEXA_MEDIA_USE_SFX"]
        name = "ping-x.mp3" if HAVE_MP3 else "ping-x.wav"
        ff("-f", "lavfi", "-i", "aevalsrc='sin(2*PI*1500*t)*exp(-t*20)':s=44100:d=0.4", os.path.join(mu, name))
        with open(os.path.join(mu, "manifest.json"), "w") as fh:
            json.dump({"ping-x": {"file": name, "duration": 0.4, "description": "sharp ping"}}, fh)
        cues = tmp("place", "mu.json")
        with open(cues, "w") as fh:
            json.dump([{"t": 1.0, "name": "ping-x"}], fh)
        r = cli_json("sfx", "place", cues, "--duration", 3, "--out", tmp("place", "mu.wav"), "--offline")
        res = r["cues"][0]["resolved"]
        self.assertEqual(res["source"], "media-use")
        self.assertEqual(res["file"], os.path.join(mu, name))            # by path, not copied
        self.assertIn("Pixabay", res["licence"])
        self.assertFalse(os.path.exists(tmp("place", "mu_files", name)))

    def test_freesound_cc0_and_elevenlabs_paid_only(self):
        env = {"FREESOUND_API_KEY": FS_KEY, "ELEVENLABS_API_KEY": EL_KEY}
        before = len(Fake.log)
        r = cli_json("sfx", "fetch", "glass break", "--source", "freesound", "--out", tmp("fetch"), env=env)
        self.assertEqual(r["licence"], "CC0")
        self.assertEqual(r["freesound_id"], 222)                          # the NC result was skipped
        self.assertIn("preview", r["quality"])
        previews = [x for x in Fake.log[before:] if x["path"].startswith("/previews/")]
        self.assertTrue(previews)
        self.assertNotIn("Authorization", previews[0]["headers"])        # the key goes only to the API host
        r = cli_json("sfx", "fetch", "door slam", "--source", "elevenlabs", "--out", tmp("fetch"), "--dur", 1.5,
                     env=env)
        self.assertEqual(r["source"], "elevenlabs")
        gen = [x for x in Fake.log if x["path"].startswith("/v1/sound-generation")][-1]
        self.assertEqual(gen["body"]["duration_seconds"], 1.5)
        ledger = load_jsonl(tmp("fetch", "ledger.jsonl"))
        self.assertEqual(ledger[-1]["model"], "elevenlabs-sfx")
        self.assertEqual(ledger[-1]["key_source"], "ELEVENLABS_API_KEY")
        Fake.el_tier = "free"
        try:
            r = cli("sfx", "fetch", "door slam", "--source", "elevenlabs", "--out", tmp("fetch"), env=env, expect=1)
            self.assertIn("free plan", r.stderr)
        finally:
            Fake.el_tier = "creator"
        cues = tmp("place", "online.json")
        with open(cues, "w") as fh:
            json.dump([{"t": 0.5, "query": "glass break"}], fh)
        r = cli_json("sfx", "place", cues, "--duration", 3, "--out", tmp("place", "online.wav"), env=env)
        self.assertEqual(r["cues"][0]["resolved"]["source"], "freesound")


@NEED_FF
class F_CleanTests(unittest.TestCase):
    def test_noise_floor_drops_and_the_output_stays_in_sync(self):
        src = shared("voice_noisy.wav")
        out = tmp("clean", "voice.wav")
        r = cli_json("clean", src, "--out", out, "--hum", 50)
        self.assertLess(r["noise_floor_db"]["after"], r["noise_floor_db"]["before"] - 6.0)
        self.assertLessEqual(abs(r["delay"]["sync_offset_ms"]), 2.0)
        pr = sound.probe(out)
        self.assertEqual((pr["sample_rate"], pr["bits"]), (48000, 24))
        self.assertAlmostEqual(pr["duration_s"], sound.probe(src)["duration_s"], delta=0.001)
        # an independent measurement of the offset
        lag, _ = sound.xcorr_offset_ms(sound.envelope_ms(src), sound.envelope_ms(out))
        self.assertLessEqual(abs(lag), 2.0)
        # pauses are quieter, measured between the known sentences
        a, b = decode(src, 1), decode(out, 1)
        gaps = [(x[1] + 0.1, y[0] - 0.1) for x, y in zip(SENTENCES, SENTENCES[1:])]
        sel = lambda s: [v for g0, g1 in gaps for v in s[int(g0 * 48000):int(g1 * 48000)]]  # noqa: E731
        self.assertLess(rms_db(sel(b)), rms_db(sel(a)) - 8.0)

    def test_isolation_falls_back_with_a_note(self):
        out = tmp("clean", "iso.wav")
        r = cli_json("clean", shared("voice_noisy.wav"), "--out", out, "--isolate",
                     env={"NEXA_SOUND_ISOLATE_BIN": "/nonexistent/voice-isolate"})
        self.assertFalse(r["isolate"]["ran"])
        self.assertTrue(any("voice isolation skipped" in n for n in r["notes"]))
        self.assertLessEqual(abs(r["delay"]["sync_offset_ms"]), 2.0)

    def test_a_known_delay_is_found(self):
        delayed = tmp("clean", "late.wav")
        ff("-i", shared("voice.wav"), "-af", "adelay=delays=12S:all=1,atrim=end_sample=576000", delayed)
        lag, _ = sound.xcorr_offset_ms(sound.envelope_ms(shared("voice.wav")), sound.envelope_ms(delayed))
        self.assertAlmostEqual(lag, 0.25, delta=0.5)
        ff("-i", shared("voice.wav"), "-af", "adelay=delays=480S:all=1,atrim=end_sample=576000", delayed)
        lag, _ = sound.xcorr_offset_ms(sound.envelope_ms(shared("voice.wav")), sound.envelope_ms(delayed))
        self.assertAlmostEqual(lag, 10.0, delta=0.5)


@NEED_FF
class G_DuckMixTests(unittest.TestCase):
    def gain_db(self, a, b, t0, t1, ch):
        i0, i1 = int(t0 * 48000), int(t1 * 48000)
        ea = sum(v * v for v in a[2 * i0 + ch:2 * i1:2])
        eb = sum(v * v for v in b[2 * i0 + ch:2 * i1:2])
        return 10 * math.log10(eb / ea)

    def test_mix_follows_the_speech_length(self):
        voice = tmp("mixlen", "voice.wav")
        music = tmp("mixlen", "music.wav")
        # speech-like: a tone that talks in 0.25 s bursts; the bed is pink noise (a pure steady sine is no mix)
        ff("-f", "lavfi", "-i", "aevalsrc='0.3*sin(2*PI*220*t)*gt(sin(2*PI*2*t),0)':s=48000:d=10", voice)
        ff("-f", "lavfi", "-i", "anoisesrc=d=40:c=pink:a=0.05:r=48000", music)
        out = tmp("mixlen", "mix.wav")
        r = cli_json("mix", "--dialogue", voice, "--music", music, "--platform", "youtube", "--out", out)
        got = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                    out], capture_output=True, text=True).stdout.strip())
        self.assertAlmostEqual(got, 10.0, delta=0.02)
        self.assertTrue(any("music is 40.000 s" in w for w in r["warnings"]), r["warnings"])

    def test_master_bus_never_writes_a_dynamic_result(self):
        import unittest.mock
        src = tmp("dyn", "src.wav")
        ff("-f", "lavfi", "-i", "sine=f=440:d=3", "-ar", 48000, src)
        out = tmp("dyn", "never.wav")
        fake = {"input_i": "-20.0", "input_tp": "-6.0", "input_lra": "1.0", "input_thresh": "-30.0",
                "target_offset": "0.0", "normalization_type": "dynamic"}
        with unittest.mock.patch.object(sound, "parse_loudnorm", return_value=fake):
            with sound.Work() as work:
                with self.assertRaises(SystemExit):
                    sound.master_bus(src, out, -14.0, -1.0, work)
        self.assertFalse(os.path.exists(out))

    def test_duck_depth_gaps_and_no_pan_law(self):
        spans = tmp("duck", "spans.json")
        with open(spans, "w") as fh:
            json.dump([[1.0, 3.0], [3.5, 5.0], [9.0, 11.0]], fh)
        out = tmp("duck", "ducked.wav")
        r = cli_json("duck", "--music", shared("bed.wav"), "--speech", spans, "--out", out)
        a, b = decode(shared("bed.wav")), decode(out)
        for ch in (0, 1):
            self.assertAlmostEqual(self.gain_db(a, b, 1.2, 2.8, ch), -14.0, delta=0.5)    # under speech
            self.assertAlmostEqual(self.gain_db(a, b, 3.05, 3.45, ch), -14.0, delta=0.5)  # a bridged pause
            self.assertAlmostEqual(self.gain_db(a, b, 6.5, 8.3, ch), 0.0, delta=0.5)      # a long gap
            self.assertAlmostEqual(self.gain_db(a, b, 12.5, 15.5, ch), 0.0, delta=0.5)
        kf = load_json(r["keyframes_file"])
        times = [t for t, _ in kf]
        self.assertEqual(times, sorted(set(times)))                       # strictly increasing, for Remotion

    def test_spans_from_a_voice_stem(self):
        r = cli_json("duck", "--music", shared("bed.wav"), "--voice", shared("voice.wav"), "--out",
                     tmp("duck", "v.wav"))
        self.assertIn("silencedetect", r["spans_source"])
        for a, b in SENTENCES:                  # every sentence sits inside a span (-35 dB, 0.35 s)
            self.assertTrue(any(s - 0.05 <= a and b <= e + 0.05 for s, e in r["spans"]), (a, b, r["spans"]))

    def test_section_warnings(self):
        self.assertEqual(sound.section_warnings({"dialogue_lufs": -20.0, "music_only_lufs": -18.0,
                                                 "end_card_lufs": -30.0}), [])
        w = sound.section_warnings({"dialogue_lufs": -20.0, "music_only_lufs": -16.5, "end_card_lufs": -36.0})
        self.assertEqual(len(w), 2)
        sec = sound.sections_report([(t / 10.0, -20.0 if t <= 50 else -15.0) for t in range(4, 121)], [[0.0, 5.0]],
                                    lambda t: True, 12.0)
        self.assertAlmostEqual(sec["dialogue_lufs"], -20.0, delta=0.01)
        self.assertAlmostEqual(sec["music_only_lufs"], -15.0, delta=0.01)
        self.assertIn("louder than the dialogue", sound.section_warnings(sec)[0])

    def test_keyframes_never_jump(self):
        for gap in (0.81, 0.9, 1.0, 1.1, 1.19, 1.2, 1.21, 2.0):
            kf = sound.duck_keyframes([[1.0, 3.0], [3.0 + gap, 5.0 + gap]])
            for (t0, g0), (t1, g1) in zip(kf, kf[1:]):
                self.assertGreater(t1, t0)
                self.assertLessEqual(abs(g1 - g0) / (t1 - t0), 70.5, (gap, kf))

    def test_mix_hits_the_platform_target_linearly(self):
        music = tmp("mix", "music.wav")
        cli("fit", shared("groove.wav"), "--target", 12.0, "--bpm", 104, "--out", music)
        cues = tmp("mix", "cues.json")
        with open(cues, "w") as fh:
            json.dump([{"t": 2.0, "name": "whoosh"}, {"t": 5.0, "name": "impact"}], fh)
        sfx = tmp("mix", "sfx.wav")
        cli("sfx", "place", cues, "--duration", 12, "--out", sfx, "--offline")
        out = tmp("mix", "mix.wav")
        r = cli_json("mix", "--voice", shared("voice.wav"), "--music", music, "--sfx", sfx, "--platform", "youtube",
                     "--out", out)
        self.assertEqual(r["normalization"], "linear")
        self.assertAlmostEqual(r["measured"]["I"], -14.0, delta=0.5)
        self.assertLessEqual(r["measured"]["TP"], -1.0)
        lo = sound.loudness(out)
        self.assertAlmostEqual(lo["I"], -14.0, delta=0.5)
        self.assertLessEqual(lo["TP"], -1.0)
        pr = sound.probe(out)
        self.assertEqual((pr["sample_rate"], pr["bits"], pr["channels"]), (48000, 24, 2))
        for k in ("voice", "music", "sfx"):
            self.assertTrue(os.path.exists(r["stems"][k]["file"]))
        spans = r["speech"]["spans"]
        m = lambda p: sound.power_mean([v for t, v in sound.momentary(p)  # noqa: E731
                                        if any(s <= t - 0.4 and t <= e for s, e in spans)])
        under = m(r["stems"]["voice"]["file"]) - m(r["stems"]["music"]["file"])
        self.assertAlmostEqual(under, 20.0, delta=2.0)                    # music 18 to 25 dB under speech
        r2 = cli_json("mix", "--voice", shared("voice.wav"), "--music", music, "--platform", "broadcast", "--out",
                      tmp("mix", "bc.wav"))
        self.assertAlmostEqual(r2["measured"]["I"], -23.0, delta=0.5)


@NEED_FF
class H_GenerateTests(unittest.TestCase):
    def interactions_since(self, before):
        return [x for x in Fake.log[before:] if x["path"] == "/v1beta/interactions"]

    def test_a_track_blocked_after_generation_is_made_once_more(self):
        brief = make_brief("outblock1", 12.0, notes="fake:outblock1")
        out = tmp("gen", "outblock1")
        before = len(Fake.log)
        r = cli_json("generate", brief, "--out", out, "--final", env={"NEXA_SOUND_OUTPUT_BLOCK_S": "0.05"})
        take = r["takes"][0]
        self.assertTrue(take["ok"], take)
        self.assertEqual(len(self.interactions_since(before)), 2)
        led = [(x["status"], x["est_usd"]) for x in load_jsonl(os.path.join(out, "ledger.jsonl"))]
        self.assertEqual(led, [("blocked", 0.0), ("ok", 0.08)])
        self.assertEqual(load_json(take["sidecar"])["response"]["blocked_before"], 1)

    def test_a_track_blocked_twice_stops_with_the_reason(self):
        brief = make_brief("outblock2", 12.0, notes="fake:outblock2")
        before = len(Fake.log)
        r = cli("generate", brief, "--out", tmp("gen", "outblock2"), "--final", expect=1,
                env={"NEXA_SOUND_OUTPUT_BLOCK_S": "0.05"})
        self.assertIn("blocked the finished track 2 time(s)", r.stdout + r.stderr)
        self.assertEqual(len(self.interactions_since(before)), 2)

    def test_two_runs_in_the_same_minute_never_share_a_name(self):
        # a draft and a final run side by side once got the same id; the second paid take could not be saved
        brief = make_brief("race", 12.0, notes="fake:slow")
        out = os.path.dirname(tmp("gen", "race", "x"))
        procs = [subprocess.Popen([sys.executable, str(SCRIPTS / "sound.py"), "generate", brief, "--out", out,
                                   "--draft", "1", "--json"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  text=True) for _ in range(2)]
        ids = []
        for p, (so, se) in [(p, p.communicate(timeout=300)) for p in procs]:
            OUTPUTS.append(so + se)
            self.assertEqual(p.returncode, 0, se[-800:])
            take = json.loads(so)["takes"][0]
            self.assertTrue(take["ok"], take)
            self.assertTrue(os.path.exists(take["file"]))
            ids.append(take["id"])
        self.assertEqual(len(set(ids)), 2, ids)
        self.assertEqual([f for f in os.listdir(out) if f.endswith(".lock")], [])

    def test_dc_on_an_original_is_a_warning_and_fit_takes_it_out(self):
        brief = make_brief("dc", 16.0, notes="fake:dc")
        out = tmp("gen", "dc")
        take = cli_json("generate", brief, "--out", out, "--final")["takes"][0]
        self.assertTrue(take["ok"], take)
        qc = load_json(take["sidecar"])["qc"]
        self.assertNotIn("dc_offset", qc["failed"])
        self.assertIn("dc_offset", qc["warnings"])
        fitted = os.path.join(out, "fit12.wav")
        f = cli_json("fit", take["file"], "--target", 12.0, "--out", fitted)
        self.assertIn("dc_block", [op["op"] for op in f["ops"]])
        self.assertLess(abs(sound.astats(fitted)["dc_offset"]), 0.0005)

    def test_final_sidecar_ledger_library_and_untouched_original(self):
        brief = make_brief("final", 12.0)
        out = tmp("gen", "final")
        still = tmp("gen", "still.png")
        ff("-f", "lavfi", "-i", "color=c=orange:s=64x36", "-frames:v", 1, still)
        before = len(Fake.log)
        r = cli_json("generate", brief, "--out", out, "--final", "--images", still)
        take = r["takes"][0]
        self.assertTrue(take["ok"], take)
        self.assertEqual(take["format"], "mp3" if HAVE_MP3 else "wav")
        req = [x for x in Fake.log[before:] if x["path"] == "/v1beta/interactions"][0]
        self.assertEqual(req["body"]["model"], "lyria-3.5")
        self.assertNotIn("response_format", req["body"])       # the live API refuses WAV and L16 for lyria-3.5
        self.assertIs(req["body"]["store"], False)
        self.assertEqual(req["body"]["images"], ["image/png"])
        data = read_bytes(take["file"])
        self.assertEqual(data[:3] if HAVE_MP3 else data[:4], b"ID3" if HAVE_MP3 else b"RIFF")
        self.assertFalse(os.access(take["file"], os.W_OK))                 # the original is read-only
        side = load_json(take["sidecar"])
        for k in ("id", "created_at", "tool", "provider", "request", "response", "original", "analysis", "qc",
                  "licence", "usage"):
            self.assertIn(k, side)
        self.assertEqual(side["provider"]["key_var_used"], "GEMINI_API_KEY")
        self.assertEqual(side["original"]["sha256"], hashlib.sha256(data).hexdigest())
        self.assertEqual(side["original"]["c2pa_manifest_present"], HAVE_MP3)
        self.assertEqual(side["response"]["section_labels"], ["A0", "B1", "C2"])
        self.assertAlmostEqual(side["analysis"]["bpm"], 104.0, delta=1.0)
        self.assertEqual(side["licence"]["content_id"], "Do not register.")
        self.assertIn("SynthID", side["original"]["synthid"])
        led = load_jsonl(os.path.join(out, "ledger.jsonl"))
        self.assertEqual((led[-1]["model"], led[-1]["est_usd"], led[-1]["status"]), ("lyria-3.5", 0.08, "ok"))
        lib = load_jsonl(os.path.join(os.environ["NEXA_SOUND_HOME"], "library.jsonl"))
        self.assertIn(take["id"], [x["id"] for x in lib])
        # fit and qc never touch the original
        cli("fit", take["file"], "--target", 10.0, "--out", os.path.join(out, "fit10.wav"))
        cli("qc", take["file"], expect=None)
        self.assertEqual(hashlib.sha256(read_bytes(take["file"])).hexdigest(), side["original"]["sha256"])
        side = load_json(take["sidecar"])
        self.assertEqual(side["fit"]["target_s"], 10.0)
        self.assertIn("start_offset_s", side["fit"])
        self.assertTrue(side["analysis"]["downbeats_file"].endswith(".beats.json"))
        self.assertEqual(side["request"]["images"][0]["mime_type"], "image/png")
        found = cli_json("library", "--mood", "corporate", "--bpm", "100-110")
        self.assertIn(take["id"], [t["id"] for t in found["tracks"]])

    def test_drafts_are_clip_mp3_in_parallel_at_most_three(self):
        brief = make_brief("drafts", 12.0, mood="ad")
        Fake.max_active = 0
        before = len(Fake.log)
        r = cli_json("generate", brief, "--out", tmp("gen", "drafts"), "--draft", 4)
        self.assertEqual(len([t for t in r["takes"] if t["ok"]]), 4)
        for t in r["takes"]:
            self.assertEqual(t["format"], "mp3" if HAVE_MP3 else "wav")
            self.assertAlmostEqual(t["duration_s"], 30.0, delta=0.2)
            side = load_json(t["sidecar"])
            self.assertEqual(side["original"]["c2pa_manifest_present"], HAVE_MP3)
            self.assertIsNone(side["request"]["response_format"])
        reqs = [x for x in Fake.log[before:] if x["path"] == "/v1beta/interactions"]
        self.assertTrue(all(x["body"]["model"] == "lyria-3-clip-preview" for x in reqs))
        self.assertTrue(all("response_format" not in x["body"] for x in reqs))
        self.assertLessEqual(Fake.max_active, 3)
        self.assertGreaterEqual(Fake.max_active, 2)
        self.assertAlmostEqual(r["est_usd"], 0.16, delta=0.001)

    def test_budget_guard_refuses_before_any_call(self):
        brief = make_brief("budget", 12.0)
        before = len(Fake.log)
        r = cli("generate", brief, "--out", tmp("gen", "budget"), "--draft", 10, "--budget", 0.2, expect=1)
        self.assertIn("over the budget", r.stderr)
        self.assertEqual(len(Fake.log), before)

    def test_a_safety_block_is_explained_and_never_retried(self):
        brief = make_brief("blocked", 12.0, notes="fake:blocked")
        before = len(Fake.log)
        r = cli("generate", brief, "--out", tmp("gen", "blocked"), "--final", expect=1)
        self.assertIn("safety filter", r.stdout + r.stderr)
        self.assertEqual(len([x for x in Fake.log[before:] if x["path"] == "/v1beta/interactions"]), 1)

    def test_timed_lyrics_in_an_instrumental_fail_qc(self):
        brief = make_brief("vocals", 12.0, notes="fake:timed-lyrics")
        r = cli_json("generate", brief, "--out", tmp("gen", "vocals"), "--final")
        take = r["takes"][0]
        self.assertTrue(take["vocals_suspected"])
        self.assertIn("vocals", take["qc_failed"])
        q = cli_json("qc", take["file"], expect=2)
        self.assertFalse(q["passed"])

    def test_listening_judge(self):
        brief = make_brief("listen", 12.0)
        take = cli_json("generate", brief, "--out", tmp("gen", "listen"), "--final")["takes"][0]
        fitted = tmp("gen", "listen", "fit.wav")
        cli("fit", take["file"], "--target", 11.0, "--out", fitted)
        before = len(Fake.log)
        q = cli_json("qc", fitted, "--listen")
        self.assertTrue(q["summary"]["listened"])
        self.assertIs(q["judge"]["vocals_present"], False)
        self.assertTrue(q["passed"], q["checks"])
        req = [x for x in Fake.log[before:] if x["path"] == "/v1beta/interactions"][0]
        self.assertEqual(req["body"]["model"], "gemini-3.8-flash")
        self.assertIn("instrumental", req["body"]["input"])
        led = load_jsonl(tmp("gen", "listen", "ledger.jsonl"))
        self.assertEqual(led[-1]["model"], "gemini-3.8-flash")
        other = make_brief("listen2", 12.0, mood="suspense")      # the fake judge hears vocals for this brief
        q = cli_json("qc", fitted, "--listen", "--brief", other, expect=2)
        self.assertIn("judge_vocals", q["summary"]["failed"])

    def test_realtime_bed_through_the_recorder(self):
        cuts = tmp("gen", "rt_cuts.json")
        with open(cuts, "w") as fh:
            json.dump([{"t": 3.0, "weight": 2.0, "label": "reveal"}], fh)
        brief = make_brief("rt", 6.0, mood="lofi", extra=["--cuts", cuts])
        log = tmp("gen", "rt", "calls.json")
        env = {"NEXA_SOUND_VENV_PYTHON": sys.executable, "NEXA_REALTIME_FAKE": "1", "NEXA_REALTIME_FAKE_LOG": log}
        r = cli_json("generate", brief, "--out", tmp("gen", "rt"), "--realtime", env=env)
        take = r["takes"][0]
        self.assertAlmostEqual(take["duration_s"], 9.0, delta=0.01)       # 6 s + 3 s, the preroll dropped
        self.assertEqual([f for f in os.listdir(tmp("gen", "rt")) if f.endswith(".lock")], [])
        side = load_json(take["sidecar"])
        rt = side["request"]["realtime"]
        self.assertEqual(rt["preroll_s"], 8.0)
        self.assertEqual(rt["config"]["scale"], "F_MAJOR_D_MINOR")
        calls = load_json(log)
        configs = [c["config"] for c in calls if c["call"] == "set_music_generation_config"]
        self.assertEqual(len(configs), 2)                                 # the start, then the cut at 3 s
        for c in configs:                                                 # the whole config every time
            self.assertEqual(set(("bpm", "scale", "density", "brightness", "guidance")) - set(c), set())
        bad = tmp("gen", "rt", "bad.json")
        with open(bad, "w") as fh:
            json.dump({"weighted_prompts": [["Lo-Fi", 1.0]], "config": {"bpm": 82, "scale": "MAJOR"}, "seconds": 5}, fh)
        p = subprocess.run([sys.executable, str(SCRIPTS / "realtime.py"), "--config", bad, "--out",
                            tmp("gen", "x.wav")],
                           capture_output=True, text=True, env=dict(os.environ, NEXA_REALTIME_FAKE="1"))
        OUTPUTS.append(p.stdout + p.stderr)
        self.assertEqual(p.returncode, 2)
        self.assertIn("not a Lyria RealTime scale", p.stderr)


@NEED_FF
class I_QcCreditsCostTests(unittest.TestCase):
    def test_qc_catches_clipping_and_an_abrupt_ending(self):
        clipped = tmp("qc", "clipped.wav")
        ff("-f", "lavfi", "-i", "aevalsrc='clip(1.5*sin(2*PI*220*t)*(1-exp(-t*20))*exp(-max(t-5,0)*5),-1,1)':"
               "s=48000:d=6", "-af", "pan=stereo|c0=c0|c1=c0", "-c:a", "pcm_s24le", clipped)
        q = cli_json("qc", clipped, "--kind", "music", expect=2)
        self.assertIn("clipping", q["summary"]["failed"])
        lowered = tmp("qc", "clipped_down.wav")
        ff("-i", clipped, "-af", "volume=-6dB", "-c:a", "pcm_s24le", lowered)
        q = cli_json("qc", lowered, "--kind", "music", expect=2)
        self.assertIn("clipping", q["summary"]["failed"])
        abrupt = tmp("qc", "abrupt.wav")
        ff("-f", "lavfi", "-i", "aevalsrc='0.5*sin(2*PI*220*t)*(1-exp(-t*20))':s=48000:d=6", "-af",
           "pan=stereo|c0=c0|c1=c0", "-c:a", "pcm_s24le", abrupt)
        q = cli_json("qc", abrupt, expect=2)
        self.assertIn("ending", q["summary"]["failed"])
        good = tmp("qc", "good.wav")
        cli("fit", shared("groove.wav"), "--target", 20.0, "--bpm", 104, "--out", good)
        q = cli_json("qc", good)
        self.assertTrue(q["passed"], q["checks"])

    def test_credits_and_cost(self):
        brief = make_brief("credits", 12.0)
        proj = tmp("proj")
        take = cli_json("generate", brief, "--out", os.path.join(proj, "music"), "--final")["takes"][0]
        cli("fit", take["file"], "--target", 10.0, "--out", os.path.join(proj, "music", "fit10.wav"))
        cues = os.path.join(proj, "cues.json")
        with open(cues, "w") as fh:
            json.dump([{"t": 1.0, "name": "whoosh"}, {"t": 2.0, "name": "whoosh"}, {"t": 3.0, "name": "click"}], fh)
        cli("sfx", "place", cues, "--duration", 5, "--out", os.path.join(proj, "sfx", "sfx.wav"), "--offline")
        out = os.path.join(proj, "CREDITS.txt")
        r = cli_json("credits", proj, "--out", out)
        self.assertEqual(r["tracks"], 1)
        text = read_text(out)
        for needle in ("lyria-3.5", "SynthID", "Content ID", "indemnity", "not exclusive", take["id"],
                       "Edited to 10.00 s", "nexa-sound's own synthesiser", "whoosh (x2)"):
            self.assertIn(needle, text)
        self.assertNotIn("\u2014", text)
        c = cli_json("cost", os.path.join(proj, "music"))
        self.assertAlmostEqual(c["ledger"]["spent_usd"], 0.08, delta=0.001)
        c = cli_json("cost", "--draft", 3, "--final", 2)
        self.assertAlmostEqual(c["estimate"]["total_usd"], 0.28, delta=0.001)

    def test_doctor(self):
        r = cli_json("doctor")
        self.assertTrue(r["ready"])
        self.assertEqual(r["key_sources"], ["GEMINI_API_KEY"])
        r = cli_json("doctor", "--live")
        self.assertEqual(r["live"], {"lyria-3.5": True, "lyria-3-clip-preview": True, "lyria-realtime-exp": True,
                                     "gemini-3.8-flash": True})


class Z_NoKeyLeaks(unittest.TestCase):
    """Runs last (classes run in name order): the fake keys appear in no file the tools wrote and in no output."""

    def test_keys_appear_nowhere(self):
        if ROOT is None:
            self.skipTest("nothing ran")
        keys = [k.encode("utf-8") for k in (FAKE_KEY, FS_KEY, EL_KEY)]
        for text in OUTPUTS:
            for k in keys:
                self.assertNotIn(k.decode("utf-8"), text)
        checked = 0
        for d, _, files in os.walk(ROOT):
            for f in files:
                with open(os.path.join(d, f), "rb") as fh:
                    data = fh.read()
                checked += 1
                for k in keys:
                    self.assertNotIn(k, data, os.path.join(d, f))
        self.assertGreater(checked, 0)


if __name__ == "__main__":
    unittest.main()
