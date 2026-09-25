"""Offline tests for nexa-video-creator: the plan compiler's rules, and the pipeline on synthetic media.

python3 -m unittest discover -s ~/.claude/skills/nexa-video-creator/tests
The pipeline test needs ffmpeg (skipped without it); the sync check also needs the skill's venv (doctor --setup).
Set NVC_RENDER_TESTS=1 to also render stills (needs the renderer set up with doctor --setup).
"""
import json
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
import nvc_dsp  # noqa: E402  (snap needs no numpy)
import nvc_plan as P  # noqa: E402

PRESETS = json.loads((SCRIPTS / "presets.json").read_text())
HAVE_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def preset(name):
    return dict(PRESETS["targets"][name], name=name)


def make_words(spec):
    """spec: [(text, start, end)] -> words with ids."""
    return [{"id": "w%04d" % (i + 1), "text": t, "start": s, "end": e} for i, (t, s, e) in enumerate(spec)]


# a talk with a greeting, a filler bounded by pauses, a long pause and three sentences
SPEC = [("Hi", 1.00, 1.20), ("everyone.", 1.25, 1.80),
        ("Um", 2.40, 2.70),
        ("Today", 3.20, 3.50), ("I", 3.55, 3.60), ("show", 3.65, 3.95), ("you", 4.00, 4.15), ("sixty", 4.20, 4.55),
        ("two", 4.60, 4.80), ("percent", 4.85, 5.30), ("faster", 5.35, 5.80), ("edits.", 5.85, 6.40),
        ("First", 7.90, 8.20), ("open", 8.25, 8.50), ("the", 8.55, 8.65), ("folder.", 8.70, 9.20),
        ("Then", 9.60, 9.80), ("drag", 9.85, 10.10), ("your", 10.15, 10.30), ("clips.", 10.35, 10.90)]


def job_for(duration=12.0, screen_offset=0.5, cam_w=1920, cam_h=1080):
    return {"id": "t", "dialogue": "cam", "fps": 30, "language": "en",
            "sources": {"cam": {"kind": "camera", "duration": duration, "width": cam_w, "height": cam_h,
                                "proxy": "media/proxies/cam.mp4", "hasVideo": True},
                        "screen": {"kind": "screen_recording", "duration": duration + 2, "width": 1920,
                                   "height": 1080, "proxy": "media/proxies/screen.mp4",
                                   "sync": {"offset_s": screen_offset, "drift_ppm": None,
                                            "segments": [{"t_ref_from": 0, "t_ref_to": 1e9,
                                                          "offset_s": screen_offset, "drift_ppm": None}]}}}}


def quote(words, a, b):
    return " ".join(w["text"] for w in words[a - 1:b])


def base_plan(words):
    return {"schema": "nvc-plan/1", "title": "t",
            "segments": [{"words": ["w0004", "w0012"], "quote": quote(words, 4, 12), "layout": "camFull"},
                         {"words": ["w0013", "w0020"], "quote": quote(words, 13, 20), "layout": "screenPip"}]}


def compile_(plan, words, job=None, target="youtube"):
    return P.compile_plan(plan, words, job or job_for(), preset(target), PRESETS["overlays"], PRESETS["sfx_defaults"])


