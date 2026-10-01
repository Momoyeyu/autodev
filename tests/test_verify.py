import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "autodev", "scripts", "autodev_verify.py")
BENCH = 'import sys; sys.path.insert(0, "src"); import impl; print("p95=" + str(impl.N))\n'
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
           GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")


def sh(cwd, *args):
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, env=ENV)


def git(cwd, *args):
    r = sh(cwd, "git", *args)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


class Harness(unittest.TestCase):
    scenario = "optimization"
    init_extra = ["--score-regex", r"p95=([0-9.]+)", "--unit", "ms", "--direction", "lower",
                  "--delta-pct", "5", "--target", "150"]
    budget = ["--budget-minutes", "10"]

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.repo = os.path.join(self.root, "repo")
        self.wt = os.path.join(self.root, "wt")
        self.home = os.path.join(self.repo, ".autodev", "runs", "t")
        os.makedirs(self.repo)
        git(self.repo, "init", "-q")
        write(self.repo, ".gitignore", "__pycache__/\n")
        self.seed()
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "base")

    def tearDown(self):
        self.tmp.cleanup()

    def seed(self):
        write(self.repo, "src/impl.py", "N=200\n")
        write(self.repo, "bench/run.py", BENCH)

    def run_v(self, *args):
        return sh(self.root, sys.executable, SCRIPT, "--home", self.home, *args)

    def init(self, *extra, scenario=None, editable="src", frozen="bench", test_cmd="python3 bench/run.py"):
        scen = scenario or self.scenario
        args = ["init", "--repo", self.repo, "--scenario", scen, "--editable", editable]
        if frozen is not None:
            args += ["--frozen", frozen]
        if test_cmd is not None:
            args += ["--test-cmd", test_cmd]
        return self.run_v(*args, *self.budget,
                          *(self.init_extra if scen == "optimization" else []), *extra)

    def start(self):
        git(self.repo, "worktree", "add", "-q", "-b", "autodev/t", self.wt, "HEAD")
        r = self.run_v("start", "--worktree", self.wt)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r

    def ready(self, *extra):
        r = self.init(*extra)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.start()

    def commit(self, files, msg="attempt"):
        for rel, text in files.items():
            write(self.wt, rel, text)
        git(self.wt, "add", "-A")
        git(self.wt, "commit", "-qm", msg)
        return git(self.wt, "rev-parse", "HEAD")

    def attempt(self, files=None, note="", route=None, *extra):
        if files:
            self.commit(files)
        self.routes = getattr(self, "routes", 0) + 1
        route = route or f"r{self.routes}"
        r = self.run_v("attempt", "--note", note, "--route", route, *extra)
        rec = json.loads(r.stdout) if r.stdout.strip().startswith("{") else None
        return r.returncode, rec

    def contract(self):
        with open(os.path.join(self.home, "contract.json")) as f:
            return json.load(f)

    def attempts(self):
        with open(os.path.join(self.home, "attempts.jsonl")) as f:
            return [json.loads(l) for l in f if l.strip()]

    def status(self):
        r = self.run_v("status")
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def read(self, rel):
        with open(os.path.join(self.wt, rel)) as f:
            return f.read()

    def clean(self):
        return git(self.wt, "status", "--porcelain") == ""


class TestInitAndStart(Harness):
    def test_init_records_baseline_delta_and_frozen_hashes(self):
        r = self.init()
        self.assertEqual(r.returncode, 0, r.stderr)
        c = self.contract()
        self.assertEqual(c["scenario"], "optimization")
        self.assertEqual(c["baseline"]["score"], 200.0)
        self.assertEqual(c["delta"], 10.0)
        self.assertIn("bench/run.py", c["frozen"])
        self.assertTrue(os.path.exists(os.path.join(self.home, "raw", "baseline.log")))

    def test_init_rejects_failing_baseline(self):
        write(self.repo, "bench/run.py", "raise SystemExit(1)\n")
        git(self.repo, "commit", "-qam", "broken")
        r = self.init()
        self.assertEqual(r.returncode, 3)
        self.assertFalse(os.path.exists(os.path.join(self.home, "contract.json")))

    def test_init_reruns_unchanged_benchmark_as_noise_control(self):
        self.assertEqual(self.init().returncode, 0)
        b = self.contract()["baseline"]
        self.assertEqual((b["control_score"], b["noise"]), (200.0, 0.0))
        self.assertTrue(os.path.exists(os.path.join(self.home, "raw", "control.log")))

    def test_init_rejects_noise_not_below_delta(self):
        write(self.repo, "bench/run.py",
              'import os\nn = int(open(".c").read()) if os.path.exists(".c") else 0\n'
              'open(".c", "w").write(str(n + 1))\nprint("p95=" + str(200 + 50 * n))\n')
        git(self.repo, "commit", "-qam", "noisy")
        r = self.init()
        self.assertEqual(r.returncode, 3)
        self.assertIn("noise", r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.home, "contract.json")))

    def test_init_rejects_frozen_inside_editable(self):
        r = self.init(editable=".", frozen="bench")
        self.assertEqual(r.returncode, 3)

    def test_start_refuses_users_checkout(self):
        self.assertEqual(self.init().returncode, 0)
        r = self.run_v("start", "--worktree", self.repo)
        self.assertEqual(r.returncode, 3)

    def test_start_smoke_passes_and_leaves_clean_worktree(self):
        self.ready()
        self.assertTrue(self.clean())
        self.assertEqual(git(self.wt, "rev-parse", "HEAD"), self.contract()["best"])
        kinds = {(a["kind"], a["verdict"]) for a in self.attempts()}
        self.assertIn(("smoke", "passed"), kinds)
        self.assertIn(("baseline", "baseline"), kinds)


