import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "evals" / "cases.json"
REQUIRED_FIELDS = {
    "id",
    "title",
    "prompt",
    "context",
    "follow_ups",
    "mode",
    "tags",
    "assertions",
}
REQUIRED_TAGS = {
    "anti-gaming",
    "bugfix",
    "development",
    "optimization",
    "scope",
    "tdd",
}
VALID_MODES = {"development", "optimization", "stop"}
VALID_EVIDENCE = {"commands", "diff", "response", "transcript"}


class EvalCasesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))

    def test_case_ids_are_unique(self):
        ids = [case["id"] for case in self.cases]
        self.assertEqual(len(ids), len(set(ids)))

    def test_cases_have_required_fields(self):
        for case in self.cases:
            with self.subTest(case=case.get("id")):
                self.assertEqual(REQUIRED_FIELDS - case.keys(), set())
                self.assertIn(case["mode"], VALID_MODES)
                self.assertTrue(case["prompt"].strip())
                self.assertTrue(case["context"].strip())
                self.assertTrue(
                    all(follow_up.strip() for follow_up in case["follow_ups"])
                )
                self.assertGreaterEqual(len(case["assertions"]), 2)

    def test_assertions_are_machine_readable(self):
        for case in self.cases:
            assertion_ids = []
            for assertion in case["assertions"]:
                with self.subTest(case=case["id"], assertion=assertion.get("id")):
                    self.assertEqual(
                        {"id", "expect", "evidence", "required"} - assertion.keys(),
                        set(),
                    )
                    self.assertIn(assertion["evidence"], VALID_EVIDENCE)
                    self.assertIsInstance(assertion["required"], bool)
                    self.assertTrue(assertion["expect"].strip())
                    assertion_ids.append(assertion["id"])
            self.assertEqual(len(assertion_ids), len(set(assertion_ids)))

    def test_fixtures_start_green(self):
        for case in self.cases:
            fixture = ROOT / "evals" / "fixtures" / case["id"]
            with self.subTest(case=case["id"]):
                self.assertTrue(fixture.is_dir())
                result = subprocess.run(
                    ["python3", "-m", "unittest", "discover", "-s", "tests", "-v"],
                    cwd=fixture,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_fixture_benchmarks_run(self):
        for case in self.cases:
            fixture = ROOT / "evals" / "fixtures" / case["id"]
            for benchmark in (fixture / "bench").glob("*.py"):
                with self.subTest(case=case["id"], benchmark=benchmark.name):
                    result = subprocess.run(
                        ["python3", str(benchmark.relative_to(fixture))],
                        cwd=fixture,
                        text=True,
                        capture_output=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_suite_covers_core_behaviors(self):
        modes = {case["mode"] for case in self.cases}
        tags = {tag for case in self.cases for tag in case["tags"]}
        self.assertEqual(modes, VALID_MODES)
        self.assertEqual(REQUIRED_TAGS - tags, set())


if __name__ == "__main__":
    unittest.main()
