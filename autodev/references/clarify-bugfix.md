# Bug fixes and TDD

Use the reported behavior to guide the fix. Keep the loop small: reproduce → fix → check regressions.

1. Inspect the affected path and nearby tests. Identify the expected behavior and the conditions that trigger the defect.
2. Prefer a focused reproduction test before changing the implementation. Run it against the pre-fix source and confirm it fails for the reported reason, rather than a broken fixture or environment. A reliable manual reproduction is useful when automation is impractical; record its steps and limitations.
3. Make the fix, rerun the reproduction, and run relevant existing checks. Add adjacent cases when they cover a plausible regression, not merely the new code's structure.
4. Explain the before/after outcome and any behavior that remains unverified. If the defect cannot be reproduced, say so and separate the diagnosis from a demonstrated fix.

Tests may evolve as understanding improves. Explain changes to expected behavior; preserve still-relevant coverage. Do not weaken an assertion, skip a case, or change an input merely to make the fix pass. If the reproduction already passes before the fix, investigate the mismatch instead of claiming a red-to-green result.

Use the project's test runner and normal development practices. No frozen test manifest, separate approval ceremony, or special repository layout is needed.
