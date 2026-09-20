# autodev evals

This suite keeps skill behavior testable without tying the repository to one model.

## Contents

- `cases.json` contains stable prompts, follow-up turns, expected modes, and observable assertions.
- `fixtures/` contains dependency-free repositories copied for each run.
- `run.py` installs the current autodev skill into isolated workspaces and invokes it explicitly with `/autodev`.
- `score.py` turns a reviewed assertion report into a deterministic pass or fail result.
- `../tests/` checks fixtures, corpus structure, cleanup safety, and scorer behavior.

## Run the skill

The runner uses Devin CLI. Authenticate it once if needed:

```bash
/Applications/Devin.app/Contents/Resources/app/extensions/windsurf/devin/bin/devin auth login
```

List or run cases from the repository root:

```bash
python3 evals/run.py list
python3 evals/run.py run --case development-feature
python3 evals/run.py run
```

Each case starts from a fresh fixture and its own Git repository. The runner copies `autodev/` to `.devin/skills/autodev/` inside that workspace, starts the prompt with `/autodev`, resumes configured follow-up turns, and runs Devin in a filesystem sandbox.

## Review artifacts

Every run is written below the ignored `.autodev-evals/<run-id>/` directory. Each case preserves:

- the mutated workspace and its Git history
- the exact prompt and follow-up turns in `manifest.json`
- the exported ATIF conversation in `transcript.json`
- stdout and stderr for every turn
- Git status and binary diff snapshots for every turn
- session ID and process return codes in `run.json`

Nothing under `.autodev-evals/` can be committed accidentally.

## Score a reviewed run

Review the response, transcript, commands, and diff, then mark every assertion `true` or `false`:

```json
{
  "run": {
    "skill_revision": "git revision",
    "agent": "Devin CLI",
    "model": "model name"
  },
  "results": [
    {
      "case_id": "development-feature",
      "assertions": {
        "classifies-development": true,
        "verifies-red": true,
        "verifies-green": true
      },
      "notes": "optional evidence location or failure detail"
    }
  ]
}
```

A full report must include every case. Missing required assertions fail closed.

```bash
python3 evals/score.py path/to/report.json
```

## Clean after review

```bash
python3 evals/run.py clean
```

The command removes only `.autodev-evals/` and refuses to operate unless the runner's management marker exists. Source fixtures and evaluation definitions are never touched.

## Validate the suite

```bash
python3 -m unittest discover -s tests -v
```

When autodev behavior changes, update or add a case before changing the skill text. Keep prompts stable unless the behavior itself changed, so results remain comparable across revisions.
