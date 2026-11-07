# 3. Use PostgreSQL for the job queue

## Status

Accepted. Supersedes 2.

## Context

Several workers now write to the queue at the same time. SQLite locks the whole database on each write, so the workers wait for each other.

## Decision

We move the job queue from SQLite to PostgreSQL.

## Consequences

- Positive: the workers write at the same time with row locks.
- Negative: the team runs and backs up a database server.
- Neutral: the queue schema stays the same.