class PlanRules(unittest.TestCase):
    def setUp(self):
        self.words = make_words(SPEC)

    def test_quote_must_match_the_transcript(self):
        plan = base_plan(self.words)
        plan["segments"][0]["quote"] = "Today I show you seventy two percent faster edits."
        rep = compile_(plan, self.words)["report"]
        self.assertFalse(rep["ok"])
        self.assertTrue(any("sixty two percent" in e for e in rep["errors"]), rep["errors"])

    def test_unknown_word_id_is_an_error(self):
        plan = base_plan(self.words)
        plan["segments"][0]["words"] = ["w0004", "w0999"]
        rep = compile_(plan, self.words)["report"]
        self.assertTrue(any("unknown word id w0999" in e for e in rep["errors"]))

    def test_frame_grid_is_contiguous_and_exact(self):
        res = compile_(base_plan(self.words), self.words)
        self.assertTrue(res["report"]["ok"], res["report"])
        clips = res["edl"]["clips"]
        cursor = 0
        for c in clips:
            self.assertEqual(c["from"], cursor)
            self.assertIsInstance(c["durationInFrames"], int)
            cursor += c["durationInFrames"]
        self.assertEqual(cursor, res["edl"]["durationInFrames"])
        total = sum(p["frames"] for p in res["pieces"])
        self.assertEqual(total, cursor)

    def test_long_pause_is_trimmed_and_padding_kept(self):
        res = compile_(base_plan(self.words), self.words)
        pieces = res["pieces"]
        # the 1.5 s gap between the segments is a cut; the first piece keeps 50 ms before "Today" (frame-rounded)
        self.assertLessEqual(pieces[0]["masterIn"], 3.20 - 0.05 + 1e-6)
        self.assertGreater(pieces[0]["masterIn"], 3.20 - 0.05 - 1 / 30.0)
        self.assertGreaterEqual(pieces[0]["masterOut"], 6.40 + 0.08 - 1e-6)
        out = res["mapped_words"]
        firsts = [m for m in out if m["id"] == "w0013"]
        lasts = [m for m in out if m["id"] == "w0012"]
        gap = firsts[0]["start"] - lasts[0]["end"]
        self.assertLess(gap, 0.3, "the pause between segments should be short after the cut")

    def test_bounded_filler_is_cut_automatically(self):
        words = self.words
        plan = {"schema": "nvc-plan/1", "segments": [{"words": ["w0001", "w0012"], "quote": quote(words, 1, 12)}]}
        res = compile_(plan, words)
        self.assertTrue(res["report"]["ok"], res["report"])
        self.assertNotIn("w0003", [m["id"] for m in res["mapped_words"]])
        self.assertTrue(any(d["kind"] == "cut_filler" and d.get("auto") for d in res["report"]["decisions"]))

    def test_every_word_lands_inside_its_clip(self):
        res = compile_(base_plan(self.words), self.words)
        fps = res["edl"]["fps"]
        clips = res["edl"]["clips"]
        for m in res["mapped_words"]:
            c = clips[m["piece"]]
            self.assertGreaterEqual(m["start"], c["from"] / fps - 1e-6)
            self.assertLessEqual(m["end"], (c["from"] + c["durationInFrames"]) / fps + 1e-6)

    def test_numbers_on_screen_must_be_said(self):
        self.assertEqual(P.numbers_in("sixty two percent"), {62.0})
        self.assertEqual(P.numbers_in("৬২% এবং 1,200"), {62.0, 1200.0})
        plan = base_plan(self.words)
        plan["overlays"] = [{"type": "stat", "words": ["w0008", "w0010"], "quote": "sixty two percent",
                             "props": {"value": "62%", "label": "faster edits"}}]
        rep = compile_(plan, self.words)["report"]
        self.assertTrue(rep["ok"], rep)
        self.assertEqual(rep["review"], [])
        plan["overlays"][0]["props"]["value"] = "72%"
        rep = compile_(plan, self.words)["report"]
        self.assertTrue(any("72" in r for r in rep["review"]), rep["review"])
        # a hook placed at the start may show a number the speaker says later in the edit
        plan["overlays"] = [{"type": "hook", "at": "start", "seconds": 3, "props": {"text": "62% faster"}}]
        rep = compile_(plan, self.words)["report"]
        self.assertEqual(rep["review"], [])
        plan["overlays"][0]["props"]["text"] = "80% faster"
        rep = compile_(plan, self.words)["report"]
        self.assertTrue(any("80" in r and "anywhere in the edit" in r for r in rep["review"]), rep["review"])

    def test_overlay_gets_its_reading_time_and_slots_do_not_collide(self):
        plan = base_plan(self.words)
        plan["overlays"] = [{"type": "stat", "words": ["w0008", "w0008"], "quote": "sixty",
                             "props": {"value": "60", "label": "a label that takes some time to read on screen"}}]
        res = compile_(plan, self.words)
        o = res["edl"]["overlays"][0]
        text = "60 a label that takes some time to read on screen"
        self.assertGreaterEqual(o["durationInFrames"] / 30.0 + 1e-6, P.reading_time(text) + 1.0 - 0.05)
        plan["overlays"].append({"type": "list", "words": ["w0009", "w0010"], "quote": "two percent",
                                 "props": {"items": ["a", "b"]}})
        rep = compile_(plan, self.words)["report"]
        self.assertTrue(any("overlaps" in e for e in rep["errors"]), rep)

    def test_word_caption_pages(self):
        plan = base_plan(self.words)
        plan["captions"] = {"style": "word", "emphasis": ["w0010"]}
        res = compile_(plan, self.words, target="shorts")
        pages = res["edl"]["captions"]["pages"]
        self.assertTrue(pages)
        for a, b in zip(pages, pages[1:]):
            self.assertLessEqual(a["endMs"], b["startMs"])
        self.assertTrue(all(len(p["tokens"]) <= 3 for p in pages))
        flagged = [t for p in pages for t in p["tokens"] if t["emphasis"]]
        self.assertEqual([t["text"].strip() for t in flagged], ["percent"])

    def test_bengali_cues_never_start_a_line_with_the_danda(self):
        spec = [("আমরা", 1.0, 1.3), ("আজ", 1.35, 1.6), ("দেখব", 1.65, 2.0), ("কীভাবে", 2.05, 2.5), ("ভিডিও", 2.55, 2.9),
                ("এডিট", 2.95, 3.2), ("করতে", 3.25, 3.5), ("হয়", 3.55, 3.7), ("।", 3.7, 3.72), ("প্রথমে", 4.2, 4.6),
                ("ফোল্ডার", 4.65, 5.0), ("খুলুন", 5.05, 5.4), ("।", 5.4, 5.42)]
        words = make_words(spec)
        plan = {"schema": "nvc-plan/1", "language": "bn",
                "segments": [{"words": ["w0001", "w0013"], "quote": quote(words, 1, 13)}]}
        res = compile_(plan, words)
        self.assertTrue(res["report"]["ok"], res["report"])
        for cue in res["cues"]:
            for line in cue["lines"]:
                self.assertFalse(line.startswith("।"), cue)
            self.assertGreaterEqual(cue["end"] - cue["start"], 0.83 - 1e-6)
        srt = P.srt(res["cues"])
        self.assertRegex(srt, r"^1\n00:00:00,\d{3} --> 00:00:\d\d,\d{3}\n")

    def test_layout_falls_back_when_the_screen_does_not_cover(self):
        plan = base_plan(self.words)
        res = compile_(plan, self.words, job=job_for(screen_offset=-9.0))
        self.assertEqual(res["edl"]["clips"][-1]["layout"], "camFull")
        self.assertTrue(any("does not cover" in w for w in res["report"]["warnings"]))

    def test_vertical_target_stacks_screen_and_camera(self):
        res = compile_(base_plan(self.words), self.words, target="shorts")
        self.assertIn("stack", [c["layout"] for c in res["edl"]["clips"]])

    def test_auto_punch_respects_the_source_resolution(self):
        words = self.words
        plan = {"schema": "nvc-plan/1", "segments": [{"words": ["w0004", "w0020"], "quote": quote(words, 4, 20),
                                                      "layout": "camFull"}]}
        res = compile_(plan, words)
        punches = [c["punch"] for c in res["edl"]["clips"]]
        self.assertGreater(len(punches), 1)
        self.assertEqual(punches[0], 1.0)
        self.assertAlmostEqual(punches[1], 1.15, places=2)
        res = compile_(plan, words, target="shorts")
        self.assertTrue(all(p == 1.0 for p in (c["punch"] for c in res["edl"]["clips"])))

    def test_hook_and_length_rules(self):
        words = make_words([(t, s + 2.0, e + 2.0) for t, s, e in SPEC])
        plan = {"schema": "nvc-plan/1", "segments": [{"from": 0.0, "to": 13.0}]}
        res = compile_(plan, words, job=job_for(duration=13.0))
        self.assertTrue(any(w.startswith("hook") for w in res["report"]["warnings"]), res["report"])
        long_words = make_words([("word%d" % i, i * 1.0, i * 1.0 + 0.6) for i in range(300)])
        plan = {"schema": "nvc-plan/1", "segments": [{"words": ["w0001", "w0300"],
                                                      "quote": " ".join(w["text"] for w in long_words)}]}
        res = compile_(plan, long_words, job=job_for(duration=301.0), target="shorts")
        self.assertTrue(any("limit of 180" in e for e in res["report"]["errors"]), res["report"])

    def test_default_sound_effects_are_thinned(self):
        plan = base_plan(self.words)
        plan["overlays"] = [{"type": "keyword", "words": ["w%04d" % i, "w%04d" % i],
                             "quote": self.words[i - 1]["text"], "props": {"text": "x"}} for i in (4, 6)]
        plan["sfx"] = [{"at": "word:w0007", "name": "ding"}]
        res = compile_(plan, self.words, target="shorts")
        names = [c["name"] for c in res["sfx"]]
        self.assertIn("ding", names)
        times = sorted(c["t"] for c in res["sfx"] if c["why"] != "plan")
        for a, b in zip(times, times[1:]):
            self.assertGreaterEqual(b - a, 1.0 - 1e-6)

    def test_chapters_start_at_zero(self):
        words = self.words
        plan = base_plan(words)
        plan["chapters"] = [{"words": ["w0004", "w0005"], "quote": "Today I", "title": "Why"},
                            {"words": ["w0013", "w0014"], "quote": "First open", "title": "How"}]
        res = compile_(plan, words)
        self.assertEqual(res["chapters"][0]["t"], 0)
        self.assertTrue(any("3 or more" in w for w in res["report"]["warnings"]))
        self.assertIn("00:00 Why", P.chapters_txt(res["chapters"]))

    def test_uningested_source_is_an_error(self):
        job = job_for()
        job["sources"]["broll1"] = {"kind": "broll", "duration": 5.0, "width": 1920, "height": 1080}
        plan = base_plan(self.words)
        plan["overlays"] = [{"type": "broll", "words": ["w0014", "w0016"], "quote": quote(self.words, 14, 16),
                             "source": "broll1"}]
        rep = compile_(plan, self.words, job=job)["report"]
        self.assertTrue(any("no proxy yet" in e for e in rep["errors"]), rep)
        job2 = job_for()
        job2["sources"]["cam"].pop("proxy")
        res = compile_(base_plan(self.words), self.words, job=job2)
        self.assertTrue(all(c["cam"] is None for c in res["edl"]["clips"]))

    def test_zoom_overlap_is_caught_per_layer(self):
        plan = base_plan(self.words)
        plan["zooms"] = [
            {"words": ["w0013", "w0020"], "quote": quote(self.words, 13, 20), "layer": "screen", "scale": 1.5},
            {"words": ["w0014", "w0014"], "quote": "open", "layer": "cam", "scale": 1.2},
            {"words": ["w0015", "w0016"], "quote": "the folder.", "layer": "screen", "scale": 1.8}]
        rep = compile_(plan, self.words)["report"]
        self.assertTrue(any("overlaps z001 on the screen layer" in e for e in rep["errors"]), rep)

    def test_subtitle_cues_never_overlap(self):
        words = make_words([("word%d" % i, 1.0 + i * 0.25, 1.0 + i * 0.25 + 0.24) for i in range(60)])
        plan = {"schema": "nvc-plan/1", "segments": [{"words": ["w0001", "w0060"], "quote": quote(words, 1, 60)}]}
        cues = compile_(plan, words, job=job_for(duration=20.0))["cues"]
        self.assertGreater(len(cues), 1)
        for a, b in zip(cues, cues[1:]):
            self.assertLessEqual(a["end"], b["start"] - 2 / 30.0 + 1e-6)

    def test_word_captions_do_not_double_punctuation(self):
        words = make_words([("Hello", 1.0, 1.4), (".", 1.4, 1.42), ("Next", 2.0, 2.4), ("line", 2.45, 2.8),
                            (".", 2.8, 2.82)])
        plan = {"schema": "nvc-plan/1", "segments": [{"words": ["w0001", "w0005"], "quote": quote(words, 1, 5)}],
                "captions": {"style": "word"}}
        res = compile_(plan, words, job=job_for(duration=4.0), target="shorts")
        srt = P.srt(res["cues"])
        self.assertIn("Hello.", srt)
        self.assertNotIn("..", srt)
        self.assertNotIn(" .", srt)
        tokens = [t["text"].strip() for pg in res["edl"]["captions"]["pages"] for t in pg["tokens"]]
        self.assertEqual(tokens, ["Hello.", "Next", "line."])

    def test_hold_on_the_last_word_extends_the_tail(self):
        plan = base_plan(self.words)
        plain = compile_(plan, self.words)["pieces"][0]["masterOut"]
        plan["holds"] = [{"words": ["w0012", "w0012"], "quote": "edits.", "seconds": 0.8}]
        held = compile_(plan, self.words)["pieces"][0]["masterOut"]
        self.assertGreater(held, plain + 0.5)

    def test_vertical_subtitles_use_narrower_lines(self):
        res = compile_(base_plan(self.words), self.words, target="shorts")
        self.assertTrue(all(P.graphemes(line) <= 32 for c in res["cues"] for line in c["lines"]))

    def test_pack_transcript_and_finders(self):
        lines = P.pack_transcript(self.words)
        self.assertTrue(lines[0].startswith("[w0001-w0002] 1.00-1.80"))
        fillers = P.find_fillers(self.words)
        self.assertEqual([f["id"] for f in fillers if f["kind"] == "filled_pause"], ["w0003"])
        retake_words = make_words([("open", 1, 1.2), ("the", 1.25, 1.4), ("folder", 1.45, 1.9), ("open", 3, 3.2),
                                   ("the", 3.25, 3.4), ("folder", 3.45, 3.9)])
        self.assertEqual(len(P.find_retakes(retake_words)), 1)


