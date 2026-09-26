"""Offline tests for the review engine (nexa_review.py) and the model layer (nexa_llm.py): canned answers through
NEXA_LLM_FAKE_FILE, no model and no network."""
import json
import os
import random
import re
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
TMP = tempfile.mkdtemp(prefix="nexa-review-test-")
os.environ["NEXA_CACHE"] = TMP
import nexa_llm  # noqa: E402
import nexa_review as R  # noqa: E402

CHECK = [{"id": "B1_hook", "question": "Does L1 state a specific tension or promise?"},
         {"id": "B2_promise", "question": "Do the first 30 seconds keep the title's promise?"}]
LINES = R.number_lines("This bakery turns people away every morning, on purpose. It has one oven. "
                       "But last spring she doubled the batch. So the oven ran all night. The bread came out pale. "
                       "People come for the queue as much as for the bread.")


def fake(answers):
    path = Path(TMP) / f"fake-{len(os.listdir(TMP))}.json"
    path.write_text(json.dumps(answers), encoding="utf-8")
    os.environ["NEXA_LLM_FAKE_FILE"] = str(path)


def reaction(pid, left, tag="none", remember="", fake_line="", confusing=""):
    return {"persona_id": pid, "t2": {"left_at": left, "reason_tag": tag, "why": f"{pid} {tag}"},
            "t3": {"actions": ["nothing"], "comment": "", "remember": remember, "fake": fake_line,
                   "confusing": confusing}}


class StatsTests(unittest.TestCase):
    def test_binomial_thresholds_match_the_research(self):
        self.assertEqual(R.binomial_threshold(100), 61)
        self.assertEqual(R.binomial_threshold(60), 39)
        self.assertEqual(R.binomial_threshold(30), 21)

    def test_wilson_interval(self):
        low, high = R.wilson(50, 100)
        self.assertAlmostEqual(high - 0.5, 0.096, delta=0.005)
        low, high = R.wilson(10, 100)
        self.assertAlmostEqual(low, 0.055, delta=0.002)
        self.assertAlmostEqual(high, 0.174, delta=0.002)

    def test_allocate_sums_to_n(self):
        counts = R.allocate(100, R.DEFAULT_SEGMENTS)
        self.assertEqual(sum(counts.values()), 100)
        self.assertEqual(counts["core"], 30)

    def test_sentences_in_three_scripts(self):
        self.assertEqual(len(R.split_sentences("One. Two! Three?")), 3)
        self.assertEqual(len(R.split_sentences("আমি যাব। তুমি আসবে? হ্যাঁ।")), 3)
        self.assertEqual(len(R.split_sentences("मैं जाऊँगा। तुम आओगे?")), 2)


class LlmTests(unittest.TestCase):
    def test_strict_schema_closes_objects(self):
        s = nexa_llm.strict_schema({"type": "object", "properties": {"a": {"type": "object", "properties": {
            "b": {"type": "string"}}}}})
        self.assertFalse(s["additionalProperties"])
        self.assertEqual(s["properties"]["a"]["required"], ["b"])

    def test_fake_answers_by_who(self):
        fake({"x": {"answer": "yes"}})
        res = nexa_llm.call_json("q", {"type": "object", "properties": {"answer": {"type": "string"}}}, who="x")
        self.assertTrue(res["ok"])
        self.assertEqual(res["data"], {"answer": "yes"})

    def test_json_from_fenced_text(self):
        self.assertEqual(nexa_llm.json_from_text('```json\n{"a": 1}\n```'), {"a": 1})
        self.assertEqual(nexa_llm.json_from_text('noise {"a": 2} noise'), {"a": 2})


