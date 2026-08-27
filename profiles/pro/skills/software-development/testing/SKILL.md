---
name: testing
description: "Software testing methodology — test-driven development (TDD) for writing code, and exploratory QA dogfooding for testing web apps. Use when implementing features or bugfixes (write tests first), or when performing systematic QA testing of a web application."
version: 1.0.0
metadata:
  hermes:
    tags: [testing, tdd, qa, dogfood, browser, web]
---

# Software Testing

Two complementary testing methodologies:

1. **Test-Driven Development (TDD)** — during development, write the test first, watch it fail, implement minimal code to pass, refactor. Use BEFORE writing implementation code.

2. **Exploratory QA (Dogfooding)** — after development, systematically explore a web app to find bugs, capture evidence, and produce structured reports. Use when testing a deployed or staging web application.

---

## Part 1: Test-Driven Development (TDD)

### The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? Delete it. Start over.

**No exceptions:**
- Don't keep it as "reference"
- Don't "adapt" it while writing tests
- Don't look at it
- Delete means delete

Implement fresh from tests. Period.

### Red-Green-Refactor

#### RED - Write Failing Test

Write one minimal test showing what should happen.

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

**Requirements:**
- One behavior
- Clear name
- Real code (no mocks unless unavoidable)

#### Verify RED - Watch It Fail (MANDATORY)

```bash
npm test path/to/test.test.ts
```

Confirm:
- Test fails (not errors)
- Failure message is expected
- Fails because feature missing (not typos)

**Test passes?** You're testing existing behavior. Fix test.
**Test errors?** Fix error, re-run until it fails correctly.

#### GREEN - Minimal Code

Write simplest code to pass the test. Don't add features, refactor other code, or "improve" beyond the test.

#### Verify GREEN - Watch It Pass (MANDATORY)

Confirm: test passes, other tests still pass, output pristine.

#### REFACTOR - Clean Up

After green only: remove duplication, improve names, extract helpers. Keep tests green. Don't add behavior.

### When to Use

**Always:** New features, bug fixes, refactoring, behavior changes.

**Exceptions (ask your human partner):** Throwaway prototypes, generated code, configuration files.

### Why Order Matters

- Tests written after code pass immediately. Passing immediately proves nothing — might test wrong thing, might test implementation not behavior, might miss edge cases.
- Test-first forces you to see the test fail, proving it actually tests something.
- Tests-after = "What does this do?" Tests-first = "What should this do?"

### Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing. |
| "Already manually tested" | Ad-hoc ≠ systematic. No record, can't re-run. |
| "Deleting X hours is wasteful" | Sunk cost fallacy. Keeping unverified code is technical debt. |
| "TDD is dogmatic" | TDD IS pragmatic — finds bugs before commit, prevents regressions. |
| "This is different because..." | No. Delete code. Start over with TDD. |

### Red Flags - STOP and Start Over

- Code before test
- Test after implementation
- Test passes immediately
- Can't explain why test failed
- Rationalizing "just this once"
- "Keep as reference" or "adapt existing code"
- "Already spent X hours, deleting is wasteful"

### Bug Fix Pattern

**Bug:** Empty email accepted

**RED**
```typescript
test('rejects empty email', async () => {
  const result = await submitForm({ email: '' });
  expect(result.error).toBe('Email required');
});
```

**Verify RED** → fails as expected (undefined, not 'Email required')

**GREEN**
```typescript
function submitForm(data: FormData) {
  if (!data.email?.trim()) {
    return { error: 'Email required' };
  }
  // ...
}
```

**Verify GREEN** → passes. Bug fixed with regression test.

### Verification Checklist

- [ ] Every new function/method has a test
- [ ] Watched each test fail before implementing
- [ ] Each test failed for expected reason
- [ ] Wrote minimal code to pass each test
- [ ] All tests pass
- [ ] Output pristine (no errors, warnings)
- [ ] Tests use real code (mocks only if unavoidable)
- [ ] Edge cases and errors covered

---

## Part 2: Exploratory QA (Dogfooding)

Systematic exploratory QA testing of web applications using the browser toolset.

### Prerequisites

- Browser toolset available (`browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, `browser_vision`, `browser_console`, `browser_scroll`, `browser_back`, `browser_press`)
- A target URL and testing scope from the user

### Workflow (5 Phases)

#### Phase 1: Plan

1. Create output directory: `{output_dir}/screenshots/` and `{output_dir}/report.md`
2. Build a rough sitemap: landing page, navigation links, key user flows, forms, edge cases.

#### Phase 2: Explore

For each page/feature:

1. **Navigate** → `browser_navigate(url="...")`
2. **Snapshot** → `browser_snapshot()` to understand DOM
3. **Check console** → `browser_console(clear=true)` — do this after EVERY navigation and interaction. Silent JS errors are high-value findings.
4. **Annotated screenshot** → `browser_vision(question="Describe layout, identify visual issues", annotate=true)` — the `annotate=true` flag overlays numbered `[N]` labels on interactive elements.
5. **Test interactions** → click buttons, fill forms, test keyboard navigation, test validation with invalid inputs, test empty submissions.
6. **After each interaction** → check console, take screenshot, compare expected vs actual.

#### Phase 3: Collect Evidence

For every issue:
- Screenshot showing the issue
- URL, steps to reproduce, expected vs actual behavior, console errors
- Classify using the issue taxonomy in `references/issue-taxonomy.md`

#### Phase 4: Categorize

De-duplicate, assign final severity (Critical/High/Medium/Low) and category (Functional/Visual/Accessibility/Console/UX/Content), sort by severity.

#### Phase 5: Report

Generate report using `templates/dogfood-report-template.md`. Include executive summary, per-issue sections with screenshot references (`MEDIA:<path>`), and summary table.

### Tips

- **Always check `browser_console()` after navigating and after significant interactions.** Silent JS errors are among the most valuable findings.
- **Use `annotate=true` with `browser_vision`** when you need to reason about interactive element positions.
- **Test with both valid and invalid inputs** — form validation bugs are common.
- **Scroll through long pages** — content below the fold may have rendering issues.
- **Test navigation flows** — click through multi-step processes end-to-end.
- **Don't forget edge cases**: empty states, very long text, special characters, rapid clicking.