def tone_speech(path, bursts, duration, rate=48000, delay=0.0, noise=0.0):
    """Syllable-shaped tone bursts (180 Hz with harmonics) at the given (start, end) times, as a mono WAV."""
    import random
    rnd = random.Random(7)
    n = int(duration * rate)
    frames = bytearray()
    for i in range(n):
        t = i / rate - delay
        v = 0.0
        for a, b in bursts:
            if a <= t < b:
                env = math.sin(math.pi * (t - a) / (b - a)) * (0.6 + 0.4 * math.sin(2 * math.pi * 5 * t) ** 2)
                v = env * (0.5 * math.sin(2 * math.pi * 180 * t) + 0.25 * math.sin(2 * math.pi * 360 * t)
                           + 0.12 * math.sin(2 * math.pi * 540 * t))
                break
        if noise:
            v += noise * (rnd.random() * 2 - 1)
        frames += struct.pack("<h", int(max(-1.0, min(1.0, v)) * 30000))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(frames))


@unittest.skipUnless(HAVE_FFMPEG, "ffmpeg is not installed")
class Snapping(unittest.TestCase):
    """Word edges moved to the measured pauses (nvc_dsp.snap)."""

    @staticmethod
    def words(*items):
        return [{"text": t, "start": a, "end": b} for t, a, b in items]

    def test_a_breath_in_a_pause_never_becomes_a_word(self):
        # the first live Bangla test (2026-09-25): a breath at 2.60 to 2.74 s between two sentences; the old rule
        # put আজ on the breath and দেখাবো on আজ
        w = self.words(("আছেন?", 1.8, 2.1), ("আজ", 3.0, 3.3), ("দেখাবো", 3.3, 3.7), ("ক্যামেরার", 3.7, 4.2))
        runs = [[1.21, 2.12], [2.6, 2.74], [3.03, 3.71], [3.83, 5.84]]
        out = nvc_dsp.snap(w, runs)
        self.assertEqual((out[0]["end"], out[1]["start"]), (2.12, 3.03))
        self.assertEqual(out[0]["pause_after"], 0.91)                  # the breath is inside the pause
        self.assertEqual((out[2]["end"], out[3]["start"]), (3.71, 3.83))

    def test_a_short_word_between_two_pauses_keeps_both(self):
        w = self.words(("so", 0.0, 1.0), ("and", 1.2, 1.35), ("then", 1.6, 2.5))
        out = nvc_dsp.snap(w, [[0.0, 1.02], [1.18, 1.36], [1.58, 2.5]])
        self.assertEqual([(x["start"], x["end"]) for x in out], [(0.0, 1.02), (1.18, 1.36), (1.58, 2.5)])

    def test_the_first_word_skips_a_breath_before_it(self):
        w = self.words(("hello", 0.9, 1.3), ("there", 1.3, 1.8))
        out = nvc_dsp.snap(w, [[0.3, 0.45], [0.88, 1.82]])
        self.assertEqual((out[0]["start"], out[-1]["end"]), (0.88, 1.82))