class TestOptimizationLoop(Harness):
    def setUp(self):
        super().setUp()
        self.ready()

    def test_regression_is_rejected_and_rolled_back(self):
        code, rec = self.attempt({"src/impl.py": "N=220\n"})
        self.assertEqual((code, rec["verdict"], rec["score"]), (1, "rejected", 220.0))
        self.assertEqual(self.read("src/impl.py"), "N=200\n")
        self.assertEqual(git(self.wt, "rev-parse", "HEAD"), self.contract()["best"])
        self.assertTrue(self.clean())

    def test_improvement_is_accepted_and_becomes_best(self):
        head = self.commit({"src/impl.py": "N=170\n"})
        code, rec = self.attempt()
        self.assertEqual((code, rec["verdict"]), (0, "accepted"))
        self.assertEqual(self.contract()["best"], head)
        self.assertEqual(self.contract()["best_score"], 170.0)

    def test_improvement_below_delta_is_rejected(self):
        self.attempt({"src/impl.py": "N=170\n"})
        code, rec = self.attempt({"src/impl.py": "N=165\n"})
        self.assertEqual((code, rec["verdict"]), (1, "rejected"))
        self.assertEqual(self.read("src/impl.py"), "N=170\n")

    def test_frozen_file_edit_is_invalid_and_rolled_back(self):
        code, rec = self.attempt({"src/impl.py": "N=100\n", "bench/run.py": BENCH + "# x\n"})
        self.assertEqual((code, rec["verdict"]), (2, "invalid"))
        self.assertIn("bench/run.py", rec["files"])
        self.assertEqual(self.read("bench/run.py"), BENCH)
        self.assertEqual(self.read("src/impl.py"), "N=200\n")
        self.assertTrue(self.clean())

    def test_new_file_outside_scope_is_invalid_and_removed(self):
        code, rec = self.attempt({"README_extra.md": "x\n", "src/impl.py": "N=100\n"})
        self.assertEqual((code, rec["verdict"]), (2, "invalid"))
        self.assertFalse(os.path.exists(os.path.join(self.wt, "README_extra.md")))
        self.assertTrue(self.clean())

    def test_new_file_inside_scope_is_kept_on_accept(self):
        code, rec = self.attempt({"src/helper.py": "pass\n", "src/impl.py": "N=160\n"})
        self.assertEqual((code, rec["verdict"]), (0, "accepted"))
        self.assertTrue(os.path.exists(os.path.join(self.wt, "src/helper.py")))

    def test_dirty_worktree_is_precondition_error(self):
        before = len(self.attempts())
        write(self.wt, "src/impl.py", "N=170\n")
        r = self.run_v("attempt")
        self.assertEqual(r.returncode, 3)
        self.assertEqual(len(self.attempts()), before)
        self.assertEqual(self.read("src/impl.py"), "N=170\n")

    def test_uncommitted_head_equals_best_is_precondition_error(self):
        r = self.run_v("attempt")
        self.assertEqual(r.returncode, 3)

    def test_crash_is_invalid(self):
        code, rec = self.attempt({"src/impl.py": "raise RuntimeError('boom')\n"})
        self.assertEqual((code, rec["verdict"]), (2, "invalid"))
        self.assertIn("exited", rec["reason"])
        self.assertEqual(self.read("src/impl.py"), "N=200\n")

    def test_target_met_status_decides_handoff(self):
        self.assertEqual(self.status()["decision"], "continue")
        self.attempt({"src/impl.py": "N=140\n"})
        s = self.status()
        self.assertTrue(s["target_met"])
        self.assertEqual((s["decision"], s["stop_reason"]), ("handoff", "target reached"))

    def test_rejected_attempt_cannot_meet_target(self):
        self.attempt({"src/impl.py": "N=170\n"})
        self.attempt({"src/impl.py": "N=165\n"})
        self.assertEqual(self.status()["decision"], "continue")

    def test_report_chart_and_caption(self):
        self.attempt({"src/impl.py": "N=220\n"})
        self.attempt({"src/impl.py": "N=170\n"})
        r = self.run_v("report")
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(self.home, "process.svg")) as f:
            self.assertIn("target", f.read())
        with open(os.path.join(self.home, "caption.json")) as f:
            cap = json.load(f)
        self.assertEqual(cap["improvement"], 30.0)
        self.assertEqual(cap["improvement_pct"], 15.0)
        self.assertFalse(cap["target_met"])


class TestRouteLedger(Harness):
    def setUp(self):
        super().setUp()
        self.ready()

    def test_route_is_required_for_optimization(self):
        self.commit({"src/impl.py": "N=170\n"})
        r = self.run_v("attempt")
        self.assertEqual(r.returncode, 3)
        self.assertIn("--route", r.stderr)

    def test_refuted_route_needs_differs(self):
        code, rec = self.attempt({"src/impl.py": "N=220\n"}, "", "cache")
        self.assertEqual((rec["route"], rec["verdict"]), ("cache", "rejected"))
        self.assertEqual(self.status()["ruled_out"], {"cache": [rec["n"]]})
        self.commit({"src/impl.py": "N=230\n"})
        r = self.run_v("attempt", "--route", "cache")
        self.assertEqual(r.returncode, 3)
        self.assertIn("refuted", r.stderr)
        code, rec = self.attempt(None, "", "cache", "--differs", "bigger cache")
        self.assertEqual((code, rec["differs"]), (1, "bigger cache"))

    def test_new_best_reopens_refuted_routes(self):
        self.attempt({"src/impl.py": "N=220\n"}, "", "cache")
        self.attempt({"src/impl.py": "N=170\n"}, "", "vectorize")
        self.assertEqual(self.status()["ruled_out"], {})
        code, rec = self.attempt({"src/impl.py": "N=150\n"}, "", "cache")
        self.assertEqual(code, 0)

    def test_caption_tallies_routes(self):
        self.attempt({"src/impl.py": "N=220\n"}, "", "cache")
        self.attempt({"src/impl.py": "N=170\n"}, "", "vectorize")
        self.assertEqual(self.run_v("report").returncode, 0)
        with open(os.path.join(self.home, "caption.json")) as f:
            routes = json.load(f)["routes"]
        self.assertEqual(routes["cache"]["rejected"], 1)
        self.assertEqual(routes["vectorize"]["accepted"], 1)


GUARD = 'import sys; sys.path.insert(0, "src"); import impl; assert impl.N > 100\n'
LAW = {"frozen": ["legacy"], "guard_cmd": "python3 guard.py",
       "budget": {"default_minutes": 10, "max_minutes": 30, "reserve_minutes": 1}}


