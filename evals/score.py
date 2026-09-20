import argparse
import json
from pathlib import Path


def score(cases, report):
    case_map = {case["id"]: case for case in cases}
    result_map = {}
    for result in report.get("results", []):
        case_id = result["case_id"]
        if case_id not in case_map:
            raise ValueError(f"unknown case: {case_id}")
        if case_id in result_map:
            raise ValueError(f"duplicate case: {case_id}")
        result_map[case_id] = result

    required_passed = 0
    required_total = 0
    optional_passed = 0
    optional_total = 0
    failures = []
    for case_id, case in case_map.items():
        answers = result_map.get(case_id, {}).get("assertions", {})
        known_assertions = {assertion["id"] for assertion in case["assertions"]}
        unknown_assertions = set(answers) - known_assertions
        if unknown_assertions:
            unknown = sorted(unknown_assertions)[0]
            raise ValueError(f"unknown assertion for {case_id}: {unknown}")
        for assertion in case["assertions"]:
            assertion_id = assertion["id"]
            passed = answers.get(assertion_id) is True
            if assertion["required"]:
                required_total += 1
                required_passed += passed
                if not passed:
                    failures.append(f"{case_id}/{assertion_id}")
            else:
                optional_total += 1
                optional_passed += passed

    missing_cases = sorted(set(case_map) - set(result_map))
    return {
        "passed": not failures and not missing_cases,
        "required": {"passed": required_passed, "total": required_total},
        "optional": {"passed": optional_passed, "total": optional_total},
        "missing_cases": missing_cases,
        "failures": failures,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument(
        "--cases",
        type=Path,
        default=Path(__file__).with_name("cases.json"),
    )
    args = parser.parse_args()
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    report = json.loads(args.report.read_text(encoding="utf-8"))
    summary = score(cases, report)
    print(json.dumps(summary, indent=2))
    raise SystemExit(0 if summary["passed"] else 1)


if __name__ == "__main__":
    main()
