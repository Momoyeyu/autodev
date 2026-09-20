# Correctness gate: worked examples

Read only when the [correctness gate](gate.md) needs a concrete illustration. These TypeScript snippets illustrate the sequence, not a framework requirement; use the target repository's language, runner, and commands.

## Retry behavior

**Anchor / RED:** exercise the operation and assert both its result and retry count.

```typescript
test('retries failed operations 3 times', async () => {
  let attempts = 0;
  const operation = () => {
    attempts++;
    if (attempts < 3) throw new Error('fail');
    return 'success';
  };

  const result = await retryOperation(operation);

  expect(result).toBe('success');
  expect(attempts).toBe(3);
});
```

Run it and verify the expected failure before implementing. A mock call-count assertion alone would omit the returned behavior.

**Ratchet / GREEN:** implement only the behavior the test requires.

```typescript
async function retryOperation<T>(fn: () => Promise<T>): Promise<T> {
  for (let i = 0; i < 3; i++) {
    try {
      return await fn();
    } catch (e) {
      if (i === 2) throw e;
    }
  }
  throw new Error('unreachable');
}
```

Do not add unrequested retry policy:

```typescript
async function retryOperation<T>(
  fn: () => Promise<T>,
  options?: {
    maxRetries?: number;
    backoff?: 'linear' | 'exponential';
    onRetry?: (attempt: number) => void;
  }
): Promise<T> {
  // YAGNI
}
```

Verify the focused test and full suite pass; refactor only while green.

## Bug reproduction

**Anchor / RED:** empty email must be rejected.

```typescript
test('rejects empty email', async () => {
  const result = await submitForm({ email: '' });
  expect(result.error).toBe('Email required');
});
```

Verify RED reports `expected 'Email required', got undefined`, not a test setup error.

**Ratchet / GREEN:** add the minimal guard.

```typescript
function submitForm(data: FormData) {
  if (!data.email?.trim()) {
    return { error: 'Email required' };
  }
  // ...
}
```

Verify GREEN for the reproduction and full suite. Extract shared validation only if needed and while tests stay green. **Prove** reruns the gate from clean conditions and includes this RED → GREEN evidence.