class TestConstitution(Harness):
    budget = []
    law = LAW

    def seed(self):
        super().seed()
        write(self.repo, "legacy/old.py", "x = 1\n")
        write(self.repo, "guard.py", GUARD)
        write(self.repo, ".autodev/constitution.json", json.dumps(self.law))

    def test_init_inherits_frozen_guard_and_budget(self):
        r = self.init()
        self.assertEqual(r.returncode, 0, r.stderr)
        c = self.contract()
        self.assertIn("legacy/old.py", c["frozen"])
        self.assertNotIn(".autodev/constitution.json", c["frozen"])
        self.assertEqual(c["guard_cmd"], "python3 guard.py")
        self.assertEqual(c["constitution"]["path"], ".autodev/constitution.json")
        self.assertEqual((c["budget_minutes"], c["reserve_minutes"]), (10, 1))

    def test_round_cannot_edit_constitution_frozen_paths(self):
        r = self.init(editable="legacy")
        self.assertEqual(r.returncode, 3)
        self.assertIn("legacy/old.py", r.stderr)

    def test_budget_above_max_dies(self):
        r = self.init("--budget-minutes", "60")
        self.assertEqual(r.returncode, 3)
        self.assertIn("max_minutes", r.stderr)

    def test_guard_failure_is_invalid_and_rolled_back(self):
        self.ready()
        code, rec = self.attempt({"src/impl.py": "N=50\n"})
        self.assertEqual((code, rec["verdict"]), (2, "invalid"))
        self.assertIn("guard", rec["reason"])
        self.assertTrue(rec["raw"].endswith(".guard.log"))
        self.assertEqual(self.read("src/impl.py"), "N=200\n")

    def test_guard_passing_attempt_is_judged_normally(self):
        self.ready()
        code, rec = self.attempt({"src/impl.py": "N=170\n"})
        self.assertEqual((code, rec["verdict"]), (0, "accepted"))

    def test_verify_runs_guard(self):
        self.ready()
        r = self.run_v("verify")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["guard_exit"], 0)

    def test_broken_guard_at_baseline_dies(self):
        write(self.repo, "guard.py", "raise SystemExit(1)\n")
        git(self.repo, "commit", "-qam", "broken guard")
        r = self.init()
        self.assertEqual(r.returncode, 3)
        self.assertIn("guard", r.stderr)

    def test_untracked_constitution_still_enforced(self):
        git(self.repo, "rm", "-q", "--cached", ".autodev/constitution.json")
        git(self.repo, "commit", "-qm", "untrack constitution")
        r = self.init()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn(".autodev", git(self.repo, "status", "--porcelain"))
        self.start()
        code, rec = self.attempt({"src/impl.py": "N=50\n"})
        self.assertEqual((code, rec["verdict"]), (2, "invalid"))
        self.assertIn("guard", rec["reason"])

    def test_constitution_change_midloop_is_invalid(self):
        self.ready()
        write(self.repo, ".autodev/constitution.json",
              json.dumps({**self.law, "frozen": ["legacy", "more"]}))
        code, rec = self.attempt({"src/impl.py": "N=170\n"})
        self.assertEqual((code, rec["verdict"]), (2, "invalid"))
        self.assertIn("modified", rec["reason"])
        self.assertEqual(self.read("src/impl.py"), "N=200\n")

    def test_verify_refuses_constitution_drift(self):
        self.ready()
        write(self.repo, ".autodev/constitution.json",
              json.dumps({**self.law, "frozen": ["legacy", "more"]}))
        r = self.run_v("verify")
        self.assertEqual(r.returncode, 3)
        self.assertIn("modified", r.stderr)

    def test_constitution_generated_inherited(self):
        write(self.repo, ".autodev/constitution.json",
              json.dumps({**self.law, "generated": ["artifacts"]}))
        git(self.repo, "commit", "-qam", "generated paths")
        r = self.init()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.contract()["generated"], ["artifacts"])

    def test_unknown_key_dies(self):
        write(self.repo, ".autodev/constitution.json", json.dumps({"forzen": ["legacy"]}))
        git(self.repo, "commit", "-qam", "typo")
        r = self.init("--budget-minutes", "10")
        self.assertEqual(r.returncode, 3)
        self.assertIn("forzen", r.stderr)


class TestConstitutionDevelopmentBudget(Harness):
    scenario = "bugfix"
    budget = []

    def seed(self):
        write(self.repo, "src/impl.py", "\n")
        write(self.repo, "tests/test_x.py",
              'import sys; sys.path.insert(0, "src"); import impl\nassert impl.add(1, 2) == 3\n')
        write(self.repo, ".autodev/constitution.json", json.dumps({"budget": {"default_minutes": 10}}))

    def test_default_budget_applies_only_to_optimization(self):
        r = self.init(frozen="tests", test_cmd="python3 tests/test_x.py")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIsNone(self.contract()["budget_minutes"])


class TestTakeover(Harness):
    def test_status_before_start_points_to_start(self):
        self.init()
        s = self.status()
        self.assertNotIn("head", s)
        self.assertIn("start", s["next"])

    def test_status_reports_in_flight_work(self):
        self.ready()
        s = self.status()
        self.assertTrue(s["head_is_best"] and s["worktree_clean"])
        self.assertIn("--route", s["next"])
        write(self.wt, "src/impl.py", "N=170\n")
        s = self.status()
        self.assertFalse(s["worktree_clean"])
        self.assertIn("uncommitted", s["next"])
        git(self.wt, "commit", "-qam", "wip")
        s = self.status()
        self.assertFalse(s["head_is_best"])
        self.assertIn("not yet judged", s["next"])

    def test_status_names_ruled_out_routes(self):
        self.ready()
        self.attempt({"src/impl.py": "N=220\n"}, "", "cache")
        self.assertIn("cache", self.status()["next"])

    def test_handoff_points_to_verify(self):
        self.ready()
        self.attempt({"src/impl.py": "N=140\n"})
        self.assertIn("verify", self.status()["next"])

    def test_unjudged_head_comes_before_handoff(self):
        self.ready()
        self.attempt({"src/impl.py": "N=140\n"})
        self.commit({"src/impl.py": "N=130\n"})
        s = self.status()
        self.assertEqual(s["decision"], "handoff")
        self.assertIn("not yet judged", s["next"])


class TestExclusiveTarget(Harness):
    def test_exclusive_target_excludes_equality(self):
        self.ready("--exclusive")
        self.attempt({"src/impl.py": "N=150\n"})
        self.assertFalse(self.status()["target_met"])
        self.attempt({"src/impl.py": "N=139\n"})
        self.assertTrue(self.status()["target_met"])


class TestBudget(Harness):
    budget = ["--budget-minutes", "0.001"]

    def test_budget_exhausted(self):
        self.ready()
        time.sleep(0.2)
        self.commit({"src/impl.py": "N=170\n"})
        self.assertEqual(self.run_v("attempt").returncode, 3)
        self.assertEqual(self.read("src/impl.py"), "N=200\n")
        self.assertEqual(git(self.wt, "rev-parse", "HEAD"), self.contract()["best"])
        s = self.status()
        self.assertEqual((s["decision"], s["stop_reason"]), ("handoff", "time budget exhausted"))


class TestBudgetRequired(Harness):
    budget = []

    def test_optimization_requires_budget(self):
        r = self.init()
        self.assertEqual(r.returncode, 3)
        self.assertIn("--budget-minutes", r.stderr)

    def test_reserve_must_be_smaller_than_budget(self):
        r = self.init("--budget-minutes", "10", "--reserve-minutes", "20")
        self.assertEqual(r.returncode, 3)


