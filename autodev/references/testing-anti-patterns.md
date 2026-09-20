# Correctness gate: testing anti-patterns

Read only when adding or changing mocks, test utilities, or test-only APIs. These checks support the [correctness gate](gate.md) across **Anchor → Ratchet → Prove**; ordinary tests need not load them.

Assert real behavior, keep utilities out of production, and understand dependencies before mocking. Examples are illustrative, not framework requirements.

## 1. Testing mock behavior

**Reject:**
```typescript
// ❌ BAD: Testing that the mock exists
test('renders sidebar', () => {
  render(<Page />);
  expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();
});
```

**Use the real component or assert the parent's behavior, not mock existence:**
```typescript
// ✅ GOOD: Test real component or don't mock it
test('renders sidebar', () => {
  render(<Page />);  // Don't mock sidebar
  expect(screen.getByRole('navigation')).toBeInTheDocument();
});

// OR if sidebar must be mocked for isolation:
// Don't assert on the mock - test Page's behavior with sidebar present
```

## 2. Test-only methods in production

**Reject:**
```typescript
// ❌ BAD: destroy() only used in tests
class Session {
  async destroy() {  // Looks like production API!
    await this._workspaceManager?.destroyWorkspace(this.id);
    // ... cleanup
  }
}

// In tests
afterEach(() => session.destroy());
```

**Keep test cleanup in test utilities, not the production API:**
```typescript
// ✅ GOOD: Test utilities handle test cleanup
// Session has no destroy() - it's stateless in production

// In test-utils/
export async function cleanupSession(session: Session) {
  const workspace = session.getWorkspaceInfo();
  if (workspace) {
    await workspaceManager.destroyWorkspace(workspace.id);
  }
}

// In tests
afterEach(() => cleanupSession(session));
```

Check real callers and resource ownership: test-only APIs belong in utilities; lifecycle methods belong to the resource's owner.

## 3. Mocking without understanding

**Reject:**
```typescript
// ❌ BAD: Mock breaks test logic
test('detects duplicate server', () => {
  // Mock prevents config write that test depends on!
  vi.mock('ToolCatalog', () => ({
    discoverAndCacheTools: vi.fn().mockResolvedValue(undefined)
  }));

  await addServer(config);
  await addServer(config);  // Should throw - but won't!
});
```

**Preserve required side effects; mock only the slow/external boundary:**
```typescript
// ✅ GOOD: Mock at correct level
test('detects duplicate server', () => {
  // Mock the slow part, preserve behavior test needs
  vi.mock('MCPServerManager'); // Just mock slow server startup

  await addServer(config);  // Config written
  await expect(addServer(config)).rejects.toThrow();  // Duplicate detected ✓
});
```

Before mocking, identify side effects and which ones the test needs. If unsure, run the real implementation first. Mock a lower-level boundary or preserve the required effects in the double; “just to be safe” is not a reason.

## 4. Incomplete mocks

**Reject:**
```typescript
// ❌ BAD: Partial mock - only fields you think you need
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' }
  // Missing: metadata that downstream code uses
};

// Later: breaks when code accesses response.metadata.requestId
```

**Mirror the complete real response schema, including downstream fields:**
```typescript
// ✅ GOOD: Mirror real API completeness
const mockResponse = {
  status: 'success',
  data: { userId: '123', name: 'Alice' },
  metadata: { requestId: 'req-789', timestamp: 1234567890 }
  // All fields real API returns
};
```

Inspect the real response/schema first. Include all documented fields and verify downstream consumers, not just the immediate assertion.

## 5. Integration tests as an afterthought

“Implementation complete, ready for testing” is not GREEN. Start with the failing integration behavior, implement it, then verify focused tests and the full suite before Prove.

## 6. Over-complex mocks

Setup longer than assertions, mocking everything, missing real methods, unexplained doubles, or mock-dependent failures are stop signals. Prefer a real integration test and re-establish RED → GREEN.
