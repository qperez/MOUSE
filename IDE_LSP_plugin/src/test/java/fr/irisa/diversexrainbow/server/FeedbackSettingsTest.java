package fr.irisa.diversexrainbow.server;

import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class FeedbackSettingsTest {

    @Test
    void defaultsPreserveExistingVibrationLevelsAndDisableNewModalities() {
        Map<?, ?> levels = (Map<?, ?>) FeedbackSettings.defaults().toPayload().get("levels");

        assertEquals(30, modality(levels, "simple", "vibration").get("pwm"));
        assertEquals(1, modality(levels, "simple", "vibration").get("pulseCount"));
        assertEquals(50, modality(levels, "moderate", "vibration").get("pwm"));
        assertEquals(2, modality(levels, "moderate", "vibration").get("pulseCount"));
        assertEquals(70, modality(levels, "high", "vibration").get("pwm"));
        assertEquals(90, modality(levels, "veryHigh", "vibration").get("pwm"));
        assertFalse((Boolean) modality(levels, "simple", "thermal").get("enabled"));
        assertFalse((Boolean) modality(levels, "simple", "mouseSpeed").get("enabled"));
    }

    @Test
    void parsesPartialWorkspaceSettingsOverDefaults() {
        Map<String, Object> settings = Map.of(
                "feedback", Map.of(
                        "levels", Map.of(
                                "moderate", Map.of(
                                        "vibration", Map.of(
                                                "enabled", false,
                                                "pulseCount", 4
                                        ),
                                        "mouseSpeed", Map.of(
                                                "enabled", true,
                                                "factor", 0.75
                                        )
                                )
                        )
                )
        );
        Map<?, ?> levels = (Map<?, ?>) FeedbackSettings.fromSettings(settings)
                .toPayload().get("levels");

        assertFalse((Boolean) modality(levels, "moderate", "vibration").get("enabled"));
        assertEquals(4, modality(levels, "moderate", "vibration").get("pulseCount"));
        assertTrue((Boolean) modality(levels, "moderate", "mouseSpeed").get("enabled"));
        assertEquals(0.75, modality(levels, "moderate", "mouseSpeed").get("factor"));
        assertEquals(30, modality(levels, "simple", "vibration").get("pwm"));
    }

    @Test
    void parsesFlatConfigurationSectionKeys() {
        Map<String, Object> settings = Map.of(
                "feedback.levels.high.mouseSpeed.enabled", true,
                "feedback.levels.high.mouseSpeed.factor", 0.6
        );
        Map<?, ?> levels = (Map<?, ?>) FeedbackSettings.fromSettings(settings)
                .toPayload().get("levels");

        assertTrue((Boolean) modality(levels, "high", "mouseSpeed").get("enabled"));
        assertEquals(0.6, modality(levels, "high", "mouseSpeed").get("factor"));
    }

    @Test
    void parsesSettingsWrappedInTheExtensionSection() {
        Map<String, Object> settings = Map.of(
                "cyclomaticLsp", Map.of(
                        "feedback", Map.of(
                                "levels", Map.of(
                                        "veryHigh", Map.of(
                                                "vibration", Map.of("pwm", 120)
                                        )
                                )
                        )
                )
        );
        Map<?, ?> levels = (Map<?, ?>) FeedbackSettings.fromSettings(settings)
                .toPayload().get("levels");

        assertEquals(120, modality(levels, "veryHigh", "vibration").get("pwm"));
    }

    @Test
    void rejectsOutOfRangeActuatorValues() {
        Map<String, Object> settings = Map.of(
                "feedback", Map.of(
                        "levels", Map.of(
                                "high", Map.of(
                                        "thermal", Map.of("pwm", 256)
                                )
                        )
                )
        );

        assertThrows(IllegalArgumentException.class, () -> FeedbackSettings.fromSettings(settings));
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> modality(Map<?, ?> levels, String level, String modality) {
        return (Map<String, Object>) ((Map<?, ?>) levels.get(level)).get(modality);
    }
}