class BanglaDigits(unittest.TestCase):
    def test_numbers_in_bangla_speech_use_bengali_digits(self):
        sys.path.insert(0, str(SCRIPTS))
        import nvc
        words = [{"text": t, "start": i, "end": i + 0.5} for i, t in enumerate(
            ["কিভাবে", "10", "সেকেন্ডে", "মাসে", "500", "টাকার", "নতুন", "iPhone", "15", "কিনুন", "4K"])]
        got = [w["text"] for w in nvc.bangla_digits(words)]
        self.assertEqual(got, ["কিভাবে", "১০", "সেকেন্ডে", "মাসে", "৫০০", "টাকার", "নতুন", "iPhone", "15", "কিনুন",
                               "4K"])
        self.assertEqual(words[1]["text"], "10")                      # the input is left alone


class SpeechImport(unittest.TestCase):
    def test_a_bangla_voice_over_keeps_its_language(self):
        # nexa-speech keeps the language per profile; the first live run labelled a Bangla voice-over "en"
        sys.path.insert(0, str(SCRIPTS))
        import nvc
        with tempfile.TemporaryDirectory() as tmp:
            d, vo = Path(tmp) / "job", Path(tmp) / "vo" / "vo_48k.wav"
            (d / "analysis").mkdir(parents=True)
            vo.parent.mkdir()
            (vo.parent / "words.json").write_text(json.dumps(
                [{"w": "আসসালামু", "start": 0.1, "end": 0.47}, {"w": "আলাইকুম,", "start": 0.47, "end": 0.8}]),
                encoding="utf-8")
            (vo.parent / "vo.manifest.json").write_text(json.dumps(
                {"schema": "nexa-speech/manifest-1", "main_profile": "bn-test",
                 "profiles": {"bn-test": {"model": "gemini-3.8-flash-tts", "language": "bn-BD"}}}),
                encoding="utf-8")
            self.assertEqual(nvc.import_speech_words(d, vo, "vo", "en"), 2)
            words = json.loads((d / "analysis" / "words.json").read_text(encoding="utf-8"))
            self.assertEqual(words["language"], "bn")
            self.assertEqual([w["id"] for w in words["words"]], ["w0001", "w0002"])


SCENE_SENTENCES = ["Most people quit learning to edit halfway through.",
                   "Step one: practise for ten minutes every day.",
                   "Get one percent better every day for a year.",
                   "The first month you barely notice it at all.",
                   "Day one and day three hundred sixty five differ.",
                   "Start today and subscribe for more."]


