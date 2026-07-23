# Mocking Patterns — Generic Reference

Framework-agnostic mocking patterns for unit tests and integration tests. Adapt to Jest or Vitest (API is nearly identical — replace `jest` with `vi`).

---

## 1. Module Mocking

```typescript
// Mock an entire module before import
jest.mock('../services/email.service', () => ({
  EmailService: jest.fn().mockImplementation(() => ({
    send: jest.fn().mockResolvedValue({ messageId: 'mock-123' }),
    sendBulk: jest.fn().mockResolvedValue([]),
  })),
}));

// Mock a third-party SDK (e.g. any HTTP client)
jest.mock('axios', () => ({
  default: {
    get: jest.fn(),
    post: jest.fn(),
    create: jest.fn().mockReturnThis(),
    interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } },
  },
}));
```

---

## 2. MSW (Mock Service Worker) — HTTP Mocking

Use MSW to intercept HTTP at the network level — works in both Node (tests) and browser (dev/storybook).

```typescript
// tests/mocks/handlers.ts — define your API mock handlers
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      name: 'Test User',
      email: 'test@example.com',
    });
  }),

  http.post('/api/auth/login', async ({ request }) => {
    const body = await request.json() as { email: string };
    if (body.email === 'bad@example.com') {
      return HttpResponse.json({ error: 'Invalid credentials' }, { status: 401 });
    }
    return HttpResponse.json({ token: 'mock-jwt-token' });
  }),
];

// tests/mocks/server.ts — Node test server
import { setupServer } from 'msw/node';
export const server = setupServer(...handlers);

// tests/setup.ts — global test setup
import { server } from './mocks/server';
beforeAll(()  => server.listen({ onUnhandledRequest: 'error' }));
afterEach(()  => server.resetHandlers()); // reset overrides between tests
afterAll(()   => server.close());
```

```typescript
// Override a handler for a specific test
import { http, HttpResponse } from 'msw';
import { server } from '../mocks/server';

it('handles 500 errors gracefully', async () => {
  server.use(
    http.get('/api/users/:id', () => {
      return HttpResponse.json({ error: 'Internal error' }, { status: 500 });
    }),
  );

  // test code that should handle the error...
  await expect(service.getUser('1')).rejects.toThrow();
});
```

---

## 3. External Service Mocks

```typescript
// Mock any external provider (payment, email, AI, storage) generically
// Never hit real external services in CI

// Payment provider mock
jest.mock('../providers/payment.provider', () => ({
  PaymentProvider: jest.fn().mockImplementation(() => ({
    charge: jest.fn().mockResolvedValue({ id: 'charge_test', status: 'succeeded' }),
    refund: jest.fn().mockResolvedValue({ id: 'refund_test', status: 'succeeded' }),
  })),
}));

// File storage mock
jest.mock('../providers/storage.provider', () => ({
  StorageProvider: jest.fn().mockImplementation(() => ({
    upload: jest.fn().mockResolvedValue({ url: 'https://mock-cdn.example.com/file.pdf' }),
    delete: jest.fn().mockResolvedValue(undefined),
    getSignedUrl: jest.fn().mockResolvedValue('https://mock-cdn.example.com/signed'),
  })),
}));

// AI/LLM provider mock (avoids real API calls and costs)
const mockCompletion = { choices: [{ message: { content: 'Mocked AI response' } }] };
jest.mock('../providers/llm.provider', () => ({
  LlmProvider: jest.fn().mockImplementation(() => ({
    complete: jest.fn().mockResolvedValue(mockCompletion),
    embed:    jest.fn().mockResolvedValue({ data: [{ embedding: new Array(1536).fill(0) }] }),
  })),
}));
```

---

## 4. Spy Patterns

```typescript
// Spy on a method without replacing the implementation
const sendSpy = jest.spyOn(emailService, 'send');

await service.register(user);

expect(sendSpy).toHaveBeenCalledTimes(1);
expect(sendSpy).toHaveBeenCalledWith(
  expect.objectContaining({ to: user.email, subject: expect.stringContaining('Welcome') })
);
sendSpy.mockRestore(); // restore original after test

// Spy and override return
jest.spyOn(cacheService, 'get').mockResolvedValue(null); // simulate cache miss
jest.spyOn(cacheService, 'get').mockResolvedValueOnce('hit').mockResolvedValue(null);
```

---

## 5. Test Data Factories

```typescript
// Use factories instead of inline objects — easier to maintain and read
// tests/factories/user.factory.ts

let counter = 0;

export function makeUser(overrides: Partial<User> = {}): User {
  counter++;
  return {
    id:        `user-${counter}`,
    email:     `user${counter}@example.com`,
    name:      `Test User ${counter}`,
    role:      'user',
    createdAt: new Date('2024-01-01'),
    ...overrides,
  };
}

export function makeAdmin(overrides: Partial<User> = {}): User {
  return makeUser({ role: 'admin', ...overrides });
}

// In tests
it('rejects non-admin users', async () => {
  const user = makeUser({ role: 'user' });
  await expect(adminService.doAdminThing(user)).rejects.toThrow('Forbidden');
});
```

---

## 6. Database Mocking Strategies

```typescript
// Option A: Mock the repository layer (unit tests — fastest)
const repo = createMockRepository(); // see jest-setup.md
repo.findOne.mockResolvedValue(makeUser());

// Option B: In-memory SQLite / test DB (integration tests)
// Spin up a real DB with migrations for integration tests
// Use a separate DATABASE_URL_TEST env var
// Reset between tests with transactions that roll back:
beforeEach(async () => { await db.query('BEGIN'); });
afterEach(async  () => { await db.query('ROLLBACK'); });

// Option C: Test containers (closest to production, slowest)
// Use @testcontainers/postgresql or similar
// Spin up a real DB container for the test suite
```

---

## 7. Timer Mocking

```typescript
// Control time in tests without real waits
jest.useFakeTimers();

it('expires cache after TTL', () => {
  service.set('key', 'value', 60_000); // 60 second TTL
  expect(service.get('key')).toBe('value');

  jest.advanceTimersByTime(60_001);
  expect(service.get('key')).toBeUndefined(); // expired
});

afterEach(() => {
  jest.useRealTimers(); // always restore after fake timer tests
});
```

---

## 8. Best Practices Checklist

- [ ] Mock at the **boundary** — never mock internal implementation details
- [ ] Use `server.resetHandlers()` after each test to avoid bleed between tests
- [ ] Clear mock state with `jest.clearAllMocks()` in `afterEach` (or set `clearMocks: true` in config)
- [ ] Never set real API keys in test env — CI should fail if a real call is accidentally made
- [ ] Use `onUnhandledRequest: 'error'` in MSW so accidental real calls surface immediately
- [ ] Factory functions for test data — avoids brittle inline object duplication
