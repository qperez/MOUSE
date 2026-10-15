"""Validation and selection of feedback profiles submitted by the LSP client."""

import math
from numbers import Real


LEVEL_NAMES = ("simple", "moderate", "high", "veryHigh")


def select_feedback_profile(complexity, settings):
    """Validate settings and select the profile matching a complexity value."""
    if isinstance(complexity, bool) or not isinstance(complexity, int) or complexity < 0:
        raise ValueError("complexity must be a non-negative integer")

    levels = _validate_settings(settings)
    if complexity <= 5:
        level_name = "simple"
    elif complexity <= 10:
        level_name = "moderate"
    elif complexity <= 20:
        level_name = "high"
    else:
        level_name = "veryHigh"

    return {"active": True, "level": level_name, **levels[level_name]}


def leave_feedback_profile():
    """Return a profile that stops hover feedback and restores neutral mouse speed."""
    disabled = {"enabled": False}
    return {
        "active": False,
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


def _validate_settings(settings):
    if not isinstance(settings, dict):
        raise ValueError("feedbackSettings must be an object")
    levels = settings.get("levels")
    if not isinstance(levels, dict):
        raise ValueError("feedbackSettings.levels must be an object")

    validated = {}
    for level_name in LEVEL_NAMES:
        profile = levels.get(level_name)
        if not isinstance(profile, dict):
            raise ValueError(f"feedbackSettings.levels.{level_name} must be an object")
        validated[level_name] = {
            "thermal": _validate_thermal(profile.get("thermal"), level_name),
            "vibration": _validate_vibration(profile.get("vibration"), level_name),
            "mouseSpeed": _validate_mouse_speed(profile.get("mouseSpeed"), level_name),
        }
    return validated


def _validate_thermal(value, level_name):
    path = f"feedbackSettings.levels.{level_name}.thermal"
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be an object")
    return {
        "enabled": _boolean(value.get("enabled"), f"{path}.enabled"),
        "durationMs": _integer(value.get("durationMs"), f"{path}.durationMs", 0),
        "pwm": _integer(value.get("pwm"), f"{path}.pwm", 0, 255),
    }


def _validate_vibration(value, level_name):
    path = f"feedbackSettings.levels.{level_name}.vibration"
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be an object")
    return {
        "enabled": _boolean(value.get("enabled"), f"{path}.enabled"),
        "durationMs": _integer(value.get("durationMs"), f"{path}.durationMs", 0),
        "pwm": _integer(value.get("pwm"), f"{path}.pwm", 0, 255),
        "pulseCount": _integer(value.get("pulseCount"), f"{path}.pulseCount", 1),
        "pulseDelayMs": _integer(value.get("pulseDelayMs"), f"{path}.pulseDelayMs", 0),
    }


def _validate_mouse_speed(value, level_name):
    path = f"feedbackSettings.levels.{level_name}.mouseSpeed"
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be an object")
    factor = value.get("factor")
    if isinstance(factor, bool) or not isinstance(factor, Real) or not math.isfinite(factor):
        raise ValueError(f"{path}.factor must be a finite number")
    if factor < 0.1:
        raise ValueError(f"{path}.factor must be >= 0.1")
    return {
        "enabled": _boolean(value.get("enabled"), f"{path}.enabled"),
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

