"""Offline tests for agy-watch-video. No network and no real agy: a fake agy stands in for the engine.

Run: python3 -m unittest discover -s ~/.claude/skills/agy-watch-video/tests
"""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

TMP = tempfile.mkdtemp(prefix="awv-test-")
os.environ["AGY_WATCH_CACHE"] = str(Path(TMP) / "cache")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import watch_video as w  # noqa: E402

HAVE_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))

FAKE_AGY = textwrap.dedent(r'''
    #!/usr/bin/env python3
    import json, os, sys
    args = sys.argv[1:]
    mode = os.environ.get("FAKE_AGY_MODE", "ok")
    log = os.environ.get("FAKE_AGY_LOG")
    if log:
        with open(log, "a") as f:
            f.write(json.dumps(args) + "\n")
    if args[:1] == ["models"]:
        print("gemini-3.8-flash-high\tGemini 3.8 Flash (High)\ngemini-3.1-pro-high\tGemini 3.1 Pro (High)")
        sys.exit(0)
    if mode == "empty":
        print("jetski: no output produced")
        sys.exit(0)
    env = {"conversation_id": "x", "status": "SUCCESS", "response": "", "duration_seconds": 1.5,
           "usage": {"input_tokens": 100, "output_tokens": 10}}
    schema_text = open(args[args.index("--json-schema") + 1]).read() if "--json-schema" in args else ""
    state = os.environ.get("FAKE_AGY_STATE")
    if mode == "deny_once":
        mode = "ok" if state and os.path.exists(state) else "denied_cmd"
        if state:
            open(state, "a").close()
    if mode == "deny_neutral":
        mode = "denied_cmd" if '"question"' in schema_text and '"short_answer"' not in schema_text else "ok"
    if mode == "denied":
        env["denied_actions"] = [{"action": "read_file", "display_name": "ViewFile"}]
    elif mode == "denied_cmd":
        env["denied_actions"] = [{"action": "command", "display_name": "RunCommand"}]
    elif mode == "replay":
        with open(os.environ["FAKE_AGY_REPLAY"]) as f:
            rec = json.load(f)["cases"][os.environ["FAKE_AGY_CASE"]]["outputs"]
        key = os.path.basename(args[args.index("--json-schema") + 1]).split("-")[0] + ":" + args[args.index("--model") + 1]
        if key in rec:
            env["structured_output"] = rec[key]
        else:
            env["status"] = "ERROR"
            env["error"] = "no recorded output for " + key
    elif mode == "error":
        env["status"] = "ERROR"
        env["error"] = "429 RESOURCE_EXHAUSTED"
    else:
        schema = {}
        if "--json-schema" in args:
            with open(args[args.index("--json-schema") + 1]) as f:
                schema = json.load(f)
        def fill(sc):
            t = sc.get("type")
            if sc.get("enum"):
                return sc["enum"][0]
            if t == "object":
                return {k: fill(v) for k, v in (sc.get("properties") or {}).items()}
            if t == "array":
                return []
            if t == "boolean":
                return True
            if t in ("number", "integer"):
                return 1
            return "x"
        out = fill(schema) if schema else {}
        if "short_answer" in out:
            out.update({"answer": "a black hose", "short_answer": "a black hose", "found": True, "confidence": "high"})
        if "question" in out:
            out["question"] = "What, if anything, is he holding?"
        if mode == "closer" and "look_closer" in out:
            out["look_closer"] = [{"t": 1.0, "what": "What is in the hand?", "x": 0.4, "y": 0.4, "w": 0.1, "h": 0.1}]
        if mode == "closer" and "items" in out and '"seen"' in schema_text:
            out["items"] = [{"t": 1.0, "asked": "What is in the hand?", "seen": "a hand holding a black hose",
                             "answer": "a black hose", "clear": True}]
        env["structured_output"] = out
    print("notice: something first")
    print(json.dumps(env))
''').lstrip()


def make_fake_agy() -> Path:
    p = Path(TMP) / "fake-agy"
    p.write_text(FAKE_AGY)
    p.chmod(p.stat().st_mode | stat.S_IXUSR)
    return p


class TimeTests(unittest.TestCase):
    def test_parse_ts_forms(self):
        self.assertEqual(w.parse_ts("12.5"), 12.5)
        self.assertEqual(w.parse_ts("12.5s"), 12.5)
        self.assertEqual(w.parse_ts("0:12.5"), 12.5)
        self.assertEqual(w.parse_ts("1:02:03"), 3723.0)
        self.assertEqual(w.parse_ts(7), 7.0)
        self.assertIsNone(w.parse_ts("soon"))
        self.assertIsNone(w.parse_ts(True))

    def test_fmt_ts(self):
        self.assertEqual(w.fmt_ts(3.04), "0:03.0")
        self.assertEqual(w.fmt_ts(75.25), "1:15.2")
        self.assertEqual(w.fmt_ts(3725), "1:02:05.0")
        self.assertEqual(w.fmt_ts(None), "?")

    def test_srt_times_round_up_cleanly(self):
        self.assertEqual(w._srt_ts(1.9996), "00:00:02,000")
        self.assertEqual(w._srt_ts(3661.5), "01:01:01,500")


class AlignTests(unittest.TestCase):
    ONSETS = [0.0, 0.616, 3.019, 5.797, 9.022, 11.157, 12.281]

    def test_late_model_times_snap_to_the_right_onsets(self):
        # Measured on 2026-09-24: Gemini said 0, 3.8, 7.2, 10.2 for sentences that start at 0, 3.0, 5.8, 9.0.
        starts, shift = w.align_starts([0.0, 3.8, 7.2, 10.2], self.ONSETS)
        self.assertEqual(starts, [0.0, 3.02, 5.8, 9.02])
        self.assertGreater(shift, 0.5)

    def test_exact_times_stay(self):
        starts, shift = w.align_starts([0.0, 3.0, 6.0, 9.0], self.ONSETS)
        self.assertEqual(starts, [0.0, 3.02, 5.8, 9.02])
        self.assertEqual(shift, 0.0)

    def test_order_is_kept_and_missing_values_pass_through(self):
        starts, _ = w.align_starts([0.0, None, 3.1], self.ONSETS)
        self.assertEqual(starts[1], None)
        self.assertEqual(starts[2], 3.02)

    def test_no_onsets_changes_nothing(self):
        self.assertEqual(w.align_starts([1.0, 2.0], []), ([1.0, 2.0], 0.0))


