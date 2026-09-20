import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGES = ["Define", "Anchor", "Ratchet", "Prove"]


class TerminologyTest(unittest.TestCase):
    def test_skill_uses_canonical_stage_names(self):
        skill = (ROOT / "autodev" / "SKILL.md").read_text(encoding="utf-8")

        for index, stage in enumerate(STAGES):
            self.assertIn(f"## Phase {index} — {stage}", skill)

        old_headings = (
            "## Phase 0 — the contract",
            "## Phase 1 — baseline",
            "## Phase 2 — the loop",
            "## Phase 3 — review",
        )
        for heading in old_headings:
            self.assertNotIn(heading, skill)

    def test_readmes_present_the_same_four_stages(self):
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (ROOT / "README_ZH.md").read_text(encoding="utf-8")

        for stage in STAGES:
            self.assertIn(f"**{stage}**", english)
            self.assertIn(f"**{stage} ·", chinese)

    def test_diagrams_use_the_same_stage_labels(self):
        english = json.loads(
            (ROOT / "docs" / "diagrams" / "autodev.workflow.json").read_text(
                encoding="utf-8"
            )
        )
        chinese = json.loads(
            (ROOT / "docs" / "diagrams" / "autodev.workflow.zh.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual([item["label"] for item in english["boundaries"]], STAGES)
        self.assertEqual(
            [item["label"] for item in chinese["boundaries"]],
            ["Define · 定义", "Anchor · 锚定", "Ratchet · 棘轮", "Prove · 证明"],
        )


if __name__ == "__main__":
    unittest.main()
