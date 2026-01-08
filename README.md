Core Runtime Components in ORCA-Next

Runtime

The Runtime acts as the central execution manager of an ORCA-Next system. It is responsible for initializing, orchestrating, and supervising the overall execution.

Concretely, the runtime:
- loads the static architecture configuration (e.g., from an architecture.json file),
- instantiates all modules based on their declared type and identifier,
- initializes and starts the Mediator and Scheduler,
- controls the global execution loop (e.g., step-based execution or continuous thread-based execution),
- supervises execution state, logging, and controlled startup and shutdown.

The runtime defines the outer control boundary of the system and ensures that all components are executed exclusively through the framework, not via direct inter-module calls.


Scheduler

The Scheduler enforces the temporal execution semantics of the system. It determines when modules are executed and ensures compliance with declared timing constraints.

Its responsibilities include:
- triggering module execution according to their specified cycle or period (e.g., every 100 ms),
- delaying, skipping, or terminating executions if timing constraints or deadlines are violated,
- optionally enforcing priorities between modules (e.g., safety or shield modules taking precedence),
- reporting warnings or errors in case of timing violations or scheduling conflicts.

By separating scheduling from module logic, ORCA-Next prevents implicit timing assumptions and makes execution behavior explicit and analyzable.


Mediator

The Mediator provides the communication infrastructure of the execution graph. All data exchange between modules is routed exclusively through the mediator.

Specifically, the mediator:
- decouples producers and consumers of information,
- manages topic-based message routing (e.g., state, raw_action, safe_action),
- ensures reliable message delivery between modules,
- optionally supports buffering, prioritization, and message logging.

The mediator does not interpret or modify message contents. Its sole purpose is to make data flow explicit, observable, and framework-controlled.


Base Module

The Base Module is an abstract superclass from which all functional modules inherit. It defines the minimal interface required for integration into the ORCA-Next runtime.

It typically:
- specifies mandatory lifecycle and execution methods,
- provides standard fields such as module ID, input topics, output topics, and execution period,
- exposes module metadata required by the scheduler and mediator.

This abstraction ensures that all modules remain manageable, schedulable, and interchangeable within the framework.


Message Abstraction

The Message abstraction defines the standardized data exchange format used throughout the system.

Messages:
- are used uniformly by all modules for communication,
- contain metadata such as timestamp, sender ID, and topic, as well as a payload,
- can optionally be extended with uncertainty estimates, confidence values, or version information,
- enable system-wide logging, traceability, and record-and-replay,
- support OC-compliant coupling through small, well-defined interfaces.

By standardizing messages, ORCA-Next ensures transparent data flow and reproducible execution behavior.


                 +----------------------+
                 |       Runtime        |  ← initializes and controls execution
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 |      Scheduler       |  ← enforces timing and priorities
                 +----------+-----------+
                            |
                            v
              +-------------+-------------+
              |                           |
        +-----------+             +--------------+
        |  Modules  | <---------> |   Mediator   |  ← routes all messages
        +-----------+             +--------------+
              ^
              |
       +----------------+
       |  Base Module   |  ← common module interface
       +----------------+
