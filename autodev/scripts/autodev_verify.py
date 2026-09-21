#!/usr/bin/env python3
"""Mechanical judge for the autodev Loop. Standard library only.

Commands follow the flow one to one:
  init     Clarify §3: run the approved test for baseline, record limits and frozen hashes
  start    Loop entry: bind the worktree, set the deadline, self-test the checks
  smoke    Prove that a frozen-file edit and an out-of-scope edit are both rejected
  attempt  One Loop round: scope check, frozen check, run test, judge, accept or roll back
  status   Exit decision: target met under the agreed rule, or budget exhausted
  report   Handoff artifact: comparison table (development) or process chart (optimization)
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import time

ACCEPTED, REJECTED, INVALID, PRECONDITION = 0, 1, 2, 3


def utc_now():
    return dt.datetime.now(dt.timezone.utc)


def iso(ts):
    return ts.replace(microsecond=0).isoformat()


def parse_iso(s):
    return dt.datetime.fromisoformat(s)


def die(msg, code=PRECONDITION):
    print(f"autodev: {msg}", file=sys.stderr)
    sys.exit(code)


def git(cwd, *args, check=True):
    r = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True)
    if check and r.returncode != 0:
        die(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout.strip()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_paths(root, rels):
    out = {}
    for rel in rels:
        p = os.path.join(root, rel)
        if os.path.isdir(p):
            for d, _, files in os.walk(p):
                for name in sorted(files):
                    full = os.path.join(d, name)
                    out[os.path.relpath(full, root)] = sha256_file(full)
        elif os.path.isfile(p):
            out[rel] = sha256_file(p)
        else:
            die(f"frozen path does not exist: {rel}")
    return out


def norm(rel):
    return rel.replace(os.sep, "/").rstrip("/")


def in_editable(rel, editable):
    rel = norm(rel)
    for e in editable:
        e = norm(e)
        if e in ("", ".") or rel == e or rel.startswith(e + "/"):
            return True
    return False


class Home:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.contract_path = os.path.join(self.path, "contract.json")
        self.attempts_path = os.path.join(self.path, "attempts.jsonl")
        self.raw = os.path.join(self.path, "raw")

    def ensure(self):
        os.makedirs(self.raw, exist_ok=True)

    def load(self):
        if not os.path.exists(self.contract_path):
            die(f"no contract at {self.contract_path}; run init first")
        with open(self.contract_path) as f:
            return json.load(f)

    def save(self, contract):
        self.ensure()
        with open(self.contract_path, "w") as f:
            json.dump(contract, f, indent=2, ensure_ascii=False)
            f.write("\n")

    def attempts(self):
        if not os.path.exists(self.attempts_path):
            return []
        with open(self.attempts_path) as f:
            return [json.loads(line) for line in f if line.strip()]

    def log(self, record):
        self.ensure()
        with open(self.attempts_path, "a") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def raw_path(self, name):
        self.ensure()
        return os.path.join(self.raw, name)


def run_test(contract, cwd, raw_path, timeout):
    t0 = time.monotonic()
    timed_out = False
    try:
        r = subprocess.run(contract["test_cmd"], shell=True, cwd=cwd, text=True,
                           capture_output=True, timeout=timeout)
        code, out = r.returncode, r.stdout + r.stderr
    except subprocess.TimeoutExpired as e:
        timed_out = True
        code = None
        out = "".join(x.decode() if isinstance(x, bytes) else (x or "") for x in (e.stdout, e.stderr))
    elapsed = time.monotonic() - t0
    with open(raw_path, "w") as f:
        f.write(f"$ {contract['test_cmd']}\n# cwd={cwd} exit={code} elapsed={elapsed:.1f}s timed_out={timed_out}\n")
        f.write(out)
    return code, out, elapsed, timed_out


def extract_score(contract, out):
    matches = re.findall(contract["score"]["regex"], out, re.MULTILINE)
    if not matches:
        return None
    m = matches[-1]
    if isinstance(m, tuple):
        m = m[0]
    try:
        return float(m)
    except ValueError:
        return None


def improves(contract, score, best):
    d = contract["delta"]
    if contract["score"]["direction"] == "lower":
        return score < best - d
    return score > best + d


def meets_target(contract, score):
    t, inc = contract.get("target"), contract.get("inclusive", True)
    if t is None or score is None:
        return False
    if contract["score"]["direction"] == "lower":
        return score <= t if inc else score < t
    return score >= t if inc else score > t


def check_frozen(contract, root):
    current = hash_paths(root, contract["frozen_paths"])
    recorded = contract["frozen"]
    changed = sorted(set(k for k in set(current) | set(recorded) if current.get(k) != recorded.get(k)))
    return changed


def check_scope(contract, wt, best):
    status = git(wt, "status", "--porcelain")
    if status:
        files = [line[3:] for line in status.splitlines()]
        return None, f"worktree is not clean; commit the attempt first or git-ignore generated files: {files}"
    changed = git(wt, "diff", "--name-only", best, "HEAD").splitlines()
    outside = [c for c in changed if not in_editable(c, contract["editable"])]
    return outside, None


def rollback(wt, best):
    git(wt, "reset", "--hard", best)
    git(wt, "clean", "-fd")


# ---------------------------------------------------------------- commands

def cmd_init(a):
    home = Home(a.home)
    if os.path.exists(home.contract_path) and not a.renew:
        die("contract exists; use --renew after a new Clarify pass")
    if a.renew and os.path.exists(home.contract_path):
        stamp = iso(utc_now()).replace(":", "")
        os.rename(home.contract_path, home.contract_path + f".{stamp}.bak")
        if os.path.exists(home.attempts_path):
            os.rename(home.attempts_path, home.attempts_path + f".{stamp}.bak")
    repo = os.path.abspath(a.repo)
    git(repo, "rev-parse", "--is-inside-work-tree")
    contract = {
        "scenario": a.scenario,
        "created": iso(utc_now()),
        "repo": repo,
        "branch_from": a.branch_from or git(repo, "rev-parse", "--abbrev-ref", "HEAD"),
        "editable": [norm(e) for e in a.editable],
        "frozen_paths": [norm(f) for f in a.frozen],
        "frozen": hash_paths(repo, a.frozen),
        "test_cmd": a.test_cmd,
        "budget_minutes": a.budget_minutes,
        "worktree": None,
        "best": None,
        "best_score": None,
        "deadline": None,
    }
    if a.scenario == "optimization":
        for name in ("score_regex", "direction", "unit"):
            if getattr(a, name) is None:
                die(f"--{name.replace('_', '-')} is required for optimization")
        if a.target is None:
            die("--target is required for optimization")
        contract["score"] = {"regex": a.score_regex, "direction": a.direction, "unit": a.unit}
        contract["target"] = a.target
        contract["inclusive"] = not a.exclusive
    for e in contract["editable"]:
        for f in contract["frozen"]:
            if in_editable(f, [e]):
                die(f"frozen file {f} lies inside editable path {e}")
    home.ensure()
    code, out, elapsed, timed_out = run_test(contract, repo, home.raw_path("baseline.log"), None)
    baseline = {"exit": code, "elapsed_s": round(elapsed, 1), "source": git(repo, "rev-parse", "HEAD"),
                "raw": "raw/baseline.log"}
    if a.scenario == "optimization":
        if code != 0:
            die(f"baseline test exited {code}; the benchmark must run cleanly before limits are proposed (see raw/baseline.log)")
        score = extract_score(contract, out)
        if score is None:
            die("baseline produced no score matching --score-regex; fix the test or the regex")
        baseline["score"] = score
        if a.delta_pct is not None:
            contract["delta"] = round(a.delta_pct / 100.0 * abs(score), 10)
            contract["delta_from"] = f"{a.delta_pct}% of baseline"
        elif a.delta is not None:
            contract["delta"] = a.delta
            contract["delta_from"] = "absolute"
        else:
            die("--delta or --delta-pct is required for optimization")
    else:
        baseline["passed"] = code == 0
    contract["baseline"] = baseline
    home.save(contract)
    print(json.dumps(contract, indent=2, ensure_ascii=False))


def cmd_start(a):
    home = Home(a.home)
    c = home.load()
    wt = os.path.abspath(a.worktree)
    git(wt, "rev-parse", "--is-inside-work-tree")
    if os.path.realpath(git(wt, "rev-parse", "--show-toplevel")) == os.path.realpath(c["repo"]):
        die("worktree is the user's checkout; create a separate git worktree for Loop")
    if git(wt, "status", "--porcelain"):
        die("worktree must be clean at start; commit the baseline state first")
    changed = check_frozen(c, wt)
    if changed:
        die(f"frozen files differ from Clarify in the worktree: {changed}")
    c["worktree"] = wt
    c["best"] = git(wt, "rev-parse", "HEAD")
    c["best_score"] = c["baseline"].get("score")
    started = utc_now()
    c["started"] = iso(started)
    c["deadline"] = iso(started + dt.timedelta(minutes=c["budget_minutes"])) if c.get("budget_minutes") else None
    home.save(c)
    home.log({"n": 0, "kind": "baseline", "commit": c["best"], "score": c["best_score"],
              "verdict": "baseline", "raw": c["baseline"]["raw"], "time": c["started"]})
    if not a.no_smoke:
        smoke(home, c)
    print(json.dumps({"worktree": wt, "best": c["best"], "best_score": c["best_score"],
                      "deadline": c["deadline"]}, indent=2))


def smoke(home, c):
    wt, best = c["worktree"], c["best"]
    frozen = c["frozen_paths"][0]
    target = os.path.join(wt, frozen)
    if os.path.isdir(target):
        target = os.path.join(wt, sorted(c["frozen"])[0])
    with open(target, "a") as f:
        f.write("\n# autodev smoke\n")
    changed = check_frozen(c, wt)
    rollback(wt, best)
    if not changed:
        die("smoke failed: frozen-file edit was not detected")
    probe = os.path.join(wt, "autodev_smoke_out_of_scope.txt")
    with open(probe, "w") as f:
        f.write("smoke\n")
    git(wt, "add", "-A")
    git(wt, "-c", "user.name=autodev", "-c", "user.email=autodev@local", "commit", "-q", "-m", "autodev smoke")
    outside, err = check_scope(c, wt, best)
    rollback(wt, best)
    if err or not outside:
        die("smoke failed: out-of-scope file was not detected")
    if git(wt, "status", "--porcelain") or git(wt, "rev-parse", "HEAD") != best:
        die("smoke failed: rollback left residue")
    home.log({"n": 0, "kind": "smoke", "verdict": "passed", "time": iso(utc_now())})
    print("smoke: frozen-file edit rejected, out-of-scope edit rejected, rollback clean")


def cmd_smoke(a):
    home = Home(a.home)
    c = home.load()
    if not c.get("worktree"):
        die("run start first")
    smoke(home, c)


def remaining_seconds(c):
    if not c.get("deadline"):
        return None
    return (parse_iso(c["deadline"]) - utc_now()).total_seconds()


def cmd_attempt(a):
    home = Home(a.home)
    c = home.load()
    wt, best = c.get("worktree"), c.get("best")
    if not wt:
        die("run start first")
    n = 1 + max([r["n"] for r in home.attempts()] + [0])
    remaining = remaining_seconds(c)
    head = git(wt, "rev-parse", "HEAD")
    if remaining is not None and remaining <= 0:
        if head != best:
            rollback(wt, best)
            home.log({"n": n, "kind": "attempt", "commit": head, "note": a.note, "time": iso(utc_now()),
                      "verdict": "invalid", "reason": "time budget exhausted before the run", "rolled_back_to": best})
        die("time budget exhausted; run status and enter Handoff", PRECONDITION)
    if head == best:
        die("HEAD is already best; commit the attempt first")
    outside, err = check_scope(c, wt, best)
    if err:
        die(err)
    record = {"n": n, "kind": "attempt", "commit": head, "note": a.note, "time": iso(utc_now())}

    def finish(verdict, code, **extra):
        record.update(verdict=verdict, **extra)
        if verdict == "accepted":
            c["best"] = head
            if "score" in extra:
                c["best_score"] = extra["score"]
            home.save(c)
        elif verdict in ("rejected", "invalid"):
            rollback(wt, best)
            record["rolled_back_to"] = best
        elif verdict == "failing":
            c["best"] = head
            home.save(c)
        home.log(record)
        print(json.dumps(record, ensure_ascii=False))
        sys.exit(code)

    if outside:
        finish("invalid", INVALID, reason="out-of-scope changes", files=outside)
    changed = check_frozen(c, wt)
    if changed:
        finish("invalid", INVALID, reason="frozen files changed", files=changed)
    raw_name = f"attempt-{n:03d}.log"
    code, out, elapsed, timed_out = run_test(c, wt, home.raw_path(raw_name), remaining)
    record.update(raw=f"raw/{raw_name}", elapsed_s=round(elapsed, 1))
    if timed_out:
        finish("invalid", INVALID, reason="test exceeded remaining budget")
    if c["scenario"] == "development":
        if code == 0:
            finish("accepted", ACCEPTED, passed=True, exit=code)
        finish("failing", REJECTED, passed=False, exit=code)
    if code != 0:
        finish("invalid", INVALID, reason=f"test exited {code}", exit=code)
    score = extract_score(c, out)
    if score is None:
        finish("invalid", INVALID, reason="no score matched regex", exit=code)
    if improves(c, score, c["best_score"]):
        finish("accepted", ACCEPTED, score=score, previous_best=c["best_score"])
    finish("rejected", REJECTED, score=score, best=c["best_score"])


def cmd_status(a):
    home = Home(a.home)
    c = home.load()
    remaining = remaining_seconds(c)
    out = {"scenario": c["scenario"], "best": c.get("best"), "best_score": c.get("best_score"),
           "remaining_seconds": None if remaining is None else int(remaining),
           "attempts": len([r for r in home.attempts() if r.get("kind") == "attempt"])}
    if c["scenario"] == "optimization":
        out["target"] = c["target"]
        out["inclusive"] = c["inclusive"]
        out["target_met"] = meets_target(c, c.get("best_score"))
        exhausted = remaining is not None and remaining <= 0
        out["budget_exhausted"] = exhausted
        out["decision"] = "handoff" if (out["target_met"] or exhausted) else "continue"
        out["stop_reason"] = ("target reached" if out["target_met"] else
                              "time budget exhausted" if exhausted else None)
    else:
        last = [r for r in home.attempts() if r.get("kind") == "attempt"]
        passing = bool(last) and last[-1]["verdict"] == "accepted"
        out["all_tests_pass"] = passing
        out["decision"] = "handoff" if passing else "continue"
    print(json.dumps(out, indent=2))


def cmd_report(a):
    home = Home(a.home)
    c = home.load()
    rows = home.attempts()
    if c["scenario"] == "development":
        report_table(home, c, rows, a.out)
    else:
        report_chart(home, c, rows, a.out)


def report_table(home, c, rows, out):
    attempts = [r for r in rows if r.get("kind") == "attempt"]
    final = attempts[-1] if attempts else None
    b = c["baseline"]
    if final:
        final_text = ("pass" if final.get("passed") else "fail") + (f" (exit {final['exit']})" if "exit" in final else "")
    else:
        final_text = "not run"
    base_text = ("pass" if b.get("passed") else "fail") + f" (exit {b['exit']})"
    lines = [
        "| Test / expected behavior | Baseline result | Final result | Evidence |",
        "|---|---|---|---|",
        f"| `{c['test_cmd']}` | {base_text} | {final_text} | {b['raw']} → {final['raw'] if final else '-'} |",
        "",
        f"Baseline source `{b['source']}`; final source `{c.get('best')}`; checkpoints logged: {len(attempts)}.",
        "Add one row per agreed case ID from the raw logs; totals must cover the whole agreed set.",
    ]
    text = "\n".join(lines) + "\n"
    path = out or os.path.join(home.path, "comparison.md")
    with open(path, "w") as f:
        f.write(text)
    print(path)


def report_chart(home, c, rows, out):
    pts = [r for r in rows if r.get("kind") in ("baseline", "attempt")]
    scored = [r for r in pts if r.get("score") is not None]
    unit, direction = c["score"]["unit"], c["score"]["direction"]
    target, baseline = c["target"], c["baseline"]["score"]
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
           f'<line x1="{L}" y1="{T}" x2="{L}" y2="{H-B}" stroke="#6B7A99"/>',
           f'<line x1="{L}" y1="{H-B}" x2="{W-R}" y2="{H-B}" stroke="#6B7A99"/>',
           f'<line x1="{L}" y1="{Y(target):.1f}" x2="{W-R}" y2="{Y(target):.1f}" stroke="#78E6DD" stroke-dasharray="6 6"/>',
           f'<text x="{W-R}" y="{Y(target)-6:.1f}" text-anchor="end" fill="#78E6DD">target {target} {unit}</text>']
    for i, r in enumerate(pts):
        s = r.get("score")
        best_line.append((X(i), Y(best)))
        if s is not None and (r["verdict"] in ("accepted", "baseline")):
            best = s
        best_line.append((X(i), Y(best)))
    svg.append('<polyline fill="none" stroke="#3C8CFF" stroke-width="2" points="' +
               " ".join(f"{x:.1f},{y:.1f}" for x, y in best_line) + '"/>')
    for i, r in enumerate(pts):
        x = X(i)
        s = r.get("score")
        v = r["verdict"]
        if s is None:
            svg.append(f'<text x="{x:.1f}" y="{H-B-8:.1f}" text-anchor="middle" fill="#FF7A7A">✕</text>')
            svg.append(f'<text x="{x:.1f}" y="{H-B+18}" text-anchor="middle" fill="#9DB5E8">{i}</text>')
            continue
        color = {"baseline": "#FFFFFF", "accepted": "#00C8D2", "rejected": "#FF7A7A"}.get(v, "#9DB5E8")
        svg.append(f'<circle cx="{x:.1f}" cy="{Y(s):.1f}" r="5" fill="{color}"/>')
        svg.append(f'<text x="{x:.1f}" y="{H-B+18}" text-anchor="middle" fill="#9DB5E8">{i}</text>')
    for v in (lo + pad, hi - pad):
        svg.append(f'<text x="{L-8}" y="{Y(v)+4:.1f}" text-anchor="end" fill="#9DB5E8">{v:g}</text>')
    svg.append(f'<text x="{L}" y="{T-14}" fill="#FFFFFF" font-size="15">score ({unit}, {direction} is better) '
               f'— white baseline, cyan accepted, red rejected, ✕ invalid, blue line = retained best</text>')
    svg.append(f'<text x="{W/2:.0f}" y="{H-14}" text-anchor="middle" fill="#9DB5E8">attempt</text>')
    svg.append("</svg>")
    path = out or os.path.join(home.path, "process.svg")
    with open(path, "w") as f:
        f.write("\n".join(svg) + "\n")
    final = c.get("best_score")
    imp = (baseline - final) if direction == "lower" else (final - baseline)
    pct = None if baseline == 0 else imp / abs(baseline) * 100
    caption = {"baseline": baseline, "final": final, "unit": unit, "direction": direction,
               "improvement": imp, "improvement_pct": pct, "target": target,
               "target_met": meets_target(c, final), "attempts": len(pts) - 1,
               "delivered_commit": c.get("best"), "rerun": c["test_cmd"], "chart": path}
    with open(os.path.join(home.path, "caption.json"), "w") as f:
        json.dump(caption, f, indent=2)
    print(json.dumps(caption, indent=2))


def main():
    p = argparse.ArgumentParser(prog="autodev_verify.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--home", required=True, help="contract directory, outside the worktree")
    sub = p.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init")
    i.add_argument("--repo", default=".")
    i.add_argument("--scenario", choices=["development", "optimization"], required=True)
    i.add_argument("--branch-from")
    i.add_argument("--editable", nargs="+", required=True)
    i.add_argument("--frozen", nargs="+", required=True)
    i.add_argument("--test-cmd", required=True)
    i.add_argument("--budget-minutes", type=float)
    i.add_argument("--score-regex")
    i.add_argument("--direction", choices=["lower", "higher"])
    i.add_argument("--unit")
    i.add_argument("--delta", type=float)
    i.add_argument("--delta-pct", type=float)
    i.add_argument("--target", type=float)
    i.add_argument("--exclusive", action="store_true", help="target excludes equality")
    i.add_argument("--renew", action="store_true")
    i.set_defaults(fn=cmd_init)

    s = sub.add_parser("start")
    s.add_argument("--worktree", required=True)
    s.add_argument("--no-smoke", action="store_true")
    s.set_defaults(fn=cmd_start)

    sub.add_parser("smoke").set_defaults(fn=cmd_smoke)

    t = sub.add_parser("attempt")
    t.add_argument("--note", default="")
    t.set_defaults(fn=cmd_attempt)

    sub.add_parser("status").set_defaults(fn=cmd_status)

    r = sub.add_parser("report")
    r.add_argument("--out")
    r.set_defaults(fn=cmd_report)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
