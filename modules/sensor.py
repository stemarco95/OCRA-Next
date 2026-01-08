import copy
import random
from typing import Dict

from core.base_module import BaseModule
from utils.context import Context


class Sensor(BaseModule):
    """
    Sensor transforms true environment state into a noisy observation.
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
        self.noise = self.config.get("noise", 0.1)

    def step(self, inputs: Dict[str, Context]) -> Dict[str, Context]:
        true_obs = inputs.get("true_temp")
        if true_obs is None:
            return {}

        if true_obs.state is None:
            return {}

        # Defensive copy
        new_obs = copy.copy(true_obs)

        noisy_temp = true_obs.state + random.uniform(-self.noise, self.noise)
        new_obs.state = noisy_temp

        return {
            "raw_temp": new_obs
        }