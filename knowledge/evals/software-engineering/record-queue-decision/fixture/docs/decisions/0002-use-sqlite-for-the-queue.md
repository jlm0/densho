# 2. Use SQLite for the job queue

## Context

One worker reads the queue, and the queue holds a few hundred jobs a day.

## Decision

We keep the job queue in a SQLite file next to the worker.