class TestReserve(Harness):
    budget = ["--budget-minutes", "0.2", "--reserve-minutes", "0.18"]

    def test_reserve_window_blocks_attempts(self):
        self.ready()
        time.sleep(1.5)
        self.commit({"src/impl.py": "N=170\n"})
        r = self.run_v("attempt")
        self.assertEqual(r.returncode, 3)
        self.assertIn("reserve", r.stderr)
        s = self.status()
        self.assertEqual((s["decision"], s["stop_reason"]), ("handoff", "reserve window reached"))
        self.assertFalse(s["budget_exhausted"])


class TestVerify(Harness):
    def test_verify_reproduces_best_state(self):
        self.ready()
        self.attempt({"src/impl.py": "N=170\n"})
        r = self.run_v("verify")
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = json.loads(r.stdout)
        self.assertEqual(rec["verdict"], "verified")
        self.assertEqual((rec["score"], rec["recorded_best"]), (170.0, 170.0))
        self.assertFalse(rec["target_met"])
        self.assertFalse(rec["target_met_recorded"])
        self.assertIn("verify", [x["kind"] for x in self.attempts()])

    def test_verify_refuses_non_best_head(self):
        self.ready()
        self.commit({"src/impl.py": "N=170\n"})
        self.assertEqual(self.run_v("verify").returncode, 3)


class TestRenew(Harness):
    def test_renew_records_previous_contract(self):
        self.init()
        self.assertIsNone(self.contract()["renewed_from"])
        old_created = self.contract()["created"]
        r = self.init("--renew")
        self.assertEqual(r.returncode, 0, r.stderr)
        rf = self.contract()["renewed_from"]
        self.assertEqual((rf["created"], rf["scenario"]), (old_created, "optimization"))


class TestHigherDirection(Harness):
    init_extra = ["--score-regex", r"rps=([0-9.]+)", "--unit", "req/s", "--direction", "higher",
                  "--delta", "10", "--target", "1000"]

    def seed(self):
        write(self.repo, "src/impl.py", "N=800\n")
        write(self.repo, "bench/run.py", BENCH.replace("p95=", "rps="))

    def test_higher_direction(self):
        self.ready()
        self.assertFalse(self.status()["target_met"])
        code, rec = self.attempt({"src/impl.py": "N=805\n"})
        self.assertEqual((code, rec["verdict"]), (1, "rejected"))
        code, rec = self.attempt({"src/impl.py": "N=820\n"})
        self.assertEqual((code, rec["verdict"]), (0, "accepted"))
        code, rec = self.attempt({"src/impl.py": "N=1000\n"})
        self.assertEqual(code, 0)
        self.assertTrue(self.status()["target_met"])


class TestBugfix(Harness):
    scenario = "bugfix"

    def seed(self):
        write(self.repo, "src/impl.py", "\n")
        write(self.repo, "tests/test_x.py",
              'import sys; sys.path.insert(0, "src"); import impl\nassert impl.add(1, 2) == 3\n')

    def test_bugfix_requires_test_cmd(self):
        r = self.init(frozen="tests", test_cmd=None)
        self.assertEqual(r.returncode, 3)

    def test_bugfix_requires_frozen(self):
        r = self.init(frozen=None, test_cmd="python3 tests/test_x.py")
        self.assertEqual(r.returncode, 3)

    def test_bugfix_scenario(self):
        r = self.init(frozen="tests", test_cmd="python3 tests/test_x.py")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(self.contract()["baseline"]["passed"])
        self.start()
        head = self.commit({"src/impl.py": "def add(a, b):\n    return a - b\n"})
        code, rec = self.attempt()
        self.assertEqual((code, rec["verdict"]), (1, "failing"))
        self.assertEqual(git(self.wt, "rev-parse", "HEAD"), head)
        self.assertEqual(self.contract()["best"], head)
        self.assertEqual(self.status()["decision"], "continue")
        code, rec = self.attempt({"src/impl.py": "def add(a, b):\n    return a + b\n"})
        self.assertEqual((code, rec["verdict"]), (0, "accepted"))
        s = self.status()
        self.assertEqual((s["decision"], s["all_tests_pass"]), ("handoff", True))
        r = self.run_v("report")
        self.assertEqual(r.returncode, 0, r.stderr)
        manifest = json.loads(r.stdout)
        with open(manifest["handoff"]) as f:
            table = f.read()
        self.assertIn("fail (exit 1)", table)
        self.assertIn("pass (exit 0)", table)
        self.assertIn("Agreed test runs", table)

    def test_bugfix_verify(self):
        self.init(frozen="tests", test_cmd="python3 tests/test_x.py")
        self.start()
        r = self.run_v("verify")
        self.assertEqual(r.returncode, 2)
        self.assertEqual(json.loads(r.stdout)["verdict"], "failed")
        self.attempt({"src/impl.py": "def add(a, b):\n    return a + b\n"})
        r = self.run_v("verify")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["verdict"], "verified")

    def test_bugfix_rejects_baseline_that_already_passes(self):
        write(self.repo, "src/impl.py", "def add(a, b):\n    return a + b\n")
        git(self.repo, "commit", "-qam", "already fixed")
        r = self.init(frozen="tests", test_cmd="python3 tests/test_x.py")
        self.assertEqual(r.returncode, 3)
        self.assertIn("must fail", r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.home, "contract.json")))

    def test_rolled_back_attempt_keeps_passing_state(self):
        self.init(frozen="tests", test_cmd="python3 tests/test_x.py")
        self.start()
        self.attempt({"src/impl.py": "def add(a, b):\n    return a + b\n"})
        code, rec = self.attempt({"README_x.md": "x\n"})
        self.assertEqual(rec["verdict"], "invalid")
        s = self.status()
        self.assertEqual((s["decision"], s["all_tests_pass"]), ("handoff", True))

    def test_bugfix_frozen_test_edit_is_invalid(self):
        self.init(frozen="tests", test_cmd="python3 tests/test_x.py")
        self.start()
        code, rec = self.attempt({"tests/test_x.py": "pass\n", "src/impl.py": "x=1\n"})
        self.assertEqual((code, rec["verdict"]), (2, "invalid"))
        self.assertIn("assert impl.add", self.read("tests/test_x.py"))


def diag(nodes, edges=None, depends=None):
    spec = {"meta": {"title": "test"}, "nodes": [{"id": n} for n in nodes]}
    if edges:
        spec["edges"] = [{"from": a, "to": b} for a, b in edges]
    if depends:
        spec["depends"] = depends
    return json.dumps(spec)


