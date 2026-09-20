import json
import re
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


class SkillStructureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ROOT / "autodev"
        cls.documents = {
            path.relative_to(cls.root).as_posix(): path.read_text(encoding="utf-8")
            for path in cls.root.rglob("*.md")
        }
        cls.core = cls.documents["SKILL.md"]

    def test_frontmatter_keeps_skill_identity_and_triggers(self):
        frontmatter = self.core.split("---", 2)[1]
        self.assertIn("name: autodev", frontmatter)
        self.assertRegex(frontmatter, r"description: .+")
        for trigger in ("feature", "bug", "refactor", "optimiz"):
            self.assertIn(trigger, frontmatter.lower())

    def test_core_names_both_gates(self):
        self.assertIn("correctness gate", self.core)
        self.assertIn("progress gate", self.core)

    def test_references_use_readme_terminology(self):
        titles = {
            "contracts.md": "# Define: the contract",
            "gate.md": "# Correctness gate: Test-Driven Development",
            "progress-gate.md": "# Progress gate: Anchor, Ratchet, Prove",
            "testing-anti-patterns.md": "# Correctness gate: testing anti-patterns",
            "testing-examples.md": "# Correctness gate: worked examples",
        }
        for name, title in titles.items():
            with self.subTest(reference=name):
                document = self.documents.get(f"references/{name}", "")
                self.assertEqual(document.splitlines()[:1], [title])

    def test_every_reference_has_a_direct_load_trigger(self):
        self.assertIn("Do not preload references", self.core)
        table = self.core.split("## Reference files\n", 1)[1].split("\n## ", 1)[0]
        links = re.findall(r"\[[^\]]+\]\((references/[^)]+\.md)\)", table)
        expected = {name for name in self.documents if name.startswith("references/")}
        self.assertEqual(set(links), expected)
        self.assertEqual(len(links), len(expected))
        for row in table.splitlines():
            if "references/" in row:
                with self.subTest(row=row):
                    self.assertRegex(row.lower(), r"\b(before|during|when|only)\b")

    def test_markdown_links_resolve_and_skill_is_self_contained(self):
        documents = {
            self.root / name: text for name, text in self.documents.items()
        }
        for name in ("README.md", "README_ZH.md", "CONTRIBUTING.md"):
            path = ROOT / name
            documents[path] = path.read_text(encoding="utf-8")
        for path, text in documents.items():
            for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                if re.match(r"[a-z]+:", link):
                    continue
                filename, _, anchor = link.partition("#")
                target = (path.parent / filename).resolve() if filename else path
                with self.subTest(document=str(path.relative_to(ROOT)), link=link):
                    self.assertTrue(target.is_file(), f"Missing link target: {link}")
                    if self.root in path.parents:
                        self.assertIn(self.root, target.parents)
                    if anchor and target.suffix == ".md":
                        headings = re.findall(
                            r"^#+ (.+)$", target.read_text(encoding="utf-8"), re.M
                        )
                        anchors = {
                            re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
                            for heading in headings
                        }
                        self.assertIn(anchor, anchors)

    def test_core_and_package_fit_context_budgets(self):
        sizes = {
            name: len(text.encode("utf-8")) for name, text in self.documents.items()
        }
        self.assertLessEqual(sizes["SKILL.md"], 5500)
        self.assertLessEqual(sum(sizes.values()), 24000)
        self.assertLessEqual(sizes["SKILL.md"] + sizes["references/gate.md"], 10000)

    def test_correctness_gate_keeps_required_checks(self):
        gate = self.documents["references/gate.md"]
        for requirement in (
            "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST",
            "### Verify RED",
            "### Verify GREEN",
            "## Rationalizations",
            "## Red flags",
            "## Prove: completion checklist",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, gate)
        self.assertGreaterEqual(gate.count("- [ ]"), 8)

    def test_core_keeps_anti_gaming_rules_visible(self):
        for rule in (
            "frozen", "hash", "assertion", ".skip", "xfail", "tolerances",
            "workload", "dependencies", "network", "hardware", "best-of-n",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, self.core.lower())

    def test_progress_gate_keeps_log_and_stop_conditions(self):
        progress = self.documents.get("references/progress-gate.md", "")
        self.assertIn("attempt\tcommit\ttests\tmetric\tdelta\tverdict\tnote", progress)
        for condition in ("Budget spent", "Target met", "Converged", "Stuck"):
            self.assertIn(condition, progress)
        self.assertIn("three", progress)
        self.assertIn("four", progress)
        self.assertIn("median", progress)
        self.assertIn("noise", progress)

    def test_development_path_keeps_shared_log_and_acceptance(self):
        for requirement in (
            "root-level TSV",
            "`attempt, commit, tests, metric, delta, verdict, note`",
            "Commit accepted states",
        ):
            with self.subTest(requirement=requirement):
                self.assertTrue(requirement in self.core, requirement)

    def test_conditional_details_do_not_relax_existing_rules(self):
        for name in ("SKILL.md", "references/progress-gate.md"):
            with self.subTest(document=name):
                self.assertTrue("below measured noise" in self.documents[name])
        self.assertTrue("no errors or warnings" in self.documents["references/gate.md"])

    def test_readmes_list_the_complete_skill(self):
        expected = {f"autodev/{name}" for name in self.documents}
        for name in ("README.md", "README_ZH.md"):
            with self.subTest(readme=name):
                text = (ROOT / name).read_text(encoding="utf-8")
                links = re.findall(r"\[[^\]]+\]\((autodev/[^)]+\.md)\)", text)
                self.assertEqual(set(links), expected)

    def test_references_do_not_redefine_the_workflow(self):
        for name, text in self.documents.items():
            with self.subTest(document=name):
                self.assertNotIn("exactly two questions", text.lower())
                self.assertNotIn("it *is* the whole workflow", text)


if __name__ == "__main__":
    unittest.main()
