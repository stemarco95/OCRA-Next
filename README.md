# ORCA-Next
ORCA-Next (Organic Runtime & Control Architecture) is a graph-based runtime framework for Organic Computing systems.
It provides a binding execution semantics for observer/controller-based architectures and enables controlled, reproducible runtime evolution of adaptive systems.

ORCA-Next does not introduce new learning or control algorithms.
Instead, it defines a minimal and explicit runtime core that makes Organic-Computing concepts executable, comparable, and auditable at runtime.

ORCA-Next is a runtime framework for adaptive systems that:
- executes systems as a statically configured, data-driven execution graph
- separates functional logic (modules) from runtime control
- supports safety-critical intervention paths
- enables controlled and observable evolution of policies and models

The framework operationalizes classical Organic-Computing concepts such as:
- Observer / Controller structures
- Multi-time-scale adaptation (e.g. MLOC-like roles)
- Self-X properties (self-optimization, self-protection, etc.)

without enforcing rigid layer pipelines.

Core ideas
- Modules encapsulate domain logic (observation, control, safety, learning)
- Messages define explicit and typed data flow
- Execution is controlled centrally by the runtime, not by modules themselves
- Safety and evolution are explicit architectural elements, not side effects

ORCA-Next is designed to be:
- reproducible
- inspectable
- extensible
- suitable for experimentation and research prototypes

Entschuldige, da habe ich dich missverstanden! Hier ist dein Text, sauber und einheitlich als Markdown formatiert, sodass du ihn direkt kopieren kannst:

---

# How to Run ORCA-Next

This section describes how to start ORCA-Next and execute a configured system.

### Requirements

* **Python 3.9** or newer
* No external dependencies (standard library only)

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/stemarco95/ORCA-Next.git
cd ORCA-Next

```

### Step 2: Configure the Execution Graph

The system structure is defined in `architecture.json`. This file specifies:

* Which modules are instantiated
* How modules are connected via message topics
* Timing and execution parameters

**Example (simplified):**

```json
{
  "modules": [
    {
      "id": "env",
      "type": "Environment",
      "period": 0.1
    },
    {
      "id": "controller",
      "type": "Controller",
      "period": 0.1
    }
  ]
}

```

> **Note:** The execution graph is statically configured before startup and remains structurally stable during runtime.

---

### Step 3: Start the Runtime

Run the main entry point:

```bash
python main.py

```

**The runtime will:**

1. Load the architecture configuration
2. Instantiate all modules
3. Initialize the mediator and scheduler
4. Start the execution loop

---

### Execution Modes

ORCA-Next supports multiple execution modes:

* **Step-based execution:** Deterministic execution for debugging and experiments.
* **Time-based execution:** Continuous execution aligned with real time.
* **Threaded execution (optional):** Parallel execution of independent modules without changing semantics.

*The execution mode is selected in the runtime configuration.*

---

### Stopping the System

The runtime terminates automatically when an episode ends or when a defined termination condition is reached. Execution can also be stopped manually (e.g., via keyboard interrupt `Ctrl+C`).

---

Soll ich noch eine Tabelle für die Konfigurationsparameter oder einen speziellen "Troubleshooting"-Block hinzufügen?

## Core Runtime Components in ORCA-Next

### Runtime

The Runtime acts as the central execution manager of an ORCA-Next system. It is responsible for initializing, orchestrating, and supervising the overall execution.

Concretely, the runtime:
- loads the static architecture configuration (e.g., from an architecture.json file),
- instantiates all modules based on their declared type and identifier,
- initializes and starts the Mediator and Scheduler,
- controls the global execution loop (e.g., step-based execution or continuous thread-based execution),
- supervises execution state, logging, and controlled startup and shutdown.

The runtime defines the outer control boundary of the system and ensures that all components are executed exclusively through the framework, not via direct inter-module calls.


### Scheduler

The Scheduler enforces the temporal execution semantics of the system. It determines when modules are executed and ensures compliance with declared timing constraints.

Its responsibilities include:
- triggering module execution according to their specified cycle or period (e.g., every 100 ms),
- delaying, skipping, or terminating executions if timing constraints or deadlines are violated,
- optionally enforcing priorities between modules (e.g., safety or shield modules taking precedence),
- reporting warnings or errors in case of timing violations or scheduling conflicts.

By separating scheduling from module logic, ORCA-Next prevents implicit timing assumptions and makes execution behavior explicit and analyzable.


### Mediator

The Mediator provides the communication infrastructure of the execution graph. All data exchange between modules is routed exclusively through the mediator.

Specifically, the mediator:
- decouples producers and consumers of information,
- manages topic-based message routing (e.g., state, raw_action, safe_action),
- ensures reliable message delivery between modules,
- optionally supports buffering, prioritization, and message logging.

The mediator does not interpret or modify message contents. Its sole purpose is to make data flow explicit, observable, and framework-controlled.


### Base Module

The Base Module is an abstract superclass from which all functional modules inherit. It defines the minimal interface required for integration into the ORCA-Next runtime.

It typically:
- specifies mandatory lifecycle and execution methods,
- provides standard fields such as module ID, input topics, output topics, and execution period,
- exposes module metadata required by the scheduler and mediator.

This abstraction ensures that all modules remain manageable, schedulable, and interchangeable within the framework.


### Message Abstraction

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
