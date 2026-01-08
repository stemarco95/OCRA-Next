import random
import copy
from core.base_module import BaseModule


class Controller(BaseModule):
    def __init__(self, module_id, inputs, outputs, cycle, is_env=False, config=None):
        super().__init__(module_id, inputs, outputs, cycle, is_env, config)

        self.low = self.config.get("low", 20.0)
        self.high = self.config.get("high", 25.0)
        self.normal_delta = self.config.get("normal_delta", 1.5)
        self.spike_delta = self.config.get("spike_delta", 10.0)
        self.spike_prob = self.config.get("spike_prob", 0.1)

    def step(self, inputs: dict) -> dict:
        """
        Controller computes an action based on the estimated state.
        """
        state_obs = inputs.get("state")
        if state_obs is None:
            return {}

        new_obs = copy.copy(state_obs)

        temp = state_obs.state
        if temp is None:
            return {}

        if temp < self.low:
            delta = self.normal_delta
        elif temp > self.high:
            delta = -self.normal_delta
        else:
            delta = 0.0

        # Inject unsafe action with small probability
        if random.random() < self.spike_prob:
            delta = self.spike_delta if delta >= 0 else -self.spike_delta

        # Action is written into info
        new_obs.info = dict(new_obs.info or {})
        new_obs.info["action"] = {"delta": delta}

        return {
            "raw_action": new_obs
        }