import unittest

from mouse_server_serial_hub.mouse.shared.feedback_profiles import (
    leave_feedback_profile,
    validate_feedback_profile,
)
from mouse_server_serial_hub.mouse.shared.shared_cyclomatic_complexity_object import (
    SharedCyclomaticComplexityObject,
)


def make_settings():
    return {
        "activeProfile": "custom",
        "level": "moderate",
        "thermal": {"enabled": True, "durationMs": 900, "pwm": 75},
        "vibration": {"enabled": False},
        "mouseSpeed": {"enabled": True, "factor": 0.8},
    }


class FeedbackProfilesTest(unittest.TestCase):
    def test_selected_profile_preserves_only_current_band_parameters(self):
        settings = make_settings()
        profile = validate_feedback_profile(8, settings)

        self.assertEqual("custom", profile["activeProfile"])
        self.assertEqual("moderate", profile["level"])
        self.assertTrue(profile["thermal"]["enabled"])
        self.assertEqual(900, profile["thermal"]["durationMs"])
        self.assertFalse(profile["vibration"]["enabled"])
        self.assertNotIn("pwm", profile["vibration"])
        self.assertTrue(profile["mouseSpeed"]["enabled"])
        self.assertEqual(0.8, profile["mouseSpeed"]["factor"])

    def test_missing_settings_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "feedbackSettings"):
            validate_feedback_profile(6, None)

    def test_full_profiles_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "activeProfile"):
            validate_feedback_profile(8, {"levels": make_settings()})

    def test_invalid_profile_or_level_is_rejected(self):
        settings = make_settings()
        settings["activeProfile"] = "unknown"
        with self.assertRaisesRegex(ValueError, "activeProfile"):
            validate_feedback_profile(8, settings)

        settings = make_settings()
        settings["level"] = "unknown"
        with self.assertRaisesRegex(ValueError, "level"):
            validate_feedback_profile(8, settings)

    def test_level_must_match_complexity(self):
        with self.assertRaisesRegex(ValueError, "match complexity"):
            validate_feedback_profile(11, make_settings())
        with self.assertRaisesRegex(ValueError, "complexity"):
            validate_feedback_profile(True, make_settings())

    def test_leave_disables_feedback_and_restores_neutral_speed(self):
        profile = leave_feedback_profile()

        self.assertFalse(profile["active"])
        self.assertFalse(profile["mouseSpeed"]["enabled"])
        self.assertEqual(1.0, profile["mouseSpeed"]["factor"])

    def test_invalid_pwm_and_mouse_factor_are_rejected(self):
        settings = make_settings()
        settings["thermal"]["pwm"] = 256
        with self.assertRaisesRegex(ValueError, "pwm"):
            validate_feedback_profile(8, settings)

        settings = make_settings()
        settings["mouseSpeed"]["factor"] = 0
        with self.assertRaisesRegex(ValueError, "factor"):
            validate_feedback_profile(8, settings)

    def test_enabled_modalities_require_parameters(self):
        settings = make_settings()
        settings["thermal"] = {"enabled": True}
        with self.assertRaisesRegex(ValueError, "durationMs"):
            validate_feedback_profile(8, settings)

    def test_report_state_keeps_profile_and_legacy_pwm_values_in_sync(self):
        state = SharedCyclomaticComplexityObject()
        profile = validate_feedback_profile(8, make_settings())
        state.update_report("Example", "work", "work()", 8, profile)

        report = state.get_report_state()
        self.assertEqual("Example", report["class_name"])
        self.assertEqual(8, report["complexity"])
        self.assertEqual(profile, report["feedback_profile"])
        self.assertEqual(0, state.get_pwm_value_erm())
        self.assertEqual(0, state.get_pwm_nb_pulse_erm())


if __name__ == "__main__":
    unittest.main()
