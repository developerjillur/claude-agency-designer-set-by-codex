"""Offline tests for nexa-speech: no network and no key. A fake Gemini server in a thread answers like the real API
(speech whose length follows the words, voices, models, transcripts with word timings), and scripted failures
check what the tool does when the service says no. ffmpeg is needed for everything that touches audio; those tests
skip cleanly without it.

Run: python3 -m unittest discover -s ~/.claude/skills/nexa-speech/tests
"""
import base64
import hashlib
import http.server
import io
import json
import math
import os
import random
import re
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading
import unicodedata
import unittest
import urllib.parse
import wave
from array import array
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SCRIPT = SKILL / "scripts" / "speech.py"
sys.path.insert(0, str(SKILL / "scripts"))
import speech as S  # noqa: E402

FAKE_KEY = "test-key-0000"
EL_FAKE_KEY = "el-test-key-0000"
HAVE_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
RATE = 24000
WORD_S, SENT_PAUSE_S, LEAD_S, TAIL_S = 0.38, 0.45, 0.10, 0.20
ENV_KEYS = ("NEXA_GEMINI_BASE_URL", "NEXA_GEMINI_SLEEP_SCALE", "NEXA_NO_KEYCHAIN", "GEMINI_API_KEY",
            "NEXA_SPEECH_HOME", "NEXA_ELEVENLABS_BASE_URL", "ELEVENLABS_API_KEY")


def nfc(s):
    return unicodedata.normalize("NFC", s)


# --------------------------------------------------------------------------------------------- fake speech

_WORDS = {}


def word_pcm(f0, gain=1.0):
    """One fake word: two syllable bursts of 0.16 s (a carrier with two harmonics under a sin^2 envelope), each
    followed by a 30 ms dip: 0.38 s, about 5 bursts a second."""
    key = (round(f0, 1), round(gain, 3))
    if key not in _WORDS:
        out = array("h")
        n = int(0.16 * RATE)
        for _ in range(2):
            for i in range(n):
                env = math.sin(math.pi * i / n) ** 2
                t = i / RATE
                v = (math.sin(2 * math.pi * f0 * t) + 0.5 * math.sin(4 * math.pi * f0 * t)
                     + 0.25 * math.sin(6 * math.pi * f0 * t)) / 1.75
                out.append(int(max(-32767, min(32767, 0.3 * gain * env * v * 32767))))
            out.extend([0] * int(0.03 * RATE))
        if sys.byteorder == "big":
            out.byteswap()
        _WORDS[key] = out.tobytes()
    return _WORDS[key]


def silence(sec):
    return b"\x00\x00" * int(round(sec * RATE))


def noise(sec, rms_dbfs=-40.0, seed=1):
    rnd = random.Random(seed)
    sd = 32767 * 10 ** (rms_dbfs / 20)
    a = array("h", [int(max(-32767, min(32767, rnd.gauss(0, sd)))) for _ in range(int(sec * RATE))])
    if sys.byteorder == "big":
        a.byteswap()
    return a.tobytes()


def fake_speech(text, voice, mode=None):
    """(PCM, [(word, start, end)]) for the words of `text`: 0.38 s a word, 450 ms between sentences, 100 ms before
    and 200 ms after. Modes: truncated (half the words), loud (+10 dB), noise_tail (0.5 s of hiss at the end)."""
    clean = re.sub(r"<[^>]*>|\[[^\]]*\]", " ", text)
    sentences = [s for s in re.split(r"(?<=[.!?\u0964])\s+", clean.strip()) if s.strip()]
    groups = [[w for w in s.split() if re.search(r"\w", w)] for s in sentences]
    if mode == "truncated":
        keep = max(1, sum(len(g) for g in groups) // 2)
        cut = []
        for g in groups:
            take = g[:max(0, keep)]
            keep -= len(take)
            if take:
                cut.append(take)
        groups = cut
    f0 = 150 + int(hashlib.sha256(voice.encode()).hexdigest(), 16) % 80
    gain = 3.16 if mode == "loud" else 1.0
    pcm = bytearray(silence(LEAD_S))
    t, words = LEAD_S, []
    for gi, g in enumerate(groups):
        if gi:
            pcm += silence(SENT_PAUSE_S)
            t += SENT_PAUSE_S
        for w in g:
            # the pitch moves a little with the word, so different texts never give the same audio
            pcm += word_pcm(f0 + int(hashlib.sha256(w.encode()).hexdigest(), 16) % 7, gain)
            words.append((w, round(t, 3), round(t + WORD_S - 0.03, 3)))
            t += WORD_S
    pcm += silence(TAIL_S)
    if mode == "noise_tail":
        pcm += noise(0.5)
    # a signature of the text in the first four samples (below -54 dBFS, gone once the lead-in is trimmed), so two
    # texts never give byte-identical audio and the fake recogniser finds each take's words by its hash
    sig = hashlib.sha256((text + "|" + voice).encode()).digest()
    for k in range(4):
        pcm[2 * k:2 * k + 2] = int(1 + sig[k] % 63).to_bytes(2, "little", signed=True)
    return bytes(pcm), words


def wav_bytes(pcm, rate=RATE):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)
    return buf.getvalue()


# --------------------------------------------------------------------------------------------- fake server

class QuickServer(http.server.ThreadingHTTPServer):
    """HTTPServer.server_bind asks for the host's full name (a reverse DNS lookup that took 35 s on one machine);
    a local test server does not need it."""
    daemon_threads = True

    def server_bind(self):
        socketserver.TCPServer.server_bind(self)
        self.server_name, self.server_port = "127.0.0.1", self.server_address[1]


class FakeGemini:
    """The parts of the Gemini API that nexa-speech uses, on 127.0.0.1. `rules` scripts failures: each is
    {"match": text or None, "mode": ..., "count": n} and fires on requests whose text contains `match`."""

    def __init__(self):
        self.lock = threading.Lock()
        self.log = []
        self.rules = []
        self.by_hash = {}
        self.last_words = []
        self.transcript_override = None
        self.fa_timeless = None             # the index of a forced-alignment word that comes back without times
        self.voice_n = 0
        self.httpd = QuickServer(("127.0.0.1", 0), self._handler())
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def start(self):
        self.thread.start()
        return self

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()

    TTS_MODES = {"quota_day", "safety", "server_once", "truncated", "loud", "noise_tail", "blocked_200", "two_parts"}
    ASR_MODES = {"asr_drop_last"}

    def rule(self, text, modes):
        """The first scripted failure for this kind of request whose text matches; it is used up once."""
        with self.lock:
            for r in self.rules:
                if r["count"] > 0 and r["mode"] in modes and (r["match"] is None or r["match"] in text):
                    r["count"] -= 1
                    return r["mode"]
        return None

    def tts(self):
        with self.lock:
            return [e for e in self.log if e["kind"] == "tts"]

    def kinds(self, kind):
        with self.lock:
            return [e for e in self.log if e["kind"] == kind]

    def _handler(fake):
        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def send(self, code, obj):
                data = json.dumps(obj).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def authorised(self):
                if self.headers.get("x-goog-api-key") != FAKE_KEY:
                    self.send(401, {"error": {"code": 401, "message": "API key not valid.",
                                              "status": "UNAUTHENTICATED"}})
                    return False
                return True

            def do_GET(self):
                if not self.authorised():
                    return
                path, _, query = self.path.partition("?")
                q = dict(urllib.parse.parse_qsl(query))
                with fake.lock:
                    fake.log.append({"kind": "get", "path": path, "query": q})
                if path == "/v1beta/models":
                    names = ["gemini-3.8-flash-tts", "gemini-3.8-flash-lite-tts", "gemini-3.5-transcribe",
                             "gemini-3.8-flash"]
                    return self.send(200, {"models": [{"name": "models/" + n} for n in names]})
                if path == "/v1beta/voices":
                    lib = [{"id": "voice_lib_bn_01", "display_name": "Rupa", "language_code": "bn-BD",
                            "gender": "female", "accent": "Dhaka", "pitch": "medium", "description": "warm"},
                           {"id": "voice_lib_bn_02", "display_name": "Tanvir", "language_code": "bn-BD",
                            "gender": "male", "accent": "Dhaka", "pitch": "low", "description": "calm"},
                           {"id": "voice_lib_en_01", "display_name": "Ada", "language_code": "en-GB",
                            "gender": "female", "accent": "London", "pitch": "medium", "description": "clear"}]
                    if q.get("language_code"):
                        lib = [v for v in lib if v["language_code"] == q["language_code"]]
                    if q.get("gender"):
                        lib = [v for v in lib if v["gender"] == q["gender"]]
                    return self.send(200, {"voices": lib})
                self.send(404, {"error": {"code": 404, "message": "not found"}})

            def do_POST(self):
                if self.path.startswith("/v1/forced-alignment"):
                    return self.forced_alignment()
                if not self.authorised():
                    return
                n = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(n) or b"{}")
                if self.path == "/v1beta/voices":
                    return self.design(body)
                if self.path != "/v1beta/interactions":
                    return self.send(404, {"error": {"code": 404, "message": "not found"}})
                if "transcription_config" in (body.get("generation_config") or {}):
                    return self.transcribe(body)
                return self.speak(body)

            def forced_alignment(self):
                """ElevenLabs: multipart file + text; each word gets an even share of the audio."""
                raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
                if self.headers.get("xi-api-key") != EL_FAKE_KEY:
                    return self.send(401, {"detail": {"status": "invalid_api_key", "message": "Invalid API key"}})
                m = re.search(rb'name="text"\r\n\r\n(.*?)\r\n--', raw, re.S)
                text = m.group(1).decode("utf-8") if m else ""
                w = re.search(rb"RIFF.{4}WAVE", raw, re.S)
                n_audio = len(raw) - (w.start() if w else 0) - 44 - 200
                dur = max(1.0, n_audio / 32000.0)
                words = text.split()
                step = dur / max(1, len(words))
                with fake.lock:
                    fake.log.append({"kind": "fa", "text": text})
                out = [{"text": t, "start": round(i * step, 3), "end": round((i + 0.9) * step, 3),
                        "loss": 0.9 if t == "ferry" else 0.05} for i, t in enumerate(words)]
                if fake.fa_timeless is not None and fake.fa_timeless < len(out):
                    out[fake.fa_timeless] = {"text": out[fake.fa_timeless]["text"], "loss": 0.05}
                return self.send(200, {"characters": [], "loss": 0.07, "words": out})

            def speak(self, body):
                inp = body.get("input")
                if isinstance(inp, str):
                    text = inp.split("#### TRANSCRIPT", 1)[1].strip() if "#### TRANSCRIPT" in inp else inp
                else:
                    text = inp[0].get("text", "")
                voice = body["generation_config"]["speech_config"][0]["voice"]
                with fake.lock:
                    fake.log.append({"kind": "tts", "body": body, "text": text, "voice": voice})
                mode = fake.rule(text, fake.TTS_MODES)
                if mode == "quota_day":
                    return self.send(429, {"error": {"code": 429, "status": "RESOURCE_EXHAUSTED", "message": (
                        "Quota exceeded for metric: generativelanguage.googleapis.com/generate_requests_per_model_per"
                        "_day, limit: 100, quota id GenerateRequestsPerDayPerProjectPerModel")}})
                if mode == "safety":
                    return self.send(400, {"error": {"code": 400, "status": "INVALID_ARGUMENT",
                                                     "message": "The request was blocked for safety reasons."}})
                if mode == "server_once":
                    return self.send(500, {"error": {"code": 500, "status": "INTERNAL", "message": "internal"}})
                if mode == "blocked_200":
                    return self.send(200, {"status": "completed", "steps": [
                        {"type": "model_output", "finish_reason": "SAFETY", "content": []}], "usage": {}})
                pcm, words = fake_speech(text, voice, mode)
                with fake.lock:
                    fake.by_hash[hashlib.sha256(pcm).hexdigest()] = words
                    fake.last_words = words
                rf = body.get("response_format") or {}
                pieces = [pcm]
                if mode == "two_parts":
                    half = len(pcm) // 4 * 2
                    pieces = [pcm[:half], pcm[half:]]
                content = []
                for piece in pieces:
                    if rf.get("mime_type") == "audio/l16":
                        data, mime = piece, "audio/l16; rate=24000; channels=1"
                    else:
                        data, mime = wav_bytes(piece), "audio/wav"
                    content.append({"type": "audio", "data": base64.b64encode(data).decode(), "mime_type": mime,
                                    "sample_rate": RATE, "channels": 1})
                secs = len(pcm) / 2 / RATE
                step = {"type": "model_output", "content": content}     # the live API sends no finish_reason
                if mode == "truncated":
                    step["finish_reason"] = "OTHER"
                self.send(200, {"status": "completed", "steps": [step],
                                "usage": {"total_input_tokens": len(text) // 3,
                                          "total_output_tokens": int(secs * 32)}})   # 32 a second, as measured

            def transcribe(self, body):
                block = body["input"][0]
                raw = base64.b64decode(block["data"])
                frames = raw
                if raw[:4] == b"RIFF":
                    with wave.open(io.BytesIO(raw), "rb") as w:
                        frames = w.readframes(w.getnframes())
                with fake.lock:
                    words = fake.by_hash.get(hashlib.sha256(frames).hexdigest())
                    if words is None:
                        words = fake.transcript_override if fake.transcript_override is not None else fake.last_words
                    fake.log.append({"kind": "asr", "body": {k: v for k, v in body.items() if k != "input"}})
                mode = fake.rule(" ".join(w for w, _, _ in words), fake.ASR_MODES)
                if mode == "asr_drop_last":
                    words = words[:-1]
                notes = [{"type": "word_info", "text": w, "start_offset": "%.3fs" % a, "end_offset": "%.3fs" % b}
                         for w, a, b in words]
                self.send(200, {"status": "completed", "steps": [{"type": "model_output", "content": [
                    {"type": "text", "text": " ".join(w for w, _, _ in words), "annotations": notes}]}],
                    "usage": {"total_input_tokens": int(len(frames) / 2 / 16000 * 25) + 1,   # audio in, as live
                              "total_output_tokens": 0}})

            def design(self, body):
                with fake.lock:
                    fake.voice_n += 1
                    vid = "voice_fake%02d" % fake.voice_n
                    fake.log.append({"kind": "design", "body": body})
                pcm, _ = fake_speech("This is how I sound.", vid)
                self.send(200, {"id": vid, "display_name": body["voice"].get("display_name"),
                                "expire_time": "2027-09-25T00:00:00Z",
                                "sample_audio": {"data": base64.b64encode(wav_bytes(pcm)).decode(),
                                                 "mime_type": "audio/wav"}})
        return Handler


