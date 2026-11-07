---
id: performance-testing
kind: densho:Concept
title: Performance testing
status: proposed
origin: template
knowledge_type: domain
sources:
  - https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf
  - https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=124
broader:
  - software-testing
---

## Definition

Testing that checks the performance of a system or a component under different volumes of load. The ISTQB Performance Testing syllabus calls it an umbrella term for each kind of test that focuses on responsiveness, and follows ISO 25010 with 3 parts: time behavior, resource utilization, and capacity. SWEBOK v4 lists performance testing as non-functional testing: it checks that the software meets its specified performance requirements, and it measures characteristics such as capacity and response time.

## Directives

- Define the objectives of each performance test with its stakeholders, as user-based objectives or technical objectives. ^performance-test-objectives
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=33
- Before a performance test, define the measurements and the metrics that show whether the test meets its objectives. ^metrics-before-performance-tests
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=17
- Define an obtainable set of metrics that supports the objectives of the performance test. ^limit-performance-metrics
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=19
- Choose the type of each performance test from its objective: load, stress, scalability, spike, endurance, concurrency, or capacity. ^choose-performance-test-type
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=12
  - sources: https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf#page=124
- If users interact with the system, define each operational profile from their roles, tasks, and numbers in each period. ^operational-profiles
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=40
- Keep each operational profile broad until a test objective requires more detail. ^broad-operational-profiles
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=41
- Review each operational profile with the stakeholders before you build a load profile from it. ^review-operational-profiles
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=41
- Build each load profile from the test objective, the operational profiles, and the distribution of the load over time. ^load-profiles
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=42
- Review the requirements, the data schemas, the architecture, and the critical code for performance risks. ^static-performance-reviews
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=13
- Start dynamic performance tests in the first iterations, not in the final iterations. ^performance-tests-early
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=14
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=13
- Put a timer around each business transaction in a performance test script. ^time-each-transaction
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=46
- In each performance test script, check the content of each response, not only its status code. ^check-performance-responses
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=46
- Give each virtual user a different set of test data, not the recorded data of `1` user. ^test-data-per-virtual-user
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=47
- Set the think times of each script to match the throughput of its operational profile. ^think-times-from-profiles
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=47
- Test each performance test script with the full range of its input data. ^test-performance-scripts
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=46
- Prefer a performance test environment that matches production in its data, its hardware, and its software. ^production-like-environment
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=48
- If the test environment differs from production, find each difference and its effect on the projection of the results. ^record-environment-differences
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=48
- Before a performance test, validate the environment and the monitoring with a controlled set of tests. ^validate-the-test-setup
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=49
- Monitor each load generator during the test. ^monitor-load-generators
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=49
- If a performance test changes the system state, restore the original state before the next run. ^restore-state-before-repeat
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=50
- Set the clocks of each test tool and each monitoring tool from `1` time source. ^time-source-for-tools
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=51
- Measure the performance in the steady state after the ramp-up, unless the test targets a transient state. ^measure-in-steady-state
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=50
- When you test a transient state, such as a spike, do not monitor only the averages. ^transient-states-without-averages
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=50
- Require repeated runs of a performance test on an unchanged system to give results within a stated tolerance. ^reproducible-performance-results
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=11
- Set each response time goal at a percentile, such as the `90th`, not at the average. ^percentile-response-goals
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=52
- Do not require `100%` of the transactions to meet a performance objective. ^no-full-compliance-goal
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=52
- If a baseline test exists, compare the results of each later performance test with its results. ^compare-with-a-baseline
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=53
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=17
- Before you read the response times, check that each virtual user finished the tasks of its profile. ^virtual-users-first
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=52
- Find the root cause of each failed transaction before you use the throughput results. ^failed-transactions-first
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=52
- If a test objective covers degradation over time, such as from a memory leak, run an endurance test. ^endurance-for-degradation
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=12
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=16
- Test the error handling of the system at its load limits and above them. ^error-handling-under-load
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=16
- Record the start, the duration, the scripts, the data, the configuration, and the defects of each test run. ^log-each-performance-run
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=54
- Report the results of each performance test against the objectives in its test plan. ^report-against-objectives
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=53
- After a performance fix, repeat the performance test to confirm the fix. ^confirm-performance-fixes
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=53
- Write the performance criteria of each user story with a performance risk into its acceptance criteria. ^performance-in-acceptance-criteria
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=31
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=29
- If a subset of the performance tests runs at build level, run that subset in continuous integration. ^performance-subset-in-ci
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=30
- In continuous integration, make each performance test raise an alert when its results leave the expected range. ^performance-alerts-in-ci
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=51
- After each delivery, monitor the performance of the system in production. ^monitor-performance-after-delivery
  - scope: subtree
  - basis: standard
  - status: proposed
  - origin: template
  - sources: https://www.istqb.org/wp-content/uploads/2024/11/ISTQB-CT-PT_Syllabus_v1.0_2018.pdf#page=31

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
