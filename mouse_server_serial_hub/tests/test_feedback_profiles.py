import unittest

from mouse_server_serial_hub.mouse.shared.feedback_profiles import (
    leave_feedback_profile,
    select_feedback_profile,
)
from mouse_server_serial_hub.mouse.shared.shared_cyclomatic_complexity_object import (
    SharedCyclomaticComplexityObject,
)


def make_settings():
    return {
        "levels": {
            "simple": {
                "thermal": {"enabled": False, "durationMs": 1000, "pwm": 100},
                "vibration": {
                    "enabled": True,
                    "durationMs": 200,
                    "pwm": 30,
                    "pulseCount": 1,
                    "pulseDelayMs": 200,
                },
                "mouseSpeed": {"enabled": False, "factor": 1},
            },
            "moderate": {
                "thermal": {"enabled": True, "durationMs": 900, "pwm": 75},
                "vibration": {
                    "enabled": False,
                    "durationMs": 150,
                    "pwm": 50,
                    "pulseCount": 2,
                    "pulseDelayMs": 100,
                },
                "mouseSpeed": {"enabled": True, "factor": 0.8},
            },
            "high": {
                "thermal": {"enabled": False, "durationMs": 1000, "pwm": 100},
                "vibration": {
                    "enabled": True,
                    "durationMs": 200,
                    "pwm": 70,
                    "pulseCount": 3,
                    "pulseDelayMs": 200,
                },
                "mouseSpeed": {"enabled": False, "factor": 1},
            },
            "veryHigh": {
                "thermal": {"enabled": False, "durationMs": 1000, "pwm": 100},
                "vibration": {
                    "enabled": True,
                    "durationMs": 200,
                    "pwm": 90,
                    "pulseCount": 3,
                    "pulseDelayMs": 200,
                },
                "mouseSpeed": {"enabled": False, "factor": 1},
            },
        }
    }


class FeedbackProfilesTest(unittest.TestCase):
    def test_complexity_boundaries_select_expected_levels(self):
        settings = make_settings()
        expected = {
            1: "simple",
            5: "simple",
            6: "moderate",
            10: "moderate",
            11: "high",
            20: "high",
            21: "veryHigh",
        }

        for complexity, level in expected.items():
            with self.subTest(complexity=complexity):
                self.assertEqual(
                    level, select_feedback_profile(complexity, settings)["level"]
                )

    def test_selected_profile_preserves_modality_parameters(self):
        profile = select_feedback_profile(8, make_settings())

        self.assertTrue(profile["thermal"]["enabled"])
        self.assertEqual(900, profile["thermal"]["durationMs"])
        self.assertFalse(profile["vibration"]["enabled"])
        self.assertTrue(profile["mouseSpeed"]["enabled"])
        self.assertEqual(0.8, profile["mouseSpeed"]["factor"])

    def test_missing_settings_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "feedbackSettings"):
            select_feedback_profile(6, None)

    def test_leave_disables_feedback_and_restores_neutral_speed(self):
        profile = leave_feedback_profile()

        self.assertFalse(profile["active"])
        self.assertFalse(profile["mouseSpeed"]["enabled"])
        self.assertEqual(1.0, profile["mouseSpeed"]["factor"])

    def test_invalid_pwm_and_mouse_factor_are_rejected(self):
        settings = make_settings()
        settings["levels"]["high"]["thermal"]["pwm"] = 256
        with self.assertRaisesRegex(ValueError, "pwm"):
            select_feedback_profile(11, settings)

        settings = make_settings()
        settings["levels"]["moderate"]["mouseSpeed"]["factor"] = 0
        with self.assertRaisesRegex(ValueError, "factor"):
            select_feedback_profile(8, settings)

    def test_non_integer_complexity_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "complexity"):
            select_feedback_profile(5.5, make_settings())

    def test_report_state_keeps_profile_and_legacy_pwm_values_in_sync(self):
        state = SharedCyclomaticComplexityObject()
        profile = select_feedback_profile(8, make_settings())
        state.update_report("Example", "work", "work()", 8, profile)

        report = state.get_report_state()
        self.assertEqual("Example", report["class_name"])
        self.assertEqual(8, report["complexity"])
        self.assertEqual(profile, report["feedback_profile"])
        self.assertEqual(0, state.get_pwm_value_erm())
        self.assertEqual(0, state.get_pwm_nb_pulse_erm())


if __name__ == "__main__":
    unittest.main()
