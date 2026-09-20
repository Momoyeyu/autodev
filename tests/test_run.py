import json
import tempfile
import unittest
from pathlib import Path

from evals.run import build_prompt, clean_artifacts, prepare_case


class EvalRunTest(unittest.TestCase):
    def test_build_prompt_invokes_autodev_explicitly(self):
        case = {"context": "Repository context", "prompt": "Implement the feature"}

        prompt = build_prompt(case)

        self.assertTrue(prompt.startswith("/autodev\n"))
        self.assertIn("Repository context", prompt)
        self.assertIn("Implement the feature", prompt)

    def test_prepare_copies_fixture_and_skill_into_ignored_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = root / "fixture"
            skill = root / "skill"
            artifacts = root / ".autodev-evals"
            fixture.mkdir()
            skill.mkdir()
            (fixture / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
            (skill / "SKILL.md").write_text("# autodev\n", encoding="utf-8")
            case = {
                "id": "sample",
                "title": "Sample",
                "prompt": "Change VALUE",
                "context": "A Python project",
                "follow_ups": [],
            }

            case_dir = prepare_case(case, fixture, skill, artifacts, "run-1")

            workspace = case_dir / "workspace"
            self.assertEqual(
                (workspace / "app.py").read_text(encoding="utf-8"), "VALUE = 1\n"
            )
            installed = workspace / ".devin" / "skills" / "autodev" / "SKILL.md"
            self.assertEqual(installed.read_text(encoding="utf-8"), "# autodev\n")
            manifest = json.loads(
                (case_dir / "manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["case_id"], "sample")
            self.assertTrue((artifacts / ".managed-by-autodev-evals").is_file())

    def test_clean_requires_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory) / ".autodev-evals"
            artifacts.mkdir()
            (artifacts / "keep.txt").write_text("keep", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "managed marker"):
                clean_artifacts(artifacts)

            self.assertTrue(artifacts.exists())

    def test_clean_removes_managed_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory) / ".autodev-evals"
            artifacts.mkdir()
            (artifacts / ".managed-by-autodev-evals").write_text("", encoding="utf-8")
            (artifacts / "run").mkdir()

            clean_artifacts(artifacts)

            self.assertFalse(artifacts.exists())


if __name__ == "__main__":
    unittest.main()
