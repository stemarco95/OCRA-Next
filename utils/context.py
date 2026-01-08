class Context:
    """
    Standardized environment output.
    This is the only allowed output format for environment modules.
    """

    def __init__(
        self,
        state,
        reward: float = 0.0,
        terminated: bool = False,
        truncated: bool = False,
        info: dict or None = None,
    ):
        self.state = state
        self.reward = reward
        self.terminated = terminated
        self.truncated = truncated
        self.info = info or {}
