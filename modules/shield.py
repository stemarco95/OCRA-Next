import copy
from core.base_module import BaseModule
from core.audit_logger import AuditLogger


class Shield(BaseModule):
    def __init__(self, module_id, inputs, outputs, cycle, is_env=False, config=None):
        super().__init__(module_id, inputs, outputs, cycle, is_env, config)
        self.max_delta = self.config.get("max_delta", 5.0)

    def step(self, inputs: dict) -> dict:
        """
        Safety shield that clips unsafe actions.
        """
        action_obs = inputs.get("raw_action")
        if action_obs is None:
            return {}

        new_obs = copy.copy(action_obs)

        action = action_obs.info.get("action")
        if not action or "delta" not in action:
            return {}

        delta = action["delta"]

        if abs(delta) > self.max_delta:
            safe_delta = max(-self.max_delta, min(delta, self.max_delta))

            AuditLogger.log_event(
                "shield_override",
                module=self.module_id,
                raw_delta=delta,
                safe_delta=safe_delta
            )

            new_obs.info = dict(new_obs.info or {})
            new_obs.info["action"]["delta"] = safe_delta

        return {
            "safe_action": new_obs
        }