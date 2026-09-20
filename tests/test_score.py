import unittest

from evals.score import score


CASES = [
    {
        "id": "case-a",
        "assertions": [
            {"id": "required", "required": True},
            {"id": "optional", "required": False},
        ],
    },
    {
        "id": "case-b",
        "assertions": [{"id": "other", "required": True}],
    },
]


class ScoreTest(unittest.TestCase):
    def test_complete_run_passes(self):
        results = {
            "results": [
                {
                    "case_id": "case-a",
                    "assertions": {"required": True, "optional": False},
                },
                {"case_id": "case-b", "assertions": {"other": True}},
            ]
        }

        summary = score(CASES, results)

        self.assertTrue(summary["passed"])
        self.assertEqual(summary["required"], {"passed": 2, "total": 2})
        self.assertEqual(summary["optional"], {"passed": 0, "total": 1})

    def test_missing_required_result_fails(self):
        results = {
            "results": [
                {
                    "case_id": "case-a",
                    "assertions": {"required": True},
                }
            ]
        }

        summary = score(CASES, results)

        self.assertFalse(summary["passed"])
        self.assertEqual(summary["missing_cases"], ["case-b"])

    def test_unknown_case_is_rejected(self):
        results = {
            "results": [
                {"case_id": "case-a", "assertions": {"required": True}},
                {"case_id": "case-b", "assertions": {"other": True}},
                {"case_id": "case-c", "assertions": {}},
            ]
        }

        with self.assertRaisesRegex(ValueError, "unknown case: case-c"):
            score(CASES, results)


if __name__ == "__main__":
    unittest.main()