class Scenes(unittest.TestCase):
    """Designed full-frame scenes: what the compiler fills in for the renderer, and what it refuses."""

    def setUp(self):
        spec, t = [], 0.3
        self.spans = []
        for s in SCENE_SENTENCES:
            first = len(spec) + 1
            for w in s.split():
                d = 0.16 + 0.04 * len(w)
                spec.append((w, round(t, 3), round(t + d, 3)))
                t += d + 0.08
            self.spans.append((first, len(spec)))
            t += 0.4
        self.words = make_words(spec)
        self.job = {"id": "v", "dialogue": "vo", "fps": 30, "language": "en",
                    "sources": {"vo": {"kind": "voice", "duration": t + 1.0, "audio": "media/audio/vo.wav"}}}

    def g(self, i):
        a, b = self.spans[i]
        return {"words": ["w%04d" % a, "w%04d" % b], "quote": quote(self.words, a, b)}

    def plan(self, overlays, lang="en"):
        return {"schema": "nvc-plan/1", "title": "t", "language": lang,
                "segments": [dict(self.g(i), layout="voiceOnly") for i in range(len(SCENE_SENTENCES))],
                "overlays": overlays}

    def test_scenes_get_lines_labels_events_and_sounds(self):
        growth = [round(1.01 ** d, 3) for d in range(0, 366, 73)]
        r = compile_(self.plan([
            dict(self.g(0), type="kinetic", props={"text": "Most people quit learning to edit halfway through",
                                                   "highlight": "halfway"}),
            dict(self.g(1), type="step", props={"n": 1, "title": "Practise ten minutes a day"}),
            dict(self.g(2), type="bigStat", props={"title": "Get 1% better every day", "value": "37.8x",
                                                   "series": growth}, facts=[{"text": "37.8x", "origin": "formula"}]),
            dict(self.g(3), type="bars", props={"rows": [{"label": "1 week", "value": 1.07},
                                                         {"label": "1 year", "value": 37.8, "text": "37.8x"}]},
                 facts=[{"text": "1.07 37.8x", "origin": "formula"}]),
            dict(self.g(5), type="endCard", props={"text": "Start today"})]), self.words, self.job)
        self.assertTrue(r["report"]["ok"], r["report"]["errors"])
        ov = {o["type"]: o for o in r["edl"]["overlays"]}
        self.assertEqual(ov["kinetic"]["props"]["lines"], ["Most people quit learning", "to edit halfway through"])
        self.assertTrue(ov["kinetic"]["props"]["hideCaptions"])                # the words are on screen already
        st = ov["step"]
        self.assertEqual((st["props"]["label"], st["props"]["numText"], st["enter"], st["slot"]),
                         ("Step 1", "1", "sweep", "full"))
        self.assertEqual(st["props"]["lines"], ["Practise", "ten minutes a day"])   # a number stays with its word
        self.assertEqual(ov["bigStat"]["enter"], "slide")
        bt = ov["bars"]["props"]["t"]
        self.assertEqual(bt["focus"], 1)                                          # the largest value
        self.assertEqual(bt["land"], bt["start"] + bt["step"] + int(math.floor(bt["len"] * 1.8 + 0.5)))
        ec = ov["endCard"]["props"]
        self.assertEqual((ec["button"], ec["pressed"]), ("Subscribe", "Subscribed"))
        cues = {(c["name"], int(round(c["t"] * 30))) for c in r["sfx"]}
        self.assertIn(("ding", ov["bigStat"]["from"] + ov["bigStat"]["props"]["t"]["land"]), cues)
        self.assertIn(("ding", ov["bars"]["from"] + bt["land"]), cues)
        self.assertIn(("click", ov["endCard"]["from"] + ec["t"]["click"]), cues)
        self.assertEqual(r["edl"]["theme"]["backdrop"], "paper")                  # nothing filmed: warm paper
        self.assertFalse(any(o["props"].get("pip") for o in r["edl"]["overlays"]))
        self.assertTrue(r["edl"]["speech"] and all(b > a for a, b in r["edl"]["speech"]))

    def test_bangla_labels_and_buttons(self):
        r = compile_(self.plan([dict(self.g(1), type="step", props={"n": 2, "title": "যা বানালেন, শেয়ার করুন"}),
                                dict(self.g(5), type="endCard", props={"text": "আজ থেকেই শুরু করুন"})], lang="bn"),
                     self.words, self.job)
        self.assertTrue(r["report"]["ok"], r["report"]["errors"])
        ov = {o["type"]: o for o in r["edl"]["overlays"]}
        self.assertEqual((ov["step"]["props"]["label"], ov["step"]["props"]["numText"]), ("ধাপ ২", "২"))
        self.assertEqual(ov["endCard"]["props"]["button"], "সাবস্ক্রাইব করুন")
        self.assertEqual(r["edl"]["theme"]["displayBn"], "AnekBangla")

    def test_scene_props_are_checked(self):
        r = compile_(self.plan([
            dict(self.g(0), type="bars", props={"rows": [{"label": "only", "value": 1}]}),
            dict(self.g(1), type="step", props={"n": "one", "title": "x"}),
            dict(self.g(2), type="versus", props={"left": {"label": "A"}, "right": "B"}),
            dict(self.g(3), type="kinetic", props={"text": "The first month"}, enter="spin")]), self.words, self.job)
        errors = " ".join(r["report"]["errors"])
        for needle in ("props.rows needs 2 to 6 rows", "props.n must be", "props.left needs", "enter must be one of"):
            self.assertIn(needle, errors)

    def test_scenes_in_a_row_leave_no_gap(self):
        r = compile_(self.plan([dict(self.g(i), type="kinetic", props={"text": SCENE_SENTENCES[i].rstrip(".")})
                                for i in range(3)]), self.words, self.job)
        self.assertTrue(r["report"]["ok"], r["report"]["errors"])
        ov = r["edl"]["overlays"]
        for a, b in zip(ov, ov[1:]):
            self.assertEqual(a["from"] + a["durationInFrames"], b["from"])       # no backdrop flash between

    def test_scene_transitions_are_heard(self):
        r = compile_(self.plan([dict(self.g(i), type="step", props={"n": i + 1, "title": "Part"})
                                for i in range(3)]), self.words, self.job)
        names = [c["name"] for c in r["sfx"]]
        self.assertEqual(names.count("whoosh"), 3)            # sweeps 3 s apart: each heard (long-form keeps 4 s
        self.assertEqual(names.count("pop"), 3)               # between other default cues)

    def test_a_trimmed_scene_still_lands_inside_itself(self):
        r = compile_(self.plan([
            dict(self.g(2), type="bigStat", props={"title": "Get one percent better every single day for a whole year",
                                                   "value": "37.8x", "label": "better after a year of small steps"},
                 facts=[{"text": "37.8x", "origin": "formula"}]),
            dict(self.g(3), type="kinetic", props={"text": "The first month you barely notice it at all"})]),
            self.words, self.job)
        self.assertTrue(r["report"]["ok"], r["report"]["errors"])
        st = r["edl"]["overlays"][0]
        self.assertTrue(any(d.get("kind") == "trim_overlay" for d in r["report"]["decisions"]))   # it was cut short
        self.assertLess(st["props"]["t"]["land"], st["durationInFrames"])
        self.assertIn(("ding", st["from"] + st["props"]["t"]["land"]),
                      {(c["name"], int(round(c["t"] * 30))) for c in r["sfx"]})

    def test_axis_labels_are_checked_like_other_numbers(self):
        r = compile_(self.plan([dict(self.g(2), type="bigStat", props={
            "value": "37.8x", "series": [1, 2, 37.8], "xLabels": ["Today", "revenue 4.2M"]},
            facts=[{"text": "37.8x", "origin": "formula"}])]), self.words, self.job)
        self.assertTrue(any("4.2" in q for q in r["report"]["review"]), r["report"]["review"])

    def test_title_lines(self):
        self.assertEqual(P.balance_lines("Get 1% better every day", 16), ["Get 1% better", "every day"])
        self.assertEqual(P.balance_lines("প্রতিদিন ১০ মিনিট অনুশীলন", 16), ["প্রতিদিন", "১০ মিনিট অনুশীলন"])
        self.assertEqual(P.balance_lines("Share what you made", 20), ["Share what you made"])
        self.assertEqual(P.title_lines(["kept", "as written"], "step", False), ["kept", "as written"])

    def test_the_presenter_shows_over_a_scene_with_a_camera_under_it(self):
        words = make_words(SPEC)
        plan = {"schema": "nvc-plan/1", "title": "t",
                "segments": [{"words": ["w0004", "w0012"], "quote": quote(words, 4, 12), "layout": "camFull"},
                             {"words": ["w0013", "w0020"], "quote": quote(words, 13, 20), "layout": "camFull"}],
                "overlays": [{"type": "bigStat", "words": ["w0004", "w0012"], "quote": quote(words, 4, 12),
                              "props": {"value": "62%", "label": "faster edits"}},
                             {"type": "step", "words": ["w0013", "w0016"], "quote": quote(words, 13, 16),
                              "props": {"n": 1, "title": "Open the folder"}}]}
        r = compile_(plan, words)
        self.assertTrue(r["report"]["ok"], r["report"]["errors"])
        ov = {o["type"]: o for o in r["edl"]["overlays"]}
        self.assertTrue(ov["bigStat"]["props"]["pip"])
        self.assertFalse(ov["step"]["props"]["pip"])                  # a step card is a short full stop
        self.assertEqual(r["edl"]["theme"]["backdrop"], "pools")


VOX_SENTENCES = ["Oil prices jumped to 116 dollars a barrel",
                 "and the debt grew bigger than the whole economy",
                 "Empires end with a bill they cannot pay"]