BLUEPRINT = diag(["user_service", "billing_api"], [("user_service", "billing_api")])
ASIS = diag(["legacy", "db"], [("legacy", "db")])
ASBUILT = diag(["user_service", "billing_api", "ledger"],
               [("user_service", "billing_api"), ("billing_api", "ledger")])


class TestDevelopment(Harness):
    scenario = "development"
    check = "python3 checks/run.py"

    def seed(self):
        write(self.repo, "docs/blueprint.json", BLUEPRINT)
        write(self.repo, "docs/asis.json", ASIS)
        write(self.repo, "src/impl.py", "OK=False\n")
        write(self.repo, "checks/run.py",
              'import sys; sys.path.insert(0, "src"); import impl\nassert impl.OK\n')

    def init_dev(self, *extra, check=None, asbuilt="src/asbuilt.json", frozen=None, test_cmd=None):
        args = ["--blueprint", "docs/blueprint.json", "--asis", "docs/asis.json",
                "--asbuilt", asbuilt]
        if check:
            args += ["--check-cmd", check]
        return self.init(*args, *extra, frozen=frozen, test_cmd=test_cmd)

    def test_init_stores_elements_and_freezes_docs(self):
        r = self.init_dev()
        self.assertEqual(r.returncode, 0, r.stderr)
        c = self.contract()
        self.assertEqual(c["elements"], ["user_service", "billing_api"])
        self.assertIn("docs/blueprint.json", c["frozen"])
        self.assertIn("docs/asis.json", c["frozen"])
        self.assertEqual(c["asbuilt"], "src/asbuilt.json")
        self.assertIsNone(c["check_cmd"])
        self.assertEqual(c["baseline"]["blueprint"], "docs/blueprint.json")
        self.assertEqual(c["baseline"]["asis"], "docs/asis.json")
        for name in ("blueprint", "asis"):
            self.assertTrue(os.path.exists(os.path.join(self.home, name + ".json")))
            with open(os.path.join(self.home, name + ".html")) as f:
                self.assertIn("<svg", f.read())

    def test_init_dies_on_invalid_blueprint(self):
        write(self.repo, "docs/blueprint.json", "graph TD\na --> b\n")
        git(self.repo, "commit", "-qam", "not json")
        r = self.init_dev()
        self.assertEqual(r.returncode, 3)

    def test_asbuilt_outside_editable_dies(self):
        r = self.init_dev(asbuilt="docs/asbuilt.json")
        self.assertEqual(r.returncode, 3)

    def test_init_rejects_test_cmd(self):
        r = self.init_dev(test_cmd="true")
        self.assertEqual(r.returncode, 3)
        self.assertIn("--check-cmd", r.stderr)

    def test_checkpoint_verdict_keeps_commit(self):
        self.init_dev()
        self.start()
        head = self.commit({"src/note.py": "x=1\n"})
        code, rec = self.attempt()
        self.assertEqual((code, rec["verdict"]), (1, "checkpoint"))
        self.assertNotIn("raw", rec)
        self.assertEqual(git(self.wt, "rev-parse", "HEAD"), head)
        self.assertEqual(self.contract()["best"], head)

    def test_green_and_failing_via_check_cmd(self):
        r = self.init_dev(check=self.check)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.contract()["baseline"]["exit"], 1)
        self.start()
        code, rec = self.attempt({"src/impl.py": "OK=False  # still\n"})
        self.assertEqual((code, rec["verdict"]), (1, "failing"))
        self.assertIn("raw", rec)
        code, rec = self.attempt({"src/impl.py": "OK=True\n"})
        self.assertEqual((code, rec["verdict"], rec["passed"]), (0, "green", True))

    def test_frozen_edit_is_invalid_and_rolled_back(self):
        self.init_dev()
        self.start()
        head = git(self.wt, "rev-parse", "HEAD")
        code, rec = self.attempt({"docs/asis.json": "changed\n", "src/impl.py": "x=1\n"})
        self.assertEqual((code, rec["verdict"]), (2, "invalid"))
        self.assertIn("docs/asis.json", rec["files"])
        self.assertEqual(git(self.wt, "rev-parse", "HEAD"), head)
        self.assertEqual(self.read("docs/asis.json"), ASIS)
        self.assertTrue(self.clean())

    def test_status_gates_on_asbuilt_elements_and_check(self):
        self.init_dev(check=self.check)
        self.start()
        self.attempt({"src/impl.py": "OK=True\n"}, "", None, "--elements", "user_service", "billing_api")
        s = self.status()
        self.assertFalse(s["asbuilt_exists"])
        self.assertEqual(s["decision"], "continue")
        code, rec = self.attempt({"src/asbuilt.json": diag(["user_service"])})
        self.assertEqual((code, rec["verdict"]), (0, "green"))
        s = self.status()
        self.assertTrue(s["asbuilt_exists"])
        self.assertEqual(s["elements_missing"], ["billing_api"])
        self.assertEqual(s["decision"], "continue")
        self.attempt({"src/asbuilt.json": ASBUILT})
        s = self.status()
        self.assertEqual(s["elements_missing"], [])
        self.assertTrue(s["check_green"])
        self.assertEqual(s["decision"], "handoff")

    def test_status_handoff_without_check_cmd(self):
        self.init_dev()
        self.start()
        self.attempt({"src/asbuilt.json": ASBUILT})
        s = self.status()
        self.assertEqual(s["decision"], "continue")
        self.assertEqual(s["elements_ready"], ["user_service", "billing_api"])
        self.attempt({"src/impl.py": "x=1\n"}, "", None, "--elements", "user_service", "billing_api")
        s = self.status()
        self.assertTrue(s["check_green"])
        self.assertEqual(s["elements_done"], ["user_service", "billing_api"])
        self.assertEqual(s["decision"], "handoff")

    def test_verify_without_check_cmd_dies(self):
        self.init_dev()
        self.start()
        self.assertEqual(self.run_v("verify").returncode, 3)

    def test_rolled_back_attempt_keeps_green_state(self):
        self.init_dev(check=self.check)
        self.start()
        self.attempt({"src/impl.py": "OK=True\n", "src/asbuilt.json": ASBUILT}, "", None,
                     "--elements", "user_service", "billing_api")
        code, rec = self.attempt({"docs/asis.json": "x\n"})
        self.assertEqual(rec["verdict"], "invalid")
        s = self.status()
        self.assertTrue(s["check_green"])
        self.assertEqual(s["decision"], "handoff")
        self.assertIn("verify", s["next"])

    def test_init_rejects_blueprint_without_new_elements(self):
        write(self.repo, "docs/asis.json", diag(["user_service", "billing_api"],
                                                [("user_service", "billing_api")]))
        git(self.repo, "commit", "-qam", "asis covers all")
        r = self.init_dev()
        self.assertEqual(r.returncode, 3)
        self.assertIn("new IDs", r.stderr)

    def test_init_records_new_elements(self):
        self.init_dev()
        self.assertEqual(self.contract()["elements_new"], ["user_service", "billing_api"])

    def test_copied_blueprint_does_not_hand_off(self):
        self.init_dev()
        self.start()
        self.attempt({"src/asbuilt.json": BLUEPRINT})
        s = self.status()
        self.assertTrue(s["asbuilt_copies_blueprint"])
        self.assertEqual(s["elements_missing"], [])
        self.assertEqual(s["decision"], "continue")

    def test_report_writes_handoff_html(self):
        self.init_dev(check=self.check)
        self.start()
        self.attempt({"src/impl.py": "OK=True\n", "src/asbuilt.json": ASBUILT}, "", None,
                     "--elements", "user_service")
        commit = self.contract()["best"][:10]
        r = self.run_v("report")
        self.assertEqual(r.returncode, 0, r.stderr)
        manifest = json.loads(r.stdout)
        self.assertEqual(manifest["handoff"], os.path.join(self.home, "handoff.html"))
        self.assertIn("open", manifest)
        with open(manifest["handoff"]) as f:
            text = f.read()
        for needle in ("Agreed blueprint", "As-built (delivered)", "Element coverage",
                       "Build order", "Dependency graph", "<svg", "user_service",
                       "billing_api", commit, "not realized", self.check):
            self.assertIn(needle, text)


