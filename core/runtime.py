import time
import json

from typing import List
from pathlib import Path

from core.messages import Message
from core.mediator import Mediator
from core.scheduler import Scheduler
from core.oc_monitor import OCMonitor
from core.base_module import BaseModule
from core.audit_logger import AuditLogger
from core.oc_property_checks import OC_RULES
from utils.module_loader import auto_load_modules
from utils.context import Context


class Runtime:
    """
    Runtime is the main orchestrator of the system.

    Responsibilities:
    - load and initialize modules
    - manage episode lifecycle (reset / termination)
    - select execution mode
    - delegate execution to Scheduler
    - run OC monitoring

    Execution modes:
    - step-based
    - time-loop-based
    - time-thread-based
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(
        self,
        modules: List[BaseModule],
        mode: str,
        max_steps: int or None,
        max_time: float or None,
    ):
        self.modules = modules
        self.mode = mode
        self.max_steps = max_steps
        self.max_time = max_time

        self.mediator = Mediator()
        self.oc_monitor = OCMonitor(self.mediator)
        self.scheduler = Scheduler(
            modules=modules,
            mediator=self.mediator,
            mode=mode,
        )

        self._register_inputs()
        self._register_oc_checks()

    # ------------------------------------------------------------------
    # Config loading
    # ------------------------------------------------------------------

    @classmethod
    def from_config(cls, json_path: str):
        module_registry = auto_load_modules()

        with open(Path(json_path), "r") as f:
            config = json.load(f)

        if not isinstance(config, dict) or "modules" not in config:
            raise ValueError("Invalid config format: expected dict with 'modules' key")

        mode = config.get("mode")
        max_steps = config.get("max_steps")
        max_time = config.get("max_time")

        if mode not in {"step-based", "time-loop-based", "time-thread-based"}:
            raise ValueError(f"Unsupported mode: {mode}")

        if mode == "step-based" and max_steps is None:
            raise ValueError("Missing 'max_steps' for step-based mode")

        if mode in {"time-loop-based", "time-thread-based"} and max_time is None:
            raise ValueError("Missing 'max_time' for time-based mode")

        modules = []
        for entry in config["modules"]:
            module_type = entry["type"]
            module_cls = module_registry.get(module_type)

            if not module_cls:
                raise ValueError(f"Unknown module type: {module_type}")

            cycle = entry.get("cycle")
            if not isinstance(cycle, (int, float)) or cycle <= 0:
                raise ValueError(
                    f"Invalid or missing 'cycle' for module '{entry.get('id', '?')}'"
                )

            module = module_cls(
                module_id=entry["id"],
                inputs=entry.get("inputs", []),
                outputs=entry.get("outputs", []),
                cycle=cycle,
                is_env=entry.get("is_env", False),
                config=entry.get("config", {}),
            )
            modules.append(module)

        if not modules:
            raise ValueError("No modules defined in configuration")

        return cls(
            modules=modules,
            mode=mode,
            max_steps=max_steps,
            max_time=max_time,
        )

    # ------------------------------------------------------------------
    # Wiring
    # ------------------------------------------------------------------

    def _register_inputs(self):
        """
        Subscribe all module inputs at the mediator.
        """
        for module in self.modules:
            for topic in module.inputs:
                self.mediator.subscribe(topic, module.module_id)

    def _register_oc_checks(self):
        for check_fn in OC_RULES.values():
            self.oc_monitor.register_check(check_fn)

    def _get_env_modules(self) -> list[BaseModule]:
        return [m for m in self.modules if getattr(m, "is_env", False)]

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self):
        """
        Entry point of the runtime.
        """
        AuditLogger.log_event("runtime_started", mode=self.mode)

        self._reset_episode()

        try:
            if self.mode == "step-based":
                self._run_step_based()

            elif self.mode in {"time-loop-based", "time-thread-based"}:
                self._run_time_based()

            else:
                raise ValueError(f"Unsupported execution mode: {self.mode}")

        finally:
            AuditLogger.log_event("runtime_stopped")
            if self.scheduler.executor:
                self.scheduler.executor.shutdown(wait=False)

    # ------------------------------------------------------------------
    # Execution modes
    # ------------------------------------------------------------------

    def _run_step_based(self):
        for step in range(self.max_steps):
            self.scheduler.run_step(step)
            self.oc_monitor.step()

            if self._episode_done():
                self._reset_episode()

    def _run_time_based(self):
        """
        Time-based execution loop.

        - max_time: seconds
        - module.cycle: seconds
        - min_cycle: seconds
        """

        start_time = time.time()

        while time.time() - start_time < self.max_time:
            cycle_start = time.time()

            self.scheduler.run_time_based()

            if self._episode_done():
                self._reset_episode()

            elapsed = time.time() - cycle_start
            sleep_time = self.scheduler.min_cycle - elapsed

            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                AuditLogger.log_event(
                    "interval_overrun",
                    overrun_s=round(-sleep_time, 4),
                )

    # ------------------------------------------------------------------
    # Episode handling
    # ------------------------------------------------------------------

    def _reset_episode(self):
        """
        Reset all environment modules and publish their initial messages.
        Env.reset() returns dict[str, Context] (topic -> Context).
        """
        AuditLogger.log_event("episode_reset")

        # Clear mediator state but keep subscriptions
        self.mediator.latest_messages.clear()

        for env in self._get_env_modules():
            outputs = env.reset() or {}

            if not isinstance(outputs, dict):
                raise TypeError(
                    f"Env '{env.module_id}' reset() must return dict[str, Context], got {type(outputs)}"
                )

            for topic, ctx in outputs.items():
                msg = Message(topic=topic, payload=ctx, sender=env.module_id)
                self.mediator.publish(msg)

    def _episode_done(self) -> bool:
        """
        An episode is done if an environment emits
        terminated=True or truncated=True.
        """
        env_ids = {m.module_id for m in self._get_env_modules()}

        for msg in self.mediator.latest_messages.values():
            if not isinstance(msg, Message):
                continue

            if msg.sender not in env_ids:
                continue

            obs = msg.payload
            if isinstance(obs, Context):
                if obs.terminated or obs.truncated:
                    return True

        return False