#!/usr/bin/env python3
"""Tiny renderer for autodev artifacts. Standard library only.

Reads a diagram JSON and emits a self-contained HTML page with inline SVG —
no JavaScript, no external assets, opens with file:// in any browser.

  python3 autodev_render.py diagram.json [-o out.html]

Diagram JSON:
  {"meta": {"title": "..."},
   "nodes":   [{"id": "order-api", "label": "...", "sublabel": "...",
                "kind": "service|store|external|decision", "row": 0, "col": 1}],
   "edges":   [{"from": "a", "to": "b", "label": "calls", "dashed": false}],
   "regions": [{"label": "backend", "wraps": ["order-api"]}],
   "depends": {"order-api": ["order-service"]}}

row/col place nodes on a grid; without them nodes are layered left-to-right by
longest incoming chain. `depends` is the build-order data the judge checks; it
also feeds the layout fallback.
"""
import html
import json
import os
import re
import subprocess
import sys

NODE_W, NODE_H = 208, 64
GAP_X, GAP_Y = 56, 72
MARGIN = 40

INK = "#DCE6F7"
MUTE = "#9DB5E8"
LINE = "#6B7A99"
NODE_BG = "#131E36"
NODE_STROKE = "#2E3F66"
ACCENT = "#00C8D2"
TARGET = "#78E6DD"
GOOD = "#3DDC97"
WARN = "#FFB454"
BAD = "#FF7A7A"

KIND_DOT = {"service": "#3C8CFF", "store": "#3DDC97", "external": "#6B7A99",
            "decision": "#FFB454", "flow": "#B78CFF"}

ID_RE = r"[A-Za-z0-9_-]+"


def esc(s):
    return html.escape(str(s), quote=True)


def load_diagram(path):
    with open(path, encoding="utf-8") as f:
        try:
            spec = json.load(f)
        except ValueError as e:
            raise ValueError(f"{path} is not valid JSON: {e}")
    return check_diagram(spec, path)


def check_diagram(spec, name="diagram"):
    if not isinstance(spec, dict) or not isinstance(spec.get("nodes"), list) or not spec["nodes"]:
        raise ValueError(f'{name} needs a non-empty "nodes" list')
    ids = []
    for n in spec["nodes"]:
        nid = n.get("id") if isinstance(n, dict) else None
        if not isinstance(nid, str) or not re.fullmatch(ID_RE, nid):
            raise ValueError(f'{name}: every node needs an id matching {ID_RE}')
        ids.append(nid)
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise ValueError(f"{name}: duplicate node ids {dupes}")
    known = set(ids)
    for e in spec.get("edges", []):
        bad = [e.get(k) for k in ("from", "to") if e.get(k) not in known]
        if bad:
            raise ValueError(f"{name}: edge mentions unknown node(s) {bad}")
    for r in spec.get("regions", []):
        bad = [w for w in r.get("wraps", []) if w not in known]
        if bad:
            raise ValueError(f"{name}: region wraps unknown node(s) {bad}")
    for node, needs in spec.get("depends", {}).items():
        bad = [x for x in [node, *needs] if x not in known]
        if bad:
            raise ValueError(f"{name}: depends mentions unknown node(s) {bad}")
    return spec


def diagram_signature(spec):
    """Content-only fingerprint: two diagrams with the same nodes, edges and
    depends are the same diagram regardless of title or layout."""
    return {
        "nodes": sorted((n["id"], n.get("label", "")) for n in spec["nodes"]),
        "edges": sorted((e["from"], e["to"], e.get("label", "")) for e in spec.get("edges", [])),
        "depends": {k: sorted(v) for k, v in sorted(spec.get("depends", {}).items())},
    }


def _depths(spec):
    preds = {n["id"]: [] for n in spec["nodes"]}
    for e in spec.get("edges", []):
        if e.get("to") in preds and e.get("from") in preds:
            preds[e["to"]].append(e["from"])
    for node, needs in spec.get("depends", {}).items():
        if node in preds:
            preds[node] += [n for n in needs if n in preds]
    depth, on_stack = {}, set()

    def d(nid):
        if nid in depth:
            return depth[nid]
        if nid in on_stack:
            return 0
        on_stack.add(nid)
        depth[nid] = max([d(p) + 1 for p in preds[nid]] or [0])
        on_stack.discard(nid)
        return depth[nid]

    return {n["id"]: d(n["id"]) for n in spec["nodes"]}


