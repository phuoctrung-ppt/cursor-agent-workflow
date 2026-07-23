# Playwright E2E — Generic Patterns

Framework-agnostic Playwright patterns. Adapt selectors and URLs to your project's routes (see `AGENTS.md §6` for critical paths).

---

## Project Structure

```
tests/
  e2e/
    fixtures/          # shared auth state, test data factories
    pages/             # Page Object Models
    specs/             # test files (*.e2e.ts)
  test-data/           # static fixtures, seed scripts
playwright.config.ts
```

---

## Config

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html'], ['line']],
  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile',   use: { ...devices['iPhone 14'] } },
  ],
  webServer: {
    command: 'npm run start:test',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## Page Object Model (POM)

```typescript
// tests/e2e/pages/login.page.ts
import { Page, Locator, expect } from '@playwright/test';

export class LoginPage {
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(private page: Page) {
    this.emailInput    = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton  = page.getByRole('button', { name: 'Sign in' });
    this.errorMessage  = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectError(message: string) {
    await expect(this.errorMessage).toContainText(message);
  }
}
```

---

## Auth Fixtures (Reuse Session State)

```typescript
// tests/e2e/fixtures/auth.fixture.ts
import { test as base, Page } from '@playwright/test';
import { LoginPage } from '../pages/login.page';

type AuthFixtures = {
  authenticatedPage: Page;
};

// Store auth state once, reuse across tests — avoids logging in for every test
export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      storageState: 'tests/e2e/fixtures/.auth.json', // saved auth state
    });
    const page = await context.newPage();
    await use(page);
    await context.close();
  },
});

// Generate .auth.json once in global setup:
// globalSetup: './tests/e2e/fixtures/global-setup.ts'
// async function globalSetup() {
//   const browser = await chromium.launch();
//   const page = await browser.newPage();
//   await new LoginPage(page).login(TEST_USER, TEST_PASS);
//   await page.context().storageState({ path: '.auth.json' });
// }
```

---

## Test Patterns

```typescript
// tests/e2e/specs/checkout.e2e.ts
import { test, expect } from '../fixtures/auth.fixture';
import { CheckoutPage } from '../pages/checkout.page';

test.describe('Checkout flow', () => {
  test('completes purchase with valid card', async ({ authenticatedPage }) => {
    const checkout = new CheckoutPage(authenticatedPage);

    await checkout.goto();
    await checkout.selectItem('Basic Plan');
    await checkout.fillCard({ number: '4242424242424242', expiry: '12/30', cvc: '123' });
    await checkout.submit();

    // Wait for navigation, not arbitrary timeout
    await authenticatedPage.waitForURL('**/success');
    await expect(authenticatedPage.getByText('Payment successful')).toBeVisible();
  });

  test('shows error for declined card', async ({ authenticatedPage }) => {
    const checkout = new CheckoutPage(authenticatedPage);
    await checkout.goto();
    await checkout.fillCard({ number: '4000000000000002', expiry: '12/30', cvc: '123' });
    await checkout.submit();

    await expect(authenticatedPage.getByRole('alert')).toContainText('Card declined');
  });
});
```

---

## Waiting Strategies

```typescript
// ✅ Prefer semantic waits over arbitrary timeouts
await page.waitForURL('**/dashboard');
await expect(locator).toBeVisible();
await expect(locator).toContainText('Ready');
await page.waitForResponse('**/api/status');

// ✅ Wait for network idle after navigation
await page.goto('/dashboard', { waitUntil: 'networkidle' });

// ❌ Avoid — flaky
await page.waitForTimeout(2000);
```

---

## API Mocking in E2E

```typescript
// Mock external payment API during E2E (don't hit real Stripe)
test('checkout with mocked payment', async ({ page }) => {
  await page.route('**/api/payments/charge', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'succeeded', id: 'ch_test_123' }),
    });
  });

  // test continues with mocked response
});
```

---

## Test Data Factories

```typescript
// tests/e2e/fixtures/factories.ts
export function createTestUser(overrides: Partial<User> = {}): User {
  return {
    email: `test+${Date.now()}@example.com`,
    password: 'Test1234!',
    name: 'Test User',
    ...overrides,
  };
}
// Use unique emails to avoid conflicts between parallel test runs
```

---

## CI Integration

```yaml
# .github/workflows/e2e.yml
- name: Install Playwright
  run: npx playwright install --with-deps chromium

- name: Run E2E tests
  run: npx playwright test
  env:
    BASE_URL: http://localhost:3000
    CI: true

- name: Upload test report
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: playwright-report
    path: playwright-report/
```