class JudgeTests(unittest.TestCase):
    def test_majority_and_ties(self):
        fail = {"criteria": [{"id": "B1_hook", "lines": ["L1"], "evidence": "L1", "reason": "r", "verdict": "fail",
                              "severity": "major", "problem": "no reason to stay"},
                             {"id": "B2_promise", "lines": [], "evidence": "", "reason": "", "verdict": "pass",
                              "severity": "none", "problem": ""}],
                "scales": {"stop_for_L1": {"evidence": "L1", "score": 2}, "publishable": {"evidence": "", "score": 3}},
                "best_lines": ["L6"], "tells": []}
        passing = json.loads(json.dumps(fail))
        passing["criteria"][0]["verdict"] = "pass"
        passing["criteria"][1]["verdict"] = "fail"
        passing["criteria"][1]["severity"] = "minor"
        answers = {}
        for member in ("codex", "gemini:a", "gemini:b"):
            answers[f"judge-{member}-run1"] = fail
            answers[f"judge-{member}-run2"] = fail if member != "gemini:b" else passing
        fake(answers)
        out = R.judge({"goal": "t"}, LINES, CHECK, roster=("codex", "gemini:a", "gemini:b"), runs=2)
        state = {c["id"]: c["state"] for c in out["criteria"]}
        self.assertEqual(state["B1_hook"], "fail")        # 5 of 6 fail
        self.assertEqual(state["B2_promise"], "pass")     # 1 of 6 fail
        self.assertEqual(out["scales"]["stop_for_L1"]["median"], 2)
        self.assertIn("L6", out["best_lines"])

    def test_answers_without_a_verdict_do_not_count(self):
        ans = {"criteria": [{"id": "B1_hook", "lines": ["L1"], "evidence": "L1", "reason": "r", "verdict": "fail",
                             "severity": "major", "problem": "no reason to stay"},
                            {"id": "B2_promise", "lines": [], "evidence": "", "reason": ""}],
               "scales": {}, "best_lines": [], "tells": []}
        fake({f"judge-{m}-run{r}": ans for m in ("codex", "gemini:a") for r in (1, 2)})
        out = R.judge({"goal": "t"}, LINES, CHECK, roster=("codex", "gemini:a"), runs=2)
        state = {c["id"]: c["state"] for c in out["criteria"]}
        self.assertEqual(state["B1_hook"], "fail")
        self.assertNotEqual(state["B2_promise"], "pass")   # four answers with no verdict prove nothing

    def test_pairwise_counts_only_agreeing_orders(self):
        fake({"pair-codex-AB": {"winner": "B", "reason": "", "decisive_lines": []},
              "pair-codex-BA": {"winner": "A", "reason": "", "decisive_lines": []},   # the same draft (two) both times
              "pair-gemini:a-AB": {"winner": "A", "reason": "", "decisive_lines": []},
              "pair-gemini:a-BA": {"winner": "A", "reason": "", "decisive_lines": []}})  # follows the order
        out = R.pairwise({"goal": "t"}, "draft one", "draft two", roster=("codex", "gemini:a"))
        self.assertEqual(out["tally"]["B"], 1)
        self.assertEqual(out["tally"]["split"], 1)
        why = R.pair_reasons(out)
        self.assertEqual((why["codex"]["verdict"], why["gemini:a"]["verdict"]), ("B", "split"))
        self.assertEqual(set(why["codex"]), {"verdict", "a_shown_first", "b_shown_first"})