class AgreementTests(unittest.TestCase):
    def test_same_object_different_words(self):
        self.assertTrue(w.answers_agree({"found": True, "short_answer": "a black hose"},
                                        {"found": True, "short_answer": "black cable, cord, or hose"}))

    def test_nothing_against_something(self):
        self.assertFalse(w.answers_agree({"found": True, "short_answer": "nothing"},
                                         {"found": True, "short_answer": "a black hose"}))

    def test_two_nothings_agree(self):
        self.assertTrue(w.answers_agree({"found": True, "short_answer": "Hands by his sides, holding nothing"},
                                        {"found": True, "short_answer": "Touching car, swinging arms; holding nothing"}))

    def test_digits_in_any_script_agree(self):
        # Measured: Pro wrote Bengali digits, Flash wrote Latin ones, for the same phone numbers.
        self.assertTrue(w.answers_agree({"found": True, "short_answer": "49.00s, ০১৭০০-১২৩৪৫৬ and ০১৯০০-৬৫৪৩২১"},
                                        {"found": True, "short_answer": "49.00s; 01700-123456 and 01900-654321"}))
        self.assertFalse(w.answers_agree({"found": True, "short_answer": "০১৭০০-১২৩৪৫৬"},
                                         {"found": True, "short_answer": "01800-111222"}))

    def test_different_counts_and_colours_disagree(self):
        """Found in review: half the words in common used to be enough."""
        self.assertFalse(w.answers_agree({"found": True, "short_answer": "3 people"}, {"found": True, "short_answer": "4 people"}))
        self.assertTrue(w.answers_agree({"found": True, "short_answer": "three people"}, {"found": True, "short_answer": "3 people"}))
        self.assertFalse(w.answers_agree({"found": True, "short_answer": "a red car"}, {"found": True, "short_answer": "a blue car"}))
        self.assertFalse(w.answers_agree({"found": True, "short_answer": "01700-123456"},
                                         {"found": True, "short_answer": "01700-123455"}))

    def test_bengali_words_stay_whole(self):
        self.assertEqual(w.tokens("সবুজ বাগান"), ["সবুজ", "বাগান"])
        self.assertTrue(w.answers_agree({"found": True, "short_answer": "সবুজ বাগান"},
                                        {"found": True, "short_answer": "সাইনে লেখা সবুজ বাগান"}))

    def test_found_mismatch(self):
        self.assertFalse(w.answers_agree({"found": True, "short_answer": "yes"}, {"found": False, "short_answer": "yes"}))

    def test_word_forms_and_different_halves_of_the_answer(self):
        """Measured live: Pro and Flash described the same walk-off in different words and was called a disagreement."""
        a = {"found": True, "short_answer": "fills tire and carries a black hose"}
        b = {"found": True, "short_answer": "Stands, walks away, carrying a black hose"}
        self.assertEqual(w.agreement_state(a, b, "What does the mechanic do, and what is he carrying?"), "agree")
        self.assertEqual(w._stem("carrying"), w._stem("carries"))
        self.assertEqual(w._stem("running"), "run")
        self.assertEqual(w._stem("filling"), "fill")

    def test_unsure_goes_to_a_fact_check(self):
        a = {"found": True, "short_answer": "a man and a woman"}
        b = {"found": True, "short_answer": "2 people"}
        self.assertEqual(w.agreement_state(a, b, "Who is at the counter?"), "unsure")
        # but a question that asks for the number needs it from both
        self.assertEqual(w.agreement_state(a, b, "How many people are at the counter?"), "disagree")

    def test_times_compare_with_a_tolerance(self):
        self.assertEqual(w.agreement_state({"found": True, "short_answer": "at 2.5 s"},
                                           {"found": True, "short_answer": "at 2.8s"}), "agree")
        self.assertEqual(w.agreement_state({"found": True, "short_answer": "the logo at 2 s"},
                                           {"found": True, "short_answer": "the logo at 5 s"}), "disagree")
        self.assertEqual(w.agreement_state({"found": True, "short_answer": "logo at 0:12"},
                                           {"found": True, "short_answer": "logo at 12.3 seconds"}), "agree")

    def test_nothing_else_is_not_a_nothing_answer(self):
        self.assertEqual(w.agreement_state({"found": True, "short_answer": "a black hose, nothing else"},
                                           {"found": True, "short_answer": "a black hose"}), "agree")
        self.assertEqual(w.agreement_state({"found": True, "short_answer": "he is not carrying anything"},
                                           {"found": True, "short_answer": "a black hose"}), "disagree")


class RegionTests(unittest.TestCase):
    def test_words(self):
        self.assertEqual(w.parse_region("left", 1000, 800), (0, 0, 500, 800))
        self.assertEqual(w.parse_region("lower-third", 1000, 900), (0, 594, 1000, 306))

    def test_fractions_and_pixels(self):
        self.assertEqual(w.parse_region("0.1,0.5,0.3,0.4", 1000, 800), (100, 400, 300, 320))
        self.assertEqual(w.parse_region("100,400,300,320", 1000, 800), (100, 400, 300, 320))

    def test_clamped_inside_the_frame(self):
        x, y, cw, ch = w.parse_region("0.9,0.9,0.5,0.5", 1000, 800)
        self.assertLessEqual(x + cw, 1000)
        self.assertLessEqual(y + ch, 800)

    def test_bad_region(self):
        with self.assertRaises(w.WatchError):
            w.parse_region("somewhere", 100, 100)


def grid(n, cols, rows, base=2, marks=None):
    """n frames of a cols x rows change grid at `base`, with {(frame, col, row): value}."""
    out = bytearray([base] * (n * cols * rows))
    for (k, c, r), val in (marks or {}).items():
        out[k * cols * rows + r * cols + c] = val
    return bytes(out)


T30 = [(k + 1) / 30 for k in range(300)]