BLUEPRINT_DEP = diag(["store", "api", "ui"], [("ui", "api"), ("api", "store")],
                     {"api": ["store"], "ui": ["api"]})


def with_depends(text, depends):
    spec = json.loads(text)
    spec.setdefault("depends", {}).update(depends)
    return json.dumps(spec)


class TestBlueprintOrder(Harness):
    scenario = "development"
    check = TestDevelopment.check

    def seed(self):
        write(self.repo, "docs/blueprint.json", BLUEPRINT_DEP)
        write(self.repo, "docs/asis.json", ASIS)
        write(self.repo, "src/impl.py", "OK=False\n")
        write(self.repo, "checks/run.py",
              'import sys; sys.path.insert(0, "src"); import impl\nassert impl.OK\n')

    init_dev = TestDevelopment.init_dev

    def claim(self, files, *elements):
        return self.attempt(files, "", None, "--elements", *elements)

    def test_init_records_depends_and_batches(self):
        self.assertEqual(self.init_dev().returncode, 0)
        c = self.contract()
        self.assertEqual(c["depends"], {"api": ["store"], "ui": ["api"]})
        self.assertEqual(c["batches"], [["store"], ["api"], ["ui"]])

    def test_cycle_dies(self):
        write(self.repo, "docs/blueprint.json", with_depends(BLUEPRINT_DEP, {"store": ["ui"]}))
        git(self.repo, "commit", "-qam", "cycle")
        r = self.init_dev()
        self.assertEqual(r.returncode, 3)
        self.assertIn("cycle", r.stderr)

    def test_unknown_dependency_dies(self):
        write(self.repo, "docs/blueprint.json", with_depends(BLUEPRINT_DEP, {"api": ["cache"]}))
        git(self.repo, "commit", "-qam", "unknown")
        r = self.init_dev()
        self.assertEqual(r.returncode, 3)
        self.assertIn("cache", r.stderr)

    def test_claim_with_unmet_dependency_is_refused(self):
        self.init_dev()
        self.start()
        head = self.commit({"src/api.py": "x=1\n"})
        r = self.run_v("attempt", "--elements", "api")
        self.assertEqual(r.returncode, 3)
        self.assertIn("store", r.stderr)
        self.assertEqual(git(self.wt, "rev-parse", "HEAD"), head)
        code, rec = self.claim(None, "store", "api")
        self.assertEqual((code, rec["elements"]), (1, ["store", "api"]))

    def test_progress_follows_dependency_order(self):
        self.init_dev()
        self.start()
        s = self.status()
        self.assertEqual((s["elements_ready"], s["elements_blocked"]), (["store"], ["api", "ui"]))
        self.claim({"src/store.py": "x=1\n"}, "store")
        s = self.status()
        self.assertEqual((s["elements_done"], s["elements_ready"]), (["store"], ["api"]))
        self.assertIn("--elements: api", s["next"])

    def test_failing_claim_is_pending_until_green(self):
        self.init_dev(check=self.check)
        self.start()
        code, rec = self.claim({"src/store.py": "x=1\n"}, "store")
        self.assertEqual(rec["verdict"], "failing")
        s = self.status()
        self.assertEqual((s["elements_done"], s["elements_pending"]), ([], ["store"]))
        self.assertEqual(self.run_v("attempt", "--elements", "api").returncode, 3)
        self.attempt({"src/impl.py": "OK=True\n"})
        self.assertEqual(self.status()["elements_done"], ["store"])

    def test_report_lists_build_order_and_dependencies(self):
        self.init_dev()
        self.start()
        self.claim({"src/store.py": "x=1\n"}, "store")
        self.assertEqual(self.run_v("report").returncode, 0)
        with open(os.path.join(self.home, "handoff.html")) as f:
            text = f.read()
        self.assertIn("<code>store</code>", text)
        self.assertIn("not realized", text)
        self.assertIn("Dependency graph", text)
        self.assertIn("<svg", text)


