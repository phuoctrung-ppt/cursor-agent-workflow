# LLM Router Pattern — Generic Reference

A central router service is the single point through which all LLM calls flow. This enforces budget checks, provider abstraction, fallback handling, cost tracking, and usage logging — preventing these concerns from being duplicated across the codebase.

---

## Core Interface

```typescript
// llm/interfaces/llm-provider.interface.ts

export interface LlmRequest {
  prompt: string;
  systemPrompt?: string;
  model?: string;           // optional — router picks default if omitted
  temperature?: number;     // default: 0.7
  maxTokens?: number;       // default: 1024
  streaming?: boolean;
  metadata?: {
    feature: string;        // which feature is calling (for cost tracking)
    userId?: string;
    [key: string]: unknown;
  };
}

export interface LlmResponse {
  content: string;
  model: string;            // actual model used (may differ from requested)
  provider: string;         // 'openai' | 'anthropic' | 'gemini' | ...
  usage: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
    costUsd: number;        // calculated cost
  };
}

export interface LlmProvider {
  complete(request: LlmRequest): Promise<LlmResponse>;
  embed(text: string | string[]): Promise<number[][]>;
  readonly name: string;
  readonly supportedModels: string[];
}
```

---

## Router Service

```typescript
// llm/llm-router.service.ts

export class LlmRouterService {
  constructor(
    private readonly providers: Map<string, LlmProvider>,
    private readonly budgetService: BudgetService,
    private readonly usageLogger: UsageLogger,
    private readonly config: LlmConfig,
  ) {}

  async complete(request: LlmRequest): Promise<LlmResponse> {
    const feature = request.metadata?.feature ?? 'unknown';

    // 1. Pre-flight budget check
    const budgetOk = await this.budgetService.checkBudget(feature);
    if (!budgetOk) {
      throw new BudgetExceededError(`Budget exhausted for feature: ${feature}`);
    }

    // 2. Select primary provider and model
    const provider = this.selectProvider(request.model);
    const model = request.model ?? this.config.defaultModel;

    // 3. Execute with fallback on failure
    let response: LlmResponse;
    try {
      response = await provider.complete({ ...request, model });
    } catch (error) {
      const fallback = this.getFallbackProvider(provider.name);
      if (!fallback) throw error;
      response = await fallback.complete({ ...request, model: this.config.fallbackModel });
    }

    // 4. Log usage (async — don't block the response)
    this.usageLogger.log({
      feature,
      provider:          response.provider,
      model:             response.model,
      promptTokens:      response.usage.promptTokens,
      completionTokens:  response.usage.completionTokens,
      costUsd:           response.usage.costUsd,
      userId:            request.metadata?.userId,
      timestamp:         new Date(),
    }).catch(console.error); // never let logging failure break the response

    return response;
  }

  private selectProvider(model?: string): LlmProvider {
    if (model) {
      for (const p of this.providers.values()) {
        if (p.supportedModels.includes(model)) return p;
      }
    }
    return this.providers.get(this.config.defaultProvider)!;
  }

  private getFallbackProvider(excludeName: string): LlmProvider | null {
    for (const [name, p] of this.providers) {
      if (name !== excludeName) return p;
    }
    return null;
  }
}
```

---

## Provider Implementation Example

```typescript
// llm/providers/openai.provider.ts
import OpenAI from 'openai';

export class OpenAiProvider implements LlmProvider {
  readonly name = 'openai';
  readonly supportedModels = ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo'];

  private client: OpenAI;

  constructor(apiKey: string) {
    this.client = new OpenAI({ apiKey });
  }

  async complete(request: LlmRequest): Promise<LlmResponse> {
    const response = await this.client.chat.completions.create({
      model: request.model ?? 'gpt-4o-mini',
      messages: [
        ...(request.systemPrompt ? [{ role: 'system' as const, content: request.systemPrompt }] : []),
        { role: 'user', content: request.prompt },
      ],
      temperature: request.temperature ?? 0.7,
      max_tokens:  request.maxTokens ?? 1024,
    });

    const choice = response.choices[0];
    return {
      content:  choice.message.content ?? '',
      model:    response.model,
      provider: 'openai',
      usage: {
        promptTokens:     response.usage?.prompt_tokens ?? 0,
        completionTokens: response.usage?.completion_tokens ?? 0,
        totalTokens:      response.usage?.total_tokens ?? 0,
        costUsd:          calculateCost('openai', response.model, response.usage),
      },
    };
  }

  async embed(text: string | string[]): Promise<number[][]> {
    const inputs = Array.isArray(text) ? text : [text];
    const response = await this.client.embeddings.create({
      model: 'text-embedding-3-small',
      input: inputs,
    });
    return response.data.map(d => d.embedding);
  }
}
```

---

## Usage in Business Logic

```typescript
// feature/some.service.ts

// ✅ Correct — always go through router
constructor(private readonly llmRouter: LlmRouterService) {}

async summarize(text: string, userId: string): Promise<string> {
  const response = await this.llmRouter.complete({
    prompt: `Summarize the following:\n\n${text}`,
    systemPrompt: 'You are a concise summarizer. Return 3 bullet points.',
    metadata: { feature: 'summarize', userId },
  });
  return response.content;
}

// ❌ Never do this — direct provider call bypasses budget, tracking, fallback
constructor(private readonly openai: OpenAI) {}
async summarize(text: string) {
  const r = await this.openai.chat.completions.create({ ... });
}
```

---

## Retry With Backoff

```typescript
async function withRetry<T>(
  fn: () => Promise<T>,
  maxAttempts = 3,
  baseDelayMs = 500,
): Promise<T> {
  let lastError: Error;
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      if (attempt < maxAttempts) {
        const delay = baseDelayMs * 2 ** (attempt - 1); // 500ms, 1s, 2s
        await new Promise(r => setTimeout(r, delay));
      }
    }
  }
  throw lastError!;
}

// Usage in router
response = await withRetry(() => provider.complete(request));
```

---

## Testing the Router

```typescript
it('falls back to secondary provider on primary failure', async () => {
  const primaryProvider = { complete: jest.fn().mockRejectedValue(new Error('Rate limited')), name: 'openai' };
  const fallbackProvider = { complete: jest.fn().mockResolvedValue(mockResponse), name: 'anthropic' };

  const router = new LlmRouterService(
    new Map([['openai', primaryProvider], ['anthropic', fallbackProvider]]),
    mockBudgetService, mockLogger, config,
  );

  const result = await router.complete({ prompt: 'Hello', metadata: { feature: 'test' } });

  expect(primaryProvider.complete).toHaveBeenCalled();
  expect(fallbackProvider.complete).toHaveBeenCalled();
  expect(result).toEqual(mockResponse);
});
```
