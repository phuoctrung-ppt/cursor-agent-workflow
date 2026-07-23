---
name: bullmq-worker
description: Implements BullMQ processors, queue configuration, dead letter queues, and idempotent job dispatch for apps/worker and apps/api queue producers.
---

# BullMQ Worker

## Job Naming

kebab-case: `cv-parse`, `ai-match`, `interview-analysis`, `billing-metering`

## Processor Pattern

`@Processor('queue-name', { concurrency: N })` extends `WorkerHost`

## Idempotency

```typescript
await queue.add('parse', data, { jobId: `cv-parse-${cvId}` });
```

## Queue Defaults

- `cv-parse`: 3 attempts, exponential backoff 2s
- `ai-match`: 2 attempts, fixed 5s
- `billing-metering`: 5 attempts

## References

- [processor-pattern.md](references/processor-pattern.md)
- [queue-configuration.md](references/queue-configuration.md)
- [dead-letter-queue.md](references/dead-letter-queue.md)

Also see nestjs-skills: `micro-use-queues.md`
