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
    budget = ["--budget-minutes", "0.05", "--reserve-minutes", "0.03"]

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
        with open(os.path.join(self.home, "comparison.md")) as f:
            table = f.read()
        self.assertIn("| fail (exit 1) | pass (exit 0) |", table)

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

    def test_bugfix_frozen_test_edit_is_invalid(self):
        self.init(frozen="tests", test_cmd="python3 tests/test_x.py")
        self.start()
        code, rec = self.attempt({"tests/test_x.py": "pass\n", "src/impl.py": "x=1\n"})
        self.assertEqual((code, rec["verdict"]), (2, "invalid"))
        self.assertIn("assert impl.add", self.read("tests/test_x.py"))


BLUEPRINT = ("graph TD\n%% autodev-elements: user_service, billing_api\n"
             "user_service --> billing_api\n")
ASIS = "graph TD\nlegacy --> db\n"


class TestDevelopment(Harness):
    scenario = "development"
    check = "python3 checks/run.py"

    def seed(self):
        write(self.repo, "docs/blueprint.md", BLUEPRINT)
        write(self.repo, "docs/asis.md", ASIS)
        write(self.repo, "src/impl.py", "OK=False\n")
        write(self.repo, "checks/run.py",
              'import sys; sys.path.insert(0, "src"); import impl\nassert impl.OK\n')

    def init_dev(self, *extra, check=None, asbuilt="src/asbuilt.md", frozen=None, test_cmd=None):
        args = ["--blueprint", "docs/blueprint.md", "--asis", "docs/asis.md",
                "--asbuilt", asbuilt]
        if check:
            args += ["--check-cmd", check]
        return self.init(*args, *extra, frozen=frozen, test_cmd=test_cmd)

    def test_init_stores_elements_and_freezes_docs(self):
        r = self.init_dev()
        self.assertEqual(r.returncode, 0, r.stderr)
        c = self.contract()
        self.assertEqual(c["elements"], ["user_service", "billing_api"])
        self.assertIn("docs/blueprint.md", c["frozen"])
        self.assertIn("docs/asis.md", c["frozen"])
        self.assertEqual(c["asbuilt"], "src/asbuilt.md")
        self.assertIsNone(c["check_cmd"])
        self.assertEqual(c["baseline"]["blueprint"], "docs/blueprint.md")
        self.assertEqual(c["baseline"]["asis"], "docs/asis.md")
        self.assertTrue(os.path.exists(os.path.join(self.home, "blueprint.md")))
        self.assertTrue(os.path.exists(os.path.join(self.home, "asis.md")))

    def test_init_dies_without_elements_line(self):
        write(self.repo, "docs/blueprint.md", "graph TD\na --> b\n")
        git(self.repo, "commit", "-qam", "no elements")
        r = self.init_dev()
        self.assertEqual(r.returncode, 3)

    def test_asbuilt_outside_editable_dies(self):
        r = self.init_dev(asbuilt="docs/asbuilt.md")
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
        code, rec = self.attempt({"docs/asis.md": "changed\n", "src/impl.py": "x=1\n"})
        self.assertEqual((code, rec["verdict"]), (2, "invalid"))
        self.assertIn("docs/asis.md", rec["files"])
        self.assertEqual(git(self.wt, "rev-parse", "HEAD"), head)
        self.assertEqual(self.read("docs/asis.md"), ASIS)
        self.assertTrue(self.clean())

    def test_status_gates_on_asbuilt_elements_and_check(self):
        self.init_dev(check=self.check)
        self.start()
        self.attempt({"src/impl.py": "OK=True\n"})
        s = self.status()
        self.assertFalse(s["asbuilt_exists"])
        self.assertEqual(s["decision"], "continue")
        code, rec = self.attempt({"src/asbuilt.md": "graph TD\nuser_service --> x\n"})
        self.assertEqual((code, rec["verdict"]), (0, "green"))
        s = self.status()
        self.assertTrue(s["asbuilt_exists"])
        self.assertEqual(s["elements_missing"], ["billing_api"])
        self.assertEqual(s["decision"], "continue")
        self.attempt({"src/asbuilt.md": "graph TD\nuser_service --> billing_api\n"})
        s = self.status()
        self.assertEqual(s["elements_missing"], [])
        self.assertTrue(s["check_green"])
        self.assertEqual(s["decision"], "handoff")

    def test_status_handoff_without_check_cmd(self):
        self.init_dev()
        self.start()
        self.attempt({"src/asbuilt.md": "graph TD\nuser_service --> billing_api\n"})
        s = self.status()
        self.assertTrue(s["check_green"])
        self.assertEqual(s["decision"], "handoff")

    def test_verify_without_check_cmd_dies(self):
        self.init_dev()
        self.start()
        self.assertEqual(self.run_v("verify").returncode, 3)

    def test_report_writes_blueprint_handoff(self):
        self.init_dev(check=self.check)
        self.start()
        self.attempt({"src/impl.py": "OK=True\n",
                      "src/asbuilt.md": "graph TD\nuser_service --> billing_api\n"})
        r = self.run_v("report")
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(self.home, "blueprint-handoff.md")) as f:
            text = f.read()
        self.assertIn("## Agreed blueprint", text)
        self.assertIn("```mermaid", text)
        self.assertIn("## As-built (delivered)", text)
        self.assertIn("## Element coverage", text)
        self.assertIn("| `user_service` | yes |", text)
        self.assertIn("| `billing_api` | yes |", text)
        self.assertIn(self.check, text)


if __name__ == "__main__":
    unittest.main()
