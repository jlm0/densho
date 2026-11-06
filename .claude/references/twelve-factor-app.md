<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Twelve-factor app

## Directives

No directive is in force at this node.

## Definition

A method by Adam Wiggins for building software-as-a-service apps. It names twelve factors: one codebase, explicit dependencies, config in the environment, backing services as attached resources, separate build and run stages, stateless processes, port binding, concurrency through processes, disposability, parity between development and production, logs as event streams, and admin tasks as one-off processes.

## Notes

The config test of the method: the codebase could become public at any moment, and no credential would leak. A clean stop differs by process. A web process stops listening, finishes its current requests, and exits. A worker returns its current job to the queue.