class Vox(unittest.TestCase):
    """Vox-style beats: elements timed to words, placed by slots, checked like an editor would."""

    def setUp(self):
        spec, t = [], 0.3
        self.spans = []
        for s in VOX_SENTENCES:
            first = len(spec) + 1
            for w in s.split():
                d = 0.16 + 0.04 * len(w)
                spec.append((w, round(t, 3), round(t + d, 3)))
                t += d + 0.08
            self.spans.append((first, len(spec)))
            t += 0.4
        self.words = make_words(spec)
        self.job = {"id": "v", "dialogue": "vo", "fps": 30, "language": "en",
                    "sources": {"vo": {"kind": "voice", "duration": t + 1.0, "audio": "media/audio/vo.wav"},
                                "ship": {"kind": "cutout", "image": "media/cutouts/ship.png", "width": 1200,
                                         "height": 500, "alpha": True},
                                "man": {"kind": "cutout", "image": "media/cutouts/man.png", "width": 900,
                                        "height": 1200, "alpha": True},
                                "photo": {"kind": "image", "image": "media/originals/photo.jpg", "width": 1280,
                                          "height": 853},
                                "fire": {"kind": "broll", "proxy": "media/keyed/fire.webm", "width": 1280,
                                         "height": 720, "alpha": True, "duration": 8.0}}}

    def w(self, text, n=0):
        """The id of a word by its text (the n-th match)."""
        hits = [x["id"] for x in self.words if x["text"].strip(".,") == text]
        return hits[n]

    def g(self, i):
        a, b = self.spans[i]
        return {"words": ["w%04d" % a, "w%04d" % b], "quote": quote(self.words, a, b)}

    def plan(self, overlays, **extra):
        return dict({"schema": "nvc-plan/1", "title": "t", "language": "en",
                     "segments": [{"words": ["w0001", "w%04d" % len(self.words)],
                                   "quote": quote(self.words, 1, len(self.words)), "layout": "voiceOnly"}],
                     "overlays": overlays}, **extra)

    def frame_of(self, r, wid):
        m = next(x for x in r["mapped_words"] if x["id"] == wid)
        return int(round(m["start"] * r["edl"]["fps"]))

    def test_times_places_sounds_and_the_look(self):
        r = compile_(self.plan([
            dict(self.g(0), type="vox", elements=[
                {"id": "ship", "kind": "cutout", "source": "ship", "at": "start"},
                {"id": "price", "kind": "tag", "value": "$116", "from": 25, "unit": "per barrel", "icon": "barrel",
                 "at": self.w("jumped"), "land": self.w("116"), "follow": "ship", "dx": 0.2, "dy": -0.5}]),
            dict(self.g(1), type="vox", elements=[
                {"id": "man", "kind": "cutout", "source": "man", "slot": "stage-left", "at": self.w("debt")},
                {"id": "big", "kind": "headline", "text": "Bigger than the economy", "at": self.w("bigger")}]),
            dict(self.g(2), type="vox", elements=[
                {"id": "type", "kind": "typewriter", "text": "Empires end with a bill they cannot pay",
                 "at": self.w("Empires")},
                {"id": "fire", "kind": "clip", "source": "fire", "x": 0.5, "y": 1.0, "anchor": "bottom", "w": 0.3,
                 "at": self.w("bill")}])],
            progress_bar="bottom"), self.words, self.job)
        self.assertTrue(r["report"]["ok"], r["report"]["errors"])
        edl = r["edl"]
        vox = [o for o in edl["overlays"] if o["type"] == "vox"]
        self.assertEqual(len(vox), 3)
        a, b, c = vox
        # beats in a row share the paper: no gap, a hard cut by default (no tail), elements vanish at the cut
        self.assertEqual(a["from"] + a["durationInFrames"], b["from"])
        self.assertEqual(a["props"]["tail"], 0)
        self.assertTrue(all(e["exit"] == "cut" and e["out"] == a["durationInFrames"] for e in a["props"]["elements"]))
        els = {e["id"]: e for o in vox for e in o["props"]["elements"]}
        # a bare word id lands the entrance just before the word; a counter lands 2 frames before its number
        self.assertEqual(a["from"] + els["price"]["at"], self.frame_of(r, self.w("jumped")) - 8)
        self.assertEqual(a["from"] + els["price"]["land"], self.frame_of(r, self.w("116")) - 2)
        self.assertEqual(b["from"] + els["man"]["at"], self.frame_of(r, self.w("debt")) - 13)
        # slots: a grounded cut-out stands a little under the bottom edge, sized by its height
        self.assertAlmostEqual(els["man"]["y"], 1.04)
        self.assertEqual(els["man"]["anchor"], "bottom")
        self.assertAlmostEqual(els["man"]["w"], round(0.8 * 1080 * (900 / 1200.0) / 1920, 3))
        self.assertEqual(els["big"]["enter"], "wipe")
        # the typewriter types each word as it is said, and the captions give way to it
        first, last = self.spans[2]
        self.assertEqual([c["from"] + t for t in els["type"]["times"]],
                         [self.frame_of(r, "w%04d" % i) for i in range(first, last + 1)])
        words = VOX_SENTENCES[2].split()
        self.assertTrue(c["props"]["hideCaptions"])
        # sounds: the counter's ding on its number, a key for every typed word, quieter than the presets
        cues = [x for x in r["sfx"] if x["why"].startswith("vox")]
        self.assertTrue(any(x["name"] == "ding" and abs(x["t"] * 30 - (a["from"] + els["price"]["land"])) < 1
                            for x in cues))
        self.assertEqual(sum(1 for x in cues if x["name"] == "key"), len(words))
        self.assertTrue(all(x["gain_db"] is not None and x["gain_db"] <= -9 for x in cues))
        # the Vox look on a faceless video, and the thick bar along the bottom
        self.assertEqual(edl["theme"]["accent"], "#FF8900")
        self.assertEqual(edl["theme"]["marker"], "#E04329")
        self.assertEqual(edl["theme"]["backdrop"], "grid")
        self.assertEqual(edl["progress"], "bottom")

    def test_what_it_refuses_and_asks(self):
        r = compile_(self.plan([
            dict(self.g(0), type="vox", elements=[
                {"kind": "hologram", "at": "start"},
                {"kind": "cutout", "source": "nothere"},
                {"kind": "label", "text": "It costs 300 dollars", "at": self.w("barrel")},
                {"kind": "label", "text": "late", "at": self.w("Empires")}]),
            dict(self.g(1), type="vox", elements=[
                {"kind": "newspaper", "masthead": "The Paper", "headline": "Debt beats the economy",
                 "marks": [{"text": "whole economy", "at": self.w("economy")}]},
                {"kind": "chart", "series": [{"values": [1, 2, 3]}], "at": "start"}])]),
            self.words, self.job)
        errors = "\n".join(r["report"]["errors"])
        review = "\n".join(r["report"]["review"])
        self.assertIn("kind must be one of", errors)
        self.assertIn("needs \"source\"", errors)
        self.assertIn("is not spoken inside this beat", errors)
        self.assertIn("mark \"whole economy\" is not in the headline", errors)
        self.assertIn("never put words in a real outlet's mouth", review)
        self.assertIn("the chart plots 3 values", review)
        self.assertIn("shows 300", review)

    def test_text_stays_in_the_safe_area_and_clear_of_other_text(self):
        r = compile_(self.plan([
            dict(self.g(0), type="vox", elements=[
                {"id": "edge", "kind": "label", "text": "Far over on the right", "x": 0.99, "y": 0.5,
                 "at": "start"},
                {"id": "one", "kind": "label", "text": "First line here", "x": 0.4, "y": 0.3, "at": "start"},
                {"id": "two", "kind": "label", "text": "Second line here", "x": 0.42, "y": 0.31, "at": "start"}])]),
            self.words, self.job)
        els = {e["id"]: e for e in r["edl"]["overlays"][0]["props"]["elements"]}
        self.assertLess(els["edge"]["x"], 0.99)
        self.assertTrue(any(d["kind"] == "vox_nudge" for d in r["report"]["decisions"]))
        self.assertTrue(any("overlaps two" in w for w in r["report"]["warnings"]), r["report"]["warnings"])

    def test_vertical_slots_and_exits(self):
        r = compile_(self.plan([
            dict(self.g(0), type="vox", exit="drop", elements=[
                {"id": "man", "kind": "cutout", "source": "man", "at": "start"},
                {"id": "head", "kind": "headline", "text": "Oil", "at": "start"},
                {"id": "gone", "kind": "cutout", "source": "ship", "x": 0.3, "y": 0.4, "anchor": "center",
                 "at": "start", "out": self.w("barrel")}]),
            dict(self.g(1), type="vox", elements=[{"kind": "label", "text": "Debt", "at": "start"}])]),
            self.words, self.job, target="shorts")
        self.assertTrue(r["report"]["ok"], r["report"]["errors"])
        a = r["edl"]["overlays"][0]
        els = {e["id"]: e for e in a["props"]["elements"]}
        self.assertAlmostEqual(els["head"]["y"], 0.18)                     # text in the top half of a short
        self.assertAlmostEqual(els["man"]["w"], round(0.4 * 1920 * 0.75 / 1080, 3))
        # a beat that hands over with a drop runs on under the next while its pictures fall away
        self.assertEqual(a["props"]["tail"], 12)
        self.assertEqual(els["man"]["exit"], "drop")
        # leaving mid-beat goes off by the nearest side, not through the other pictures
        self.assertEqual(els["gone"]["exit"], "slideLeft")


