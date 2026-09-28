#!/usr/bin/env python3
"""Mechanical judge for the autodev Loop. Standard library only.

Commands follow the flow one to one:
  init     Clarify §3: record limits and frozen hashes, run the baseline check if any
  start    Loop entry: bind the worktree, set the deadline, self-test the checks
  smoke    Prove that a frozen-file edit and an out-of-scope edit are both rejected
  attempt  One Loop round: scope check, frozen check, run the check, judge, keep or roll back
  status   Exit decision: agreed rule met (bugfix test, dev blueprint, opt target), or budget out
  verify   Rerun the agreed command on the retained best commit before Handoff
  report   Handoff artifact: comparison table (bugfix), blueprint handoff (development), chart (optimization)
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

ACCEPTED, REJECTED, INVALID, PRECONDITION = 0, 1, 2, 3
CONSTITUTION = ".autodev/constitution.json"


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


def blueprint_elements(path):
    ids = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.search(r"%%\s*autodev-elements:\s*(.+)", line)
            if m:
                ids += [t for t in re.split(r"[\s,]+", m.group(1))
                        if re.fullmatch(r"[A-Za-z0-9_-]+", t)]
    ids = list(dict.fromkeys(ids))
    if not ids:
        die("blueprint has no %% autodev-elements line")
    return ids


def blueprint_depends(path, elements):
    deps = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.search(r"%%\s*autodev-depends:\s*([A-Za-z0-9_-]+)\s*:\s*(.+)", line)
            if not m:
                continue
            node, needs = m.group(1), [t for t in re.split(r"[\s,]+", m.group(2)) if t]
            unknown = [e for e in [node, *needs] if e not in elements]
            if unknown:
                die(f"autodev-depends names IDs missing from autodev-elements: {unknown}")
            if node in needs:
                die(f"element {node} depends on itself")
            deps.setdefault(node, [])
            deps[node] += [n for n in needs if n not in deps[node]]
    return deps


def build_batches(elements, deps):
    batches, placed = [], set()
    while len(placed) < len(elements):
        batch = [e for e in elements if e not in placed and set(deps.get(e, [])) <= placed]
        if not batch:
            die(f"blueprint dependencies form a cycle among {[e for e in elements if e not in placed]}")
        batches.append(batch)
        placed |= set(batch)
    return batches


def element_progress(c, attempts):
    pending, realized = set(), {}
    for r in attempts:
        if r.get("kind") != "attempt":
            continue
        claimed = set(r.get("elements", []))
        if r["verdict"] == "failing":
            pending |= claimed
        elif r["verdict"] in ("green", "checkpoint"):
            for e in pending | claimed:
                realized.setdefault(e, r["commit"])
            pending = set()
    done = [e for e in c["elements"] if e in realized]
    open_ = [e for e in c["elements"] if e not in realized]
    ready = [e for e in open_ if set(c.get("depends", {}).get(e, [])) <= set(done)]
    return {"done": done, "ready": ready, "blocked": [e for e in open_ if e not in ready],
            "pending": [e for e in open_ if e in pending], "realized_in": realized}


def element_found(element, text):
    return bool(re.search(r"(?<![A-Za-z0-9_-])" + re.escape(element) + r"(?![A-Za-z0-9_-])", text))


def diagram_body(text):
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return [line for line in lines if line and not line.startswith("%%") and not line.startswith("```")]


def load_constitution(repo, rel):
    path = os.path.join(repo, rel or CONSTITUTION)
    if not os.path.isfile(path):
        if rel:
            die(f"constitution file does not exist: {rel}")
        return None, None
    try:
        with open(path, encoding="utf-8") as f:
            law = json.load(f)
    except ValueError as e:
        die(f"constitution is not valid JSON: {e}")
    unknown = set(law) - {"frozen", "guard_cmd", "budget"}
    unknown |= {f"budget.{k}" for k in set(law.get("budget", {})) - {"default_minutes", "max_minutes", "reserve_minutes"}}
    if unknown:
        die(f"constitution has unknown keys: {sorted(unknown)}")
    return law, norm(os.path.relpath(path, repo))


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


def run_command(cmd, cwd, raw_path, timeout):
    t0 = time.monotonic()
    timed_out = False
    try:
        r = subprocess.run(cmd, shell=True, cwd=cwd, text=True,
                           capture_output=True, timeout=timeout)
        code, out = r.returncode, r.stdout + r.stderr
    except subprocess.TimeoutExpired as e:
        timed_out = True
        code = None
        out = "".join(x.decode() if isinstance(x, bytes) else (x or "") for x in (e.stdout, e.stderr))
    elapsed = time.monotonic() - t0
    with open(raw_path, "w") as f:
        f.write(f"$ {cmd}\n# cwd={cwd} exit={code} elapsed={elapsed:.1f}s timed_out={timed_out}\n")
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
    renewed_from = None
    if a.renew and os.path.exists(home.contract_path):
        with open(home.contract_path) as f:
            old = json.load(f)
        renewed_from = {"created": old.get("created"), "scenario": old.get("scenario"),
                        "best_score": old.get("best_score")}
        stamp = iso(utc_now()).replace(":", "")
        os.rename(home.contract_path, home.contract_path + f".{stamp}.bak")
        if os.path.exists(home.attempts_path):
            os.rename(home.attempts_path, home.attempts_path + f".{stamp}.bak")
    repo = os.path.abspath(a.repo)
    git(repo, "rev-parse", "--is-inside-work-tree")
    if a.scenario == "development":
        if a.test_cmd:
            die("use --check-cmd for development")
        for name in ("blueprint", "asis", "asbuilt"):
            if getattr(a, name) is None:
                die(f"--{name} is required for development")
    else:
        if not a.test_cmd:
            die("--test-cmd is required")
        if not a.frozen:
            die("--frozen is required")
    law, law_rel = load_constitution(repo, a.constitution)
    if law:
        a.frozen = list(dict.fromkeys((a.frozen or []) + law.get("frozen", []) + [law_rel]))
        budget = law.get("budget", {})
        if a.scenario == "optimization":
            if a.budget_minutes is None:
                a.budget_minutes = budget.get("default_minutes")
            if a.reserve_minutes is None:
                a.reserve_minutes = budget.get("reserve_minutes")
        cap = budget.get("max_minutes")
        if cap is not None and a.budget_minutes is not None and a.budget_minutes > cap:
            die(f"--budget-minutes {a.budget_minutes:g} exceeds the constitution's max_minutes {cap:g}")
    contract = {
        "scenario": a.scenario,
        "created": iso(utc_now()),
        "repo": repo,
        "branch_from": a.branch_from or git(repo, "rev-parse", "--abbrev-ref", "HEAD"),
        "editable": [norm(e) for e in a.editable],
        "frozen_paths": [norm(f) for f in (a.frozen or [])],
        "frozen": hash_paths(repo, a.frozen or []),
        "test_cmd": a.test_cmd,
        "budget_minutes": a.budget_minutes,
        "reserve_minutes": a.reserve_minutes,
        "renewed_from": renewed_from,
        "constitution": {"path": law_rel, "sha256": sha256_file(os.path.join(repo, law_rel))} if law else None,
        "guard_cmd": law.get("guard_cmd") if law else None,
        "worktree": None,
        "best": None,
        "best_score": None,
        "deadline": None,
    }
    docs = {}
    if a.scenario == "development":
        if not in_editable(a.asbuilt, contract["editable"]):
            die("--asbuilt must lie inside --editable")
        contract["asbuilt"] = norm(a.asbuilt)
        contract["check_cmd"] = a.check_cmd
        contract["test_cmd"] = a.check_cmd
        for name in ("blueprint", "asis"):
            rel = norm(getattr(a, name))
            src = os.path.join(repo, rel)
            if not os.path.isfile(src):
                die(f"--{name} file does not exist: {rel}")
            docs[name] = (rel, src)
        contract["elements"] = blueprint_elements(docs["blueprint"][1])
        contract["depends"] = blueprint_depends(docs["blueprint"][1], contract["elements"])
        contract["batches"] = build_batches(contract["elements"], contract["depends"])
        with open(docs["asis"][1], encoding="utf-8") as f:
            asis_text = f.read()
        contract["elements_new"] = [e for e in contract["elements"] if not element_found(e, asis_text)]
        if not contract["elements_new"]:
            die("every blueprint element already appears in the as-is diagrams, so the coverage check "
                "cannot fail; give added or changed elements new IDs")
        for rel, src in docs.values():
            contract["frozen"][rel] = sha256_file(src)
            if rel not in contract["frozen_paths"]:
                contract["frozen_paths"].append(rel)
    if a.scenario == "optimization":
        for name in ("score_regex", "direction", "unit"):
            if getattr(a, name) is None:
                die(f"--{name.replace('_', '-')} is required for optimization")
        if a.target is None:
            die("--target is required for optimization")
        if a.budget_minutes is None:
            die("--budget-minutes is required for optimization; agree a wall-clock limit in Clarify")
        if a.reserve_minutes is not None and a.reserve_minutes >= a.budget_minutes:
            die("--reserve-minutes must be smaller than --budget-minutes")
        contract["score"] = {"regex": a.score_regex, "direction": a.direction, "unit": a.unit}
        contract["target"] = a.target
        contract["inclusive"] = not a.exclusive
    for e in contract["editable"]:
        for f in contract["frozen"]:
            if in_editable(f, [e]):
                die(f"frozen file {f} lies inside editable path {e}")
    home.ensure()
    source = git(repo, "rev-parse", "HEAD")
    if contract["guard_cmd"]:
        code, _, _, _ = run_command(contract["guard_cmd"], repo, home.raw_path("guard-baseline.log"), None)
        if code != 0:
            die(f"the constitution's guard exited {code} on the unchanged source; a floor that is already "
                "broken cannot judge attempts (see raw/guard-baseline.log)")
    if a.scenario == "development":
        for name in ("blueprint", "asis"):
            shutil.copyfile(docs[name][1], os.path.join(home.path, name + ".md"))
        baseline = {"source": source, "asis": docs["asis"][0], "blueprint": docs["blueprint"][0]}
        if a.check_cmd:
            code, out, elapsed, timed_out = run_command(contract["test_cmd"], repo, home.raw_path("baseline.log"), None)
            baseline.update(exit=code, elapsed_s=round(elapsed, 1), raw="raw/baseline.log")
    else:
        code, out, elapsed, timed_out = run_command(contract["test_cmd"], repo, home.raw_path("baseline.log"), None)
        baseline = {"exit": code, "elapsed_s": round(elapsed, 1), "source": source,
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
            code, out, _, _ = run_command(contract["test_cmd"], repo, home.raw_path("control.log"), None)
            control = extract_score(contract, out) if code == 0 else None
            if control is None:
                die("the benchmark did not score on an unchanged rerun (see raw/control.log)")
            noise = abs(control - score)
            baseline.update(control_score=control, noise=noise, control_raw="raw/control.log")
            if noise >= contract["delta"]:
                die(f"an unchanged rerun moved the score by {noise:g}, not below delta {contract['delta']:g}; "
                    "raise --delta/--delta-pct above the noise or stabilise the benchmark")
        else:
            if code == 0:
                die("the agreed tests already pass on the unchanged source; the reproduction test must fail "
                    "before the fix (see raw/baseline.log)")
            baseline["passed"] = False
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
              "verdict": "baseline", "raw": c["baseline"].get("raw"), "time": c["started"]})
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


def reserve_seconds(c):
    return (c.get("reserve_minutes") or 0) * 60


def ruled_out(home, c):
    dead = {}
    for r in home.attempts():
        refuted = r.get("verdict") == "rejected" or (r.get("verdict") == "invalid" and r.get("raw"))
        if r.get("kind") == "attempt" and r.get("route") and refuted and r.get("base") == c.get("best"):
            dead.setdefault(r["route"], []).append(r["n"])
    return dead


def cmd_attempt(a):
    home = Home(a.home)
    c = home.load()
    wt, best = c.get("worktree"), c.get("best")
    if not wt:
        die("run start first")
    n = 1 + max([r["n"] for r in home.attempts()] + [0])
    remaining = remaining_seconds(c)
    head = git(wt, "rev-parse", "HEAD")
    if remaining is not None and remaining <= reserve_seconds(c):
        reason = ("time budget exhausted before the run" if remaining <= 0
                  else "inside the reserve window kept for final verification")
        if head != best:
            rollback(wt, best)
            home.log({"n": n, "kind": "attempt", "commit": head, "note": a.note, "time": iso(utc_now()),
                      "verdict": "invalid", "reason": reason, "rolled_back_to": best})
        die(reason + "; run verify and status, then enter Handoff", PRECONDITION)
    if head == best:
        die("HEAD is already best; commit the attempt first")
    if a.route and not re.fullmatch(r"[A-Za-z0-9_.-]+", a.route):
        die("--route must be a short label of letters, digits, '.', '_' or '-'")
    if c["scenario"] == "optimization":
        if not a.route:
            die("--route is required for optimization; name the idea this attempt tests")
        dead = ruled_out(home, c).get(a.route)
        if dead and not a.differs:
            die(f"route '{a.route}' was already refuted against the current best (attempt {dead}); "
                "pass --differs to say what is new, or try another route")
    claimed = a.elements or []
    if claimed and c["scenario"] != "development":
        die("--elements applies to development only")
    if claimed:
        unknown = [e for e in claimed if e not in c["elements"]]
        if unknown:
            die(f"unknown blueprint elements: {unknown}")
        done = set(element_progress(c, home.attempts())["done"])
        unmet = sorted({d for e in claimed for d in c.get("depends", {}).get(e, [])} - done - set(claimed))
        if unmet:
            die(f"dependencies not yet realized: {unmet}; implement them first or claim them in this checkpoint")
    outside, err = check_scope(c, wt, best)
    if err:
        die(err)
    record = {"n": n, "kind": "attempt", "commit": head, "note": a.note, "time": iso(utc_now()), "base": best}
    if a.route:
        record["route"] = a.route
    if a.differs:
        record["differs"] = a.differs
    if claimed:
        record["elements"] = claimed

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
        elif verdict in ("failing", "green", "checkpoint"):
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
    if c.get("guard_cmd"):
        guard_name = f"attempt-{n:03d}.guard.log"
        code, _, _, timed_out = run_command(c["guard_cmd"], wt, home.raw_path(guard_name), remaining)
        if code != 0:
            finish("invalid", INVALID, reason="guard timed out" if timed_out else f"guard exited {code}",
                   raw=f"raw/{guard_name}")
        remaining = remaining_seconds(c)
    if c["scenario"] == "development" and not c["check_cmd"]:
        finish("checkpoint", REJECTED)
    raw_name = f"attempt-{n:03d}.log"
    code, out, elapsed, timed_out = run_command(c["test_cmd"], wt, home.raw_path(raw_name), remaining)
    record.update(raw=f"raw/{raw_name}", elapsed_s=round(elapsed, 1))
    if timed_out:
        finish("invalid", INVALID, reason="command exceeded remaining budget")
    if c["scenario"] == "bugfix":
        if code == 0:
            finish("accepted", ACCEPTED, passed=True, exit=code)
        finish("failing", REJECTED, passed=False, exit=code)
    if c["scenario"] == "development":
        if code == 0:
            finish("green", ACCEPTED, passed=True, exit=code)
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
        out["budget_exhausted"] = remaining is not None and remaining <= 0
        exhausted = remaining is not None and remaining <= reserve_seconds(c)
        out["decision"] = "handoff" if (out["target_met"] or exhausted) else "continue"
        out["stop_reason"] = ("target reached" if out["target_met"] else
                              "time budget exhausted" if out["budget_exhausted"] else
                              "reserve window reached" if exhausted else None)
        out["ruled_out"] = ruled_out(home, c)
    elif c["scenario"] == "bugfix":
        kept = kept_attempts(home)
        passing = bool(kept) and kept[-1]["verdict"] == "accepted"
        out["all_tests_pass"] = passing
        out["decision"] = "handoff" if passing else "continue"
    else:
        wt, text = c.get("worktree"), ""
        asbuilt_exists = bool(wt) and os.path.isfile(os.path.join(wt, c["asbuilt"]))
        if asbuilt_exists:
            with open(os.path.join(wt, c["asbuilt"])) as f:
                text = f.read()
        attempts = kept_attempts(home)
        if c.get("check_cmd"):
            out["check_green"] = bool(attempts) and attempts[-1]["verdict"] == "green"
        else:
            out["check_green"] = bool(attempts)
        with open(os.path.join(home.path, "blueprint.md"), encoding="utf-8") as f:
            blueprint = f.read()
        out["asbuilt_exists"] = asbuilt_exists
        out["asbuilt_copies_blueprint"] = asbuilt_exists and diagram_body(text) == diagram_body(blueprint)
        out["elements_missing"] = [e for e in c["elements"] if not element_found(e, text)]
        progress = element_progress(c, attempts)
        out.update(elements_done=progress["done"], elements_ready=progress["ready"],
                   elements_blocked=progress["blocked"], elements_pending=progress["pending"])
        out["decision"] = ("handoff" if asbuilt_exists and not out["asbuilt_copies_blueprint"]
                           and not out["elements_missing"] and out["check_green"]
                           and len(progress["done"]) == len(c["elements"]) else "continue")
    wt = c.get("worktree")
    if wt and os.path.isdir(wt):
        out["head"] = git(wt, "rev-parse", "HEAD")
        out["head_is_best"] = out["head"] == c.get("best")
        out["worktree_clean"] = not git(wt, "status", "--porcelain")
    out["next"] = next_step(c, out)
    print(json.dumps(out, indent=2))


def kept_attempts(home):
    return [r for r in home.attempts() if r.get("kind") == "attempt" and r.get("verdict") != "invalid"]


def next_step(c, s):
    if not c.get("worktree"):
        return "create the loop worktree and run start"
    if "head" not in s:
        return f"worktree {c['worktree']} is missing; restore it at best {c.get('best')} or run a new Clarify"
    if not s["worktree_clean"]:
        return "uncommitted changes in the worktree: commit them and run attempt, or discard them"
    if not s["head_is_best"]:
        return "HEAD is a commit not yet judged: run attempt on it, or reset to best"
    if s["decision"] == "handoff":
        return "run verify, then report, and enter Handoff"
    if c["scenario"] == "optimization":
        dead = ", ".join(s["ruled_out"]) or "none"
        return f"commit the next attempt under a new --route (refuted against best: {dead})"
    if c["scenario"] == "bugfix":
        return "fix within the approved impact and run attempt until the agreed tests pass"
    if s["elements_pending"]:
        return "make the regression check green to realize: " + " ".join(s["elements_pending"])
    if s["elements_ready"]:
        return "implement and claim with --elements: " + " ".join(s["elements_ready"])
    if not s["check_green"]:
        return "make the regression check green"
    return "draw the as-built diagrams from the delivered code, covering: " + " ".join(s["elements_missing"] or c["elements"])


def cmd_verify(a):
    home = Home(a.home)
    c = home.load()
    wt, best = c.get("worktree"), c.get("best")
    if not wt:
        die("run start first")
    if not c.get("test_cmd") and not c.get("guard_cmd"):
        die("no check command recorded for this contract")
    if git(wt, "status", "--porcelain"):
        die("worktree is dirty; commit or clean before verify")
    head = git(wt, "rev-parse", "HEAD")
    if head != best:
        die("HEAD differs from the retained best; git reset --hard to best before verify")
    rec = {"n": 1 + max([r["n"] for r in home.attempts()] + [0]), "kind": "verify",
           "commit": head, "time": iso(utc_now())}
    ok = True
    if c.get("guard_cmd"):
        code, _, _, _ = run_command(c["guard_cmd"], wt, home.raw_path("verify.guard.log"), None)
        rec.update(guard_exit=code, guard_raw="raw/verify.guard.log")
        ok = code == 0
    if c.get("test_cmd"):
        code, out, elapsed, _ = run_command(c["test_cmd"], wt, home.raw_path("verify.log"), None)
        rec.update(raw="raw/verify.log", exit=code, elapsed_s=round(elapsed, 1))
        ok = ok and code == 0
        if c["scenario"] == "optimization":
            score = extract_score(c, out)
            rec.update(score=score, recorded_best=c.get("best_score"),
                       target_met=meets_target(c, score),
                       target_met_recorded=meets_target(c, c.get("best_score")))
            ok = ok and score is not None and rec["target_met"] == rec["target_met_recorded"]
    rec["verdict"] = "verified" if ok else "failed"
    home.log(rec)
    print(json.dumps(rec, indent=2))
    sys.exit(0 if ok else INVALID)


def cmd_report(a):
    home = Home(a.home)
    c = home.load()
    rows = home.attempts()
    if c["scenario"] == "bugfix":
        report_table(home, c, rows, a.out)
    elif c["scenario"] == "development":
        report_blueprint(home, c, a.out)
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


def report_blueprint(home, c, out):
    wt = c.get("worktree") or c["repo"]
    with open(os.path.join(home.path, "blueprint.md")) as f:
        blueprint = f.read().rstrip()
    asbuilt = None
    asbuilt_path = os.path.join(wt, c["asbuilt"])
    if os.path.isfile(asbuilt_path):
        with open(asbuilt_path) as f:
            asbuilt = f.read().rstrip()
    def block(text):
        return text if "```" in text else "```mermaid\n" + text + "\n```"

    lines = ["## Agreed blueprint", "", block(blueprint), "",
             "## As-built (delivered)", ""]
    lines += [block(asbuilt)] if asbuilt is not None else [
        f"as-built file is missing: `{c['asbuilt']}`"]
    progress = element_progress(c, home.attempts())
    deps = c.get("depends", {})
    lines += ["", "## Element coverage", "", "| Element | Depends on | Realized in | In as-built |",
              "|---|---|---|---|"]
    for e in c["elements"]:
        found = asbuilt is not None and element_found(e, asbuilt)
        needs = ", ".join(f"`{d}`" for d in deps.get(e, [])) or "-"
        commit = progress["realized_in"].get(e)
        lines.append(f"| `{e}` | {needs} | {f'`{commit[:10]}`' if commit else 'not realized'} | "
                     f"{'yes' if found else 'no'} |")
    lines += ["", "## Build order", ""]
    batches = c.get("batches", [c["elements"]])
    lines += [f"{i}. " + " ".join(f"`{e}`" for e in batch) for i, batch in enumerate(batches, 1)]
    node = {e: f"e{i}" for i, e in enumerate(c["elements"])}
    graph = ["graph LR"] + [f'  {node[e]}["{e}"]' for e in c["elements"]]
    graph += [f"  {node[d]} --> {node[e]}" for e in c["elements"] for d in deps.get(e, [])]
    graph += ["  classDef done fill:#0f5132,stroke:#75b798,color:#fff",
              "  classDef pending fill:#664d03,stroke:#ffda6a,color:#fff"]
    for state in ("done", "pending"):
        if progress[state]:
            graph.append(f"  class {','.join(node[e] for e in progress[state])} {state}")
    lines += ["", "## Dependency graph", "", "Green: realized; amber: claimed while the check was failing.", "",
              "```mermaid", *graph, "```"]
    tail = f"Delivered commit `{c.get('best')}`."
    if c.get("check_cmd"):
        tail += f" Rerun with `{c['check_cmd']}`."
    lines += ["", tail]
    path = out or os.path.join(home.path, "blueprint-handoff.md")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
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
    routes = {}
    for r in pts[1:]:
        tally = routes.setdefault(r.get("route") or "-", {"accepted": 0, "rejected": 0, "invalid": 0})
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    caption = {"baseline": baseline, "final": final, "unit": unit, "direction": direction,
               "improvement": imp, "improvement_pct": pct, "target": target,
               "target_met": meets_target(c, final), "attempts": len(pts) - 1, "routes": routes,
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
    i.add_argument("--scenario", choices=["development", "bugfix", "optimization"], required=True)
    i.add_argument("--branch-from")
    i.add_argument("--editable", nargs="+", required=True)
    i.add_argument("--frozen", nargs="+")
    i.add_argument("--test-cmd")
    i.add_argument("--check-cmd")
    i.add_argument("--blueprint")
    i.add_argument("--asis")
    i.add_argument("--asbuilt")
    i.add_argument("--budget-minutes", type=float)
    i.add_argument("--reserve-minutes", type=float,
                   help="tail of the budget kept for verify and Handoff; new attempts are refused inside it")
    i.add_argument("--score-regex")
    i.add_argument("--direction", choices=["lower", "higher"])
    i.add_argument("--unit")
    i.add_argument("--delta", type=float)
    i.add_argument("--delta-pct", type=float)
    i.add_argument("--target", type=float)
    i.add_argument("--exclusive", action="store_true", help="target excludes equality")
    i.add_argument("--renew", action="store_true")
    i.add_argument("--constitution", help=f"standing project rules; defaults to {CONSTITUTION} when present")
    i.set_defaults(fn=cmd_init)

    s = sub.add_parser("start")
    s.add_argument("--worktree", required=True)
    s.add_argument("--no-smoke", action="store_true")
    s.set_defaults(fn=cmd_start)

    sub.add_parser("smoke").set_defaults(fn=cmd_smoke)

    t = sub.add_parser("attempt")
    t.add_argument("--note", default="")
    t.add_argument("--route", help="label of the idea under test; required for optimization")
    t.add_argument("--differs", help="what is new when retrying a route refuted against the current best")
    t.add_argument("--elements", nargs="+", help="blueprint element IDs this development checkpoint realizes")
    t.set_defaults(fn=cmd_attempt)

    sub.add_parser("status").set_defaults(fn=cmd_status)

    sub.add_parser("verify").set_defaults(fn=cmd_verify)

    r = sub.add_parser("report")
    r.add_argument("--out")
    r.set_defaults(fn=cmd_report)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