def _layout(spec):
    nodes = spec["nodes"]
    if all(isinstance(n.get("row"), int) and isinstance(n.get("col"), int) for n in nodes):
        return {n["id"]: (MARGIN + n["col"] * (NODE_W + GAP_X),
                          MARGIN + n["row"] * (NODE_H + GAP_Y)) for n in nodes}
    depth = _depths(spec)
    col_of = {dd: i for i, dd in enumerate(sorted(set(depth.values())))}
    rows, pos = {}, {}
    for n in nodes:
        c = col_of[depth[n["id"]]]
        r = rows.get(c, 0)
        rows[c] = r + 1
        pos[n["id"]] = (MARGIN + c * (NODE_W + GAP_X), MARGIN + r * (NODE_H + GAP_Y))
    return pos


def _edge(spec, pos, e):
    sx, sy = pos[e["from"]]
    tx, ty = pos[e["to"]]
    srx, smy = sx + NODE_W, sy + NODE_H / 2
    tlx, tmy = tx, ty + NODE_H / 2
    if tlx > srx + 8:                                   # forward
        mx = (srx + tlx) / 2
        path = f"M {srx} {smy} H {mx:.1f} V {tmy} H {tlx}"
        label_at = (mx, (smy + tmy) / 2 - 6)
    elif tx == sx:                                      # same column: dogleg right
        dx = sx + NODE_W + 22
        path = f"M {srx} {smy} H {dx} V {tmy} H {tx + NODE_W}"
        label_at = (dx + 4, (smy + tmy) / 2)
    else:                                               # back edge: over the top
        scx, tcx = sx + NODE_W / 2, tx + NODE_W / 2
        lane = min(sy, ty) - 24
        path = f"M {scx} {sy} V {lane} H {tcx} V {ty}"
        label_at = ((scx + tcx) / 2, lane - 6)
    dash = ' stroke-dasharray="6 5"' if e.get("dashed") else ""
    out = [f'<path d="{path}" fill="none" stroke="{LINE}" stroke-width="1.5"{dash} marker-end="url(#arr)"/>']
    if e.get("label"):
        out.append(f'<text x="{label_at[0]:.1f}" y="{label_at[1]:.1f}" text-anchor="middle" '
                   f'fill="{MUTE}" font-size="11">{esc(e["label"][:28])}</text>')
    return out


def graph_svg(spec, progress=None):
    """progress: {id: 'done'|'pending'} colors element nodes by loop state."""
    progress = progress or {}
    pos = _layout(spec)
    xs = [x for x, _ in pos.values()]
    ys = [y for _, y in pos.values()]
    w = max(xs) + NODE_W + MARGIN
    h = max(ys) + NODE_H + MARGIN
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
           f'font-family="Helvetica, Arial, sans-serif" font-size="13">',
           '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
           f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{LINE}"/></marker></defs>']
    for r in spec.get("regions", []):
        rxs = [pos[i][0] for i in r["wraps"]]
        rys = [pos[i][1] for i in r["wraps"]]
        x0, y0 = min(rxs) - 18, min(rys) - 34
        x1, y1 = max(rxs) + NODE_W + 18, max(rys) + NODE_H + 18
        svg += [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="12" fill="none" '
                f'stroke="#3A4B70" stroke-width="1.2" stroke-dasharray="4 5"/>',
                f'<text x="{x0 + 12}" y="{y0 + 16}" fill="{MUTE}" font-size="11" '
                f'letter-spacing="1">{esc(r.get("label", ""))}</text>']
    for e in spec.get("edges", []):
        svg += _edge(spec, pos, e)
    for n in spec["nodes"]:
        x, y = pos[n["id"]]
        state = progress.get(n["id"])
        stroke = {"done": GOOD, "pending": WARN}.get(state, NODE_STROKE)
        svg.append(f'<rect x="{x}" y="{y}" width="{NODE_W}" height="{NODE_H}" rx="10" '
                   f'fill="{NODE_BG}" stroke="{stroke}" stroke-width="1.5"/>')
        dot = KIND_DOT.get(n.get("kind"))
        tx = x + 14
        if dot or state:
            svg.append(f'<circle cx="{x + 16}" cy="{y + NODE_H / 2}" r="4" '
                       f'fill="{dot or {"done": GOOD, "pending": WARN}[state]}"/>')
            tx = x + 30
        label, sub = n.get("label", n["id"])[:24], n.get("sublabel", "")[:36]
        if sub:
            svg.append(f'<text x="{tx}" y="{y + 28}" fill="{INK}" font-weight="600">{esc(label)}</text>')
            svg.append(f'<text x="{tx}" y="{y + 47}" fill="{MUTE}" font-size="11">{esc(sub)}</text>')
        else:
            svg.append(f'<text x="{tx}" y="{y + NODE_H / 2 + 5}" fill="{INK}" font-weight="600">{esc(label)}</text>')
    svg.append("</svg>")
    return "".join(svg)


