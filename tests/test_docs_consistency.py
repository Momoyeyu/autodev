import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DOCS = [ROOT / name for name in (
    "README.md", "README_ZH.md", "CONTRIBUTING.md", "autodev/SKILL.md",
    "docs/evaluation.md", "docs/visuals.md", "docs/website-redesign.md",
)] + sorted((ROOT / "autodev/references").glob("*.md"))


class ResourceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in {"src", "href"} and value:
                self.paths.append(value)


class TestResources(unittest.TestCase):
    def test_document_links_resolve(self):
        for doc in DOCS:
            text = doc.read_text()
            parser = ResourceParser()
            parser.feed(text)
            links = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text) + parser.paths
            for link in links:
                url = urlsplit(link)
                if url.scheme or url.netloc or not url.path:
                    continue
                with self.subTest(doc=doc.relative_to(ROOT), link=link):
                    self.assertTrue((doc.parent / unquote(url.path)).is_file())

    def test_readme_svgs_parse(self):
        for path in (ROOT / "docs/assets").glob("*.svg"):
            with self.subTest(path=path.name):
                self.assertEqual(ET.parse(path).getroot().tag, "{http://www.w3.org/2000/svg}svg")


class TestInvocationPolicy(unittest.TestCase):
    def test_codex_requires_explicit_invocation(self):
        text = (ROOT / "autodev/agents/openai.yaml").read_text()
        self.assertRegex(text, r"(?m)^policy:\n[ ]+allow_implicit_invocation: false$")


class TestReadmeParity(unittest.TestCase):
    def levels(self, name):
        return re.findall(r"(?m)^(#{1,6}) ", (ROOT / name).read_text())

    def test_heading_structure_matches(self):
        self.assertEqual(self.levels("README.md"), self.levels("README_ZH.md"))

    def test_table_columns_match(self):
        def tables(name):
            return [len(line.split("|")) - 2
                    for line in (ROOT / name).read_text().splitlines()
                    if line.startswith("|") and set(line) - {"|", "-", " ", ":"}]

        self.assertEqual(tables("README.md"), tables("README_ZH.md"))


if __name__ == "__main__":
    unittest.main()
