# LLM Cost Tracking — Generic Reference

Every LLM call must log its cost. Without this you cannot enforce budgets, detect abuse, or optimize model selection. Patterns below are framework-agnostic — adapt to your stack.

---

## Token Cost Calculation

```typescript
// llm/utils/cost-calculator.ts

// Model pricing per 1M tokens (update when providers change pricing)
// Source: provider pricing pages — keep this file current
const PRICING: Record<string, { input: number; output: number }> = {
  // OpenAI
  'gpt-4o':          { input: 5.00,   output: 15.00 },
  'gpt-4o-mini':     { input: 0.15,   output: 0.60 },
  'gpt-4-turbo':     { input: 10.00,  output: 30.00 },
  // Anthropic
  'claude-3-5-sonnet-20241022': { input: 3.00, output: 15.00 },
  'claude-3-haiku':             { input: 0.25, output: 1.25 },
  // Google
  'gemini-1.5-pro':  { input: 3.50,   output: 10.50 },
  'gemini-1.5-flash':{ input: 0.075,  output: 0.30 },
};

export function calculateCost(
  model: string,
  promptTokens: number,
  completionTokens: number,
): number {
  const pricing = PRICING[model];
  if (!pricing) {
    console.warn(`Unknown model for cost calc: ${model}`);
    return 0;
  }
  return (
    (promptTokens / 1_000_000) * pricing.input +
    (completionTokens / 1_000_000) * pricing.output
  );
}
```

---

## Usage Event Schema

```typescript
// llm/interfaces/usage-event.interface.ts
export interface LlmUsageEvent {
  // Identity
  id:        string;          // UUID
  timestamp: Date;
  feature:   string;          // which product feature triggered the call
  userId?:   string;          // if applicable
  tenantId?: string;          // for multi-tenant projects

  // LLM details
  provider: string;           // 'openai' | 'anthropic' | 'gemini'
  model:    string;           // exact model name used
  
  // Token accounting
  promptTokens:     number;
  completionTokens: number;
  totalTokens:      number;
  costUsd:          number;   // 6 decimal precision (e.g. 0.000150)

  // Performance
  latencyMs: number;          // wall-clock time of the LLM call
  
  // Outcome
  cached:   boolean;          // was this a cache hit?
  success:  boolean;
  errorCode?: string;         // if success = false
}
```

---

## Usage Logger

```typescript
// llm/usage-logger.service.ts

export class UsageLogger {
  constructor(
    private readonly db: DatabaseConnection,
    private readonly metricsClient?: MetricsClient, // optional: Prometheus, Datadog, etc.
  ) {}

  async log(event: LlmUsageEvent): Promise<void> {
    // 1. Persist to DB for auditing and reporting
    await this.db.table('llm_usage_events').insert({
      ...event,
      cost_usd: event.costUsd,           // snake_case for SQL
      latency_ms: event.latencyMs,
    });

    // 2. Push to metrics (optional) for real-time dashboards
    this.metricsClient?.gauge('llm.cost_usd', event.costUsd, {
      feature: event.feature,
      model:   event.model,
      provider: event.provider,
    });
    this.metricsClient?.histogram('llm.latency_ms', event.latencyMs, {
      feature: event.feature,
    });
  }
}
```

---

## Budget Enforcement

```typescript
// llm/budget.service.ts

export class BudgetService {
  // Check budget before making LLM call
  async checkBudget(feature: string, tenantId?: string): Promise<boolean> {
    const key = tenantId ? `budget:${tenantId}:${feature}` : `budget:global:${feature}`;
    
    // Get current spend for the billing period (e.g. current month)
    const spent = await this.cache.get<number>(key) ?? 0;
    const limit = await this.getBudgetLimit(feature, tenantId);
    
    return spent < limit;
  }

  // Called after each successful LLM call
  async recordSpend(feature: string, costUsd: number, tenantId?: string): Promise<void> {
    const key = tenantId ? `budget:${tenantId}:${feature}` : `budget:global:${feature}`;
    
    const ttl = this.secondsUntilEndOfMonth();
    await this.cache.incrbyfloat(key, costUsd);
    await this.cache.expire(key, ttl);

    // Alert if approaching limit (80% threshold)
    const spent = await this.cache.get<number>(key) ?? costUsd;
    const limit = await this.getBudgetLimit(feature, tenantId);
    if (spent / limit > 0.8) {
      await this.alertService.sendBudgetWarning({ feature, tenantId, spent, limit });
    }
  }

  private secondsUntilEndOfMonth(): number {
    const now = new Date();
    const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1);
    return Math.floor((endOfMonth.getTime() - now.getTime()) / 1000);
  }
}
```

---

## Response Caching (Reduce Costs)

```typescript
// Cache identical prompts to avoid redundant LLM calls
// Use SHA-256 hash of (model + prompt) as cache key

import { createHash } from 'crypto';

function cacheKey(model: string, prompt: string): string {
  return createHash('sha256').update(`${model}::${prompt}`).digest('hex');
}

async function completeWithCache(request: LlmRequest): Promise<LlmResponse> {
  const key = cacheKey(request.model ?? 'default', request.prompt);
  
  const cached = await cache.get<LlmResponse>(key);
  if (cached) {
    return { ...cached, usage: { ...cached.usage, costUsd: 0 } }; // no cost on cache hit
  }
  
  const response = await llmRouter.complete(request);
  
  // Cache for 1 hour — adjust TTL based on how dynamic the content is
  await cache.set(key, response, 3_600);
  return response;
}
```

---

## Reporting Queries

```sql
-- Monthly spend by feature
SELECT 
  feature,
  SUM(cost_usd) AS total_cost,
  SUM(total_tokens) AS total_tokens,
  COUNT(*) AS call_count,
  AVG(latency_ms) AS avg_latency_ms
FROM llm_usage_events
WHERE timestamp >= date_trunc('month', CURRENT_DATE)
GROUP BY feature
ORDER BY total_cost DESC;

-- Top cost drivers by model
SELECT model, provider, SUM(cost_usd) AS total_cost, COUNT(*) AS calls
FROM llm_usage_events
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY model, provider
ORDER BY total_cost DESC;

-- Error rate by provider
SELECT provider, 
  COUNT(*) FILTER (WHERE NOT success) AS errors,
  COUNT(*) AS total,
  ROUND(100.0 * COUNT(*) FILTER (WHERE NOT success) / COUNT(*), 2) AS error_rate
FROM llm_usage_events
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY provider;
```

---

## Best Practices

- [ ] Log **every** LLM call — both successes and failures
- [ ] Check budget **before** the call, not after (avoid surprise overage)
- [ ] Cache responses for deterministic prompts (reduces cost and latency)
- [ ] Track `latencyMs` — slow calls often indicate model overload, switch to fallback
- [ ] Set per-feature budget limits, not just global limits
- [ ] Alert at 80% budget — don't let features go dark with no warning
- [ ] Never log the prompt content if it contains PII (log feature name + token counts only)