def chart_svg(pts, unit, direction, target, baseline):
    """Optimization process chart: baseline → attempts → retained best."""
    scored = [r for r in pts if r.get("score") is not None]
    ys = [r["score"] for r in scored] + [target, baseline]
    lo, hi = min(ys), max(ys)
    pad = (hi - lo) * 0.15 or abs(hi) * 0.1 or 1.0
    lo, hi = lo - pad, hi + pad
    W, H, L, R, T, B = 960, 480, 90, 30, 40, 70
    n = max(len(pts) - 1, 1)

    def X(i):
        return L + (W - L - R) * i / n

    def Y(v):
        return T + (H - T - B) * (hi - v) / (hi - lo)

    best = baseline
    best_line = []
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="Helvetica, Arial, sans-serif" font-size="13">',
           f'<rect width="{W}" height="{H}" fill="#0B1220"/>',
           f'<line x1="{L}" y1="{T}" x2="{L}" y2="{H - B}" stroke="{LINE}"/>',
           f'<line x1="{L}" y1="{H - B}" x2="{W - R}" y2="{H - B}" stroke="{LINE}"/>',
           f'<line x1="{L}" y1="{Y(target):.1f}" x2="{W - R}" y2="{Y(target):.1f}" stroke="{TARGET}" stroke-dasharray="6 6"/>',
           f'<text x="{W - R}" y="{Y(target) - 6:.1f}" text-anchor="end" fill="{TARGET}">target {target} {unit}</text>']
    for i, r in enumerate(pts):
        s = r.get("score")
        best_line.append((X(i), Y(best)))
        if s is not None and r["verdict"] in ("accepted", "baseline"):
            best = s
        best_line.append((X(i), Y(best)))
    svg.append('<polyline fill="none" stroke="#3C8CFF" stroke-width="2" points="' +
               " ".join(f"{x:.1f},{y:.1f}" for x, y in best_line) + '"/>')
    for i, r in enumerate(pts):
        x, s, v = X(i), r.get("score"), r["verdict"]
        if s is None:
            svg.append(f'<text x="{x:.1f}" y="{H - B - 8:.1f}" text-anchor="middle" fill="{BAD}">✕</text>')
        else:
            color = {"baseline": "#FFFFFF", "accepted": ACCENT, "rejected": BAD}.get(v, MUTE)
            svg.append(f'<circle cx="{x:.1f}" cy="{Y(s):.1f}" r="5" fill="{color}"/>')
        svg.append(f'<text x="{x:.1f}" y="{H - B + 18}" text-anchor="middle" fill="{MUTE}">{i}</text>')
    for v in (lo + pad, hi - pad):
        svg.append(f'<text x="{L - 8}" y="{Y(v) + 4:.1f}" text-anchor="end" fill="{MUTE}">{v:g}</text>')
    svg.append(f'<text x="{L}" y="{T - 14}" fill="#FFFFFF" font-size="15">score ({unit}, {direction} is better) '
               f'— white baseline, cyan accepted, red rejected, ✕ invalid, blue line = retained best</text>')
    svg.append(f'<text x="{W / 2:.0f}" y="{H - 14}" text-anchor="middle" fill="{MUTE}">attempt</text>')
    svg.append("</svg>")
    return "".join(svg)


