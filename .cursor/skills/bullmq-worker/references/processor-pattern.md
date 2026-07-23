# Processor Pattern

```typescript
@Processor('cv-parse', { concurrency: 5 })
export class CvParseProcessor extends WorkerHost {
  async process(job: Job<CvParsePayload>): Promise<void> {
    // download → parse → AI enhance → embed → save
    // throw to trigger retry; @OnWorkerEvent('failed') for DLQ logging
  }
}
```

Log: `{ jobId, cvId, tenantId, attempt }` via Winston.
