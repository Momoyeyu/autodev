import argparse
import json
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "evals" / "cases.json"
FIXTURES_ROOT = ROOT / "evals" / "fixtures"
SKILL_ROOT = ROOT / "autodev"
ARTIFACT_ROOT = ROOT / ".autodev-evals"
MARKER = ".managed-by-autodev-evals"
MAC_DEVIN = Path(
    "/Applications/Devin.app/Contents/Resources/app/extensions/windsurf/devin/bin/devin"
)


def load_cases():
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def build_prompt(case):
    return (
        "/autodev\n\n"
        f"Repository context:\n{case['context']}\n\n"
        f"Task:\n{case['prompt']}"
    )


def git(workspace, *args, capture=False):
    env = os.environ | {
        "GIT_AUTHOR_NAME": "autodev eval",
        "GIT_AUTHOR_EMAIL": "eval@localhost",
        "GIT_COMMITTER_NAME": "autodev eval",
        "GIT_COMMITTER_EMAIL": "eval@localhost",
    }
    result = subprocess.run(
        ["git", *args],
        cwd=workspace,
        env=env,
        check=True,
        text=True,
        capture_output=capture,
    )
    return result.stdout if capture else ""


def prepare_case(case, fixture, skill, artifacts, run_id):
    artifacts.mkdir(parents=True, exist_ok=True)
    marker = artifacts / MARKER
    marker.touch(exist_ok=True)
    case_dir = artifacts / run_id / case["id"]
    if case_dir.exists():
        raise FileExistsError(f"case already prepared: {case_dir}")
    workspace = case_dir / "workspace"
    shutil.copytree(fixture, workspace)
    installed_skill = workspace / ".devin" / "skills" / "autodev"
    shutil.copytree(skill, installed_skill)
    git(workspace, "init", "-q")
    git(workspace, "add", ".")
    git(workspace, "commit", "-q", "-m", "chore: initialize eval fixture")
    manifest = {
        "case_id": case["id"],
        "title": case["title"],
        "prompt": build_prompt(case),
        "follow_ups": case.get("follow_ups", []),
        "prepared_at": datetime.now(UTC).isoformat(),
    }
    case_dir.mkdir(parents=True, exist_ok=True)
    (case_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return case_dir


def find_devin():
    configured = os.environ.get("DEVIN_BIN")
    if configured:
        return Path(configured)
    discovered = shutil.which("devin")
    if discovered:
        return Path(discovered)
    if MAC_DEVIN.is_file():
        return MAC_DEVIN
    raise FileNotFoundError("devin CLI not found; set DEVIN_BIN")


def ensure_authenticated(devin):
    result = subprocess.run(
        [str(devin), "auth", "status"],
        text=True,
        capture_output=True,
    )
    output = result.stdout + result.stderr
    if result.returncode != 0 or "not logged in" in output.lower():
        raise RuntimeError(f"Devin CLI authentication required: {devin} auth login")


def latest_session(devin, workspace):
    result = subprocess.run(
        [str(devin), "list", "--format", "json"],
        cwd=workspace,
        check=True,
        text=True,
        capture_output=True,
    )
    sessions = json.loads(result.stdout)
    matching = [
        session
        for session in sessions
        if Path(session["working_directory"]).resolve() == workspace.resolve()
    ]
    if not matching:
        raise RuntimeError("Devin session was not created")
    return max(matching, key=lambda session: session["last_activity_at"])["id"]


def capture_workspace(case_dir, turn):
    workspace = case_dir / "workspace"
    (case_dir / f"diff-{turn}.patch").write_text(
        git(workspace, "diff", "--binary", capture=True),
        encoding="utf-8",
    )
    (case_dir / f"status-{turn}.txt").write_text(
        git(workspace, "status", "--short", capture=True),
        encoding="utf-8",
    )


def invoke(devin, case_dir, prompt, turn, session_id=None, timeout=900):
    workspace = case_dir / "workspace"
    transcript = case_dir / "transcript.json"
    command = [
        str(devin),
        "--sandbox",
        "--permission-mode",
        "dangerous",
        "--respect-workspace-trust",
        "false",
        "--export",
        str(transcript),
    ]
    if session_id:
        command.extend(["-r", session_id, "-p", prompt])
    else:
        command.extend(["-p", prompt])
    result = subprocess.run(
        command,
        cwd=workspace,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    (case_dir / f"response-{turn}.txt").write_text(result.stdout, encoding="utf-8")
    (case_dir / f"stderr-{turn}.txt").write_text(result.stderr, encoding="utf-8")
    capture_workspace(case_dir, turn)
    return result.returncode


def run_case(devin, case_dir, timeout):
    manifest = json.loads((case_dir / "manifest.json").read_text(encoding="utf-8"))
    return_codes = [invoke(devin, case_dir, manifest["prompt"], 1, timeout=timeout)]
    session_id = latest_session(devin, case_dir / "workspace")
    for turn, follow_up in enumerate(manifest["follow_ups"], start=2):
        return_codes.append(
            invoke(
                devin,
                case_dir,
                follow_up,
                turn,
                session_id=session_id,
                timeout=timeout,
            )
        )
    summary = {
        "case_id": manifest["case_id"],
        "session_id": session_id,
        "return_codes": return_codes,
        "completed_at": datetime.now(UTC).isoformat(),
    }
    (case_dir / "run.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    return all(code == 0 for code in return_codes)


def clean_artifacts(artifacts=ARTIFACT_ROOT):
    if not artifacts.exists():
        return
    if artifacts.is_symlink() or not (artifacts / MARKER).is_file():
        raise RuntimeError(f"refusing to clean without managed marker: {artifacts}")
    shutil.rmtree(artifacts)


def selected_cases(case_ids):
    cases = load_cases()
    if not case_ids:
        return cases
    case_map = {case["id"]: case for case in cases}
    unknown = sorted(set(case_ids) - set(case_map))
    if unknown:
        raise ValueError(f"unknown case: {unknown[0]}")
    return [case_map[case_id] for case_id in case_ids]


def prepare(case_ids, run_id):
    case_dirs = []
    for case in selected_cases(case_ids):
        fixture = FIXTURES_ROOT / case.get("fixture", case["id"])
        case_dirs.append(
            prepare_case(case, fixture, SKILL_ROOT, ARTIFACT_ROOT, run_id)
        )
    return case_dirs


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list")
    list_parser.set_defaults(action="list")
    for name in ("prepare", "run"):
        command_parser = subparsers.add_parser(name)
        command_parser.add_argument("--case", action="append", dest="case_ids")
        command_parser.add_argument("--run-id")
        if name == "run":
            command_parser.add_argument("--timeout", type=int, default=900)
        command_parser.set_defaults(action=name)
    clean_parser = subparsers.add_parser("clean")
    clean_parser.set_defaults(action="clean")
    args = parser.parse_args()

    if args.action == "list":
        for case in load_cases():
            print(f"{case['id']}\t{case['title']}")
        return
    if args.action == "clean":
        clean_artifacts()
        print(f"removed {ARTIFACT_ROOT}")
        return

    run_id = args.run_id or datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    devin = None
    if args.action == "run":
        try:
            devin = find_devin()
            ensure_authenticated(devin)
        except (FileNotFoundError, RuntimeError) as error:
            parser.error(str(error))
    case_dirs = prepare(args.case_ids, run_id)
    if args.action == "prepare":
        print(ARTIFACT_ROOT / run_id)
        return

    outcomes = [run_case(devin, case_dir, args.timeout) for case_dir in case_dirs]
    print(ARTIFACT_ROOT / run_id)
    raise SystemExit(0 if all(outcomes) else 1)


if __name__ == "__main__":
    main()
