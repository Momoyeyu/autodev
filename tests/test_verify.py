import json
import os
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
        self.home = os.path.join(self.root, "home")
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
        return self.run_v("init", "--repo", self.repo, "--scenario", scenario or self.scenario,
                          "--editable", editable, "--frozen", frozen, "--test-cmd", test_cmd,
                          *self.budget, *(self.init_extra if (scenario or self.scenario) == "optimization" else []),
                          *extra)

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

    def attempt(self, files=None, note=""):
        if files:
            self.commit(files)
        r = self.run_v("attempt", "--note", note)
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


class TestDevelopment(Harness):
    scenario = "development"

    def seed(self):
        write(self.repo, "src/impl.py", "\n")
        write(self.repo, "tests/test_x.py",
              'import sys; sys.path.insert(0, "src"); import impl\nassert impl.add(1, 2) == 3\n')

    def test_development_scenario(self):
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
        with open(os.path.join(self.home, "comparison.md")) as f:
            table = f.read()
        self.assertIn("| fail (exit 1) | pass (exit 0) |", table)

    def test_development_frozen_test_edit_is_invalid(self):
        self.init(frozen="tests", test_cmd="python3 tests/test_x.py")
        self.start()
        code, rec = self.attempt({"tests/test_x.py": "pass\n", "src/impl.py": "x=1\n"})
        self.assertEqual((code, rec["verdict"]), (2, "invalid"))
        self.assertIn("assert impl.add", self.read("tests/test_x.py"))


if __name__ == "__main__":
    unittest.main()
