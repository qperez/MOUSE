"""Validation and selection of feedback profiles submitted by the LSP client."""

import math
from numbers import Real


LEVEL_NAMES = ("simple", "moderate", "high", "veryHigh")
PROFILE_NAMES = ("vibration", "thermal", "mouse", "custom")


def validate_feedback_profile(complexity, settings):
    """Validate the active profile and feedback settings for one complexity band."""
    if isinstance(complexity, bool) or not isinstance(complexity, int) or complexity < 0:
        raise ValueError("complexity must be a non-negative integer")
    if not isinstance(settings, dict):
        raise ValueError("feedbackSettings must be an object")

    active_profile = settings.get("activeProfile")
    if active_profile not in PROFILE_NAMES:
        raise ValueError(
            "feedbackSettings.activeProfile must be vibration, thermal, mouse, or custom"
        )
    level_name = settings.get("level")
    if level_name not in LEVEL_NAMES:
        raise ValueError(
            "feedbackSettings.level must be simple, moderate, high, or veryHigh"
        )
    expected_level = _level_for_complexity(complexity)
    if level_name != expected_level:
        raise ValueError(
            f"feedbackSettings.level must match complexity ({expected_level})"
        )

    feedback = {
        "active": True,
        "activeProfile": active_profile,
        "level": level_name,
        "thermal": _validate_thermal(settings.get("thermal")),
        "vibration": _validate_vibration(settings.get("vibration")),
        "mouseSpeed": _validate_mouse_speed(settings.get("mouseSpeed")),
    }
    return feedback


def _level_for_complexity(complexity):
    if complexity <= 5:
        return "simple"
    if complexity <= 10:
        return "moderate"
    if complexity <= 20:
        return "high"
    return "veryHigh"


def leave_feedback_profile():
    """Return a profile that stops hover feedback and restores neutral mouse speed."""
    disabled = {"enabled": False}
    return {
        "active": False,
        "activeProfile": None,
        "level": None,
        "thermal": {**disabled, "durationMs": 0, "pwm": 0},
        "vibration": {
            **disabled,
            "durationMs": 0,
            "pwm": 0,
            "pulseCount": 1,
            "pulseDelayMs": 0,
        },
        "mouseSpeed": {**disabled, "factor": 1.0},
    }


def _validate_thermal(value):
    path = "feedbackSettings.thermal"
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be an object")
    enabled = _boolean(value.get("enabled"), f"{path}.enabled")
    if not enabled:
        return {"enabled": False}
    return {
        "enabled": True,
        "durationMs": _integer(value.get("durationMs"), f"{path}.durationMs", 0),
        "pwm": _integer(value.get("pwm"), f"{path}.pwm", 0, 255),
    }


def _validate_vibration(value):
    path = "feedbackSettings.vibration"
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be an object")
    enabled = _boolean(value.get("enabled"), f"{path}.enabled")
    if not enabled:
        return {"enabled": False}
    return {
        "enabled": True,
        "durationMs": _integer(value.get("durationMs"), f"{path}.durationMs", 0),
        "pwm": _integer(value.get("pwm"), f"{path}.pwm", 0, 255),
        "pulseCount": _integer(value.get("pulseCount"), f"{path}.pulseCount", 1),
        "pulseDelayMs": _integer(value.get("pulseDelayMs"), f"{path}.pulseDelayMs", 0),
    }


def _validate_mouse_speed(value):
    path = "feedbackSettings.mouseSpeed"
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be an object")
    enabled = _boolean(value.get("enabled"), f"{path}.enabled")
    if not enabled:
        return {"enabled": False, "factor": 1.0}
    factor = value.get("factor")
    if isinstance(factor, bool) or not isinstance(factor, Real) or not math.isfinite(factor):
        raise ValueError(f"{path}.factor must be a finite number")
    if factor < 0.1:
        raise ValueError(f"{path}.factor must be >= 0.1")
    return {
        "enabled": True,
        "factor": float(factor),
    }


def _boolean(value, name):
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be a boolean")
    return value


def _integer(value, name, minimum, maximum=None):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if value < minimum or (maximum is not None and value > maximum):
        if maximum is None:
            raise ValueError(f"{name} must be >= {minimum}")
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value
