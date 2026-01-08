from core.audit_logger import AuditLogger
from core.messages import Message
from typing import Callable, Dict


class OCMonitor:
    """
    Core-level OC compliance monitor.
    Passively observes message traffic and checks for OC property violations.
    """

    def __init__(self, mediator):
        self.mediator = mediator
        self.checks: list[Callable[[Dict[str, Message]], bool or str]] = []

    def register_check(self, check_fn):
        """
        Register a new OC-check function.

        Args:
            check_fn (Callable): Function with signature (dict[str, Message]) -> bool | str
                                 Returns True if check passes, string message if it fails.
        """
        self.checks.append(check_fn)

    def step(self):
        """
        Pull current messages from the mediator and evaluate all checks.
        """
        self.observe_all(self.mediator.latest_messages)

    def observe_all(self, messages: Dict[str, Message]):
        """
        Run all registered checks on the current message set.
        """
        for check in self.checks:
            result = check(messages)
            if result:  # True or str = violation
                AuditLogger.log_event("oc_violation", detail=result)