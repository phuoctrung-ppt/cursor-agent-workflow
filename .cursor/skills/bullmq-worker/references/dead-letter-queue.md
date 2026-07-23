# Dead Letter Queue

Failed jobs after max retries → inspect via admin `DeadLetterController` (SuperAdmin).

Endpoints:
- `GET /dead-letter/:queueName` — list failed jobs
- `POST /dead-letter/:queueName/:jobId/retry` — manual retry

Log permanent failures with `failedReason` and `attemptsMade`.
