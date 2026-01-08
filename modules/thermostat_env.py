import random
from typing import Dict

from core.base_module import BaseModule
from utils.context import Context


class ThermostatEnv(BaseModule):
    def __init__(
        self,
        module_id,
        inputs,
        outputs,
        cycle,
        is_env: bool = True,
        config=None
    ):
        super().__init__(module_id, inputs, outputs, cycle, is_env, config)

        self.initial_temp = self.config.get("initial_temp", 22.0)
        self.target = self.config.get("target_temp", 22.0)
        self.alpha = self.config.get("alpha", 0.5)
        self.drift_std = self.config.get("drift_std", 0.1)

        self.min_temp = self.config.get("min_temp", 5.0)
        self.max_temp = self.config.get("max_temp", 45.0)

        self.temp = self.initial_temp

    # ------------------------------------------------------------------
    # Episode lifecycle
    # ------------------------------------------------------------------

    def reset(self) -> Dict[str, Context]:
        """
        Reset environment state and return initial observation.
        """
        self.temp = self.initial_temp

        obs = Context(
            state=self.temp,
            reward=0.0,
            terminated=False,
            truncated=False,
            info={}
        )

        return {"true_temp": obs}

    # ------------------------------------------------------------------
    # Environment dynamics
    # ------------------------------------------------------------------

    def step(self, inputs: Dict[str, Context]) -> Dict[str, Context]:
        """
        Apply action and advance the environment by one step.
        """
        # Default action
        action = 0.0

        action_obs = inputs.get("safe_action")
        if action_obs is not None:
            # Convention: action is stored in obs.info["action"]
            action = float(action_obs.info.get("delta", 0.0))

        # Dynamics
        drift = random.gauss(0, self.drift_std)
        self.temp += self.alpha * action + drift
        self.temp = max(self.min_temp, min(self.temp, self.max_temp))

        # Observation
        obs = Context(
            state=self.temp,
            reward=-abs(self.temp - self.target),
            terminated=False,
            truncated=False,
            info={}
        )

        return {"true_temp": obs}