# --------------------------------------------------------------------------------------------- helpers

def measure(path):
    """ebur128 integrated loudness and true peak, the silences (-40 dB, 100 ms), and the first sample above -40 dBFS
    (the lead-in is too short for silencedetect) of an audio file."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-v", "info", "-i", str(path), "-af",
                        "ebur128=peak=true:framelog=quiet,silencedetect=noise=-40dB:d=0.1", "-f", "null", "-"],
                       capture_output=True, text=True)
    err = r.stderr
    summ = err[err.rfind("Summary:"):]
    i = float(re.search(r"I:\s*(-?[0-9.]+) LUFS", summ).group(1))
    tp = float(re.search(r"Peak:\s*(-?[0-9.]+) dBFS", summ).group(1))
    starts = [float(x) for x in re.findall(r"silence_start: (-?[0-9.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", err)]
    raw = subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-i", str(path), "-t", "2", "-ac", "1", "-ar",
                          "48000", "-f", "s16le", "-"], capture_output=True).stdout
    a = array("h")
    a.frombytes(raw[: len(raw) // 2 * 2])
    if sys.byteorder == "big":
        a.byteswap()
    lim = 32768 * 10 ** (-40 / 20)
    first = next((k / 48000.0 for k, x in enumerate(a) if abs(x) > lim), None)
    return {"I": i, "TP": tp, "sil": list(zip(starts, ends)), "first": first}


def audio_format(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
                        "stream=sample_rate,channels,codec_name", "-of", "json", str(path)], capture_output=True,
                       text=True)
    s = json.loads(r.stdout)["streams"][0]
    return int(s["sample_rate"]), int(s["channels"]), s["codec_name"]


def make_profile_dir(root, name, preset, **kw):
    pdir = Path(root)
    pdir.mkdir(parents=True, exist_ok=True)
    p = S.new_profile(name, S.preset_by_id(preset), pdir, **kw)
    S.write_json(pdir / f"{name}.json", p)
    return pdir


# --------------------------------------------------------------------------------------------- unit tests

class TextTests(unittest.TestCase):
    def en(self, text):
        return S.normalise(text, "speech_metadata", [], "words")["spoken"]

    def test_english_numbers(self):
        cases = {"It costs $5.": "It costs five dollars.",
                 "Only $4.99 today.": "Only four dollars ninety-nine cents today.",
                 "A 3.5 km walk.": "A three point five km walk.",
                 "Sales rose 40%.": "Sales rose forty percent.",
                 "The 1st, 2nd and 21st.": "The first, second and twenty-first.",
                 "In 1971, in 2005 and in 2026.": "In nineteen seventy-one, in two thousand five and in twenty "
                                                 "twenty-six.",
                 "Meet at 10:30.": "Meet at ten thirty.",
                 "About 3,250,000,000 people.": "About three billion two hundred fifty million people.",
                 "Wait 1,500 days.": "Wait one thousand five hundred days.",
                 "It hit $1.5 million.": "It hit one point five million dollars.",
                 "On April 26, 1956, it sailed.": "On April twenty-sixth, nineteen fifty-six, it sailed.",
                 "Due 3 May.": "Due the third of May.",
                 "By March 2026.": "By March twenty twenty-six.",
                 "On Dec. 1st we open.": "On December first we open."}
        for raw, want in cases.items():
            self.assertEqual(self.en(raw), want, raw)
        self.assertEqual(S.en_int(0), "zero")
        self.assertEqual(S.en_ordinal(112), "one hundred twelfth")
        self.assertEqual(S.en_year(1900), "nineteen hundred")

    def test_bangla_numbers(self):
        cases = {"১৫০০০০": "এক লাখ পঞ্চাশ হাজার", "১২৫০০০০০০": "বারো কোটি পঞ্চাশ লাখ", "২৫০": "দুইশো পঞ্চাশ",
                 "১০০": "একশো", "০": "শূন্য", "২০২৬": "দুই হাজার ছাব্বিশ"}
        for raw, want in cases.items():
            self.assertEqual(S.bn_num_text(raw), nfc(want), raw)
        spoken = S.normalise(nfc("১৯৭১ সালে দেশ স্বাধীন হয়। ২০২৬ সালে নতুন শুরু।"), "speech_metadata", [],
                             "words")["spoken"]
        self.assertIn(nfc("উনিশশো একাত্তর সালে"), spoken)
        self.assertIn(nfc("দুই হাজার ছাব্বিশ সালে"), spoken)
        self.assertEqual(S.normalise(nfc("২৫% ছাড়, দাম ৳৫০০।"), "speech_metadata", [], "words")["spoken"],
                         nfc("পঁচিশ শতাংশ ছাড়, দাম পাঁচশো টাকা।"))
        self.assertIn(nfc("পাঁচটি"), S.normalise(nfc("৫টি বই আছে।"), "speech_metadata", [], "words")["spoken"])
        # ASCII digits inside Bengali text read in Bangla
        self.assertIn(nfc("একশো"), S.normalise(nfc("মোট 100 জন এসেছে।"), "speech_metadata", [], "words")["spoken"])

    def test_bangla_table_0_to_99(self):
        self.assertEqual(len(S.BN_0_99), 100)
        self.assertEqual(len(set(S.BN_0_99)), 100)
        sample = {0: "শূন্য", 7: "সাত", 11: "এগারো", 19: "উনিশ", 29: "ঊনত্রিশ", 35: "পঁয়ত্রিশ", 42: "বিয়াল্লিশ",
                  59: "ঊনষাট", 71: "একাত্তর", 76: "ছিয়াত্তর", 89: "ঊননব্বই", 99: "নিরানব্বই"}
        for n, word in sample.items():
            self.assertEqual(S.BN_0_99[n], nfc(word), n)
            self.assertEqual(S.bn_int(n), nfc(word))

    def test_lexicon_and_inline(self):
        lex = [("NexaLance", "Nexa-Lance"), ("AI", "A I"), ("SaaS", "sass")]
        nm = S.normalise("NexaLance builds AI and SaaS tools; nexalance again, but AIM stays.", "speech_metadata",
                         lex, "words")
        self.assertEqual(nm["display"], "NexaLance builds AI and SaaS tools; nexalance again, but AIM stays.")
        self.assertEqual(nm["spoken"], "Nexa-Lance builds A I and sass tools; Nexa-Lance again, but AIM stays.")
        self.assertIn(["AI", "A I"], nm["terms"])
        ai_lower = S.normalise("the ai model", "speech_metadata", lex, "words")
        self.assertEqual(ai_lower["spoken"], "the ai model")          # acronyms are case-sensitive
        inline = S.normalise("Try {NexaLance|Nexus Lance} and {Q3|the third quarter}.", "speech_metadata", lex, "words")
        self.assertEqual(inline["display"], "Try NexaLance and Q3.")
        self.assertEqual(inline["spoken"], "Try Nexus Lance and the third quarter.")
        words = S.word_map(inline["segs"])
        self.assertEqual([w["w"] for w in words], ["Try", "NexaLance", "and", "Q3."])
        self.assertEqual(words[3]["sp"], "the third quarter.")
        multi = S.normalise("We met in New York today.", "speech_metadata", [("New York", "Nu Yawk City")], "words")
        self.assertEqual(multi["spoken"], "We met in Nu Yawk City today.")
        self.assertEqual([(w["w"], w["sp"]) for w in S.word_map(multi["segs"])][2:5],
                         [("in", "in"), ("New", "Nu Yawk"), ("York", "City")])

    def test_errors_in_plain_words(self):
        class E(Exception):
            def __init__(self, kind):
                super().__init__("detail")
                self.kind = kind
        self.assertIn("security add-generic-password", S.explain(E("no_key")))
        self.assertIn("billing", S.explain(E("billing")))
        self.assertIn("midnight Pacific", S.explain(E("quota_day")))
        self.assertIn("in a minute", S.explain(E("quota_minute")))
        self.assertIn("never retried", S.explain(E("safety")))
        self.assertIn("rejected", S.explain(E("bad_request")))
        self.assertIn("not retried", S.explain(E("timeout")))
        self.assertIn("nothing is paid twice", S.explain(E("server")))

    def test_warnings(self):
        def kinds(text, family="speech_metadata", numbers="words"):
            nm = S.normalise(text, family, [], numbers)
            return {w["kind"] for w in S.text_warnings(nm["spoken"], family, [], numbers, S.is_bn(text))}
        self.assertEqual(kinds("A clean sentence with 3 numbers in 2026."), set())
        self.assertIn("latin_in_bangla", kinds(nfc("আমি তোমাকে ami bhalobashi বলি।")))
        self.assertNotIn("latin_in_bangla", kinds(nfc("আমাদের YouTube channel দেখুন।")))
        self.assertIn("url", kinds("Visit www.example.com today."))
        self.assertIn("email", kinds("Write to hello@example.com now."))
        self.assertIn("symbol", kinds("R&D costs more."))
        self.assertIn("digits", kinds("Shot in 4K."))
        self.assertNotIn("digits", kinds("Shot in 4K.", numbers="keep"))
        self.assertIn("screen_words", kinds("The prices are in the table below, see below."))
        self.assertIn("screen_words", kinds(nfc("দাম জানতে নিচে দেখুন।")))
        self.assertIn("square_brackets", kinds("Hello [whispering] there."))
        self.assertNotIn("square_brackets", kinds("Hello [whispering] there.", family="director_text"))

    def test_sentence_split(self):
        self.assertEqual(S.split_sentences("Dr. Rahman paid $3.5 for it. Then he left!"),
                         ["Dr. Rahman paid $3.5 for it.", "Then he left!"])
        self.assertEqual(S.split_sentences("It is 3.5 km, e.g. a walk. J. K. Rowling wrote it. Next?"),
                         ["It is 3.5 km, e.g. a walk.", "J. K. Rowling wrote it.", "Next?"])
        self.assertEqual(S.split_sentences("Visit example.com. The U.S. economy grew."),
                         ["Visit example.com.", "The U.S. economy grew."])
        self.assertEqual(S.split_sentences(nfc("আমরা শুরু করি। চলুন দেখি! কেমন হলো?")),
                         [nfc("আমরা শুরু করি।"), nfc("চলুন দেখি!"), nfc("কেমন হলো?")])
        self.assertEqual(S.split_sentences("Go {A. B.|a b} now. <short pause> Then stop."),
                         ["Go {A. B.|a b} now.", "<short pause> Then stop."])

    def test_graphemes(self):
        self.assertEqual(S.graphemes(nfc("ক্ষমা")), 2)
        self.assertEqual(S.graphemes(nfc("বাংলাদেশ")), 4)
        self.assertEqual(S.graphemes("hello"), 5)

    def test_prices(self):
        # 10 minutes at 32 audio tokens a second (the usage the live API reported on 2026-09-25)
        self.assertAlmostEqual(S.tts_usd("gemini-3.8-flash-tts", 600, 0, "2026-09-25"), 0.1728, places=6)
        self.assertAlmostEqual(S.tts_usd("gemini-3.8-flash-tts", 600, 0, "2027-01-01"), 0.3456, places=6)
        self.assertAlmostEqual(S.tts_usd("gemini-3.8-flash-lite-tts", 600, 0, "2026-12-31"), 0.1152, places=6)
        self.assertAlmostEqual(S.tts_usd("gemini-3.1-flash-tts-preview", 600, 0), 0.384, places=6)
        self.assertAlmostEqual(S.asr_usd(600), 0.05, places=6)
        self.assertEqual(S.PRICES_AS_OF, "2026-09-25")


class ScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="nexa-speech-unit-"))
        cls.saved_home = os.environ.get("NEXA_SPEECH_HOME")
        os.environ["NEXA_SPEECH_HOME"] = str(cls.tmp / "home")
        cls.pdir = cls.tmp / "profiles"
        make_profile_dir(cls.pdir, "doc", "documentary-m", modes={"story": "calm and visual storytelling"})
        make_profile_dir(cls.pdir, "ad", "ad-upbeat-m")
        make_profile_dir(cls.pdir, "bn", "bn-yt-explainer-m")
        make_profile_dir(cls.pdir, "old", "documentary-m", model="gemini-3.1-flash-tts-preview")
        make_profile_dir(cls.pdir, "rafi", "explainer-friendly-m")
        make_profile_dir(cls.pdir, "nadia", "explainer-clear-f")

    @classmethod
    def tearDownClass(cls):
        if cls.saved_home is None:
            os.environ.pop("NEXA_SPEECH_HOME", None)
        else:
            os.environ["NEXA_SPEECH_HOME"] = cls.saved_home
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def plan(self, text, profile="doc", precise=None):
        return S.build_plan(text, profile, self.pdir, precise, "test")

    def test_every_directive(self):
        text = "\n".join([
            "@cast Rafi=rafi, Nadia=nadia",
            "// a comment that is never read",
            "# Hook",
            "@profile doc",
            "Every river starts as a small spring high in the hills above the valley.",
            "@mode story",
            "Farmers built their first villages along the banks of this long river.",
            "@mode off",
            "",
            "@takes 3",
            "This line is the hook of the whole video and it matters most of all.",
            "@pause 1.2",
            "Then the story moves on to the markets and the busy harbour towns.",
            "",
            "# Talk",
            "Rafi: So the launch is Thursday, and the whole team is ready for it.",
            "Nadia: Ready enough. <short pause> The last bug in the upload screen is fixed.",
            "It was a long night for everybody on the team, but it is done.",
            "",
            "Say {NexaLance|Nexa-Lance} clearly at the end of this last line please.",
        ])
        plan = self.plan(text)
        self.assertEqual(plan["errors"], [])
        self.assertEqual([s["title"] for s in plan["scenes"]], ["Hook", "Talk"])
        ch = plan["chunks"]
        self.assertEqual(plan["cast"], {"Rafi": "rafi", "Nadia": "nadia"})
        self.assertEqual(ch[0]["mode"], None)
        self.assertEqual(ch[1]["mode"], "story")
        self.assertEqual(ch[1]["style"], "calm and visual storytelling")
        self.assertEqual(ch[0]["gap_after"]["kind"], "sentence")      # the mode change starts a new chunk
        hero = next(c for c in ch if c["hero"])
        self.assertEqual(hero["takes"], 3)
        self.assertEqual(hero["gap_after"], {"kind": "pause", "s": 1.2})
        rafi = next(c for c in ch if c["speaker"] == "Rafi")
        nadia = [c for c in ch if c["speaker"] == "Nadia"]
        self.assertEqual(rafi["profile"], "rafi")
        self.assertEqual(len(nadia), 1)                                 # the next line continues Nadia's turn
        self.assertEqual(nadia[0]["profile"], "nadia")
        self.assertIn("<short pause>", nadia[0]["spoken"])
        self.assertNotIn("<short pause>", nadia[0]["display"])
        last = ch[-1]
        self.assertIn("Nexa-Lance", last["spoken"])
        self.assertIn("NexaLance", last["display"])
        self.assertEqual(last["gap_after"]["kind"], "end")
        prev = ch[-2]
        self.assertEqual(prev["gap_after"]["kind"], "paragraph")
        scene_end = [c for c in ch if c["scene"] == "s1"][-1]
        self.assertEqual(scene_end["gap_after"]["kind"], "scene")

    def test_lead_tail_pause_and_speaker_typo(self):
        plan = self.plan("@cast Rafi=rafi\n@pause 0.5\nThe first line is here and it is long enough to count.\n"
                         "Rafii: A typo in the name makes this line plain narration today.\n@pause 2")
        self.assertEqual(plan["lead_pause_s"], 0.5)
        self.assertEqual(plan["chunks"][-1]["gap_after"], {"kind": "pause", "s": 2.0})
        self.assertIn("speaker", [w["kind"] for w in plan["warnings"]])
        self.assertIsNone(plan["chunks"][-1]["speaker"])

    def test_profile_from_the_script(self):
        plan = S.build_plan("@profile ad\nA line said by the profile named in the script itself.", None, self.pdir)
        self.assertEqual(plan["main_profile"], "ad")
        with self.assertRaises(S.ProfileError):
            S.build_plan("No profile anywhere in this script at all.", None, self.pdir)
        self.assertTrue(any("no spoken lines" in e["error"] for e in self.plan("// only a comment\n")["errors"]))

    def test_two_x_note_when_paragraphs_cannot_balance(self):
        long_para = " ".join(["The quiet river carries silt and stories from the high hills to the sea."] * 10)
        plan = self.plan(long_para + "\n\nThe town is small and old.\n")
        self.assertTrue(any("more than 2x" in n["note"] for n in plan["notes"]))

    def test_directive_errors(self):
        plan = self.plan("Hello there, this is fine.\n@cast A=doc\n@pause 99\n@takes 9\n@wobble\n@mode nope\n"
                         "Another line <giggle> here.")
        errs = " | ".join(e["error"] for e in plan["errors"])
        for want in ("@cast goes at the top", "@pause wants seconds", "@takes wants a number", "unknown directive",
                     "mode nope is not in profile", "tag <giggle> is not in profile"):
            self.assertIn(want, errs)

    def test_chunk_limits(self):
        sent = "The quiet river carries silt and stories from the high hills to the wide sea today."
        para = " ".join([sent] * 12)
        plan = self.plan(para)
        self.assertEqual(plan["errors"], [])
        chunks = plan["chunks"]
        self.assertGreater(len(chunks), 2)
        for c in chunks:
            self.assertLessEqual(len(c["sentences"]), 4)
            self.assertLessEqual(c["est_s"], 45)
            self.assertLessEqual(c["n_words"], 110)
        self.assertLessEqual(max(c["est_s"] for c in chunks), 2 * min(c["est_s"] for c in chunks))
        # a fragment merges into its neighbour; a paragraph of one short line stands alone
        plan = self.plan("This is a sentence that is long enough for a chunk. Right. And this one also has enough "
                         "words in it.\n\nReady?")
        texts = [c["display"] for c in plan["chunks"]]
        self.assertNotIn("Right.", texts)
        ready = plan["chunks"][-1]
        self.assertEqual(ready["display"], "Ready?")
        self.assertTrue(ready["standalone"])
        self.assertEqual(ready["style"], "")
        self.assertEqual(ready["takes"], 2)
        # a sentence too long for one request is an error
        long_sent = " ".join(["word"] * 130) + "."
        self.assertTrue(any("too long" in e["error"] for e in self.plan(long_sent)["errors"]))

    def test_bangla_limits(self):
        s = nfc("নদী পাহাড় থেকে পলি আর গল্প বয়ে আনে আর সেই গল্প আমরা আজ আবার শুনব খুব মন দিয়ে সবাই মিলে।")
        plan = self.plan(" ".join([s] * 12), "bn")
        for c in plan["chunks"]:
            self.assertLessEqual(c["n_words"], 124)
            self.assertLessEqual(len(c["spoken"]), 1488)
            self.assertLessEqual(c["est_s"], 45)

    def test_precise_is_one_sentence_per_chunk(self):
        text = ("Big summer savings start this Friday in every store. Everything must go. Bring the whole family "
                "along for the day.")
        plan = self.plan(text, "ad")
        self.assertTrue(plan["precise"])
        self.assertEqual(len(plan["chunks"]), 2)                     # one sentence each; the fragment rides along
        self.assertEqual(sorted(len(c["sentences"]) for c in plan["chunks"]), [1, 2])
        self.assertNotIn("Everything must go.", [c["display"] for c in plan["chunks"]])
        plan = self.plan(text, "doc")
        self.assertEqual(len(plan["chunks"]), 1)

    def test_request_bodies(self):
        plan = self.plan("A calm line about rivers and hills for the test. <short pause> And the second sentence.\n\n"
                         "Ready?")
        c = plan["chunks"][0]
        body = S.request_body(c)
        self.assertEqual(body["input"][0]["text"], c["spoken"])
        self.assertEqual(body["input"][0]["annotations"], [{"type": "speech_metadata", "style": c["style"]}])
        self.assertNotIn(c["style"], body["input"][0]["text"])
        self.assertEqual(body["response_format"], {"type": "audio", "mime_type": "audio/l16", "sample_rate": 24000})
        self.assertEqual(body["generation_config"], {"speech_config": [{"voice": "Charon"}]})
        self.assertFalse(body["store"])
        self.assertNotIn("temperature", json.dumps(body))
        ready = S.request_body(plan["chunks"][1])
        self.assertNotIn("annotations", ready["input"][0])                    # empty style: no annotation
        old = self.plan("A calm line about rivers and hills for the test. <short pause> And the second one.", "old")
        body = S.request_body(old["chunks"][0])
        self.assertIsInstance(body["input"], str)
        self.assertTrue(body["input"].startswith(S.DIRECTOR_HEAD + "\n### PERFORMANCE\n"))
        self.assertIn("\n#### TRANSCRIPT\n", body["input"])
        self.assertIn("[short pause]", body["input"])
        self.assertNotIn("<short pause>", body["input"])
        self.assertEqual(body["response_format"], {"type": "audio"})

    def test_cache_key(self):
        c = self.plan("A calm line about rivers and hills for the test here.")["chunks"][0]
        k1, k2 = S.take_key(c, 1), S.take_key(c, 2)
        self.assertNotEqual(k1, k2)
        self.assertEqual(k1, S.take_key(dict(c), 1))
        self.assertRegex(k1, r"^[0-9a-f]{16}$")
        self.assertNotEqual(k1, S.take_key(dict(c, style="louder"), 1))
        self.assertNotEqual(k1, S.take_key(dict(c, voice_key="Kore"), 1))
        self.assertNotEqual(k1, S.take_key(dict(c, send_language_code=True), 1))   # a language code changes the call
        self.assertEqual(S.voice_key({"id": "voice_x", "type": "designed", "expire_time": "2027-01-01T00:00:00Z"}),
                         "voice_x@2027-01-01T00:00:00Z")

    def test_profile_lexicon_file(self):
        (self.pdir / "brand.tsv").write_text("# display<TAB>spoken\nNexaLance\tNexa-Lance\nAI\tA I\n", encoding="utf-8")
        make_profile_dir(self.pdir, "lex", "documentary-m", lexicon="brand.tsv")
        plan = S.build_plan("NexaLance uses AI to cut the edit time for every client video.", "lex", self.pdir, None,
                            "t")
        c = plan["chunks"][0]
        self.assertIn("Nexa-Lance uses A I", c["spoken"])
        self.assertEqual(c["lexicon_terms"], [["AI", "A I"], ["NexaLance", "Nexa-Lance"]])
        v = S.load_profile("lex", self.pdir)["version"]
        (self.pdir / "brand.tsv").write_text("NexaLance\tNeksa-Lance\n", encoding="utf-8")
        self.assertEqual(S.load_profile("lex", self.pdir)["version"], v + 1)     # a new lexicon is a new version
        (self.pdir / "bad.tsv").write_text("no tab here\n", encoding="utf-8")
        make_profile_dir(self.pdir, "badlex", "documentary-m", lexicon="bad.tsv")
        with self.assertRaises(S.ProfileError):
            S.build_plan("Any line at all for this test.", "badlex", self.pdir, None, "t")

    def test_designed_voice_expiry_is_a_note(self):
        make_profile_dir(self.pdir, "soon", "documentary-m")
        raw = json.loads((self.pdir / "soon.json").read_text())
        raw["voice"] = {"id": "voice_abc", "type": "designed", "expire_time": "2000-01-01T00:00:00Z", "sample": None}
        (self.pdir / "soon.json").write_text(json.dumps(raw))
        plan = S.build_plan("A plain line about the hills and the river for this test.", "soon", self.pdir, None, "t")
        self.assertEqual(plan["warnings"], [])
        self.assertTrue(any("expired" in n["note"] for n in plan["notes"]))
        self.assertEqual(plan["chunks"][0]["voice_key"], "voice_abc@2000-01-01T00:00:00Z")
        self.assertLess(S.voice_days_left(S.load_profile("soon", self.pdir)), 0)

    def test_profile_version_bumps_on_change(self):
        p = S.load_profile("doc", self.pdir)
        v = p["version"]
        p["style"] = "a different style"
        S.save_profile(p, self.pdir)
        self.assertEqual(S.load_profile("doc", self.pdir)["version"], v + 1)
        raw = json.loads((self.pdir / "doc.json").read_text())
        raw["modes"]["evidence"] = "precise"                 # a hand edit is noticed on the next load
        (self.pdir / "doc.json").write_text(json.dumps(raw))
        self.assertEqual(S.load_profile("doc", self.pdir)["version"], v + 2)
        raw = json.loads((self.pdir / "doc.json").read_text())
        raw["style"] = S.preset_by_id("documentary-m")["style"]
        (self.pdir / "doc.json").write_text(json.dumps(raw))


class CaptionTests(unittest.TestCase):
    def test_bangla_lines_never_start_with_danda(self):
        text = nfc("আজ আমরা দেখব ভিডিওর শব্দ কীভাবে পরিষ্কার করা যায় আর কেন সেটা এত জরুরি । তারপর আমরা একটা "
                   "ছোট উদাহরণ দেখব যেটা সবাই সহজে বুঝতে পারবে ।")
        words = []
        t = 0.0
        for si, sent in enumerate([s for s in S.split_sentences(text)]):
            nm = S.normalise(sent, "speech_metadata", [], "words")
            for w in S.word_map(nm["segs"]):
                words.append({"w": w["w"], "start": round(t, 3), "end": round(t + 0.35, 3), "sentence": si})
                t += 0.4
            t += 0.5
        self.assertTrue(any(w["w"].endswith("\u0964") for w in words))
        cues = S.build_cues(words)
        for c in cues:
            self.assertLessEqual(len(c["lines"]), 2)
            for line in c["lines"]:
                self.assertFalse(line.startswith("\u0964"), line)
                self.assertLessEqual(S.graphemes(line), 42, line)
            self.assertLessEqual(c["end"] - c["start"], 7.0 + 1e-6)
        srt = "".join(f"{i}\n{S.srt_ts(c['start'])} --> {S.srt_ts(c['end'])}\n" + "\n".join(c["lines"]) + "\n\n"
                      for i, c in enumerate(cues, 1))
        self.assertRegex(srt, r"^1\n00:00:00,000 --> 00:00:0\d,\d{3}\n")

    def test_cue_rules(self):
        words = [{"w": w, "start": i * 0.3, "end": i * 0.3 + 0.25, "sentence": 0}
                 for i, w in enumerate("This is a fairly long sentence, and it keeps going with more words to force "
                                       "a break somewhere near the middle of it.".split())]
        words.append({"w": "Next.", "start": 9.0, "end": 9.3, "sentence": 1})
        cues = S.build_cues(words)
        self.assertGreater(len(cues), 1)
        self.assertEqual(cues[-1]["lines"], ["Next."])                   # never across sentences
        self.assertGreaterEqual(cues[-1]["end"] - cues[-1]["start"], 1.0 - 1e-6)
        for a, b in zip(cues, cues[1:]):
            self.assertLessEqual(a["end"], b["start"] - 0.079)
        self.assertEqual(S.srt_ts(3661.5), "01:01:01,500")
        self.assertEqual(S.srt_ts(1.25, "."), "00:00:01.250")

    def test_close_sentences_never_overlap(self):
        words = [{"w": "Wait.", "start": 10.0, "end": 10.2, "sentence": 0},
                 {"w": "Stop!", "start": 10.2, "end": 10.5, "sentence": 1},
                 {"w": "Now.", "start": 10.5, "end": 10.7, "sentence": 2}]
        cues = S.build_cues(words)
        for a, b in zip(cues, cues[1:]):
            self.assertLessEqual(a["end"], b["start"])
            self.assertGreater(a["end"], a["start"])

    def test_match_boundaries(self):
        parts = S.match_boundaries(10.0, 20.0, [10, 10], [(12.0, 12.2), (14.8, 15.3), (18.0, 18.1)])
        self.assertEqual(parts, [(10.0, 14.8), (15.3, 20.0)])
        parts = S.match_boundaries(0.0, 9.0, [1, 1, 1], [])
        self.assertEqual([round(a, 2) for a, _ in parts], [0.0, 3.0, 6.0])

    def test_spread_words_snaps_to_pauses(self):
        words = [{"w": w, "sp": w} for w in ("aaa", "bbb", "ccc", "ddd")]
        times = S.spread_words(0.0, 4.0, words, [(1.9, 2.3)])      # the 2nd boundary falls at 1.8, near the pause
        self.assertEqual(times[1][1], 1.9)
        self.assertEqual(times[2][0], 2.3)
        self.assertTrue(all(a < b for a, b in times))


class Gate2WindowTests(unittest.TestCase):
    """On the live API 3.8 Flash TTS spoke up to 39 % faster than the Bangla preset, every word present."""

    M = {"voiced_s": 4.987, "empty": False, "lead_s": 0.05, "click": False, "noise_tail": False, "clipped": False,
         "loudness_i": -16.3, "centroid_hz": 1800.0}

    def gate2(self, voiced, calibrated):
        ref = {"wps": 2.444, "wps_source": "x", "drift": None, "calibrated": calibrated}
        res = S.evaluate({"n_words": 17}, {"finish_class": "ok"}, dict(self.M, voiced_s=voiced), ref)
        return res["gates"]["2"], res["measures"]["gate2_window"]

    def test_a_preset_guess_gets_the_wide_window(self):
        self.assertEqual(self.gate2(4.987, False), ("pass", [0.65, 1.5]))     # ratio 0.72, the live chunk c002
        self.assertEqual(self.gate2(4.987, True), ("fail", [0.8, 1.25]))
        self.assertEqual(self.gate2(3.4, False)[0], "fail")                     # half the words missing
        self.assertEqual(self.gate2(11.2, False)[0], "fail")                    # babble


class AlignMatchTests(unittest.TestCase):
    """The first live Bangla transcript (2026-09-25): a joined greeting, digits for spoken numbers, কিভাবে for
    কীভাবে. The old matcher placed 86 % of the words; these all match now."""

    def script(self, words):
        return [{"tok": t} for w in words for t in S.norm_tokens(w, True)]

    def heard(self, items):
        return S.heard_tokens([{"text": t, "start": a, "end": b} for t, a, b in items], True)

    def test_joined_words_digits_and_spelling(self):
        script = self.script(["আসসালামু", "আলাইকুম,", "সবাই", "কীভাবে", "দশ", "সেকেন্ডে", "মাসে", "পাঁচশো", "টাকার"])
        hyp = self.heard([("আসসালামুআলাইকুম,", 0.1, 0.8), ("সবাই", 1.3, 1.6), ("কিভাবে", 5.8, 6.25),
                          ("10", 6.25, 6.7), ("সেকেন্ডে", 6.7, 7.0), ("মাসে", 8.9, 9.2), ("500", 9.2, 9.8),
                          ("টাকার", 9.8, 9.9)])
        matched, close = S.place_tokens(script, hyp)
        self.assertEqual((matched + close, len(script)), (9, 9))
        self.assertAlmostEqual(script[0]["t"][0], 0.1)
        self.assertAlmostEqual(script[1]["t"][1], 0.8)
        self.assertAlmostEqual(script[0]["t"][1], script[1]["t"][0])            # the heard span shared by length
        self.assertEqual(script[4]["t"], (6.25, 6.7))                           # দশ heard as 10
        self.assertEqual(script[7]["t"], (9.2, 9.8))                            # পাঁচশো heard as 500

    def test_digits_after_english_stay_english(self):
        toks = [x["tok"] for x in self.heard([("নতুন", 0, 0.3), ("iPhone", 0.3, 0.7), ("15", 0.7, 1.0)])]
        self.assertEqual(toks, ["নতুন", "iphone", "fifteen"])

    def test_spelling_fold(self):
        self.assertEqual(S.match_key("কীভাবে"), S.match_key("কিভাবে"))
        self.assertEqual(S.match_key("দেখাবো"), S.match_key("দেখাব"))
        self.assertNotEqual(S.match_key("কাল"), S.match_key("কাজ"))


class NumberWordTests(unittest.TestCase):
    """Numbers count as the words a voice says for them, so a line with a date or a price is not judged slow."""

    def test_numbers_as_read(self):
        cases = {"26,": 1, "1956,": 2, "2023.": 2, "$5.86": 5, "58": 1, "116": 3, "24,346": 5, "80%": 2,
                 "1,200": 4, "3.5x": 4, "10k": 2, "1990s": 2, "box": 1, "১৯৫৬": 2, "৫০০": 1}
        for token, words in cases.items():
            self.assertEqual(S.number_words(token, token[0] in "০১২৩৪৫৬৭৮৯"), words, token)

    def test_a_dated_line_is_not_counted_short(self):
        words = S.spoken_words("On April 26, 1956, the Ideal-X left Newark for Houston.")
        self.assertEqual(len(words), 10)
        self.assertEqual(S.spoken_count(words), 11)


class RenderSummaryTests(unittest.TestCase):
    def test_a_failing_chunk_says_how_to_ask_for_new_takes(self):
        res = {"rendered": 1, "chunks": 11, "calls": 2, "est_usd": 0.003, "budget": 0.05, "rerolls": [],
               "reroll_notes": [], "failures": [], "stopped": None, "stop_kind": None, "missing": [],
               "flagged": ["c011"], "flagged_takes": {"c011": 2}}
        text = "\n".join(S.render_summary_lines(Path("/tmp/p"), {}, res))
        self.assertIn("c011 (2 takes; --takes 4 for 2 more)", text)      # --takes counts the takes already made


class AsrCheckTests(unittest.TestCase):
    def chunk(self, spoken, style="calm documentary narration", terms=None):
        return {"spoken": spoken, "style": style, "tags": [], "lexicon_terms": terms or []}

    def test_clean_transcript_passes(self):
        ch = self.chunk("In nineteen seventy-one the river carried silt.")
        self.assertEqual(S.asr_check(ch, "In 1971 the river carried silt.")["fails"], [])

    def test_failures(self):
        ch = self.chunk("The river carried silt to the sea.", terms=[["NexaLance", "Nexa-Lance"]])
        res = S.asr_check(ch, "The river carried silt to the")
        self.assertTrue(any("missing at the end" in f for f in res["fails"]))
        self.assertTrue(any("lexicon term not heard" in f for f in res["fails"]))
        res = S.asr_check(self.chunk("The river carried silt to the sea."), "Calm documentary narration. The river "
                                                                           "carried silt to the sea. Thank you.")
        self.assertTrue(any("extra word" in f for f in res["fails"]))
        self.assertTrue(any("direction words spoken" in f for f in res["fails"]))
        bn = self.chunk(nfc("আমরা আজ নদীর গল্প শুনব।"))
        self.assertEqual(S.asr_check(bn, nfc("আমরা আজ নদীর গল্প শুনব।"))["metric"], "cer")
        self.assertTrue(S.asr_check(bn, nfc("আমরা কাল পাহাড়ের কথা বলব।"))["fails"])


class FitTests(unittest.TestCase):
    def manifest(self):
        chunks, t = [], 0.06
        spec = [("s1", 5.0, "sentence"), ("s1", 5.0, "paragraph"), ("s1", 5.0, "scene"), ("s2", 6.0, "sentence"),
                ("s2", 6.0, "scene"), ("s3", 4.0, "end")]
        gaps = {"sentence": 0.32, "paragraph": 0.75, "scene": 1.1, "end": 0.0}
        for i, (sc, dur, kind) in enumerate(spec):
            chunks.append({"id": f"c{i + 1:03d}", "scene": sc, "start": round(t, 3), "end": round(t + dur, 3),
                           "gap_after": {"kind": kind, "s": gaps[kind]}})
            t += dur + gaps[kind]
        scenes = [{"id": s, "title": s, "start": min(c["start"] for c in chunks if c["scene"] == s),
                   "end": max(c["end"] for c in chunks if c["scene"] == s)} for s in ("s1", "s2", "s3")]
        return {"chunks": chunks, "scenes": scenes}

    def plan(self):
        tmp = Path(tempfile.mkdtemp(prefix="nexa-speech-fit-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        p = S.new_profile("fit", S.preset_by_id("documentary-m"), tmp)
        return {"main_profile": "fit", "profiles": {"fit": p}}

    def test_gaps_first_then_tempo_then_advice(self):
        man, plan = self.manifest(), self.plan()
        cur = {r["scene"]: r["current_s"] for r in S.fit_plan(man, plan, {}, False)["scenes"]}
        fp = S.fit_plan(man, plan, {"s1": cur["s1"] + 0.5, "s2": cur["s2"] - 0.5, "s3": cur["s3"] - 3.0}, False)
        rows = {r["scene"]: r for r in fp["scenes"]}
        self.assertEqual(rows["s1"]["tempo"], 1.0)                     # 0.5 s fits in the gaps
        self.assertTrue(rows["s1"]["gaps"])
        self.assertAlmostEqual(rows["s1"]["residual_s"], 0.0, places=2)
        self.assertGreater(rows["s2"]["tempo"], 1.0)                    # one sentence gap gives 0.14 s, then tempo
        self.assertLessEqual(rows["s2"]["tempo"], 1.03 + 1e-9)          # its neighbour s1 sits at 1.0
        self.assertIn("cut the script", rows["s3"]["advice"])            # 3 s off a 4 s scene is out of range
        self.assertRegex(rows["s3"]["advice"], r"about \d+ words to cut")
        for a, b in zip(fp["scenes"], fp["scenes"][1:]):
            self.assertLessEqual(abs(a["tempo"] - b["tempo"]), 0.03 + 1e-9)
        ad = {r["scene"]: r for r in S.fit_plan(man, plan, {"s1": cur["s1"] - 3.2}, True)["scenes"]}
        self.assertGreaterEqual(ad["s1"]["tempo"], 1.0)
        self.assertLessEqual(ad["s1"]["tempo"], 1.10 + 1e-9)


@unittest.skipUnless(HAVE_FFMPEG, "needs ffmpeg and ffprobe")
class AudioTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="nexa-speech-audio-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def wav(self, name, pcm):
        path = self.tmp / name
        path.write_bytes(wav_bytes(pcm))
        return path

    def test_analysis_flags(self):
        pcm, words = fake_speech("One two three four five six seven eight.", "Charon")
        m = S.analyse_audio(self.wav("clean.wav", pcm))
        self.assertAlmostEqual(m["first_sound"], LEAD_S, delta=0.02)
        self.assertAlmostEqual(m["last_sound"], words[-1][2], delta=0.03)
        self.assertAlmostEqual(m["voiced_s"], 8 * WORD_S - 0.03, delta=0.06)
        self.assertFalse(m["click"] or m["noise_tail"] or m["clipped"])
        click = array("h", [0] * 48 + [30000, -30000, 28000, -20000] + [0] * 2000)
        if sys.byteorder == "big":
            click.byteswap()
        m = S.analyse_audio(self.wav("click.wav", click.tobytes() + pcm))
        self.assertTrue(m["click"])
        self.assertGreater(m["first_sound"], 0.05)
        noisy, _ = fake_speech("One two three four five six seven eight.", "Charon", "noise_tail")
        m = S.analyse_audio(self.wav("noise.wav", noisy))
        self.assertTrue(m["noise_tail"])
        self.assertAlmostEqual(m["last_sound"], words[-1][2], delta=0.05)     # the hiss is not speech
        m = S.analyse_audio(self.wav("tight.wav", pcm[int(LEAD_S * RATE) * 2:]))
        self.assertLess(m["lead_s"], 0.02)
        loud = array("h", [32767 if (i // 40) % 2 else -32768 for i in range(RATE)])
        if sys.byteorder == "big":
            loud.byteswap()
        m = S.analyse_audio(self.wav("clip.wav", loud.tobytes()))
        self.assertTrue(m["clipped"])

    def test_room_tone_none_and_file(self):
        pcm, _ = fake_speech("One two three four five six.", "Charon")
        a = array("h")
        a.frombytes(pcm)
        voice = array("f", [x / 32768.0 for x in a])
        canvas = array("f", voice) + array("f", [0.0] * RATE * 2)          # 2 s of gap after the voice
        cpath = self.tmp / "canvas.f32"
        S.write_f32(cpath, canvas)
        seconds = len(canvas) / float(RATE)

        def gap_rms(path):
            b = S.read_f32(path)[-RATE:]
            return 10 * math.log10(max(1e-20, sum(x * x for x in b) / len(b)))
        post = dict(S.DEFAULT_POST, room_tone="none")
        S.build_pre(cpath, seconds, post, self.tmp / "none.f32", self.tmp)
        self.assertLess(gap_rms(self.tmp / "none.f32"), -100)
        S.build_pre(cpath, seconds, dict(S.DEFAULT_POST), self.tmp / "pink.f32", self.tmp)
        self.assertAlmostEqual(gap_rms(self.tmp / "pink.f32"), -65.0, delta=2.0)
        tone = self.wav("tone.wav", noise(1.0, -30.0))
        S.build_pre(cpath, seconds, dict(S.DEFAULT_POST, room_tone=str(tone)), self.tmp / "file.f32", self.tmp)
        self.assertAlmostEqual(gap_rms(self.tmp / "file.f32"), -65.0, delta=2.0)

    def test_analysis_reads_24_bit_files(self):
        pcm, _ = fake_speech("One two three four five six seven eight.", "Charon")
        src = self.wav("s16.wav", pcm)
        s24 = self.tmp / "s24.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-ar", "48000", "-c:a", "pcm_s24le", str(s24)],
                       check=True)
        m = S.analyse_audio(s24)
        self.assertAlmostEqual(m["first_sound"], LEAD_S, delta=0.02)
        self.assertAlmostEqual(m["voiced_s"], 8 * WORD_S - 0.03, delta=0.08)

    def test_limiter_first_then_linear_loudnorm(self):
        """Quiet speech with full-scale spikes: the gain to -16 LUFS would push the peaks over, so the limiter goes in
        first and pass 2 must still be linear."""
        pcm, _ = fake_speech(" ".join(["word"] * 40) + ".", "Charon")
        a = array("h")
        a.frombytes(pcm)
        f = array("f", [x / 32768.0 * 0.25 for x in a])
        for k in range(RATE // 2, len(f), RATE):
            f[k] = 0.99
            f[k + 1] = -0.99
        pre = self.tmp / "pre.f32"
        S.write_f32(pre, f)
        out = self.tmp / "out.wav"
        fin = S.finish_loudness(pre, RATE, {"stem_I": -16.0, "TP": -1.5, "LRA": 11.0}, out)
        self.assertEqual(fin["normalization"], "linear")
        self.assertIsNotNone(fin["limiter_db"])
        got = measure(out)
        self.assertLessEqual(abs(got["I"] + 16.0), 0.5, got)
        self.assertLessEqual(got["TP"], -1.5, got)
        self.assertEqual(audio_format(out), (48000, 1, "pcm_s24le"))

    def test_peaks_between_samples_are_caught_after_the_resample(self):
        """A voice at 24 kHz with energy near 12 kHz: its sample peaks hide much higher true peaks, which show up once
        it is resampled to 48 kHz. The ceiling works on the 48 kHz signal, so the master still lands on target."""
        pcm, _ = fake_speech(" ".join(["word"] * 40) + ".", "Charon")
        a = array("h")
        a.frombytes(pcm)
        f = array("f", [x / 32768.0 * 0.22 for x in a])
        for k in range(RATE // 3, len(f) - 1200, RATE):
            for j in range(1200):          # 50 ms of an 11.9 kHz tone, sampled where its peaks fall between samples
                f[k + j] += 0.6 * math.sin(2 * math.pi * 11900.0 * j / RATE + 0.7)
        pre = self.tmp / "pre_hf.f32"
        S.write_f32(pre, f)
        out = self.tmp / "out_hf.wav"
        fin = S.finish_loudness(pre, RATE, {"stem_I": -16.0, "TP": -1.5, "LRA": 11.0}, out)
        got = measure(out)
        self.assertLessEqual(abs(got["I"] + 16.0), 0.5, got)
        self.assertLessEqual(got["TP"], -1.5, got)
        self.assertEqual(fin["normalization"], "linear")


# --------------------------------------------------------------------------------------------- end to end

MAIN_SCRIPT = """# Hook
Every river starts as a small spring high in the hills. It gathers rain and snow as it moves down the slope. By the time it reaches the valley, it carries the story of the whole land.

