# Queue Configuration

```typescript
BullModule.registerQueue({
  name: 'cv-parse',
  defaultJobOptions: {
    attempts: 3,
    backoff: { type: 'exponential', delay: 2000 },
    removeOnComplete: { count: 100 },
    removeOnFail: { count: 50 },
  },
});
```

Register in feature module; inject `@InjectQueue('cv-parse')` in service.
