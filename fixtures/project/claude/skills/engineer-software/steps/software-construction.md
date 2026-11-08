<!-- Generated from the knowledge graph. Do not edit. Change the node file. -->
# Software construction

This file is step 5 of 8 of the skill `engineer-software`.

## Directives

From [Twelve-factor app](../../../references/twelve-factor-app.md):

- Keep each config value that differs between deploys out of the source code. ^config-out-of-code
- Declare each dependency of an app in a dependency manifest. ^declare-each-dependency
- Stop each process cleanly when it receives `SIGTERM`. ^graceful-shutdown
- Write the logs of each process to `stdout` as an unbuffered stream. ^logs-to-stdout
- Do not call a system tool that the app does not declare as a dependency. ^no-implicit-system-tool
- Use the same type and version of each backing service in development and in production. ^same-backing-services
- Store each persistent state in a backing service, not in the memory or the disk of a process. ^stateless-processes

## Required reads

Read each file in this list, and follow the directives that its line names.

- Read [Accessibility](../../../references/accessibility.md), and follow each directive from Accessibility.
- Read [Responsive design](../../../references/responsive-design.md), and follow each directive from Responsive design.

## Inputs

- The interface contracts and the UI contracts of the change
- The automated tests of the change

The output of each node in this list is an input of this step:

- [Software testing](software-testing.md)

## Procedure

The procedure of this step is missing.

## Output

The code that passes the tests, in each lane that the change needs: infrastructure, backend, frontend, and native.

The output of this step is an input of each node in this list:

- [Software configuration management](software-configuration-management.md)

## Exit gate

Check the code against each directive of this step and of the skill, and report each one that it misses.

## Next step

Read [Software configuration management](software-configuration-management.md).

## References

- You build a service, its logic, or its data store. Read [Backend engineering](../../../references/backend-engineering.md).
- You build the web client of a product. Read [Frontend engineering](../../../references/frontend-engineering.md).
- You define where a service runs or how it deploys. Read [Infrastructure engineering](../../../references/infrastructure-engineering.md).
- You build a native mobile app. Read [Native engineering](../../../references/native-engineering.md).