class StockVerdict(unittest.TestCase):
    def c(self, **kw):
        base = {"subject": 4, "action": 4, "setting": 4, "people_market": None, "quality": 4, "framing": 4,
                "gates": {}}
        base.update(kw)
        return base

    def test_the_rubric_and_the_gates(self):
        sys.path.insert(0, str(SCRIPTS))
        import nvc
        self.assertEqual(nvc.stock_verdict(self.c())[0], "accept")
        self.assertEqual(nvc.stock_verdict(self.c(subject=3))[0], "near")               # subject must be 4
        self.assertEqual(nvc.stock_verdict(self.c(gates={"logo_or_brand": True}))[0], "reject")
        self.assertEqual(nvc.stock_verdict(self.c(gates={"identifiable_person": True, "sensitive_context": True}))[0],
                         "reject")                                                      # the licence's people rule
        self.assertEqual(nvc.stock_verdict(self.c(gates={"identifiable_person": True}), ad=True)[0], "human")
        self.assertEqual(nvc.stock_verdict(self.c(gates={"ai_look": True}), real_only=True)[0], "reject")
        v, score = nvc.stock_verdict(self.c(subject=4, action=4, setting=3, people_market=3, quality=3, framing=4),
                                     accept=0.70)
        self.assertEqual((v, round(score, 2)), ("accept", 0.72))                        # b-roll takes 0.70


@unittest.skipUnless(HAVE_FFMPEG, "needs ffmpeg")
class Stock(unittest.TestCase):
    """nvc.py stock against a fake Pixabay: search, filters, sheet, pick, licence record."""

    @classmethod
    def setUpClass(cls):
        import http.server
        import threading
        import urllib.parse
        cls.tmp = Path(tempfile.mkdtemp(prefix="nvc-stock-"))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=1",
                        "-frames:v", "1", str(cls.tmp / "thumb.jpg")], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=1920x1080:rate=25:duration=2",
                        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", str(cls.tmp / "clip.mp4")],
                       check=True)
        log = cls.log = []

        class H(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def send(self, code, data, ctype):
                self.send_response(code)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("X-RateLimit-Remaining", "99")
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                url = urllib.parse.urlparse(self.path)
                q = urllib.parse.parse_qs(url.query)
                log.append({"path": url.path, "q": q})
                base = "http://127.0.0.1:%d" % self.server.server_address[1]
                if url.path == "/api/videos/":
                    if q.get("key") != ["px-test"]:
                        return self.send(400, b"[ERROR 400] Invalid or missing API key", "text/plain")
                    hits = []
                    for i, (w, h, low, ai) in enumerate(((1920, 1080, False, False), (1280, 720, False, False),
                                                         (1920, 1080, True, False), (3840, 2160, False, True))):
                        hits.append({"id": 100 + i, "pageURL": "https://pixabay.com/videos/id-%d/" % (100 + i),
                                     "type": "film", "tags": "laptop, typing, keyboard", "duration": 12,
                                     "user": "maker%d" % i, "user_id": i, "isLowQuality": low, "isAiGenerated": ai,
                                     "videos": {"large": {"url": base + "/files/clip.mp4", "width": w, "height": h,
                                                          "size": 900000, "thumbnail": base + "/files/thumb.jpg"},
                                                "tiny": {"url": base + "/files/clip.mp4", "width": 640, "height": 360,
                                                         "size": 90000, "thumbnail": base + "/files/thumb.jpg"}}})
                    body = json.dumps({"total": 4, "totalHits": 4, "hits": hits}).encode()
                    return self.send(200, body, "application/json")
                if url.path.startswith("/files/"):
                    return self.send(200, (cls.tmp / url.path.split("/")[-1]).read_bytes(),
                                     "video/mp4" if url.path.endswith(".mp4") else "image/jpeg")
                return self.send(404, b"no route", "text/plain")

        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.env = dict(os.environ, NVC_HOME=str(cls.tmp / "home"), NEXA_NO_KEYCHAIN="1", PIXABAY_API_KEY="px-test",
                       NEXA_PIXABAY_BASE_URL="http://127.0.0.1:%d" % cls.server.server_address[1],
                       NEXA_PIXABAY_CACHE=str(cls.tmp / "cache"))

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def nvc(self, *args):
        r = subprocess.run([sys.executable, str(SCRIPTS / "nvc.py")] + [str(a) for a in args], capture_output=True,
                           text=True, env=self.env, timeout=600)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r

    def test_search_filters_sheet_and_pick(self):
        job = self.tmp / "job"
        self.nvc("new", job, "--target", "youtube", "--title", "Stock test")
        r = self.nvc("stock", job, "laptop typing", "--also", "hands on keyboard", "--n", 8, "--no-ai")
        self.assertNotIn("px-test", r.stdout + r.stderr)                     # the key never shows
        cand = json.loads((job / "media" / "stock" / "laptop-typing" / "candidates.json").read_text())
        ids = [it["id"] for it in cand["items"]]
        self.assertEqual(ids, [100, 101])                  # low quality and AI-made left out, 1080p fills first
        self.assertEqual([it["fills_frame"] for it in cand["items"]], [True, False])
        self.assertEqual(cand["skipped"], {"low quality": 1, "AI-made": 1, "too short": 0})
        searches = [x for x in self.log if x["path"] == "/api/videos/"]
        self.assertEqual(len(searches), 2)                                   # the query and one variant
        self.assertEqual(searches[0]["q"]["safesearch"], ["true"])
        self.assertEqual(searches[0]["q"]["min_width"], ["1920"])
        self.assertTrue((job / "media" / "stock" / "laptop-typing" / "sheet.png").exists())
        again = len(self.log)
        self.nvc("stock", job, "laptop typing", "--also", "hands on keyboard", "--n", 8, "--no-ai")
        self.assertEqual(len([x for x in self.log[again:] if x["path"] == "/api/videos/"]), 0)   # 24 h cache
        self.nvc("stock", job, "--pick", 100, "--id", "broll-typing")
        side = json.loads((job / "media" / "stock" / "pixabay-100.mp4.json").read_text())
        self.assertEqual(side["page_url"], "https://pixabay.com/videos/id-100/")
        self.assertEqual(side["licence"]["name"], "Pixabay Content License")
        jobj = json.loads((job / "job.json").read_text())
        self.assertEqual(jobj["sources"]["broll-typing"]["role"], "broll")
        self.assertIn("100", jobj["stock"])
        sys.path.insert(0, str(SCRIPTS))
        import nvc
        notes = nvc.disclosure_notes(job, jobj)
        self.assertIn("https://pixabay.com/videos/id-100/ by maker0", notes)

    def test_deliver_checks_the_clean_dialogue_too(self):
        sys.path.insert(0, str(SCRIPTS))
        import nvc
        job = self.tmp / "credits-job"
        (job / "audio" / "youtube").mkdir(parents=True, exist_ok=True)
        self.assertEqual(nvc.credit_roots(job, "youtube"), [job / "audio" / "youtube"])
        (job / "media" / "audio").mkdir(parents=True, exist_ok=True)
        self.assertEqual(nvc.credit_roots(job, "youtube"), [job / "audio" / "youtube", job / "media" / "audio"])

    def test_sheet_without_swift_keeps_every_number_in_place(self):
        import unittest.mock
        sys.path.insert(0, str(SCRIPTS))
        import nvc
        items = [{"n": i + 1, "thumb": str(self.tmp / "thumb.jpg") if i != 1 else None, "caption": "c%d" % i}
                 for i in range(3)]
        out = self.tmp / "fallback.png"
        with unittest.mock.patch.object(nvc, "compile_swift", return_value=None):
            self.assertEqual(nvc.stock_sheet(items, out), out)
        size = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0",
                               str(out)], capture_output=True, text=True).stdout.strip()
        self.assertEqual(size, "1440,270")                                   # three cells, none dropped

        def cell_is_flat(k):                         # the missing preview is one grey, a real one is not
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(out), "-vf", "crop=480:270:%d:0,format=gray"
                                  % (480 * k), "-f", "rawvideo", "-"], capture_output=True).stdout
            return max(raw) - min(raw) < 8
        self.assertEqual([cell_is_flat(k) for k in range(3)], [False, True, False])


class Pipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="nvc-test-"))
        cls.words = make_words(SPEC)
        bursts = [(w["start"], w["end"]) for w in cls.words]
        tone_speech(cls.tmp / "cam.wav", bursts, 12.0)
        tone_speech(cls.tmp / "screen.wav", bursts, 13.5, delay=1.25, noise=0.01)
        for name, size, dur in (("cam", "1280x720", 12.0), ("screen", "1280x720", 13.5)):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                            "testsrc2=size=%s:rate=30:duration=%s" % (size, dur), "-i", str(cls.tmp / (name + ".wav")),
                            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac",
                            "-shortest", str(cls.tmp / (name + ".mp4"))], check=True)
        cls.job = cls.tmp / "job"
        cls.env = dict(os.environ, NVC_HOME=str(cls.tmp / "home"), CLAUDE_SKILLS_DIR=str(cls.tmp / "no-skills"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def nvc(self, *args, ok=True):
        r = subprocess.run([sys.executable, str(SCRIPTS / "nvc.py")] + [str(a) for a in args], capture_output=True,
                           text=True, env=self.env, timeout=900)
        if ok:
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r

    def test_pipeline(self):
        self.nvc("new", self.job, "--target", "youtube", "--title", "Pipeline test")
        self.nvc("add", self.job, self.tmp / "cam.mp4", "--role", "camera")
        self.nvc("add", self.job, self.tmp / "screen.mp4", "--role", "screen")
        self.nvc("ingest", self.job, "--no-faces")
        job = json.loads((self.job / "job.json").read_text())
        self.assertEqual(job["dialogue"], "cam")
        for sid in ("cam", "screen"):
            self.assertTrue((self.job / job["sources"][sid]["proxy"]).exists())
        venv = SCRIPTS.parent / ".venv" / "bin" / "python3"
        if venv.exists():
            self.nvc("sync", self.job)
            job = json.loads((self.job / "job.json").read_text())
            self.assertAlmostEqual(job["sources"]["screen"]["sync"]["offset_s"], 1.25, delta=0.01)
        else:
            self.nvc("sync", self.job, "--set", "screen=1.25")
        (self.job / "analysis").mkdir(exist_ok=True)
        (self.job / "analysis" / "words.json").write_text(json.dumps(
            {"schema": "nvc-words/1", "source": "cam", "language": "en", "engine": "test", "words": self.words}))
        self.nvc("brief", self.job)
        brief = (self.job / "edit-brief.md").read_text()
        self.assertIn("[w0004-w0012]", brief)
        self.assertIn("w0003 \"Um\"", brief)
        plan = base_plan(self.words)
        plan["overlays"] = [{"type": "hook", "at": "start", "props": {"text": "Faster edits"}}]
        (self.job / "plan.json").write_text(json.dumps(plan))
        r = self.nvc("compile", self.job)
        self.assertIn("edit:", r.stdout)
        edl = json.loads((self.job / "out" / "youtube" / "edl.json").read_text())
        self.nvc("audio", self.job, "--no-music", "--no-sfx")
        dialogue = self.job / "audio" / "youtube" / "dialogue.wav"
        got = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                    str(dialogue)], capture_output=True, text=True).stdout.strip())
        self.assertAlmostEqual(got, edl["durationInFrames"] / 30.0, delta=0.002)
        mix = self.job / "audio" / "youtube" / "mix.wav"
        self.assertTrue(mix.exists())
        report = json.loads((self.job / "audio" / "youtube" / "audio.json").read_text())
        self.assertLess(abs(report["measured"]["I"] - (-14.0)), 1.0, report)
        edl = json.loads((self.job / "out" / "youtube" / "edl.json").read_text())
        self.assertEqual(edl["audio"], "audio/youtube/mix.wav")
        self.assertTrue((self.job / "out" / "youtube" / "captions.srt").read_text().startswith("1\n"))
        if os.environ.get("NVC_RENDER_TESTS") == "1":
            env = dict(self.env)
            env.pop("NVC_HOME")
            r = subprocess.run([sys.executable, str(SCRIPTS / "nvc.py"), "stills", str(self.job), "--frames", "5,60"],
                               capture_output=True, text=True, env=env, timeout=900)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue((self.job / "out" / "youtube" / "stills.png").exists())

    def test_shared_module_copies_are_identical(self):
        repo = SCRIPTS.parent.parent
        for module in ("gemini_api.py", "elevenlabs_api.py"):
            copies = [p for p in (repo / "nexa-speech" / "scripts" / module,
                                  repo / "nexa-sound" / "scripts" / module) if p.exists()]
            mine = (SCRIPTS / module).read_bytes()
            for p in copies:
                self.assertEqual(p.read_bytes(), mine, "%s differs from nexa-video-creator's copy" % p)


if __name__ == "__main__":
    unittest.main()
