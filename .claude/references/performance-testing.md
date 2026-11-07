<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Performance testing

## Directives

No directive is in force at this node.

## Definition

Testing that checks the performance of a system or a component under different volumes of load. The ISTQB Performance Testing syllabus calls it an umbrella term for each kind of test that focuses on responsiveness, and follows ISO 25010 with 3 parts: time behavior, resource utilization, and capacity. SWEBOK v4 lists performance testing as non-functional testing: it checks that the software meets its specified performance requirements, and it measures characteristics such as capacity and response time.

## Notes

The ISTQB syllabus names 7 types of performance test:

- A load test checks the system under increasing levels of realistic load.
- A stress test checks the system at its peak load or beyond it, or with fewer resources.
- A scalability test checks whether the system can grow beyond its current requirements.
- A spike test checks the response to a sudden burst of load, and the return to a steady state.
- An endurance test checks the stability of the system over a long period, and finds leaks of memory, connections, or threads.
- A concurrency test checks what happens when specific actions occur at the same time.
- A capacity test finds how many users or transactions the system supports within its objectives.

An operational profile describes how 1 kind of user or system uses the system under test. A load profile combines the operational profiles with a number of virtual users and a distribution over time, such as a ramp-up, a step, or a daily cycle.

The syllabus names 4 common failure modes. The response is slow at each load level, from causes such as a bad database design. The response is slow under moderate or heavy load, from a saturated resource. The response degrades over time, from a memory leak or data growth. The error handling degrades at high load, from small resource pools, small queues, or short timeouts.

The syllabus warns about 2 traps of recorded scripts. Virtual users that share 1 set of data can hit a cache and give results better than production. They can also wait on the same locks and give results worse than production. Performance is a non-linear function of the environment, so a projection from a small environment to production is less reliable as the gap grows.

The average response time can hide outliers, so the 90th percentile is often used as the goal. A failed transaction takes less time than a successful one, so a failure can inflate the throughput.