class PanelTests(unittest.TestCase):
    def panel(self):
        personas = [{"id": f"P{i:03d}", "segment": "core" if i <= 60 else "sceptic", "card": "c", "context": ""}
                    for i in range(1, 101)]
        segs = [{"id": "core", "name": "core", "weight": 0.6, "priority": True},
                {"id": "sceptic", "name": "sceptic", "weight": 0.4, "priority": False}]
        return {"personas": personas, "segments": segs, "brief": {"goal": "t"}}

    def test_survival_spikes_fixes_and_keep(self):
        panel = self.panel()
        reactions = []
        for i in range(1, 101):
            pid = f"P{i:03d}"
            if i <= 30:
                r = reaction(pid, "L2", "slow", remember="L1")
            elif i <= 40:
                r = reaction(pid, "L5", "fake", fake_line="L5")
            else:
                r = reaction(pid, "end", remember="L6")
            r["family"] = "codex" if i % 2 else "gemini"
            r["segment"] = "core" if i <= 60 else "sceptic"
            reactions.append(r)
        run = {"reactions": reactions, "families": ["codex", "gemini"], "noise": {"act_on_panel": True}}
        out = R.aggregate(panel, run, LINES)
        self.assertEqual(out["finished"]["count"], 60)
        self.assertEqual(out["survival"][1]["share"], 0.7)
        self.assertTrue(any(s["line"] == "L2" for s in out["spikes"]))
        tags = {(f["line"], f["tag"]) for f in out["fixes"]}
        self.assertIn(("L2", "slow"), tags)
        self.assertIn(("L5", "fake"), tags)
        self.assertLessEqual(len(out["fixes"]), 5)
        self.assertIn("L6", out["keep"])   # remembered by 60 %
        self.assertIn("L1", out["keep"])   # remembered by 30 %
        self.assertIn("synthetic", out["label"])

    def test_comments_are_spread_across_segments(self):
        panel = self.panel()
        reactions = []
        for i in range(1, 101):
            r = reaction(f"P{i:03d}", "end")
            r["t3"]["comment"] = f"comment {i}"
            r["segment"] = "core" if i <= 90 else "sceptic"
            r["family"] = "codex"
            reactions.append(r)
        out = R.aggregate(panel, {"reactions": reactions, "families": ["codex"]}, LINES)
        self.assertEqual(len(out["comments"]), 24)
        self.assertEqual(sum(1 for c in out["comments"] if c["segment"] == "sceptic"), 10)  # not drowned by 90 core

    def test_issue_seen_in_one_family_waits(self):
        panel = self.panel()
        reactions = []
        for i in range(1, 101):
            r = reaction(f"P{i:03d}", "L3" if i <= 20 else "end", "confusing" if i <= 20 else "none")
            r["family"] = "codex" if i <= 20 else "gemini"
            r["segment"] = "core"
            reactions.append(r)
        out = R.aggregate(panel, {"reactions": reactions, "families": ["codex", "gemini"]}, LINES)
        self.assertFalse(any(f["line"] == "L3" for f in out["fixes"]))
        self.assertTrue(any(w["line"] == "L3" for w in out["watch"]))

    def test_run_panel_with_noise_probe(self):
        panel = self.panel()
        answers = {}
        for gi in range(10):
            answers[f"panel-{gi}-{'codex' if gi % 2 == 0 else 'gemini'}"] = {"reactions": [
                reaction(p["id"], "end") for p in panel["personas"]]}
        answers["panel-probe-codex"] = {"reactions": [reaction(p["id"], "end") for p in panel["personas"]]}
        fake(answers)
        out = R.run_panel(panel, LINES, seed=1)
        self.assertEqual(len(out["reactions"]), 100)
        self.assertEqual(out["noise"]["disagree"], 0)
        self.assertTrue(out["noise"]["act_on_panel"])

    def test_prefer_needs_the_threshold_in_each_family(self):
        panel = self.panel()
        rng = random.Random(11)
        personas = list(panel["personas"])
        rng.shuffle(personas)
        new_is = {}
        for gi in range(0, 100, 10):
            new_is[gi] = "A" if rng.random() < 0.5 else "B"
        answers = {}
        for gi in range(0, 100, 10):
            group = personas[gi:gi + 10]
            eng = "codex" if (gi // 10) % 2 == 0 else "gemini"
            new = new_is[gi]
            old = "B" if new == "A" else "A"
            answers[f"prefer-{gi}-{eng}"] = {"choices": [
                {"persona_id": p["id"], "choice": new if j < 7 else old, "reason": "r"} for j, p in enumerate(group)]}
        fake(answers)
        out = R.panel_prefer(panel, "old text", "new text")
        self.assertEqual(out["new_wins"], 70)
        self.assertEqual(out["threshold"], 61)
        self.assertTrue(out["clears"])


class ChunkAndIdTests(unittest.TestCase):
    def test_chunks_follow_the_staged_watch(self):
        lines = [{"id": f"L{i}", "text": "x", "t": t} for i, t in enumerate([0, 4, 14, 16, 29, 45, 70], start=1)]
        c = R.chunk_map(lines)
        self.assertEqual([c[f"L{i}"] for i in range(1, 8)], [0, 1, 1, 2, 2, 3, 4])
        self.assertEqual(c["end"], 5)

    def test_line_ids_from_messy_answers(self):
        self.assertEqual(R.line_ids(["L5", "L5: \u201cthe quote\u201d", "L2-L3", "none", "L10"]),
                         ["L2", "L3", "L5", "L10"])


class ValidationTests(unittest.TestCase):
    def test_spearman_and_ties(self):
        self.assertEqual(R.spearman([1, 2, 3, 4, 5], [10, 20, 30, 40, 50]), 1.0)
        self.assertEqual(R.spearman([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]), -1.0)
        self.assertEqual(R.ranks([3, 1, 3, 2]), [3.5, 1.0, 3.5, 2.0])
        self.assertIsNone(R.spearman([1, 1, 1], [1, 2, 3]))

    def test_validate_panel_ranks_past_pieces(self):
        personas = [{"id": f"P{i:03d}", "segment": "core", "card": "c"} for i in range(1, 31)]
        panel = {"personas": personas, "segments": [{"id": "core", "name": "core", "weight": 1}], "brief": {}}
        items = [{"id": f"v{i}", "text": f"piece {i} " + "yes " * i, "actual": i * 100} for i in range(1, 6)]

        def fake_many(jobs, workers=6):
            out = []
            for job in jobs:
                pieces = re.findall(r"^(I\d+):\n(piece \d+[^\n]*)", job["prompt"], re.M)
                members = re.findall(r"^(P\d{3}) \(", job["prompt"], re.M)
                answers = [{"persona_id": pid, "item": lab, "stop": int(pid[1:]) % 5 < text.count("yes"),
                            "finish": int(pid[1:]) % 5 < text.count("yes")} for pid in members for lab, text in pieces]
                out.append({"ok": True, "data": {"answers": answers}})
            return out

        original = nexa_llm.call_many
        nexa_llm.call_many = fake_many
        try:
            res = R.validate_panel(panel, items)
        finally:
            nexa_llm.call_many = original
        self.assertEqual(res["spearman"], 1.0)       # the labels were mapped back to the right pieces
        self.assertTrue(res["ok"])
        self.assertFalse(R.validate_panel(panel, items[:3])["ok"])

    def test_build_panel_reports_shortfall_and_invented_ids(self):
        fake({"*": {"personas": [{"card": "x", "quote_ids": ["v1", "zz"], "context": "c"}]}})
        panel = R.build_panel({"goal": "t"}, [{"id": "v1", "text": "real comment"}], n=10)
        self.assertTrue(any("asked for 3 personas, got 1" in e for e in panel["errors"]))
        self.assertTrue(any("not in the evidence" in e for e in panel["errors"]))
        self.assertTrue(all(p["quote_ids"] == ["v1"] for p in panel["personas"]))
        self.assertFalse(panel["validation"]["ok"])

    def test_unvalidated_panel_is_named_in_decide(self):
        d = R.decide(1, True, {"criteria": []}, {"fixes": [], "validated": False})
        self.assertTrue(any("not validated" in w for w in d["why"]))


class BlandnessTests(unittest.TestCase):
    def test_edit_share_and_guard(self):
        old = "Mira sells 200 loaves by 9 a.m. in Dhaka. She has one oven. The queue is the product."
        self.assertEqual(R.edit_share(old, old), 0.0)
        bland = "Our bakery offers a wonderful selection of fresh bread. Customers love our products."
        guard = R.blandness(old, bland, baselines=[bland])
        self.assertFalse(guard["ok"])
        self.assertTrue(any("budget" in p for p in guard["problems"]))
        self.assertTrue(any("specificity" in p for p in guard["problems"]))

    def test_guard_tracks_lost_details_not_dilution(self):
        old = "Mira sells 200 loaves by 9 a.m. in Dhaka. She has one oven. The queue is the product."
        worried = "Worried it is just hype? " + old
        self.assertFalse(any("specificity" in x or "removed" in x for x in R.blandness(old, worried)["problems"]))
        fewer = old.replace("200 loaves", "loaves")
        self.assertTrue(any("removed: 200" in x for x in R.blandness(old, fewer)["problems"]))
        # punctuation after a number and a repeat said once are not lost details
        self.assertEqual(R.specific_tokens("Open at 7, shut at 9. Rs 1,000 or 3.5% off, at 9:02."),
                         ["7", "9", "1,000", "3.5%", "9:02"])
        v1 = "At 9, it turns people away. The line starts at 7, and at 9, it is gone."
        v2 = "At 9, it turns people away. That is why the line starts at 7."
        self.assertFalse(any("removed" in x for x in R.blandness(v1, v2)["problems"]))

    def test_specificity_counts_numbers_and_names(self):
        self.assertGreater(R.specificity("Mira sells 200 loaves in Dhaka by 9."), 20)
        self.assertEqual(R.specificity("It is good and people like it a lot."), 0.0)
        self.assertGreater(R.specificity("দাম ৮৫০ টাকা।"), 0)

    def test_decide_caps_rounds(self):
        d = R.decide(2, True, {"criteria": [{"id": "B1", "state": "fail"}]}, {"fixes": []})
        self.assertFalse(d["continue"])
        self.assertTrue(any("cap" in w for w in d["why"]))
        d = R.decide(1, True, {"criteria": [{"id": "B1", "state": "fail"}]}, {"fixes": []})
        self.assertTrue(d["continue"])


class CopiesTests(unittest.TestCase):
    def test_shared_modules_match_the_family(self):
        repo = SCRIPTS.parent.parent
        mine = (SCRIPTS / "gemini_api.py").read_bytes()
        other = repo / "nexa-video-creator" / "scripts" / "gemini_api.py"
        if other.exists():
            self.assertEqual(other.read_bytes(), mine, "gemini_api.py differs from nexa-video-creator's copy")
        for module in ("nexa_llm.py", "nexa_review.py"):
            for skill in ("nexa-copy", "nexa-research"):
                p = repo / skill / "scripts" / module
                if p.exists():
                    self.assertEqual(p.read_bytes(), (SCRIPTS / module).read_bytes(), f"{p} differs")


if __name__ == "__main__":
    unittest.main()
