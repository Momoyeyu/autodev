import os
import re
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
SCRIPT = os.path.join(ROOT, "autodev", "scripts", "autodev_verify.py")

SKILL_DOCS = [os.path.join(ROOT, "autodev", "SKILL.md"),
              os.path.join(ROOT, "README.md"),
              os.path.join(ROOT, "README_ZH.md")]
SKILL_DOCS += sorted(
    os.path.join(ROOT, "autodev", "references", f)
    for f in os.listdir(os.path.join(ROOT, "autodev", "references"))
    if f.endswith(".md"))
ALL_DOCS = SKILL_DOCS + [os.path.join(ROOT, "CONTRIBUTING.md")]

FORBIDDEN = [re.compile(p, re.I) for p in
             (r"mermaid", r"report_chart", r"\.autodev/run(?!s)",
              r"BLUEPRINT\.md", r"principles\.md", r"commits the file")]

GIT_FLAGS = {"--porcelain", "--ignored", "--git-dir", "--git-common-dir",
             "--absolute-git-dir", "--is-inside-work-tree", "--show-toplevel",
             "--abbrev-ref", "--name-only", "--hard", "--cached", "--check",
             "--force", "--quiet", "--list", "--set-upstream"}


def judge_flags():
    with open(SCRIPT) as f:
        return set(re.findall(r'add_argument\("(--[a-z][a-z-]*)"', f.read()))


class TestForbiddenTerms(unittest.TestCase):
    def test_no_resurrected_terms(self):
        for doc in ALL_DOCS:
            with open(doc) as f:
                text = f.read()
            for pat in FORBIDDEN:
                self.assertIsNone(pat.search(text),
                                  f"{pat.pattern!r} found in {os.path.relpath(doc, ROOT)}")


class TestDocumentedFlags(unittest.TestCase):
    def test_flags_exist_in_judge(self):
        known = judge_flags() | GIT_FLAGS
        for doc in SKILL_DOCS:
            with open(doc) as f:
                for flag in set(re.findall(r"--[a-z][a-z-]+", f.read())):
                    self.assertIn(flag, known,
                                  f"{flag} in {os.path.relpath(doc, ROOT)} is not a judge flag")


class TestReadmeParity(unittest.TestCase):
    def levels(self, name):
        with open(os.path.join(ROOT, name)) as f:
            return [m.group(1) for m in
                    (re.match(r"(#{1,6}) ", line) for line in f) if m]

    def test_heading_structure_matches(self):
        self.assertEqual(self.levels("README.md"), self.levels("README_ZH.md"))

    def test_table_columns_match(self):
        def tables(name):
            with open(os.path.join(ROOT, name)) as f:
                return [len(l.split("|")) - 2 for l in f
                        if l.startswith("|") and set(l) - {"|", "-", " ", ":"}]

        self.assertEqual(tables("README.md"), tables("README_ZH.md"))


if __name__ == "__main__":
    unittest.main()
