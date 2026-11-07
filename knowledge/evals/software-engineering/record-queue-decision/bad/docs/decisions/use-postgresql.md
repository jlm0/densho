# Use PostgreSQL for the job queue

## Context

Several workers write to the queue at the same time, and SQLite locks the database on each write.

## Decision

We move the job queue to PostgreSQL.
