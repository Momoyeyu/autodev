import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "autodev", "scripts"))
import autodev_render as render


def spec(**kw):
    base = {"meta": {"title": "t"},
            "nodes": [{"id": "a"}, {"id": "b", "label": "Bee", "sublabel": "sub"},
                      {"id": "c", "kind": "store"}],
            "edges": [{"from": "a", "to": "b", "label": "calls"},
                      {"from": "b", "to": "c", "dashed": True}]}
    base.update(kw)
    return base


def write(tmp, obj):
    path = os.path.join(tmp, "d.json")
    with open(path, "w") as f:
        f.write(obj if isinstance(obj, str) else json.dumps(obj))
    return path


class TestLoadDiagram(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def load(self, obj):
        return render.load_diagram(write(self.tmp.name, obj))

    def test_valid(self):
        self.assertEqual(len(self.load(spec())["nodes"]), 3)

    def test_rejects_non_json(self):
        with self.assertRaises(ValueError):
            self.load("graph TD\na --> b\n")

    def test_rejects_empty_nodes(self):
        with self.assertRaisesRegex(ValueError, "nodes"):
            self.load({"nodes": []})

    def test_rejects_duplicate_ids(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.load(spec(nodes=[{"id": "a"}, {"id": "a"}]))

    def test_rejects_bad_id(self):
        with self.assertRaisesRegex(ValueError, "id"):
            self.load(spec(nodes=[{"id": "has space"}]))

    def test_rejects_unknown_edge_endpoint(self):
        with self.assertRaisesRegex(ValueError, "zzz"):
            self.load(spec(edges=[{"from": "a", "to": "zzz"}]))

    def test_rejects_unknown_region_member(self):
        with self.assertRaisesRegex(ValueError, "zzz"):
            self.load(spec(regions=[{"label": "r", "wraps": ["zzz"]}]))

    def test_rejects_unknown_depends(self):
        with self.assertRaisesRegex(ValueError, "cache"):
            self.load(spec(depends={"a": ["cache"]}))


class TestSignature(unittest.TestCase):
    def test_same_content_different_meta_is_copy(self):
        a = spec()
        b = spec(meta={"title": "as built"})
        b["nodes"][0]["row"], b["nodes"][0]["col"] = 3, 3
        self.assertEqual(render.diagram_signature(a), render.diagram_signature(b))

    def test_content_diff_is_not_copy(self):
        b = spec(nodes=[{"id": "a"}, {"id": "b"}, {"id": "c"}, {"id": "d"}])
        self.assertNotEqual(render.diagram_signature(spec()), render.diagram_signature(b))


class TestGraphSvg(unittest.TestCase):
    def test_grid_layout(self):
        s = spec()
        for i, n in enumerate(s["nodes"]):
            n["row"], n["col"] = 0, i
        svg = render.graph_svg(s)
        for needle in ('<svg', 'marker-end', 'stroke-dasharray', 'calls', 'Bee', 'sub'):
            self.assertIn(needle, svg)

    def test_auto_layout_layers_by_edges(self):
        s = spec(nodes=[{"id": "ui"}, {"id": "api"}, {"id": "db"}],
                 edges=[{"from": "ui", "to": "api"}, {"from": "api", "to": "db"}])
        pos = render._layout(s)
        self.assertLess(pos["ui"][0], pos["api"][0])
        self.assertLess(pos["api"][0], pos["db"][0])

    def test_depends_feeds_layout(self):
        s = spec(nodes=[{"id": "ui"}, {"id": "api"}, {"id": "store"}],
                 edges=[],
                 depends={"api": ["store"], "ui": ["api"]})
        pos = render._layout(s)
        self.assertLess(pos["store"][0], pos["api"][0])
        self.assertLess(pos["api"][0], pos["ui"][0])

    def test_cycle_does_not_hang(self):
        s = spec(nodes=[{"id": "a"}, {"id": "b"}, {"id": "c"}],
                 edges=[{"from": "a", "to": "b"}, {"from": "b", "to": "c"}, {"from": "c", "to": "a"}])
        self.assertIn("<svg", render.graph_svg(s))

    def test_progress_colors(self):
        svg = render.graph_svg(spec(), {"a": "done", "b": "pending"})
        self.assertIn(render.GOOD, svg)
        self.assertIn(render.WARN, svg)

    def test_region_drawn(self):
        s = spec(regions=[{"label": "CORE", "wraps": ["a", "b"]}])
        self.assertIn("CORE", render.graph_svg(s))


class TestChartSvg(unittest.TestCase):
    def test_chart_elements(self):
        pts = [{"verdict": "baseline", "score": 200}, {"verdict": "rejected", "score": 220},
               {"verdict": "accepted", "score": 170}, {"verdict": "invalid"}]
        svg = render.chart_svg(pts, "ms", "lower", 150, 200)
        for needle in ("<svg", "target 150 ms", "polyline", "✕"):
            self.assertIn(needle, svg)


class TestPage(unittest.TestCase):
    def test_self_contained(self):
        html = render.page("T", '<span class="badge">x</span>', render.section("S", "<p>b</p>"))
        self.assertIn("<style>", html)
        self.assertNotIn("http://", html.replace("http://www.w3.org", ""))
        self.assertNotIn("<script", html)

    def test_write_and_cli_smoke(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write(tmp, spec())
            out = os.path.join(tmp, "out.html")
            argv = sys.argv
            try:
                sys.argv = ["autodev_render.py", path, "-o", out]
                render.main()
            finally:
                sys.argv = argv
            with open(out) as f:
                self.assertIn("<svg", f.read())


if __name__ == "__main__":
    unittest.main()
