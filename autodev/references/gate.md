# Correctness gate: Test-Driven Development

Read before changing production code or tests in either mode: **Anchor** verifies RED, **Ratchet** runs GREEN/REFACTOR, **Prove** verifies cleanly. This gate does not replace the four stages or the progress gate.

## The Iron Law

```text
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Discard code written before its test; implement afresh, without retaining or adapting the attempt as reference. Preserve pre-existing user work. Throwaway prototypes, generated code, and configuration need explicit user permission for an exception.

## Anchor: RED

Write one minimal test per behavior, named for its expected result. Show the intended API and observable outcome using real code; mock only when unavoidable. Reproduce a bug before fixing it.

### Verify RED

**Mandatory:** run the focused test using the repository's test command.

- Confirm failure is caused by the missing behavior, with the expected failure message.
- A test that already passes does not demonstrate the change; correct the test.
- A typo, import error, or broken setup is not RED evidence; repair it and rerun.

Freeze the verified acceptance test before implementation.

## Ratchet: GREEN

Write only enough production code to pass that test. No speculative options, unrelated refactoring, or extra behavior.

### Verify GREEN

**Mandatory:** run the focused test and the full suite. Both must pass with no errors or warnings. Fix production code, not the test or its tolerance. Resolve regressions before accepting the attempt.

### REFACTOR

Only while green: remove duplication, improve names, or extract helpers without adding behavior. Rerun tests after each change; optimization also reruns its metric. Start the next behavior with another failing test.

For a worked sequence, read only the relevant section of [testing examples](testing-examples.md). When introducing mocks or helpers, first read [testing anti-patterns](testing-anti-patterns.md).

## Rationalizations

| Excuse | Response |
|---|---|
| “Too simple” | Simple code breaks; test it. |
| “Test after” / “same goals” | An immediate pass proves no defect detection. |
| “Manually tested” / “manual is faster” | Automate for a record and reruns. |
| “Deleting work is wasteful” | Sunk cost is not evidence. |
| “Keep as reference” | Adapting it is test-after; discard it. |
| “Explore first” | Discard exploration, then test first. |
| “Hard to test” | Simplify API and dependencies. |
| “TDD is slow / dogmatic” | Keep runnable regression proof. |
| “No existing tests” | Add the missing behavior test. |

## Red flags

Stop on code-before-test, immediate passes, unexplained failures, or deferred tests. “Just this once”, “spirit not ritual”, manual checks, sunk cost, and reference code are not exemptions. Restart the attempt from RED, preserving unrelated work.

## Prove: completion checklist

- [ ] Every new function/method has a behavior test.
- [ ] Each test was observed failing before implementation.
- [ ] Every RED failure had the intended cause, not a setup error.
- [ ] Only the minimal passing behavior was implemented.
- [ ] The focused tests and full suite pass from clean conditions.
- [ ] Output contains no errors or warnings.
- [ ] Tests exercise real code; unavoidable mocks preserve required behavior.
- [ ] Edge cases and error paths are covered.

An unchecked item means missing evidence, not permission to declare completion.

## When stuck

Write the wished-for API and assertion first. Simplify interfaces, inject dependencies, and extract repeated setup into helpers. If setup still dominates, simplify the design. Ask about unclear behavior or exceptions.