class TestHygiene(Harness):
    def init_with_home(self, home):
        return sh(self.root, sys.executable, SCRIPT, "--home", home,
                  "init", "--repo", self.repo, "--scenario", "optimization",
                  "--editable", "src", "--frozen", "bench",
                  "--test-cmd", "python3 bench/run.py", *self.budget, *self.init_extra)

    def test_home_outside_runs_dies(self):
        for home in (os.path.join(self.repo, "contracts"),
                     os.path.join(self.root, "home"),
                     os.path.join(self.repo, ".autodev"),
                     os.path.join(self.repo, ".autodev", "contracts"),
                     os.path.join(self.repo, ".autodev", "runs")):
            r = self.init_with_home(home)
            self.assertEqual(r.returncode, 3, home)
            self.assertIn("runs", r.stderr)

    def test_home_inside_worktree_dies_at_start(self):
        git(self.repo, "worktree", "add", "-q", "-b", "autodev/t", self.wt, "HEAD")
        self.assertEqual(self.init().returncode, 0)
        home = os.path.join(self.wt, ".autodev", "runs", "t")
        os.makedirs(home, exist_ok=True)
        shutil.copy(os.path.join(self.home, "contract.json"),
                    os.path.join(home, "contract.json"))
        r = sh(self.root, sys.executable, SCRIPT, "--home", home,
               "start", "--worktree", self.wt)
        self.assertEqual(r.returncode, 3)
        self.assertIn("worktree", r.stderr)

    def test_autodev_dir_is_excluded_per_clone(self):
        r = self.init()
        self.assertEqual(r.returncode, 0, r.stderr)
        git_dir = git(self.repo, "rev-parse", "--absolute-git-dir")
        with open(os.path.join(git_dir, "info", "exclude")) as f:
            self.assertIn("/.autodev/", f.read().splitlines())
        status = git(self.repo, "status", "--porcelain")
        self.assertNotIn(".autodev", status)
        write(self.repo, "sub/.autodev/marker", "x\n")
        self.assertIn("sub", git(self.repo, "status", "--porcelain"))

    def test_worktree_autodev_is_refused(self):
        self.ready()
        write(self.wt, ".autodev/stash.txt", "x\n")
        self.assertFalse(git(self.wt, "status", "--porcelain"))
        self.commit({"src/impl.py": "N=150\n"})
        r = self.run_v("attempt", "--route", "x")
        self.assertEqual(r.returncode, 3)
        self.assertIn(".autodev", r.stderr)
        st = json.loads(self.run_v("status").stdout)
        self.assertFalse(st["worktree_clean"])
        self.assertEqual(st["hidden_ignored"], [".autodev/"])
        self.assertIn("delete", st["next"])
        r = self.run_v("verify")
        self.assertEqual(r.returncode, 3)
        self.assertIn(".autodev/", r.stderr)

    def test_init_in_linked_worktree_dies(self):
        git(self.repo, "worktree", "add", "-q", "-b", "autodev/other", self.wt, "HEAD")
        home = os.path.join(self.wt, ".autodev", "runs", "t")
        r = sh(self.root, sys.executable, SCRIPT, "--home", home,
               "init", "--repo", self.wt, "--scenario", "optimization",
               "--editable", "src", "--frozen", "bench",
               "--test-cmd", "python3 bench/run.py", *self.budget, *self.init_extra)
        self.assertEqual(r.returncode, 3)
        self.assertIn("working clone", r.stderr)
        self.assertIn("linked worktree", r.stderr)

    def clone_repo(self, name="repo2"):
        dst = os.path.join(self.root, name)
        git(self.root, "clone", "-q", self.repo, dst)
        return dst

    def move_home(self, repo2):
        shutil.move(os.path.join(self.repo, ".autodev"), repo2)
        return os.path.join(repo2, ".autodev", "runs", "t")

    def relocate(self, home, repo, *extra):
        return sh(self.root, sys.executable, SCRIPT, "--home", home,
                  "relocate", "--repo", repo, *extra)

    def test_relocate_repoints_clone(self):
        self.assertEqual(self.init().returncode, 0)
        repo2 = self.clone_repo()
        home2 = self.move_home(repo2)
        self.assertIn(".autodev", git(repo2, "status", "--porcelain"))
        r = self.relocate(home2, repo2)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.home = home2
        self.assertEqual(self.contract()["repo"], repo2)
        git_dir = git(repo2, "rev-parse", "--absolute-git-dir")
        with open(os.path.join(git_dir, "info", "exclude")) as f:
            self.assertIn("/.autodev/", f.read().splitlines())
        self.assertNotIn(".autodev", git(repo2, "status", "--porcelain"))

    def test_relocate_requires_run_dir_in_new_clone(self):
        self.assertEqual(self.init().returncode, 0)
        r = self.relocate(self.home, self.clone_repo())
        self.assertEqual(r.returncode, 3)
        self.assertIn("runs", r.stderr)

    def test_relocate_same_clone_dies(self):
        self.assertEqual(self.init().returncode, 0)
        r = self.relocate(self.home, self.repo)
        self.assertEqual(r.returncode, 3)
        self.assertIn("already", r.stderr)

    def test_relocate_to_linked_worktree_dies(self):
        self.assertEqual(self.init().returncode, 0)
        repo2 = self.clone_repo()
        wt2 = os.path.join(self.root, "wt2")
        git(repo2, "worktree", "add", "-q", "-b", "x", wt2, "HEAD")
        r = self.relocate(self.home, wt2)
        self.assertEqual(r.returncode, 3)
        self.assertIn("linked worktree", r.stderr)

    def test_relocate_constitution_must_match(self):
        write(self.repo, ".autodev/constitution.json", json.dumps({"frozen": ["bench"]}))
        self.assertEqual(self.init().returncode, 0)
        repo2 = self.clone_repo()
        home2 = self.move_home(repo2)
        write(repo2, ".autodev/constitution.json", json.dumps({"frozen": ["src"]}))
        r = self.relocate(home2, repo2)
        self.assertEqual(r.returncode, 3)
        self.assertIn("constitution", r.stderr)
        write(repo2, ".autodev/constitution.json", json.dumps({"frozen": ["bench"]}))
        r = self.relocate(home2, repo2)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_relocate_requires_best_commit_and_repoints_worktree(self):
        self.ready()
        repo2 = self.clone_repo()
        code, _ = self.attempt({"src/impl.py": "N=150\n"})
        self.assertEqual(code, 0)
        home2 = self.move_home(repo2)
        r = self.relocate(home2, repo2)
        self.assertEqual(r.returncode, 3)
        self.assertIn("best commit", r.stderr)
        git(repo2, "fetch", "-q", self.repo, "autodev/t")
        r = self.relocate(home2, repo2, "--worktree", self.wt)
        self.assertEqual(r.returncode, 3)
        self.assertIn("different clone", r.stderr)
        wt2 = os.path.join(self.root, "wt2")
        git(repo2, "worktree", "add", "-q", wt2, "FETCH_HEAD")
        r = self.relocate(home2, repo2, "--worktree", wt2)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.home = home2
        c = self.contract()
        self.assertEqual((c["repo"], c["worktree"]), (repo2, wt2))
        r = self.run_v("status")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_relocate_worktree_must_not_be_the_clone(self):
        self.ready()
        repo2 = self.clone_repo()
        home2 = self.move_home(repo2)
        r = self.relocate(home2, repo2, "--worktree", repo2)
        self.assertEqual(r.returncode, 3)
        self.assertIn("working clone", r.stderr)

    def test_relocate_worktree_must_contain_best(self):
        self.ready()
        repo2 = self.clone_repo()
        code, _ = self.attempt({"src/impl.py": "N=150\n"})
        self.assertEqual(code, 0)
        home2 = self.move_home(repo2)
        git(repo2, "fetch", "-q", self.repo, "autodev/t")
        wt2 = os.path.join(self.root, "wt2")
        git(repo2, "worktree", "add", "-q", wt2, "HEAD")
        r = self.relocate(home2, repo2, "--worktree", wt2)
        self.assertEqual(r.returncode, 3)
        self.assertIn("does not contain", r.stderr)

    def test_relocate_warns_when_branch_from_missing(self):
        self.assertEqual(self.init().returncode, 0)
        bf = self.contract()["branch_from"]
        repo2 = self.clone_repo()
        home2 = self.move_home(repo2)
        git(repo2, "branch", "-m", bf, "renamed")
        r = self.relocate(home2, repo2)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(bf, r.stderr)
        self.assertIn("does not exist", r.stderr)

    def bench_writes_artifacts(self):
        write(self.repo, "bench/run.py",
              'import sys, os; sys.dont_write_bytecode = True\n'
              'sys.path.insert(0, "src"); import impl\n'
              'os.makedirs("artifacts", exist_ok=True)\n'
              'open("artifacts/bench.log", "w").write("x")\n'
              'print("p95=" + str(impl.N))\n')
        git(self.repo, "commit", "-qam", "bench writes artifacts")

    def test_baseline_side_effects_recorded(self):
        self.bench_writes_artifacts()
        r = self.init()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("artifacts/", self.contract()["baseline"]["side_effects"])
        self.assertIn("left changes", r.stderr)

    def test_baseline_mutating_frozen_dies(self):
        write(self.repo, "bench/run.py",
              'import sys; sys.path.insert(0, "src"); import impl\n'
              'open("bench/run.py", "a").write("# touched\\n")\n'
              'print("p95=" + str(impl.N))\n')
        git(self.repo, "commit", "-qam", "self-mutating bench")
        r = self.init()
        self.assertEqual(r.returncode, 3)
        self.assertIn("frozen", r.stderr)

    def test_generated_paths_are_not_dirty(self):
        self.bench_writes_artifacts()
        r = self.init("--generated", "artifacts")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.start()
        code, rec = self.attempt({"src/impl.py": "N=170\n"})
        self.assertEqual((code, rec["verdict"]), (0, "accepted"))
        self.assertTrue(json.loads(self.run_v("status").stdout)["worktree_clean"])
        write(self.wt, "src/impl.py", "N=150\n")
        git(self.wt, "add", "src/impl.py")
        git(self.wt, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x")
        code, rec = self.attempt()
        self.assertEqual((code, rec["verdict"]), (0, "accepted"))

    def test_undeclared_artifacts_block_with_hint(self):
        self.bench_writes_artifacts()
        self.ready()
        self.attempt({"src/impl.py": "N=170\n"})
        write(self.wt, "src/impl.py", "N=160\n")
        git(self.wt, "add", "src/impl.py")
        git(self.wt, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x")
        r = self.run_v("attempt", "--route", "x")
        self.assertEqual(r.returncode, 3)
        self.assertIn("--generated", r.stderr)

    def test_committed_generated_files_are_invalid(self):
        self.ready("--generated", "artifacts")
        code, rec = self.attempt({"src/impl.py": "N=150\n", "artifacts/out.txt": "x\n"})
        self.assertEqual((code, rec["verdict"]), (2, "invalid"))
        self.assertIn("artifacts/out.txt", rec["files"])
        self.assertIn("artifact", rec["reason"])
        self.assertEqual(self.read("src/impl.py"), "N=200\n")
        self.assertTrue(self.clean())

    def test_generated_overlapping_frozen_dies(self):
        r = self.init("--generated", "bench/out")
        self.assertEqual(r.returncode, 3)
        self.assertIn("overlap", r.stderr)


class TestApprovalGate(Harness):
    def test_approve_before_start_dies(self):
        self.assertEqual(self.init().returncode, 0)
        r = self.run_v("approve")
        self.assertEqual(r.returncode, 3)
        self.assertIn("not started", r.stderr)

    def test_handoff_waits_for_approval(self):
        self.ready()
        code, _ = self.attempt({"src/impl.py": "N=150\n"})
        self.assertEqual(code, 0)
        s = self.status()
        self.assertEqual(s["decision"], "handoff")
        self.assertIsNone(s["approved"])
        self.assertIn("approve", s["next"])
        self.assertNotIn("merge the loop branch", s["next"])
        self.assertEqual(self.run_v("verify").returncode, 0)
        self.assertEqual(self.run_v("report").returncode, 0)
        r = self.run_v("approve", "--note", "looks right")
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = json.loads(r.stdout)
        self.assertEqual(rec["note"], "looks right")
        self.assertIn("at", rec)
        s = self.status()
        self.assertEqual(s["approved"]["note"], "looks right")
        self.assertIn("merge the loop branch", s["next"])

    def test_new_attempt_stales_approval(self):
        self.ready()
        code, _ = self.attempt({"src/impl.py": "N=150\n"})
        self.assertEqual(code, 0)
        self.assertEqual(self.run_v("approve").returncode, 0)
        code, _ = self.attempt({"src/impl.py": "N=130\n"})
        self.assertEqual(code, 0)
        self.assertIsNone(self.contract().get("approved"))
        self.assertIsNone(self.status()["approved"])


class TestContractIntegrity(Harness):
    def rewrite(self, **fields):
        c = self.contract()
        c.update(fields)
        with open(os.path.join(self.home, "contract.json"), "w") as f:
            json.dump(c, f)

    def test_tampered_agreement_is_refused(self):
        self.ready()
        path = os.path.join(self.home, "contract.json")
        with open(path) as f:
            original = f.read()
        for field, value in (("target", 0), ("editable", ["src", "x"]), ("test_cmd", "true")):
            self.rewrite(**{field: value})
            for cmd in (("status",), ("attempt", "--route", "x"), ("verify",)):
                r = self.run_v(*cmd)
                self.assertEqual(r.returncode, 3, (field, cmd))
                self.assertIn("init --renew", r.stderr)
            with open(path, "w") as f:
                f.write(original)
        self.assertEqual(self.run_v("status").returncode, 0)

    def test_tampered_sealed_state_is_refused(self):
        self.ready()
        self.rewrite(deadline="2999-01-01T00:00:00+00:00")
        r = self.run_v("status")
        self.assertEqual(r.returncode, 3)
        self.assertIn("init --renew", r.stderr)

    def test_renew_reseals(self):
        self.ready()
        r = self.init("--renew")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.run_v("status").returncode, 0)


if __name__ == "__main__":
    unittest.main()