@mode story
Farmers built their first villages along these banks. The water gave them fish, fields and a road to the sea. Trade grew, and the villages became towns with busy markets.

@mode off
# The numbers
In 1971 the river carried 3.5 million tonnes of silt. Today it carries about 40% less. A ticket on the old ferry cost $4.99 in 2005.
@pause 1.2
The 21st century brought dams, canals and new bridges. Each one changed the way the water moves across the delta.

# Close
@takes 2
So next time you cross a bridge, look down for a moment. The river is still telling its story.

Ready?
"""

DRIFT_SCRIPT = """# Drift
The first chapter opens with a quiet walk along the old stone wall.

The second chapter follows the copper roof of the station in the rain.

The third chapter stops at the orchard where the apples fall every autumn.

The fourth chapter crosses the meadow where the horses graze all summer long.

The fifth chapter climbs the steep lane toward the chapel on the hill.

The sixth chapter ends at the harbour as the boats return with the tide.
"""


@unittest.skipUnless(HAVE_FFMPEG, "needs ffmpeg and ffprobe")
class EndToEndTests(unittest.TestCase):
    outputs = []

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="nexa-speech-e2e-"))
        cls.fake = FakeGemini().start()
        cls.saved = {k: os.environ.get(k) for k in ENV_KEYS}
        cls.saved_pool = {k: v for k, v in os.environ.items() if k.startswith("GEMINI_API_KEY_")}
        for k in cls.saved_pool:
            del os.environ[k]
        os.environ.update({"NEXA_GEMINI_BASE_URL": cls.fake.url, "NEXA_GEMINI_SLEEP_SCALE": "0",
                           "NEXA_NO_KEYCHAIN": "1", "GEMINI_API_KEY": FAKE_KEY,
                           "NEXA_SPEECH_HOME": str(cls.tmp / "home"), "NEXA_ELEVENLABS_BASE_URL": cls.fake.url,
                           "ELEVENLABS_API_KEY": EL_FAKE_KEY})
        cls.cli("profile", "new", "en-doc", "--preset", "documentary-m", "--mode", "story=calm and visual storytelling")
        cls.cli("profile", "new", "en-31", "--preset", "documentary-m", "--model", "gemini-3.1-flash-tts-preview")
        cls.cli("profile", "new", "bn-yt", "--preset", "bn-yt-explainer-m")
        cls.main = cls.tmp / "main"
        (cls.tmp / "main.md").write_text(MAIN_SCRIPT, encoding="utf-8")
        cls.r1 = cls.cli("render", cls.tmp / "main.md", "--profile", "en-doc", "--out", cls.main, "--json")
        cls.calls1 = len(cls.fake.tts())
        cls.r2 = cls.cli("render", cls.tmp / "main.md", "--profile", "en-doc", "--out", cls.main, "--json")
        cls.calls2 = len(cls.fake.tts())
        cls.m = cls.cli("master", cls.main, "--json")
        cls.a = cls.cli("align", cls.main, "--engine", "pauses", "--json")

    @classmethod
    def tearDownClass(cls):
        cls.fake.stop()
        for k, v in cls.saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        os.environ.update(cls.saved_pool)
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def cli(cls, *args, ok=True):
        r = subprocess.run([sys.executable, str(SCRIPT), *[str(a) for a in args]], capture_output=True, text=True,
                           timeout=600)
        cls.outputs.append(r.stdout + r.stderr)
        if ok and r.returncode != 0:
            raise AssertionError(f"{args[0]} failed ({r.returncode}):\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
        return r

    def js(self, r):
        return json.loads(r.stdout)

    def script(self, name, text):
        path = self.tmp / f"{name}.md"
        path.write_text(text, encoding="utf-8")
        return path

    # ---- the main project

    def test_render_calls_once_per_take_and_logs_them(self):
        res = self.js(self.r1)
        plan = json.loads((self.main / "plan.json").read_text())
        takes = sum(c["takes"] for c in plan["chunks"])
        self.assertEqual(len(plan["chunks"]), 6)
        self.assertEqual(takes, 8)                                     # the @takes 2 hook and the lone "Ready?"
        self.assertEqual(res["calls"], self.calls1)
        self.assertGreaterEqual(self.calls1, takes)
        ledger = [json.loads(x) for x in (self.main / "ledger.jsonl").read_text().splitlines()]
        self.assertEqual(len([e for e in ledger if e["result"] == "ok" and e["command"] == "render"]), self.calls1)
        for e in ledger:
            if e.get("model") == "elevenlabs-forced-alignment":
                self.assertEqual(e["key_source"], "ELEVENLABS_API_KEY")          # align's own line
                continue
            self.assertEqual(e["key_source"], "GEMINI_API_KEY")
            self.assertGreater(e["est_usd"], 0)
            self.assertIn("usage", e)
        state = json.loads((self.main / "takes.json").read_text())
        for entry in state["chunks"].values():
            for rec in entry["takes"].values():
                self.assertTrue((self.main / rec["file"]).exists())
                self.assertTrue((self.tmp / "home" / "cache" / (rec["key"] + ".wav")).exists())
                self.assertTrue((self.tmp / "home" / "cache" / (rec["key"] + ".json")).exists())

    def test_second_render_makes_no_call(self):
        self.assertEqual(self.calls2, self.calls1)
        self.assertEqual(self.js(self.r2)["calls"], 0)

    def test_request_bodies_on_the_wire(self):
        plan = json.loads((self.main / "plan.json").read_text())
        sent = {e["text"]: e["body"] for e in self.fake.tts()}
        story = next(c for c in plan["chunks"] if c["mode"] == "story")
        body = sent[story["spoken"]]
        self.assertEqual(body["input"][0]["annotations"][0]["style"], "calm and visual storytelling")
        self.assertEqual(body["response_format"]["mime_type"], "audio/l16")
        ready = next(c for c in plan["chunks"] if c["standalone"])
        self.assertNotIn("annotations", sent[ready["spoken"]]["input"][0])
        for body in sent.values():
            self.assertNotIn("temperature", json.dumps(body))
            style = (body["input"][0].get("annotations") or [{}])[0].get("style")
            if style:
                self.assertNotIn(style, body["input"][0]["text"])
        numbers = next(c for c in plan["chunks"] if "1971" in c["display"])
        self.assertIn("nineteen seventy-one", numbers["spoken"])
        self.assertIn("four dollars ninety-nine cents", numbers["spoken"])

    def test_hero_and_standalone_keep_every_take(self):
        state = json.loads((self.main / "takes.json").read_text())
        plan = json.loads((self.main / "plan.json").read_text())
        for c in plan["chunks"]:
            if c["hero"] or c["standalone"]:
                entry = state["chunks"][c["base_key"]]
                self.assertGreaterEqual(len(entry["takes"]), 2)
                self.assertIn("best of", entry["chosen_by"])

    def test_master_loudness_and_format(self):
        res = self.js(self.m)
        out = self.main / "vo_48k.wav"
        self.assertEqual(audio_format(out), (48000, 1, "pcm_s24le"))
        got = measure(out)
        self.assertLessEqual(abs(got["I"] + 16.0), 0.5, got)
        self.assertLessEqual(got["TP"], -1.5, got)
        self.assertEqual(res["loudness"]["normalization"], "linear")
        man = json.loads((self.main / "vo.manifest.json").read_text())
        self.assertEqual(man["schema"], "nexa-speech/manifest-1")
        self.assertEqual(man["sample_rate"], 48000)
        self.assertEqual(man["file"], "vo_48k.wav")
        for key in ("duration_s", "loudness", "profiles", "scenes", "chunks", "sentences", "cost"):
            self.assertIn(key, man)
        self.assertEqual(man["profiles"]["en-doc"]["voice"], "Charon")
        self.assertEqual([s["id"] for s in man["scenes"]], ["s1", "s2", "s3"])

    def test_timeline_matches_the_audio(self):
        man = json.loads((self.main / "vo.manifest.json").read_text())
        chunks = man["chunks"]
        for a, b in zip(chunks, chunks[1:]):
            self.assertAlmostEqual(b["start"] - a["end"], a["gap_after"]["s"], delta=0.0021)
        pause = next(c for c in chunks if c["gap_after"]["kind"] == "pause")
        self.assertEqual(pause["gap_after"]["s"], 1.2)
        got = measure(self.main / "vo_48k.wav")
        onsets = [got["first"]] + [e for _, e in got["sil"]]
        for s in man["sentences"]:
            near = min(abs(o - s["start"]) for o in onsets)
            self.assertLessEqual(near, 0.020, (s, near))
        gap = [e - s for s, e in got["sil"] if abs(s - pause["end"]) < 0.05]
        self.assertTrue(gap and abs(gap[0] - 1.2) <= 0.03, gap)
        self.assertGreater(len(man["sentences"]), len(chunks))

    def test_align_pauses_outputs(self):
        res = self.js(self.a)
        self.assertEqual(res["engine"], "pauses")
        words = json.loads((self.main / "words.json").read_text())
        sents = json.loads((self.main / "sentences.json").read_text())
        self.assertEqual({"w", "start", "end", "sentence", "chunk", "scene"}, set(words[0]))
        self.assertIn("$4.99", [w["w"] for w in words])                   # captions show what is written
        for a, b in zip(words, words[1:]):
            self.assertLessEqual(a["start"], a["end"])
            self.assertLessEqual(a["end"], b["start"] + 1e-6)
        for w in words:
            s = sents[w["sentence"]]
            self.assertGreaterEqual(w["start"], s["start"] - 1e-6)
            self.assertLessEqual(w["end"], s["end"] + 1e-6)
        srt = (self.main / "vo.srt").read_text()
        vtt = (self.main / "vo.vtt").read_text()
        self.assertTrue(srt.startswith("1\n00:00:00,"))
        self.assertTrue(vtt.startswith("WEBVTT\n\n00:00:00."))
        for block in srt.strip().split("\n\n"):
            lines = block.split("\n")
            self.assertRegex(lines[1], r"^\d\d:\d\d:\d\d,\d{3} --> \d\d:\d\d:\d\d,\d{3}$")
            self.assertLessEqual(len(lines) - 2, 2)
            for line in lines[2:]:
                self.assertLessEqual(len(line), 42)

    def test_align_elevenlabs_sends_the_spoken_script(self):
        words = json.loads((self.main / "words.json").read_text())
        before = len(self.fake.log)
        r = self.cli("align", self.main, "--engine", "elevenlabs", "--json")
        info = self.js(r)["info"]
        fa = [x for x in self.fake.log[before:] if x.get("kind") == "fa"]
        self.assertEqual(len(fa), 1)
        self.assertIn("four dollars ninety-nine cents", fa[0]["text"])        # the spoken form goes up
        self.assertNotIn("$4.99", fa[0]["text"])
        self.assertEqual((info["engine"], info["matched_share"]), ("elevenlabs", 1.0))
        self.assertIn("ferry", info["suspect_words"])                          # a high per-word loss is flagged
        got = json.loads((self.main / "words.json").read_text())
        self.assertEqual([w["w"] for w in got], [w["w"] for w in words])      # the display words come back
        self.assertTrue(all(a["start"] <= b["start"] for a, b in zip(got, got[1:])))
        self.cli("align", self.main, "--engine", "pauses")                     # leave words.json as it was made

    def test_align_elevenlabs_skips_a_word_without_times(self):
        words = json.loads((self.main / "words.json").read_text())
        self.fake.fa_timeless = 2
        try:
            r = self.cli("align", self.main, "--engine", "elevenlabs", "--json")
        finally:
            self.fake.fa_timeless = None
        info = self.js(r)["info"]
        self.assertLess(info["matched_share"], 1.0)                             # that word is placed, not matched
        got = json.loads((self.main / "words.json").read_text())
        self.assertEqual([w["w"] for w in got], [w["w"] for w in words])
        self.assertTrue(all(a["start"] <= b["start"] for a, b in zip(got, got[1:])))
        self.cli("align", self.main, "--engine", "pauses")                     # leave words.json as it was made

    def test_align_gemini_carries_the_display_text(self):
        words = json.loads((self.main / "words.json").read_text())
        plan = json.loads((self.main / "plan.json").read_text())
        spoken = []
        for c in plan["chunks"]:
            for s in c["sentences"]:
                for w in s["words"]:
                    spoken.append(w["sp"] or w["w"])
        self.assertEqual(len(spoken), len(words))
        asr = []
        for w, sp in zip(words, spoken):
            toks = sp.replace("-", " ").split()
            step = (w["end"] - w["start"]) / len(toks)
            for i, t in enumerate(toks):
                asr.append((t, round(w["start"] + i * step, 3), round(w["start"] + (i + 1) * step, 3)))
        dropped = asr[10]
        asr = asr[:10] + asr[11:]                           # one word the recogniser missed
        self.fake.transcript_override = asr
        try:
            r = self.cli("align", self.main, "--engine", "gemini", "--json")
        finally:
            self.fake.transcript_override = None
        info = self.js(r)["info"]
        self.assertEqual(info["engine"], "gemini")
        self.assertGreater(info["matched_share"], 0.95)
        got = json.loads((self.main / "words.json").read_text())
        self.assertEqual([w["w"] for w in got], [w["w"] for w in words])
        self.assertIn("$4.99", [w["w"] for w in got])
        for g, w in zip(got, words):
            self.assertAlmostEqual(g["start"], w["start"], delta=0.02 if g is not got[10] else 0.6)
        self.assertLessEqual(got[9]["end"], got[10]["start"] + 1e-6)
        self.assertLessEqual(got[10]["end"], got[11]["start"] + 1e-6)
        self.assertTrue(dropped)
        self.cli("align", self.main, "--engine", "pauses")               # back to the offline captions

    def test_qa_writes_a_table(self):
        r = self.cli("qa", self.main, "--json")
        res = self.js(r)
        self.assertEqual(res["summary"]["missing"], 0)
        qa = json.loads((self.main / "qa.json").read_text())
        self.assertIn("speaker_similarity", qa)
        for row in qa["chunks"]:
            self.assertIn(row["result"], ("pass", "flag", "fail"))
        plain = self.cli("qa", self.main).stdout
        self.assertIn("pass", plain)

    def test_pick_by_hand(self):
        plan = json.loads((self.main / "plan.json").read_text())
        hero = next(c for c in plan["chunks"] if c["hero"])
        self.cli("pick", self.main, hero["id"], "1")
        state = json.loads((self.main / "takes.json").read_text())
        self.assertEqual(state["chunks"][hero["base_key"]]["chosen"], 1)
        self.assertEqual(state["chunks"][hero["base_key"]]["chosen_by"], "pick")
        r = self.cli("pick", self.main, hero["id"], "9", ok=False)
        self.assertNotEqual(r.returncode, 0)

    def test_a_paid_take_is_in_the_ledger_even_when_saving_fails(self):
        plan = json.loads((self.main / "plan.json").read_text())
        ch = dict(plan["chunks"][0])
        resp = {"status": "completed", "steps": [{"type": "model_output", "content": [
            {"type": "audio", "data": base64.b64encode(bytes(4800)).decode(),
             "mime_type": "audio/l16; rate=24000; channels=1", "sample_rate": 24000, "channels": 1}]}],
            "usage": {"total_output_tokens": 3}}
        out = self.tmp / "savefail"
        out.mkdir(exist_ok=True)

        def fail(parts, key):
            raise OSError("disk full")
        saved = S.G.interactions, S.save_master
        S.G.interactions = lambda body, timeout=None: (resp, {"key": "GEMINI_API_KEY", "attempts": 1})
        S.save_master = fail
        try:
            with self.assertRaises(OSError):
                S.synth_take(ch, 9, out, "render")
        finally:
            S.G.interactions, S.save_master = saved
        led = [json.loads(x) for x in (out / "ledger.jsonl").read_text().splitlines()]
        self.assertEqual((led[-1]["take"], led[-1]["result"]), (9, "ok"))

    def test_cost_estimate_and_actual(self):
        est = self.js(self.cli("cost", "--minutes", "10", "--model", "gemini-3.8-flash-tts", "--json"))
        row = est["rows"][0]
        self.assertAlmostEqual(row["interactive"], 0.1743, delta=0.005)
        self.assertAlmostEqual(row["batch_or_flex"], row["interactive"] / 2, delta=0.0001)   # both rounded
        act = self.js(self.cli("cost", self.main, "--json"))
        self.assertGreaterEqual(act["calls"], self.calls1)                 # align --engine gemini adds its own line
        self.assertIsNotNone(act["usage_usd"])

    def test_plan_is_free_and_prints_the_cost(self):
        before = len(self.fake.log)
        r = self.cli("plan", self.tmp / "main.md", "--profile", "en-doc", "--out", self.tmp / "planonly")
        self.assertEqual(len(self.fake.log), before)
        self.assertIn("interactive", r.stdout)
        self.assertIn("batch or flex", r.stdout)
        self.assertTrue((self.tmp / "planonly" / "plan.json").exists())

    # ---- other projects

    def test_riff_answers_are_not_wrapped_twice(self):
        path = self.script("old", "A calm line about the old harbour lights. <short pause> The second line is here "
                                  "too.\n")
        out = self.tmp / "old"
        self.cli("render", path, "--profile", "en-31", "--out", out)
        body = self.fake.tts()[-1]["body"]
        self.assertIsInstance(body["input"], str)
        self.assertIn("### PERFORMANCE\ncalm documentary narration", body["input"])
        self.assertIn("[short pause]", body["input"])
        state = json.loads((out / "takes.json").read_text())
        rec = next(iter(next(iter(state["chunks"].values()))["takes"].values()))
        self.assertTrue(rec["riff"])
        with wave.open(str(out / rec["file"])) as w:
            frames = w.readframes(w.getnframes())
            self.assertNotEqual(frames[:4], b"RIFF")
            self.assertEqual(w.getframerate(), 24000)
        pcm, _ = fake_speech(self.fake.tts()[-1]["text"], "Charon")
        self.assertEqual(len(frames), len(pcm))                            # no 44-byte header inside the data

    def test_truncated_take_is_rerolled_once(self):
        path = self.script("trunc", "The lighthouse keeper climbs the stairs every evening at dusk.\n\n"
                                    "The Harbour master counts the boats that come home before the storm.\n")
        out = self.tmp / "trunc"
        self.fake.rules.append({"match": "Harbour", "mode": "truncated", "count": 1})
        before = len(self.fake.tts())
        r = self.cli("render", path, "--profile", "en-doc", "--out", out, "--json")
        res = self.js(r)
        self.assertEqual(len(self.fake.tts()) - before, 3)
        self.assertEqual([x["chunk"] for x in res["rerolls"]], ["c002"])
        plan = json.loads((out / "plan.json").read_text())
        state = json.loads((out / "takes.json").read_text())
        entry = state["chunks"][plan["chunks"][1]["base_key"]]
        self.assertEqual(sorted(entry["takes"]), ["1", "2"])
        self.assertEqual(entry["takes"]["1"]["finish_class"], "truncated")
        self.assertEqual(entry["chosen"], 2)
        self.assertTrue(entry["auto_reroll"])
        ledger = [json.loads(x) for x in (out / "ledger.jsonl").read_text().splitlines()]
        self.assertEqual([e["result"] for e in ledger if e["chunk"] == "c002"], ["truncated", "ok"])
        again = self.js(self.cli("render", path, "--profile", "en-doc", "--out", out, "--json"))
        self.assertEqual(again["calls"], 0)
        more = self.js(self.cli("render", path, "--profile", "en-doc", "--out", out, "--only", "c001", "--takes", "2",
                                "--json"))
        self.assertEqual(more["calls"], 1)
        state = json.loads((out / "takes.json").read_text())
        first = state["chunks"][plan["chunks"][0]["base_key"]]
        self.assertEqual(sorted(first["takes"]), ["1", "2"])
        self.assertIn("best of 2", first["chosen_by"])

    def test_budget_guard_refuses_before_any_call(self):
        path = self.script("budget", "A new line that nobody has rendered before, about the tall ships.\n")
        before = len(self.fake.tts())
        r = self.cli("render", path, "--profile", "en-doc", "--out", self.tmp / "budget", "--budget", "0.00001",
                     ok=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("over the budget", r.stderr)
        self.assertEqual(len(self.fake.tts()), before)

    def test_daily_quota_stops_without_a_loop(self):
        path = self.script("quota", "The first quota line talks about green valleys and slow rivers.\n\n"
                                    "The second quota line talks about grey cliffs and cold seas.\n\n"
                                    "The third quota line talks about warm towns and busy streets.\n")
        self.fake.rules.append({"match": "quota line", "mode": "quota_day", "count": 99})
        before = len(self.fake.tts())
        try:
            r = self.cli("render", path, "--profile", "en-doc", "--out", self.tmp / "quota", ok=False)
        finally:
            self.fake.rules[-1]["count"] = 0
        self.assertEqual(r.returncode, 1)
        self.assertIn("midnight Pacific", r.stdout + r.stderr)
        texts = [e["text"] for e in self.fake.tts()[before:]]
        self.assertLessEqual(len(texts), 3)
        self.assertEqual(len(texts), len(set(texts)))                       # nobody asked twice

    def test_safety_block_is_reported_not_retried(self):
        path = self.script("safety", "This forbidden line will be refused by the service today.\n\n"
                                     "This other line about gentle hills is perfectly fine to say.\n")
        self.fake.rules.append({"match": "forbidden", "mode": "safety", "count": 5})
        before = len(self.fake.tts())
        r = self.cli("render", path, "--profile", "en-doc", "--out", self.tmp / "safety", ok=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("Rephrase", r.stdout + r.stderr)
        texts = [e["text"] for e in self.fake.tts()[before:]]
        self.assertEqual(sum("forbidden" in t for t in texts), 1)
        self.assertEqual(sum("gentle hills" in t for t in texts), 1)

    def test_a_moved_project_pays_nothing_on_a_new_machine(self):
        path = self.script("moved", "The ferry leaves the old pier at seven every single morning.\n")
        out = self.tmp / "moved"
        self.assertEqual(self.js(self.cli("render", path, "--profile", "en-doc", "--out", out, "--json"))["calls"], 1)
        old_home = os.environ["NEXA_SPEECH_HOME"]
        os.environ["NEXA_SPEECH_HOME"] = str(self.tmp / "home-elsewhere")          # an empty cache
        try:
            again = self.js(self.cli("render", path, "--profile", "en-doc", "--out", out, "--profiles",
                                     Path(old_home) / "profiles", "--json"))
        finally:
            os.environ["NEXA_SPEECH_HOME"] = old_home
        self.assertEqual(again["calls"], 0)
        key = next(p.stem for p in (out / "masters").glob("*.wav"))
        self.assertTrue((self.tmp / "home-elsewhere" / "cache" / f"{key}.wav").exists())
        side = json.loads((self.tmp / "home-elsewhere" / "cache" / f"{key}.json").read_text())
        self.assertEqual(side["model"], "gemini-3.8-flash-tts")

    def test_the_same_words_twice_are_paid_once(self):
        line = "Subscribe for a new story about the sea every single week of the year."
        path = self.script("twice", f"{line}\n\nThe middle paragraph says something else entirely today.\n\n{line}\n")
        out = self.tmp / "twice"
        res = self.js(self.cli("render", path, "--profile", "en-doc", "--out", out, "--json"))
        self.assertEqual(res["calls"], 2)
        plan = json.loads((out / "plan.json").read_text())
        self.assertEqual(plan["totals"]["requests"], 2)
        self.cli("master", out)
        man = json.loads((out / "vo.manifest.json").read_text())
        self.assertEqual(man["chunks"][0]["master"], man["chunks"][2]["master"])
        self.assertAlmostEqual(man["chunks"][0]["end"] - man["chunks"][0]["start"],
                               man["chunks"][2]["end"] - man["chunks"][2]["start"], delta=0.002)

    def test_render_refuses_warnings_until_forced(self):
        path = self.script("warn", "Find the full price list at www.example.com before you order today.\n")
        out = self.tmp / "warn"
        before = len(self.fake.tts())
        r = self.cli("render", path, "--profile", "en-doc", "--out", out, ok=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("render refuses warnings", r.stdout)
        self.assertIn("www.example.com", r.stdout)
        self.assertEqual(len(self.fake.tts()), before)
        self.cli("render", path, "--profile", "en-doc", "--out", out, "--force")
        self.assertEqual(len(self.fake.tts()), before + 1)

    def test_a_refusal_with_http_200_is_reported_and_not_kept(self):
        path = self.script("refused", "The refused line talks about a thing the filter dislikes today.\n")
        out = self.tmp / "refused"
        self.fake.rules.append({"match": "refused line", "mode": "blocked_200", "count": 1})
        r = self.cli("render", path, "--profile", "en-doc", "--out", out, ok=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("refused (SAFETY)", r.stdout)
        state = json.loads((out / "takes.json").read_text())
        self.assertEqual([len(e["takes"]) for e in state["chunks"].values()], [0])
        ledger = [json.loads(x) for x in (out / "ledger.jsonl").read_text().splitlines()]
        self.assertEqual(ledger[-1]["result"], "blocked")
        self.cli("render", path, "--profile", "en-doc", "--out", out)          # asked once more, by hand

    def test_audio_in_two_parts_is_joined(self):
        path = self.script("parts", "This answer arrives in two pieces that must become one clean take.\n")
        out = self.tmp / "parts"
        self.fake.rules.append({"match": "two pieces", "mode": "two_parts", "count": 1})
        self.cli("render", path, "--profile", "en-doc", "--out", out)
        state = json.loads((out / "takes.json").read_text())
        rec = next(iter(next(iter(state["chunks"].values()))["takes"].values()))
        with wave.open(str(out / rec["file"])) as w:
            frames = w.readframes(w.getnframes())
        pcm, _ = fake_speech(self.fake.tts()[-1]["text"], "Charon")
        self.assertEqual(frames, pcm)

    def test_server_error_is_waited_out_by_the_shared_module(self):
        path = self.script("server", "The weather station reports a calm and sunny afternoon ahead.\n")
        self.fake.rules.append({"match": "weather station", "mode": "server_once", "count": 1})
        out = self.tmp / "server"
        self.cli("render", path, "--profile", "en-doc", "--out", out)
        ledger = [json.loads(x) for x in (out / "ledger.jsonl").read_text().splitlines()]
        self.assertEqual(ledger[-1]["result"], "ok")
        self.assertEqual(ledger[-1]["attempts"], 2)

    def test_drift_noise_tail_and_asr_gates(self):
        path = self.script("drift", DRIFT_SCRIPT)
        out = self.tmp / "drift"
        self.fake.rules.append({"match": "copper", "mode": "loud", "count": 1})
        self.fake.rules.append({"match": "orchard", "mode": "noise_tail", "count": 1})
        res = self.js(self.cli("render", path, "--profile", "en-doc", "--out", out, "--json"))
        self.assertEqual([x["chunk"] for x in res["rerolls"]], ["c002"])
        self.assertIn("gate 5", res["rerolls"][0]["why"])
        qa = json.loads((out / "qa.json").read_text())
        rows = {r["chunk"]: r for r in qa["chunks"]}
        self.assertEqual(rows["c002"]["take"], 2)
        self.assertEqual(rows["c002"]["result"], "pass")
        self.assertTrue(any("noise after the last word" in f for f in rows["c003"]["flags"]))
        self.assertEqual(rows["c003"]["take"], 1)                           # a flag is fixed in master, no re-roll
        self.assertGreaterEqual(qa["references"]["en-doc"]["drift"]["n"], 5)
        cal = json.loads((out / "calibration.json").read_text())
        self.assertAlmostEqual(cal["profiles"]["en-doc"]["measured_wps"], 1 / WORD_S, delta=0.25)
        # gate 4: the recogniser drops the last word of one chunk
        self.fake.rules.append({"match": "meadow", "mode": "asr_drop_last", "count": 1})
        q = self.js(self.cli("qa", out, "--asr", "--json"))
        rows = {r["chunk"]: r for r in q["chunks"]}
        self.assertTrue(any("missing at the end" in f for f in rows["c004"]["fails"]), rows["c004"])
        self.assertEqual(rows["c001"]["result"], "pass")
        self.assertEqual(rows["c001"]["gates"]["4"], "pass")
        man = self.js(self.cli("master", out, "--json"))
        self.assertIn("c004", man["flagged"])
        m = json.loads((out / "vo.manifest.json").read_text())
        c3 = next(c for c in m["chunks"] if c["id"] == "c003")
        self.assertLess(c3["end"] - c3["start"], 13 * WORD_S + 0.1)          # the hiss is not part of the chunk

    def test_bangla_render_and_captions(self):
        self.cli("profile", "new", "bn-plain", "--preset", "bn-documentary-m")
        text = nfc("# শুরু\n১৯৭১ সালে দেশ স্বাধীন হয় । সেই বছর নদীর পাড়ে বহু মানুষ নতুন করে ঘর বাঁধে ।\n\n"
                   "আজ ২০২৬ সালে সেই গ্রামে প্রায় ১৫০০০০ মানুষ থাকে । তাদের গল্প আমরা ধীরে ধীরে শুনব ।\n")
        path = self.script("bangla", text)
        out = self.tmp / "bangla"
        self.cli("render", path, "--profile", "bn-plain", "--out", out)
        plan = json.loads((out / "plan.json").read_text())
        spoken = " ".join(c["spoken"] for c in plan["chunks"])
        for want in ("উনিশশো একাত্তর সালে", "দুই হাজার ছাব্বিশ সালে", "এক লাখ পঞ্চাশ হাজার"):
            self.assertIn(nfc(want), spoken)
        self.assertFalse(re.search("[0-9০-৯]", spoken))
        body = self.fake.tts()[-1]["body"]
        self.assertEqual(body["generation_config"]["speech_config"], [{"voice": "Sadaltager"}])  # no language code
        self.cli("master", out)
        self.cli("align", out, "--engine", "pauses")
        srt = (out / "vo.srt").read_text(encoding="utf-8")
        for block in srt.strip().split("\n\n"):
            for line in block.split("\n")[2:]:
                self.assertFalse(line.startswith("।"), line)
                self.assertLessEqual(S.graphemes(line), 42)
        words = json.loads((out / "words.json").read_text(encoding="utf-8"))
        self.assertIn(nfc("১৯৭১"), [w["w"] for w in words])                   # captions keep the digits

    def test_render_asr_rerolls_on_gate_4(self):
        path = self.script("asr", "The old mill turns slowly beside the stream in the green valley.\n\n"
                                  "The baker opens the shop before sunrise every single morning.\n")
        out = self.tmp / "asr"
        self.fake.rules.append({"match": "baker", "mode": "asr_drop_last", "count": 1})
        res = self.js(self.cli("render", path, "--profile", "en-doc", "--out", out, "--asr", "--json"))
        self.assertEqual([x["chunk"] for x in res["rerolls"]], ["c002"])
        self.assertIn("gate 4", res["rerolls"][0]["why"])
        qa = json.loads((out / "qa.json").read_text())
        rows = {r["chunk"]: r for r in qa["chunks"]}
        self.assertEqual(rows["c002"]["take"], 2)
        self.assertEqual(rows["c002"]["gates"]["4"], "pass")
        ledger = [json.loads(x) for x in (out / "ledger.jsonl").read_text().splitlines()]
        self.assertEqual(len([e for e in ledger if e["model"] == S.TRANSCRIBE_MODEL]), 3)

    def test_say_is_cached(self):
        out = self.tmp / "say" / "line.wav"
        r1 = self.js(self.cli("say", "The quick line is ready for the preview.", "--profile", "en-doc", "--out",
                              out, "--json"))
        self.assertEqual(r1["calls"], 1)
        self.assertTrue(out.exists())
        side = json.loads(out.with_suffix(".json").read_text())
        self.assertEqual(side["schema"], "nexa-speech/say-1")
        self.assertTrue((out.parent / "ledger.jsonl").exists())
        r2 = self.js(self.cli("say", "The quick line is ready for the preview.", "--profile", "en-doc", "--out",
                              out, "--json"))
        self.assertEqual(r2["calls"], 0)
        got = measure(out)
        self.assertLessEqual(abs(got["I"] + 16.0), 0.5)
        foreign = self.tmp / "say" / "mine.wav"
        foreign.write_bytes(b"not ours")
        r3 = self.cli("say", "Any line at all for this one.", "--profile", "en-doc", "--out", foreign, ok=False)
        self.assertIn("was not made by say", r3.stderr)
        self.assertEqual(foreign.read_bytes(), b"not ours")

    def test_audition_side_by_side(self):
        text = self.tmp / "aud.txt"
        text.write_text("A short line to compare two voices side by side.\n", encoding="utf-8")
        out = self.tmp / "aud"
        r = self.js(self.cli("audition", "--voices", "Charon,Kore", "--text", text, "--profile", "en-doc", "--out",
                             out, "--json"))
        self.assertEqual([f["voice"] for f in r["files"]], ["Charon", "Kore"])
        for f in r["files"]:
            self.assertTrue(Path(f["file"]).exists())
        self.assertTrue((out / "audition-all.wav").exists())
        long_text = self.tmp / "long.txt"
        long_text.write_text(" ".join(["word"] * 80) + ".\n", encoding="utf-8")
        bad = self.cli("audition", "--voices", "Charon", "--text", long_text, "--profile", "en-doc", "--out", out,
                       ok=False)
        self.assertIn("15 s or less", bad.stderr)

    def test_design_and_keep(self):
        out = self.tmp / "design"
        r = self.js(self.cli("design", "--desc", "Native Bangladeshi man in his thirties, warm baritone.", "--gender",
                             "male", "--lang", "bn-BD", "--takes", "2", "--out", out, "--json"))
        self.assertEqual(len(r["voices"]), 2)
        body = self.fake.kinds("design")[-1]["body"]
        self.assertEqual(body["voice"]["type"], "prompted")
        self.assertEqual(body["voice"]["language_code"], "bn-BD")
        self.assertTrue(body["store"])
        for v in r["voices"]:
            self.assertTrue(Path(v["sample"]).exists())
        vid = r["voices"][0]["id"]
        k = self.js(self.cli("design", "keep", vid, "--profile", "bn-yt", "--json"))
        self.assertEqual(k["voice"]["type"], "designed")
        self.assertEqual(k["version"], 2)
        shown = self.js(self.cli("profile", "show", "bn-yt", "--json"))["profile"]
        self.assertEqual(shown["voice"]["id"], vid)
        self.assertEqual(shown["voice"]["expire_time"], "2027-09-25T00:00:00Z")

    def test_voices_presets_doctor(self):
        v = self.js(self.cli("voices", "--gender", "f", "--json"))
        self.assertEqual(len(v["voices"]), 14)
        self.assertEqual(len(self.js(self.cli("voices", "--json"))["voices"]), 30)
        self.assertEqual(len(self.js(self.cli("presets", "--json"))["presets"]), 15)
        lib = self.js(self.cli("voices", "--library", "--lang", "bn-BD", "--json"))
        self.assertEqual({x["id"] for x in lib["voices"]}, {"voice_lib_bn_01", "voice_lib_bn_02"})
        doc = self.js(self.cli("doctor", "--json"))
        self.assertTrue(doc["ready"])
        self.assertEqual(doc["keys"], ["GEMINI_API_KEY"])
        live = self.js(self.cli("doctor", "--live", "--json"))
        self.assertTrue(live["live"]["ours"]["gemini-3.8-flash-tts"])
        self.assertFalse(live["live"]["ours"]["gemini-2.5-pro-preview-tts"])
        listed = self.js(self.cli("profile", "list", "--json"))
        self.assertIn("en-doc", [p["name"] for p in listed["profiles"]])

    def test_zy_fit_apply_failure_restores_the_master(self):
        import argparse
        import unittest.mock
        proj = self.tmp / "fit-fail"
        shutil.copytree(self.main, proj)
        before = (proj / "vo_48k.wav").read_bytes()
        man = json.loads((proj / "vo.manifest.json").read_text())
        cur = {r["scene"]: r["current_s"] for r in S.fit_plan(man, json.loads((proj / "plan.json").read_text()),
                                                               {}, False)["scenes"]}
        scenes = self.tmp / "scenes-fail.json"
        scenes.write_text(json.dumps([{"scene": "s1", "target_s": round(cur["s1"] + 0.4, 3)}]))
        args = argparse.Namespace(dir=str(proj), scenes=str(scenes), ad=False, apply=True, json=True)
        with unittest.mock.patch.object(S, "master_project", side_effect=S.ToolError("simulated failure")):
            with self.assertRaises(SystemExit):
                S.cmd_fit(args)
        self.assertEqual((proj / "vo_48k.wav").read_bytes(), before)
        self.assertTrue((proj / "vo.manifest.json").exists())
        if (self.main / "words.json").exists():
            self.assertTrue((proj / "words.json").exists())

    def test_zz_fit_apply_keeps_the_old_master(self):
        man = json.loads((self.main / "vo.manifest.json").read_text())
        cur = {r["scene"]: r["current_s"] for r in S.fit_plan(man, json.loads((self.main / "plan.json").read_text()),
                                                               {}, False)["scenes"]}
        scenes = self.tmp / "scenes.json"
        scenes.write_text(json.dumps([{"scene": "s1", "target_s": round(cur["s1"] + 0.4, 3)},
                                      {"scene": "s2", "target_s": round(cur["s2"] - 0.6, 3)}]))
        dry = self.js(self.cli("fit", self.main, "--scenes", scenes, "--json"))
        self.assertFalse(dry["applied"])
        r = self.js(self.cli("fit", self.main, "--scenes", scenes, "--apply", "--json"))
        self.assertTrue(r["applied"])
        self.assertTrue(any(k.startswith("vo_48k.before-fit-") for k in r["kept"]))
        self.assertTrue((self.main / "fit.json").exists())
        new = json.loads((self.main / "vo.manifest.json").read_text())
        self.assertIsNotNone(new["fit"])
        rows = {x["scene"]: x for x in r["plan"]["scenes"]}
        s1 = next(s for s in new["scenes"] if s["id"] == "s1")
        s2 = next(s for s in new["scenes"] if s["id"] == "s2")
        self.assertAlmostEqual(s2["start"] - s1["start"], rows["s1"]["new_s"], delta=0.06)
        got = measure(self.main / "vo_48k.wav")
        self.assertLessEqual(abs(got["I"] + 16.0), 0.5)

    def test_zzz_the_key_is_nowhere(self):
        for text in self.outputs:
            self.assertNotIn(FAKE_KEY, text)
        for path in self.tmp.rglob("*"):
            if path.is_file():
                self.assertNotIn(FAKE_KEY.encode(), path.read_bytes(), str(path))


if __name__ == "__main__":
    unittest.main()