class GridTests(unittest.TestCase):
    """The change grid: brief events between frames, appearances, movement and its track."""

    def test_a_blink_is_one_brief_event_with_a_frame_in_between(self):
        marks = {(k, 7, r): 60 for k in (40, 43) for r in (0, 1)}
        a = w.analyse_grid(grid(90, 8, 6, marks=marks), 8, 6, T30[:90])
        ev = [e for e in a["events"] if e["kind"] == "brief"]
        self.assertEqual(len(ev), 1)
        self.assertEqual((ev[0]["start"], ev[0]["end"]), (round(T30[40], 3), round(T30[43], 3)))
        self.assertTrue(T30[40] - 0.001 <= ev[0]["t"] < T30[43] - 0.01)      # a frame on which it shows
        self.assertEqual(w.region_words(ev[0]["region"]), "top right")

    def test_a_label_shown_for_a_second_pairs_up(self):
        marks = {(k, c, 5): 90 for k in (30, 60) for c in (5, 6)}
        a = w.analyse_grid(grid(120, 8, 6, marks=marks), 8, 6, T30[:120])
        ev = [e for e in a["events"] if e["kind"] == "brief"]
        self.assertEqual(len(ev), 1)
        self.assertAlmostEqual(ev[0]["end"] - ev[0]["start"], 1.0, places=2)
        self.assertEqual(w.region_words(ev[0]["region"]), "bottom right")

    def test_something_that_appears_and_stays_is_a_step(self):
        a = w.analyse_grid(grid(60, 8, 6, marks={(20, 3, 3): 80}), 8, 6, T30[:60])
        self.assertEqual([e["kind"] for e in a["events"]], ["step"])

    def test_weak_changes_are_not_events(self):
        a = w.analyse_grid(grid(60, 8, 6, marks={(20, 3, 3): 14, (23, 3, 3): 14}), 8, 6, T30[:60])
        self.assertEqual(a["events"], [])

    def test_a_camera_move_lifts_every_cell_and_is_no_event(self):
        marks = {(k, c, r): 40 for k in range(20, 26) for c in range(8) for r in range(6)}
        self.assertEqual(w.analyse_grid(grid(60, 8, 6, marks=marks), 8, 6, T30[:60])["events"], [])

    def test_movement_has_a_track_and_a_pop_up_beside_it_stays_its_own_event(self):
        marks = {(k, min(7, k // 12), 3): 22 for k in range(90)}         # one cell further every 12 frames
        marks.update({(50, 6, 3): 95, (53, 6, 3): 95})                     # a strong pop-up two cells ahead
        a = w.analyse_grid(grid(90, 8, 6, marks=marks), 8, 6, T30[:90])
        kinds = sorted(e["kind"] for e in a["events"])
        self.assertEqual(kinds, ["brief", "motion"])
        near = w.activity_near(a, 1.0, 1.2)
        self.assertTrue(near and near[0] <= 0.3 < near[2])

    def test_fast_blinking_in_one_place_is_a_flicker_with_a_frame(self):
        """Found in review: blinks less than 0.3 s apart joined into one long cluster and were called movement."""
        marks = {(k, 2, 2): 60 for k in (10, 13, 20, 23, 30, 33)}
        a = w.analyse_grid(grid(60, 8, 6, marks=marks), 8, 6, T30[:60])
        self.assertEqual([e["kind"] for e in a["events"]], ["flicker"])
        e = a["events"][0]
        self.assertTrue(T30[10] - 0.001 <= e["t"] < T30[13] - 0.01)        # while it shows the first time
        pr = {"duration": 2.0, "video": {"width": 1280, "height": 720}, "audio": None}
        p = w.plan_watch(pr, {"video": {"activity": a}}, "standard", "general", None, True)
        self.assertIn(e["t"], p["detail_times"])

    def test_a_band_along_the_edge_is_no_close_up(self):
        act = {"bin": 0.25, "events": [{"kind": "motion", "start": 0, "end": 2, "peak": 40,
                                        "track": [[0.5, 0.0, 0.0, 0.9, 0.15, 40]]}]}
        self.assertIsNone(w.activity_near(act, 0.3, 0.7))

    def test_seek_time_lands_on_the_frame(self):
        self.assertEqual(w.seek_time(71 / 30), 2.366)
        self.assertEqual(w.seek_time(2.4), 2.399)
        self.assertEqual(w.seek_time(0.0), 0.0)

    def test_grid_shape_follows_the_picture(self):
        self.assertEqual(w.grid_dims(1920, 1080), (32, 18))
        self.assertEqual(w.grid_dims(1080, 1920), (18, 32))
        self.assertEqual(w.activity_step(30, 60), 1)
        self.assertEqual(w.activity_step(30, 3600), 3)


class PlanTests(unittest.TestCase):
    PR = {"duration": 8.0, "video": {"width": 1080, "height": 840}, "audio": {"codec": "aac"}}

    def test_quick_has_no_frames_but_audio(self):
        p = w.plan_watch(self.PR, {}, "quick", "general", None, False)
        self.assertEqual(p["detail_times"], [])
        self.assertTrue(p["audio"])
        self.assertFalse(p["review"])

    def test_standard_one_frame_a_second(self):
        p = w.plan_watch(self.PR, {}, "standard", "general", None, False)
        self.assertEqual(p["detail_times"], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 7.95])   # the last frame too
        self.assertEqual(p["detail_fps"], 1.0)

    def test_deep_two_a_second_and_text_check(self):
        p = w.plan_watch(self.PR, {}, "deep", "promo", None, True)
        self.assertEqual(len(p["detail_times"]), 17)
        self.assertTrue(p["text_check"])
        self.assertFalse(p["audio"])

    def test_long_video_is_covered_to_the_end(self):
        """Found in review: with more cuts than the budget, the frames used to stop at 2:55 of a 10-minute video."""
        pr = {"duration": 600.0, "video": {"width": 1920, "height": 1080}, "audio": None}
        cuts = [10.0 * i for i in range(1, 60)]
        p = w.plan_watch(pr, {"video": {"cuts": cuts}}, "standard", "general", None, False)
        self.assertLessEqual(len(p["detail_times"]), 36)
        self.assertGreater(max(p["detail_times"]), 590)
        self.assertLess(p["largest_gap_s"], 26)

    def test_brief_changes_get_their_own_frames_and_close_ups(self):
        act = {"bin": 0.25, "events": [
            {"kind": "brief", "start": 2.333, "end": 2.433, "t": 2.366, "region": [0.9, 0.05, 0.97, 0.17], "peak": 60},
            {"kind": "motion", "start": 0.0, "end": 8.0, "t": 4.0, "region": [0.1, 0.4, 0.8, 0.8], "peak": 30,
             "track": [[round(i * 0.25, 2), 0.1 + i * 0.02, 0.4, 0.18 + i * 0.02, 0.8, 30] for i in range(32)]}]}
        p = w.plan_watch(self.PR, {"video": {"activity": act}}, "standard", "general", None, False)
        self.assertIn(2.366, p["detail_times"])
        self.assertEqual(p["events"][0]["where"], "top right")
        self.assertEqual({c["why"] for c in p["closeups"]}, {"a brief change", "the moving area"})
        self.assertIn("brief change", p["sampling"])

    def test_brief_frames_never_exceed_the_budget(self):
        """Found in review: with --max-frames 2 a brief change came on top of the budget."""
        act = {"bin": 0.25, "events": [{"kind": "brief", "start": 2.3, "end": 2.4, "t": 2.366,
                                        "region": [0.9, 0.05, 0.97, 0.17], "peak": 60}]}
        for mf in (2, 3, 4):
            p = w.plan_watch(self.PR, {"video": {"activity": act}}, "standard", "general", None, True, max_frames=mf)
            self.assertLessEqual(len(p["detail_times"]), mf)
        self.assertIn(2.366, p["detail_times"])

    def test_busy_promo_sees_the_hook_and_the_end_card(self):
        pr = {"duration": 60.0, "video": {"width": 1080, "height": 1920}, "audio": None}
        cuts = [1.5 * i for i in range(1, 40)]
        p = w.plan_watch(pr, {"video": {"cuts": cuts}}, "standard", "promo", None, False)
        ts = p["detail_times"]
        self.assertLessEqual(len(ts), 36)
        self.assertGreaterEqual(sum(1 for t in ts if t <= 3.0), 3)       # the hook
        self.assertGreaterEqual(sum(1 for t in ts if t >= 57.0), 2)      # the end card
        self.assertLess(p["largest_gap_s"], 6)

    def test_cuts_are_kept_when_the_frames_fit(self):
        pr = {"duration": 10.0, "video": {"width": 640, "height": 360}, "audio": None}
        p = w.plan_watch(pr, {"video": {"cuts": [2.5, 6.5]}}, "standard", "general", None, False)
        self.assertIn(2.6, p["detail_times"])
        self.assertIn(6.6, p["detail_times"])

    def test_window(self):
        p = w.plan_watch(self.PR, {}, "standard", "general", (2.0, 5.0), False)
        self.assertEqual(p["detail_times"][0], 2.0)
        self.assertLessEqual(max(p["detail_times"]), 5.0)


class EnvelopeTests(unittest.TestCase):
    def test_notice_then_json(self):
        env = w.parse_envelope("jetski: note\n" + json.dumps({"status": "SUCCESS", "structured_output": {"a": 1}}))
        self.assertEqual(env["structured_output"], {"a": 1})

    def test_nested_result(self):
        self.assertEqual(w.parse_envelope(json.dumps({"result": {"status": "SUCCESS"}}))["status"], "SUCCESS")

    def test_garbage(self):
        self.assertIsNone(w.parse_envelope("nothing here"))

    def test_notice_with_a_brace_then_pretty_json(self):
        env = {"status": "SUCCESS", "structured_output": {"a": {"b": 1}}}
        out = "warning: unexpected token '{' in config\n" + json.dumps(env, indent=2)
        self.assertEqual(w.parse_envelope(out)["structured_output"], {"a": {"b": 1}})

    def test_json_from_text(self):
        self.assertEqual(w.json_from_text("```json\n{\"x\": 2}\n```"), {"x": 2})
        self.assertEqual(w.json_from_text("Here: {\"x\": 3} done"), {"x": 3})
        self.assertIsNone(w.json_from_text("no json"))


class SamplingTests(unittest.TestCase):
    CH_STATIC = {"bin": 0.25, "sum": [0.01] * 40, "max": [0.004] * 40}          # 10 s of a still picture
    CH_ACTION = {"bin": 0.25, "sum": [0.01] * 20 + [2.0] * 8 + [0.01] * 12, "max": [0.004] * 20 + [0.5] * 8 + [0.004] * 12}

    def test_change_between(self):
        s_, m_ = w.change_between(self.CH_ACTION, 5.0, 7.0)
        self.assertGreater(s_, 10)
        self.assertEqual(w.change_between(None, 0, 1), (None, None))

    def test_motion_weighted_times_crowd_the_action(self):
        ts = w.motion_times(0.0, 10.0, 10, self.CH_ACTION)
        self.assertGreaterEqual(sum(1 for t in ts if 5.0 <= t <= 7.0), 5)   # uniform spacing would put 2 there
        self.assertTrue(all(0.0 <= t <= 10.0 for t in ts))

    def test_still_frames_are_skipped_but_not_all(self):
        times = [float(i) for i in range(10)]
        kept, skipped = w.drop_static(times, {0.0}, self.CH_STATIC, "general", max_gap=4.0)
        self.assertGreater(skipped, 0)
        self.assertEqual(kept[0], 0.0)
        self.assertEqual(kept[-1], 9.0)
        self.assertTrue(all(b - a <= 4.0 for a, b in zip(kept, kept[1:])))

    def test_screen_goal_keeps_small_changes(self):
        ch = {"bin": 0.25, "sum": [0.03] * 40, "max": [0.01] * 40}
        kept, skipped = w.drop_static([float(i) for i in range(10)], {0.0}, ch, "screen", max_gap=4.0)
        self.assertEqual(skipped, 0)

    def test_plan_reports_sampling(self):
        pr = {"duration": 10.0, "video": {"width": 640, "height": 360}, "audio": None}
        p = w.plan_watch(pr, {"video": {"cuts": [], "change": self.CH_STATIC}}, "standard", "general", None, True)
        self.assertGreater(p["static_skipped"], 0)
        self.assertIn("skipped", p["sampling"])
        p2 = w.plan_watch(pr, {"video": {"cuts": []}}, "standard", "general", None, True, max_frames=4)
        self.assertLessEqual(len(p2["detail_times"]), 4)

    def test_model_times_outside_the_window_are_dropped(self):
        d = {"timeline": [{"t": 3.0, "what": "a"}, {"t": 99.0, "what": "b"}, {"t": 1.0, "what": "c"}]}
        self.assertEqual(w.drop_bad_times(d, 0.0, 8.0), 1)
        self.assertEqual([x["t"] for x in d["timeline"]], [1.0, 3.0])


class WindowTests(unittest.TestCase):
    def test_explicit_zero_counts(self):
        self.assertEqual(w.resolve_window(0.0, 5.0, 20.0), (0.0, 5.0))
        self.assertEqual(w.resolve_window(5.0, None, 20.0), (5.0, 20.0))
        with self.assertRaises(w.WatchError):
            w.resolve_window(5.0, 0.0, 20.0)

    def test_audio_cut_points_follow_the_pauses(self):
        cuts = w.audio_cut_points(700.0, 300.0, [{"start": 290.0, "end": 292.0}, {"start": 610.0, "end": 611.0}])
        self.assertEqual(cuts, [291.0, 610.5])
        self.assertEqual(w.audio_cut_points(700.0, 300.0, []), [300.0, 600.0])


class FactsTests(unittest.TestCase):
    def test_shift_times_moves_only_time_fields(self):
        d = {"t": 1.0, "start": 2.0, "end": 3.0, "speech": True, "items": [{"t": 0.5, "n": 4}]}
        w._shift_times(d, 10.0)
        self.assertEqual((d["t"], d["start"], d["end"], d["speech"]), (11.0, 12.0, 13.0, True))
        self.assertEqual(d["items"][0], {"t": 10.5, "n": 4})

    def test_shrink_facts_fits_the_limit(self):
        frames = [{"t": i, "what": "x" * 900, "people": "y" * 900, "objects": "", "text": "", "change": ""}
                  for i in range(200)]
        facts = {"detail_passes_full_resolution": [{"frames": frames}]}
        small = w.shrink_facts(facts, limit=60_000)
        self.assertLessEqual(len(json.dumps(small)), 60_000)
        self.assertEqual(len(facts["detail_passes_full_resolution"][0]["frames"]), 200)


class PlatformTests(unittest.TestCase):
    def test_reels_checks(self):
        pr = {"duration": 30.0, "faststart": True,
              "video": {"width": 1080, "height": 1920, "aspect": "9:16", "fps": 30.0, "codec": "h264", "pix_fmt": "yuv420p"}}
        meas = {"audio": {"integrated_lufs": -14.0, "true_peak_dbtp": -1.5}}
        boxes = {"f.jpg": [{"text": "SALE", "box": [100, 1800, 300, 60], "frame_w": 1080, "frame_h": 1920}]}
        res = w.platform_checks(pr, meas, "reels", boxes)
        status = {c["item"]: c["status"] for c in res["checks"]}
        self.assertEqual(status["aspect"], "pass")
        self.assertEqual(status["loudness"], "pass")
        self.assertEqual(status["text inside safe zones"], "fail")
        self.assertEqual(len(res["safe_zone_hits"]), 1)

    def test_wrong_aspect_fails(self):
        pr = {"duration": 8.0, "video": {"width": 1080, "height": 840, "aspect": "1080:840", "fps": 30.0, "codec": "h264"}}
        res = w.platform_checks(pr, {}, "reels")
        self.assertEqual({c["item"]: c["status"] for c in res["checks"]}["aspect"], "fail")

    def test_failed_audio_measurement_is_not_no_audio(self):
        pr = {"duration": 8.0, "audio": {"codec": "aac"}, "video": {"width": 1080, "height": 1920, "aspect": "9:16", "fps": 30}}
        res = w.platform_checks(pr, {"audio": {"error": "ffmpeg died"}}, "reels")
        loud = {c["item"]: c for c in res["checks"]}["loudness"]
        self.assertEqual(loud["status"], "unclear")
        self.assertIn("could not be measured", loud["detail"])

    def test_unknown_platform(self):
        with self.assertRaises(w.WatchError):
            w.platform_checks({}, {}, "myspace")


class QaHelperTests(unittest.TestCase):
    def test_three_flashes_are_not_flagged_but_five_are(self):
        """Found in review: direction changes were counted, so 3 flashes read as 5."""
        def series(n_flashes):
            ys, t = [], 0.0
            for _ in range(n_flashes):
                ys += [(t, 60.0), (t + 0.04, 200.0), (t + 0.08, 60.0)]
                t += 0.2
            ys += [(t + k * 0.04, 60.0) for k in range(10)]
            return ys
        self.assertEqual(w.flash_windows(series(3)), [])
        self.assertTrue(w.flash_windows(series(5)))

    def test_flash_windows(self):
        steady = [(i / 25, 100.0) for i in range(50)]
        self.assertEqual(w.flash_windows(steady), [])
        strobe = [(i / 25, 40.0 if i % 2 else 200.0) for i in range(50)]
        self.assertTrue(w.flash_windows(strobe))

    def test_short_cue_is_stretched_when_there_is_room(self):
        cues = w.srt_cues([{"start": 1.0, "end_final": 1.4, "text": "Hi."}, {"start": 5.0, "end_final": 6.0, "text": "Next."}])
        self.assertGreaterEqual(round(cues[0]["end"] - cues[0]["start"], 3), round(5 / 6, 3))

    def test_subtitle_cues(self):
        segs = [{"start": 0.0, "end_final": 6.0, "text": "word " * 30}, {"start": 6.5, "end_final": 7.0, "text": "Hi."}]
        cues = w.srt_cues(segs)
        self.assertTrue(all(len(c["lines"]) <= 2 and all(len(l) <= 42 for l in c["lines"]) for c in cues))
        self.assertTrue(all(c["end"] - c["start"] >= 0.3 for c in cues))
        self.assertTrue(all(a["end"] <= b["start"] for a, b in zip(cues, cues[1:])))


class SheetTests(unittest.TestCase):
    def test_sheets_fit_2000_px(self):
        for n, aspect in ((24, 9 / 16), (16, 1080 / 840), (48, 16 / 9), (5, 1.0)):
            c, cw = w.sheet_layout(n, aspect)
            rows = (n + c - 1) // c
            self.assertLessEqual(c * cw + (c + 1) * 6, 2000, (n, aspect))
            self.assertLessEqual(rows * (cw / aspect) + (rows + 1) * 6, 2001, (n, aspect))


class CompareTests(unittest.TestCase):
    def test_small_edit_is_found(self):
        """Found in review: a 60x20 px change moved SSIM only from 0.996 to 0.989 and was missed."""
        rows = [(i / 4, 0.9960 + (0.0004 if i % 2 else -0.0004)) for i in range(40)]
        rows[20:24] = [(t, 0.989) for t, _ in rows[20:24]]
        times = w.changed_times(rows, 0.95)
        self.assertEqual((min(times), max(times)), (5.0, 5.75))
        self.assertEqual(w.changed_times([(i / 4, 0.9962) for i in range(40)], 0.95), [])

    def test_colour_change_is_found(self):
        # Measured: a grey section keeps Y at 0.997 but drops U and V to about 0.83.
        stats = Path(TMP) / "ssim.log"
        lines = [f"n:{n} Y:0.9973 U:0.9965 V:0.9964 All:0.9970" for n in range(1, 13)]
        lines += [f"n:{n} Y:0.9972 U:0.8350 V:0.8550 All:0.9460" for n in range(13, 21)]
        lines += [f"n:{n} Y:0.9970 U:0.9950 V:0.9950 All:0.9962" for n in range(21, 33)]
        stats.write_text("\n".join(lines) + "\n")
        times = w.changed_times(w.ssim_rows(stats), 0.95)
        self.assertEqual((min(times), max(times)), (3.0, 4.75))


class Mp4Tests(unittest.TestCase):
    def _box(self, kind: bytes, size: int = 16) -> bytes:
        return size.to_bytes(4, "big") + kind + b"\0" * (size - 8)

    def test_moov_first(self):
        p = Path(TMP) / "fast.mp4"
        p.write_bytes(self._box(b"ftyp") + self._box(b"moov") + self._box(b"mdat"))
        self.assertTrue(w.moov_first(p))
        q = Path(TMP) / "slow.mp4"
        q.write_bytes(self._box(b"ftyp") + self._box(b"mdat") + self._box(b"moov"))
        self.assertFalse(w.moov_first(q))


class ReportTests(unittest.TestCase):
    def test_markdown_has_the_sections_and_no_em_dash(self):
        rep = {"probe": {"name": "a.mp4", "file": "/x/a.mp4", "duration": 8.0,
                         "video": {"width": 1080, "height": 1920, "aspect": "9:16", "fps": 30, "codec": "h264"}, "audio": None},
               "goal": "promo", "depth": "standard", "focus": None,
               "review": {"verdict": "fix first", "summary": "S", "goal_review": [{"item": "hook", "status": "pass", "detail": "d", "evidence": "e"}],
                          "timeline": [{"t": 1.0, "what": "w", "source": "s"}], "issues": [], "conflicts": [], "uncertain": ["u"],
                          "top_fixes": ["f"]},
               "measure": {"video": {"cuts": [2.0], "shots": [{}, {}], "black": [], "freeze": []}},
               "calls": [{"pass": "overview", "model": "m", "seconds": 1}], "evidence": ["contact sheet: s.jpg"]}
        md = w.write_report_md(rep)
        for part in ("# Video report: a.mp4", "**Verdict: fix first**", "## Checklist", "## Timeline", "## Measured",
                     "## Look yourself", "## Passes"):
            self.assertIn(part, md)
        self.assertNotIn("\u2014", md)   # no em dash in a report


class CliTests(unittest.TestCase):
    def test_every_command_parses(self):
        p = w.build_parser()
        for argv in (["doctor", "--setup"], ["watch", "v.mp4", "--goal", "promo", "--depth", "deep", "--platform", "reels"],
                     ["ask", "v.mp4", "what?", "--at", "3.5", "--region", "auto", "--quick"], ["transcribe", "v.mp4", "--lang", "bn"],
                     ["verify", "v.mp4", "the logo shows first", "--at", "2"], ["watch", "v.mp4", "--max-frames", "12"],
                     ["frames", "v.mp4", "--fps", "2", "--sheet"], ["qa", "v.mp4", "--platform", "tiktok"], ["compare", "a", "b"],
                     ["probe", "v.mp4"], ["usage"], ["fetch", "https://example.com/v"], ["cache"]):
            self.assertTrue(p.parse_args(argv).cmd)

    def test_url_needs_fetch(self):
        with self.assertRaises(w.WatchError):
            w.resolve_input("https://example.com/video.mp4")


class FakeAgyTests(unittest.TestCase):
    """The engine plumbing (arguments, parsing, cache, denials, retries) against a fake agy."""

    @classmethod
    def setUpClass(cls):
        cls.agy = make_fake_agy()
        cls.media = Path(TMP) / "cache" / "misc" / "frame.jpg"
        cls.media.parent.mkdir(parents=True, exist_ok=True)
        cls.media.write_bytes(b"\xff\xd8fake")

    def setUp(self):
        os.environ["AGY_BIN"] = str(self.agy)
        os.environ["FAKE_AGY_MODE"] = "ok"
        self.log = Path(TMP) / f"agy-{self._testMethodName}.log"
        os.environ["FAKE_AGY_LOG"] = str(self.log)

    def tearDown(self):
        for k in ("AGY_BIN", "FAKE_AGY_MODE", "FAKE_AGY_LOG"):
            os.environ.pop(k, None)

    def _call(self, name, fresh=True):
        return w.agy_call(None, name, "prompt", w.SCHEMA_ASK, "gemini-3.8-flash-high", [self.media], timeout=60, fresh=fresh)

    def test_ok_and_arguments(self):
        r = self._call("t-ok")
        self.assertTrue(r["ok"])
        self.assertEqual(r["data"]["short_answer"], "a black hose")
        args = json.loads(self.log.read_text().splitlines()[0])
        self.assertIn("--json-schema", args)
        self.assertIn("--add-dir", args)
        self.assertIn("--print-timeout", args)
        self.assertNotIn("--dangerously-skip-permissions", args)

    def test_cache_hit(self):
        self._call("t-cache", fresh=True)
        r = self._call("t-cache", fresh=False)
        self.assertTrue(r["cache"])

    def _models(self):
        return [json.loads(line)[json.loads(line).index("--model") + 1] for line in self.log.read_text().splitlines()]

    def test_denied_is_never_accepted(self):
        os.environ["FAKE_AGY_MODE"] = "denied"
        r = self._call("t-denied")
        self.assertFalse(r["ok"])
        self.assertIn("ViewFile", r["error"])
        self.assertIn("added folder", r["error"])
        # once more on the same model with a stricter prompt, then the sibling model
        self.assertEqual(self._models(), ["gemini-3.8-flash-high", "gemini-3.8-flash-high", "gemini-3.7-flash-high"])

    def test_a_stray_tool_is_retried_with_a_stricter_prompt(self):
        os.environ["FAKE_AGY_MODE"] = "deny_once"
        os.environ["FAKE_AGY_STATE"] = str(Path(TMP) / "deny-once.state")
        try:
            r = self._call("t-deny-once")
        finally:
            os.environ.pop("FAKE_AGY_STATE", None)
        self.assertTrue(r["ok"], r)
        prompts = [json.loads(line)[json.loads(line).index("-p") + 1] for line in self.log.read_text().splitlines()]
        self.assertEqual(len(prompts), 2)
        self.assertNotIn("Use no tool except view_file", prompts[0])
        self.assertIn("Use no tool except view_file", prompts[1])

    def test_a_text_only_denial_names_the_tool(self):
        os.environ["FAKE_AGY_MODE"] = "denied_cmd"
        r = w.agy_call(None, "t-text", "prompt", w.SCHEMA_NEUTRAL, "gemini-3.8-flash-medium", [], timeout=60, fresh=True)
        self.assertFalse(r["ok"])
        self.assertIn("RunCommand", r["error"])
        self.assertIn("outside the task", r["error"])
        last = json.loads(self.log.read_text().splitlines()[-1])
        self.assertIn(w.TEXT_ONLY, last[last.index("-p") + 1])

    def test_empty_reply_retries_then_falls_back(self):
        os.environ["FAKE_AGY_MODE"] = "empty"
        r = self._call("t-empty")
        self.assertFalse(r["ok"])
        models = [json.loads(line)[json.loads(line).index("--model") + 1] for line in self.log.read_text().splitlines()]
        self.assertEqual(models, ["gemini-3.8-flash-high", "gemini-3.8-flash-high", "gemini-3.7-flash-high"])

    def test_unclear_wording_is_settled_by_a_fact_check(self):
        state, how = w.resolve_agreement(None, "Who is at the counter?", {"found": True, "short_answer": "a man and a woman"},
                                         {"found": True, "short_answer": "2 people"}, "t-agree", fresh=True)
        self.assertEqual(state, "agree")   # the fake engine reports no conflict
        self.assertIn("fact check", how)
        self.assertIn(w.TEXT_ONLY, json.loads(self.log.read_text().splitlines()[-1])[1])

    def test_quota_error_is_named(self):
        os.environ["FAKE_AGY_MODE"] = "error"
        r = self._call("t-quota")
        self.assertFalse(r["ok"])
        self.assertIn("quota", r["error"])
        self.assertEqual(len(self.log.read_text().splitlines()), 1)  # no sibling model: same quota pool


@unittest.skipUnless(HAVE_FFMPEG, "ffmpeg not installed")
class FfmpegTests(unittest.TestCase):
    """Probe, measure and frames on a generated 3 s clip with a cut to black and a tone."""

    @classmethod
    def setUpClass(cls):
        cls.clip = Path(TMP) / "clip.mp4"
        subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y",
                        "-f", "lavfi", "-i", "testsrc2=size=640x360:rate=25:duration=2",
                        "-f", "lavfi", "-i", "color=black:size=640x360:rate=25:duration=1",
                        "-f", "lavfi", "-i", "sine=frequency=440:duration=3",
                        "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]", "-map", "[v]", "-map", "2:a",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(cls.clip)], check=True)
        cls.v = w.Video(cls.clip)

    def test_probe(self):
        pr = self.v.probe()
        self.assertAlmostEqual(pr["duration"], 3.0, delta=0.15)
        self.assertEqual(pr["video"]["width"], 640)
        self.assertEqual(pr["video"]["aspect"], "16:9")
        self.assertTrue(pr["audio"])

    def test_measure_finds_the_black_second_and_the_cut(self):
        m = w.measure(self.v, fresh=True)
        self.assertTrue(m["video"]["black"], m["video"])
        self.assertAlmostEqual(m["video"]["black"][0]["start"], 2.0, delta=0.15)
        self.assertTrue(any(abs(c - 2.0) < 0.2 for c in m["video"]["cuts"]), m["video"]["cuts"])
        self.assertIsNotNone(m["audio"]["integrated_lufs"])

    def test_frames_zoom_and_sheet(self):
        frames = w.extract_frames(self.v, [0.5, 1.5])
        self.assertEqual(len(frames), 2)
        self.assertTrue(all(p.exists() and p.stat().st_size > 0 for _, p in frames))
        zooms = w.zoom_frames(self.v, frames, "top-left")
        self.assertTrue(zooms[0][1].exists())
        sheet = w.contact_sheet(self.v, frames, "t", cols=2, cell=200)
        self.assertTrue(sheet and sheet.exists())

    def test_long_overview_runs_in_parts(self):
        """A 50-minute window is watched as three proxies in parallel, then merged (fake agy, fake proxies)."""
        agy = make_fake_agy()
        os.environ["AGY_BIN"] = str(agy)
        os.environ["FAKE_AGY_MODE"] = "ok"
        real = w.make_proxy
        made = []

        def fake_proxy(v, start=None, end=None):
            p = v.sub("media", f"fake-{start or 0:g}-{end or 0:g}.mp4")
            p.write_bytes(b"x")
            made.append((start, end))
            return p
        w.make_proxy = fake_proxy
        try:
            plan = {"window": [0.0, 3000.0], "duration": 3000.0, "goal": "general", "overview_model": "gemini-3.8-flash-high"}
            r = w.pass_overview(self.v, plan, None, True)
        finally:
            w.make_proxy = real
            os.environ.pop("AGY_BIN", None)
        self.assertTrue(r["ok"])
        self.assertEqual(r["parts"], 3)
        self.assertEqual(sorted(made), [(0.0, 1200.0), (1200.0, 2400.0), (2400.0, 3000.0)])

    def test_proxy_settings_stay_small(self):
        self.assertEqual(w.proxy_settings(60), (1280, 24))
        self.assertEqual(w.proxy_settings(900), (960, 28))
        self.assertEqual(w.proxy_settings(3600), (854, 31))

    def test_measure_in_a_cache_path_with_quote_and_colon(self):
        """ffmpeg's filtergraph once mangled such paths and returned empty measurements."""
        old = w.CACHE
        try:
            w.CACHE = Path(TMP) / "it's: odd cache"
            v = w.Video(self.clip)
            m = w.measure(v, fresh=True)
        finally:
            w.CACHE = old
        self.assertTrue(m["video"]["cuts"], m["video"])
        self.assertIsNotNone(m["video"]["luma_mean"])

    def test_letterbox_on_a_rotated_clip(self):
        """A phone clip stored landscape with a 90 degree rotation, with bars around the picture."""
        rot = Path(TMP) / "rot.mp4"
        subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-f", "lavfi",
                        "-i", "testsrc2=size=480x270:rate=25:duration=2", "-vf", "pad=640:360:80:45:black",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(Path(TMP) / "flat.mp4")], check=True)
        subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-display_rotation", "90",
                        "-i", str(Path(TMP) / "flat.mp4"), "-c", "copy", str(rot)], check=True)
        v = w.Video(rot)
        pr = v.probe(fresh=True)
        self.assertEqual((pr["video"]["width"], pr["video"]["height"]), (360, 640))
        self.assertTrue(w.measure(v, fresh=True)["video"]["letterbox"])

    def test_cache_clear_by_id_and_refusal(self):
        v = w.Video(self.clip)
        (v.dir / "marker").write_text("x")
        buf = __import__("io").StringIO()
        with __import__("contextlib").redirect_stdout(buf):
            w.main(["cache", "--clear", v.dir.name])
        self.assertFalse(v.dir.exists())
        with self.assertRaises(SystemExit):
            with __import__("contextlib").redirect_stdout(__import__("io").StringIO()):
                w.main(["cache", "--clear", "0123456789abcdef"])

    def test_verify_end_to_end_with_a_fake_engine(self):
        agy = make_fake_agy()
        os.environ["AGY_BIN"] = str(agy)
        os.environ["FAKE_AGY_MODE"] = "ok"
        buf = __import__("io").StringIO()
        try:
            with __import__("contextlib").redirect_stdout(buf):
                w.main(["verify", str(self.clip), "the test pattern shows colour bars", "--at", "1.0", "--no-zoom",
                        "--fresh"])
        finally:
            os.environ.pop("AGY_BIN", None)
        out = json.loads(buf.getvalue())
        self.assertTrue(out["ok"])
        self.assertEqual(out["neutral_question"], "What, if anything, is he holding?")
        self.assertEqual(out["verdict"], "supported")
        self.assertEqual(out["agreement"], "agree")

    def _fake(self):
        agy = make_fake_agy()
        os.environ["AGY_BIN"] = str(agy)
        os.environ["FAKE_AGY_MODE"] = "ok"
        log = Path(TMP) / f"fake-{self._testMethodName}.log"
        os.environ["FAKE_AGY_LOG"] = str(log)
        return log

    def _run(self, argv):
        buf = __import__("io").StringIO()
        try:
            with __import__("contextlib").redirect_stdout(buf):
                w.main(argv)
        finally:
            for k in ("AGY_BIN", "FAKE_AGY_LOG"):
                os.environ.pop(k, None)
        return json.loads(buf.getvalue())

    def test_watch_end_to_end_with_a_fake_engine(self):
        self._fake()
        out = self._run(["watch", str(self.clip), "--depth", "standard", "--fresh", "--out", str(Path(TMP) / "rep")])
        self.assertTrue(out["ok"], out)
        md = Path(out["report_md"]).read_text()
        for part in ("## What this report covers", "Sharp frames:", "## Measured (ffmpeg)", "## Passes"):
            self.assertIn(part, md)
        self.assertTrue(Path(out["contact_sheet"]).exists())

    def test_ask_end_to_end_and_the_order_check(self):
        self._fake()
        out = self._run(["ask", str(self.clip), "What colour is the first thing that appears?", "--at", "1.0",
                         "--no-zoom", "--fresh"])
        self.assertTrue(out["ok"])
        self.assertEqual(out["answers"][0]["agreement"], "agree")
        log2 = self._fake()
        v = self._run(["verify", str(self.clip), "the bars appear before the black screen", "--at", "1.5",
                       "--no-zoom", "--fresh"])
        self.assertEqual(v["order_check"], "the second viewer saw the frames in reverse order")
        self.assertIn("reverse order", log2.read_text())

    def test_verify_survives_a_failed_rewrite(self):
        self._fake()
        os.environ["FAKE_AGY_MODE"] = "deny_neutral"
        try:
            out = self._run(["verify", str(self.clip), "the bars appear before the black screen", "--at", "1.5",
                             "--fresh"])
        finally:
            os.environ["FAKE_AGY_MODE"] = "ok"
        self.assertTrue(out["ok"], out)
        self.assertTrue(out["question_source"].startswith("generic"))
        self.assertEqual(out["neutral_question"], w.GENERIC_ORDER_Q)
        self.assertNotIn("bars", out["neutral_question"])
        self.assertIsNone(out["zoom_region"])

    def test_measure_has_the_change_grid(self):
        m = w.measure(w.Video(self.clip))
        act = m["video"]["activity"]
        self.assertEqual(act["grid"], [32, 18])
        self.assertGreater(act["frames"], 50)

    def test_close_ups_go_with_their_frame(self):
        log = self._fake()
        plan = {"detail_times": [0.5, 1.0], "detail_fps": None, "goal": "general", "detail_model": w.MODELS["deep"],
                "closeups": [{"t": 1.0, "region": "0.3,0.3,0.3,0.3", "why": "the moving area", "where": "centre"}]}
        try:
            res = w.pass_detail(w.Video(self.clip), plan, None, True)
        finally:
            for k in ("AGY_BIN", "FAKE_AGY_LOG"):
                os.environ.pop(k, None)
        self.assertEqual(res[0]["closeups"], 1)
        self.assertEqual(res[0]["times"], [0.5, 1.0])
        args = json.loads(log.read_text().splitlines()[-1])
        self.assertIn("close-up of the moving area (centre), enlarged", args[args.index("-p") + 1])

    def test_watch_takes_a_closer_look_when_asked(self):
        self._fake()
        os.environ["FAKE_AGY_MODE"] = "closer"
        try:
            out = self._run(["watch", str(self.clip), "--depth", "standard", "--fresh", "--out", str(Path(TMP) / "rep2")])
        finally:
            os.environ["FAKE_AGY_MODE"] = "ok"
        rep = json.loads(Path(out["report_json"]).read_text())
        self.assertEqual(rep["closer"]["items"][0]["answer"], "a black hose")
        self.assertIn("## Closer looks", Path(out["report_md"]).read_text())

    def test_recorded_live_verify_runs_replay_to_the_same_verdicts(self):
        """Real model answers from five live verify runs: the logic after the models must reach the live verdicts."""
        fixture = Path(__file__).resolve().parent / "fixtures" / "live-verify.json"
        for case, spec in json.loads(fixture.read_text())["cases"].items():
            with self.subTest(case=case):
                self._fake()
                os.environ.update({"FAKE_AGY_MODE": "replay", "FAKE_AGY_REPLAY": str(fixture), "FAKE_AGY_CASE": case})
                try:
                    out = self._run(["verify", str(self.clip), spec["claim"], "--at", "1.5", "--fresh"])
                finally:
                    for k in ("FAKE_AGY_REPLAY", "FAKE_AGY_CASE"):
                        os.environ.pop(k, None)
                    os.environ["FAKE_AGY_MODE"] = "ok"
                self.assertEqual(out["verdict"], spec["verdict"], out.get("reason"))
                self.assertEqual(out["agreement"], "agree")
                self.assertEqual(bool(out["order_check"]), case.startswith("order"))

    def test_the_offline_self_test_passes(self):
        clips = w.make_selftest_clips(Path(TMP) / "selftest")
        failed = [r for r in w.selftest_offline(clips) if not r["pass"]]
        self.assertEqual(failed, [])

    def test_audio_and_onsets(self):
        wav = w.extract_audio(self.v)
        self.assertTrue(wav and wav.exists())
        self.assertIsInstance(w.speech_onsets(self.v, wav), list)


def tearDownModule():
    shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