PAGE_CSS = """\
body{margin:0;background:#0B1220;color:#DCE6F7;font:14px/1.55 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
main{max-width:1080px;margin:0 auto;padding:32px 24px 64px}
h1{font-size:22px;margin:0 0 6px}
.sub{color:#9DB5E8;margin:0 0 28px}
.badge{display:inline-block;padding:2px 10px;border-radius:999px;border:1px solid #3C8CFF;color:#7FB2FF;font-size:11px;letter-spacing:.08em;text-transform:uppercase}
.badge.ok{border-color:#3DDC97;color:#3DDC97}
.badge.bad{border-color:#FF7A7A;color:#FF7A7A}
section{margin:26px 0}
h2{font-size:13px;color:#9DB5E8;text-transform:uppercase;letter-spacing:.1em;margin:0 0 12px}
table{border-collapse:collapse;width:100%}
th,td{padding:8px 12px;border-bottom:1px solid #22304E;text-align:left;font-size:13px;vertical-align:top}
th{color:#9DB5E8;font-weight:600}
code{background:#131E36;padding:1px 6px;border-radius:4px;font-size:12px}
svg{max-width:100%;height:auto;background:#0E1730;border:1px solid #22304E;border-radius:8px}
.stats{display:flex;gap:14px;flex-wrap:wrap}
.stats>div{background:#0E1730;border:1px solid #22304E;border-radius:8px;padding:10px 18px;min-width:110px}
.stats b{display:block;font-size:19px}
.stats span{color:#9DB5E8;font-size:11px;text-transform:uppercase;letter-spacing:.06em}
a{color:#7FB2FF}
details{margin:6px 0}
summary{cursor:pointer;color:#9DB5E8}
pre{background:#0E1730;border:1px solid #22304E;border-radius:8px;padding:12px;overflow:auto;font-size:12px;max-height:340px}
.ok{color:#3DDC97}.bad{color:#FF7A7A}.warn{color:#FFB454}.mute{color:#9DB5E8}
ol.batches li{margin:4px 0}
"""


def page(title, subtitle_html, body):
    return ("<!doctype html><html><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{esc(title)}</title><style>{PAGE_CSS}</style></head><body><main>"
            f"<h1>{esc(title)}</h1><p class=\"sub\">{subtitle_html}</p>{body}</main></body></html>")


def stats(items):
    cells = "".join(f"<div><b>{v}</b><span>{esc(k)}</span></div>" for k, v in items)
    return f'<div class="stats">{cells}</div>'


def table(headers, rows):
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def section(title, inner):
    return f"<section><h2>{esc(title)}</h2>{inner}</section>"


def write_page(path, title, subtitle_html, body):
    with open(path, "w") as f:
        f.write(page(title, subtitle_html, body))
    return os.path.abspath(path)


def open_command(path):
    if sys.platform == "darwin":
        return ["open", path]
    if os.name == "nt":
        return None
    return ["xdg-open", path]


def open_path(path):
    try:
        if os.name == "nt":
            os.startfile(path)  # noqa: S606 — deliberate viewer launch
            return True
        cmd = open_command(path)
        if cmd:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
    except OSError:
        pass
    return False


def main():
    import argparse
    p = argparse.ArgumentParser(prog="autodev_render.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("diagram", help="diagram JSON file")
    p.add_argument("-o", "--out", help="output HTML path (default: <input>.html)")
    a = p.parse_args()
    try:
        spec = load_diagram(a.diagram)
    except (OSError, ValueError) as e:
        print(f"autodev_render: {e}", file=sys.stderr)
        sys.exit(3)
    out = a.out or os.path.splitext(a.diagram)[0] + ".html"
    title = spec.get("meta", {}).get("title") or os.path.basename(a.diagram)
    path = write_page(out, title, '<span class="badge">diagram</span>', graph_svg(spec))
    print(path)


if __name__ == "__main__":
    main()
