# Jest / Vitest Unit Test Setup

Generic setup patterns for any Node.js / frontend project. Adapt imports to your test runner.

---

## Basic Test Structure

```typescript
// user.service.spec.ts
import { UserService } from './user.service';
import { createMockRepository } from '../test/helpers/mock-repository';

describe('UserService', () => {
  let service: UserService;
  let userRepo: ReturnType<typeof createMockRepository>;

  beforeEach(() => {
    userRepo = createMockRepository();
    service = new UserService(userRepo as any);
  });

  afterEach(() => {
    jest.clearAllMocks(); // reset call counts between tests
  });

  describe('findById', () => {
    it('returns user when found', async () => {
      const user = { id: '1', email: 'a@b.com' };
      userRepo.findOne.mockResolvedValue(user);

      const result = await service.findById('1');

      expect(result).toEqual(user);
      expect(userRepo.findOne).toHaveBeenCalledWith({ where: { id: '1' } });
    });

    it('throws NotFoundException when user does not exist', async () => {
      userRepo.findOne.mockResolvedValue(null);

      await expect(service.findById('missing')).rejects.toThrow('User not found');
    });
  });
});
```

---

## Mock Repository Factory (framework-agnostic)

```typescript
// test/helpers/mock-repository.ts
export function createMockRepository<T = any>() {
  return {
    find:         jest.fn(),
    findOne:      jest.fn(),
    findOneBy:    jest.fn(),
    findAndCount: jest.fn(),
    save:         jest.fn(),
    create:       jest.fn((dto) => dto),
    update:       jest.fn(),
    delete:       jest.fn(),
    softDelete:   jest.fn(),
    count:        jest.fn(),
    // QueryBuilder chain — return `this` for chaining
    createQueryBuilder: jest.fn().mockReturnValue({
      where:      jest.fn().mockReturnThis(),
      andWhere:   jest.fn().mockReturnThis(),
      leftJoinAndSelect: jest.fn().mockReturnThis(),
      orderBy:    jest.fn().mockReturnThis(),
      skip:       jest.fn().mockReturnThis(),
      take:       jest.fn().mockReturnThis(),
      getOne:     jest.fn(),
      getMany:    jest.fn(),
      getManyAndCount: jest.fn(),
    }),
  };
}
```

---

## Async / Promise Patterns

```typescript
// Testing resolved values
it('handles resolved promise', async () => {
  mockService.doWork.mockResolvedValue({ status: 'ok' });
  const result = await sut.trigger();
  expect(result.status).toBe('ok');
});

// Testing rejected values
it('propagates errors', async () => {
  mockService.doWork.mockRejectedValue(new Error('DB down'));
  await expect(sut.trigger()).rejects.toThrow('DB down');
});

// Testing that a function was NOT called
it('skips expensive step when cache hits', async () => {
  cache.get.mockResolvedValue('cached');
  await sut.process();
  expect(expensiveOp).not.toHaveBeenCalled();
});
```

---

## Spy vs Mock — When to Use Each

```typescript
// Spy: watch a real method, optionally override return
const spy = jest.spyOn(logger, 'error');
// ... run code ...
expect(spy).toHaveBeenCalledWith(expect.stringContaining('FAILED'));
spy.mockRestore(); // restore original after test

// Mock: replace an entire module
jest.mock('../email/email.service', () => ({
  EmailService: jest.fn().mockImplementation(() => ({
    send: jest.fn().mockResolvedValue(undefined),
  })),
}));
```

---

## Vitest Equivalent

```typescript
// Replace jest with vi — API is identical
import { vi, describe, it, expect, beforeEach } from 'vitest';

const mockFn = vi.fn();
vi.spyOn(obj, 'method');
vi.mock('../module');
vi.clearAllMocks(); // same as jest.clearAllMocks()
```

---

## Common Matchers Reference

```typescript
// Equality
expect(val).toBe(x);           // strict ===
expect(val).toEqual(x);        // deep equality
expect(val).toStrictEqual(x);  // includes undefined keys

// Truthiness
expect(val).toBeTruthy();
expect(val).toBeFalsy();
expect(val).toBeNull();
expect(val).toBeUndefined();

// Numbers
expect(val).toBeGreaterThan(0);
expect(val).toBeCloseTo(3.14, 2);

// Arrays / Objects
expect(arr).toContain('item');
expect(arr).toHaveLength(3);
expect(obj).toMatchObject({ key: 'value' }); // partial match
expect(obj).toHaveProperty('a.b.c');

// Errors
expect(() => fn()).toThrow('message');
expect(async () => fn()).rejects.toThrow(SomeError);

// Calls
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledTimes(2);
expect(mockFn).toHaveBeenCalledWith(arg1, expect.any(String));
expect(mockFn).toHaveBeenLastCalledWith(arg);
```

---

## Setup Files

```typescript
// jest.config.ts
export default {
  preset: 'ts-jest',            // or use Vitest config
  testEnvironment: 'node',      // use 'jsdom' for browser/React tests
  setupFilesAfterFramework: ['./test/setup.ts'],
  clearMocks: true,             // clear mock state between tests automatically
  coverageThreshold: {
    global: { lines: 70, functions: 70, branches: 60 },
  },
};

// test/setup.ts — global setup
process.env.NODE_ENV = 'test';
process.env.DATABASE_URL = 'postgresql://localhost:5432/test';
// Never use real external service credentials here — mock them instead
```
