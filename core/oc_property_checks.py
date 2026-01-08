from core.messages import Message
from typing import Dict, Union, List

# Global memory for optimization and healing checks
_reward_history: List[float] = []
_last_was_override: bool = False


def check_self_protection(messages: Dict[str, Message]) -> Union[bool, str]:
    """
    Rule: Check if Safety Shield overrides any unsafe actions.
    """
    raw = messages.get("raw_action")
    safe = messages.get("safe_action")

    if not raw or not safe:
        return "Missing action messages"

    if raw.payload != safe.payload:
        return True  # Protection active
    return False  # No override


def check_self_healing(messages: Dict[str, Message]) -> Union[bool, str]:
    """
    Rule: Detect if system recovers after unsafe override.
    """
    global _last_was_override
    raw = messages.get("raw_action")
    safe = messages.get("safe_action")

    if not raw or not safe:
        return "Missing action messages"

    current_override = raw.payload != safe.payload

    if _last_was_override and not current_override:
        _last_was_override = False
        return True  # System healed (back to safe decisions)
    _last_was_override = current_override
    return False


def check_self_optimization(messages: Dict[str, Message]) -> Union[bool, str]:
    """
    Rule: Check if average reward increases over time.
    """
    global _reward_history
    reward_msg = messages.get("reward")
    if not reward_msg or not isinstance(reward_msg.payload, (float, int)):
        return "Missing or invalid reward message"

    _reward_history.append(reward_msg.payload)

    window = 5
    if len(_reward_history) < 2 * window:
        return "Insufficient data"

    first_half = _reward_history[-2 * window:-window]
    second_half = _reward_history[-window:]

    if sum(second_half) > sum(first_half):
        return True  # Performance improved
    return False


def check_self_configuration(messages: Dict[str, Message]) -> Union[bool, str]:
    """
    Rule: Check if model or policy module has changed.
    """
    update = messages.get("module_update")
    if update:
        return True
    return False


# Registry of all OC property checks
OC_RULES = {
    # "self_protection": check_self_protection,
    # "self_healing": check_self_healing,
    # "self_optimization": check_self_optimization,
    # "self_configuration": check_self_configuration,
}