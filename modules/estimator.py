import copy
from typing import Dict

from core.base_module import BaseModule
from utils.context import Context


class Estimator(BaseModule):
    """
    State estimator using exponential smoothing.
    """

    def __init__(
        self,
        module_id,
        inputs,
        outputs,
        cycle,
        is_env: bool = False,
        config=None
    ):
        super().__init__(module_id, inputs, outputs, cycle, is_env, config)
        self.alpha = self.config.get("alpha", 0.5)
        self.estimate = None

    def reset(self) -> dict:
        """
        Reset internal estimator state at episode start.
        """
        self.estimate = None
        return {}

    def step(self, inputs: Dict[str, Context]) -> Dict[str, Context]:
        raw_obs = inputs.get("raw_temp")
        if raw_obs is None or raw_obs.state is None:
            return {}

        # Defensive copy
        new_obs = copy.copy(raw_obs)

        if self.estimate is None:
            self.estimate = raw_obs.state
        else:
            self.estimate = (
                self.alpha * raw_obs.state
                + (1 - self.alpha) * self.estimate
            )

        new_obs.state = self.estimate

        return {
            "state": new_obs
        }