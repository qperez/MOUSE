package fr.irisa.diversexrainbow.server;

import org.eclipse.lsp4j.DidChangeConfigurationParams;
import org.eclipse.lsp4j.InitializeParams;
import org.eclipse.lsp4j.jsonrpc.json.MessageJsonHandler;
import com.google.gson.JsonObject;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class FeedbackSettingsTest {

    @Test
    void defaultsPreserveExistingVibrationLevelsAndDisableNewModalities() {
        Map<?, ?> levels = (Map<?, ?>) FeedbackSettings.defaults().toPayload().get("levels");
        Map<?, ?> defaults = FeedbackSettings.defaults().toPayload();

        assertEquals(30, modality(levels, "simple", "vibration").get("pwm"));
        assertEquals(1, modality(levels, "simple", "vibration").get("pulseCount"));
        assertEquals(50, modality(levels, "moderate", "vibration").get("pwm"));
        assertEquals(2, modality(levels, "moderate", "vibration").get("pulseCount"));
        assertEquals(70, modality(levels, "high", "vibration").get("pwm"));
        assertEquals(90, modality(levels, "veryHigh", "vibration").get("pwm"));
        assertFalse((Boolean) modality(levels, "simple", "thermal").get("enabled"));
        assertFalse(modality(levels, "simple", "thermal").containsKey("pwm"));
        assertFalse((Boolean) modality(levels, "simple", "mouseSpeed").get("enabled"));
        assertFalse(modality(levels, "simple", "mouseSpeed").containsKey("factor"));
        assertEquals("vibration", defaults.get("activeProfile"));
    }

    @Test
    void definesThermalAndMouseProfilesWithRequestedDefaults() {
        Map<String, Object> thermalSettings = Map.of(
                "activeProfile", "thermal"
        );
        Map<String, Object> mouseSettings = Map.of(
                "activeProfile", "mouse"
        );
        Map<?, ?> thermal = (Map<?, ?>) FeedbackSettings.fromSettings(thermalSettings)
                .toPayload().get("levels");
        Map<?, ?> mouse = (Map<?, ?>) FeedbackSettings.fromSettings(mouseSettings)
                .toPayload().get("levels");

        assertTrue((Boolean) modality(thermal, "simple", "thermal").get("enabled"));
        assertEquals(5000, modality(thermal, "simple", "thermal").get("durationMs"));
        assertEquals(50, modality(thermal, "simple", "thermal").get("pwm"));
        assertEquals(200, modality(thermal, "veryHigh", "thermal").get("pwm"));
        assertFalse((Boolean) modality(thermal, "simple", "vibration").get("enabled"));
        assertTrue((Boolean) modality(mouse, "simple", "mouseSpeed").get("enabled"));
        assertEquals(1.0, modality(mouse, "simple", "mouseSpeed").get("factor"));
        assertEquals(0.8, modality(mouse, "moderate", "mouseSpeed").get("factor"));
        assertEquals(0.6, modality(mouse, "high", "mouseSpeed").get("factor"));
        assertEquals(0.4, modality(mouse, "veryHigh", "mouseSpeed").get("factor"));
    }

    @Test
    void parsesSelectedProfileAndPartialOverrides() {
        Map<String, Object> settings = Map.of(
                "activeProfile", "custom",
                "profiles", Map.of(
                        "custom", Map.of(
                                "moderate", Map.of(
                                        "vibration", Map.of("pwm", 65)
                                )
                        )
                )
        );
        Map<?, ?> payload = FeedbackSettings.fromSettings(settings).toPayload();
        Map<?, ?> levels = (Map<?, ?>) payload.get("levels");

        assertEquals("custom", payload.get("activeProfile"));
        assertEquals(65, modality(levels, "moderate", "vibration").get("pwm"));
        assertEquals(2, modality(levels, "moderate", "vibration").get("pulseCount"));
        assertEquals(30, modality(levels, "simple", "vibration").get("pwm"));
    }

    @Test
    void payloadContainsOnlyTheSelectedProfileAndComplexityBand() {
        Map<String, Object> settings = Map.of(
                "activeProfile", "custom",
                "profiles", Map.of(
                        "custom", Map.of(
                                "moderate", Map.of(
                                        "thermal", Map.of(
                                                "enabled", true,
                                                "durationMs", 7000,
                                                "pwm", 120
                                        ),
                                        "vibration", Map.of("enabled", false),
                                        "mouseSpeed", Map.of(
                                                "enabled", true,
                                                "factor", 0.8
                                        )
                                )
                        )
                )
        );
        Map<String, Object> payload =
                FeedbackSettings.fromSettings(settings).toPayload(8);

        assertEquals("custom", payload.get("activeProfile"));
        assertEquals("moderate", payload.get("level"));
        assertEquals(5, payload.size());
        assertEquals(7000, ((Map<?, ?>) payload.get("thermal")).get("durationMs"));
        assertFalse(((Map<?, ?>) payload.get("vibration")).containsKey("pwm"));
        assertEquals(0.8, ((Map<?, ?>) payload.get("mouseSpeed")).get("factor"));
    }

    @Test
    void payloadMapsComplexityBoundariesToOneFeedbackBand() {
        FeedbackSettings settings = FeedbackSettings.defaults();

        assertEquals("simple", settings.toPayload(5).get("level"));
        assertEquals("moderate", settings.toPayload(6).get("level"));
        assertEquals("high", settings.toPayload(11).get("level"));
        assertEquals("veryHigh", settings.toPayload(21).get("level"));
    }

    @Test
    void workspaceConfigurationChangeAppliesTheNewActiveProfile() {
        CyclomaticLanguageServer server = new CyclomaticLanguageServer();
        server.initialize(new InitializeParams()).join();

        Map<String, Object> changedSettings = Map.of(
                "activeProfile", "thermal",
                "profiles", Map.of(
                        "thermal", Map.of(
                                "moderate", Map.of(
                                        "thermal", Map.of(
                                                "enabled", true,
                                                "durationMs", 8000,
                                                "pwm", 125
                                        ),
                                        "vibration", Map.of("enabled", false),
                                        "mouseSpeed", Map.of("enabled", false)
                                )
                        )
                )
        );
        server.getWorkspaceService().didChangeConfiguration(
                new DidChangeConfigurationParams(changedSettings));

        Map<String, Object> feedback =
                server.getFeedbackSettings().toPayload(8);
        assertEquals("thermal", feedback.get("activeProfile"));
        assertEquals(125, ((Map<?, ?>) feedback.get("thermal")).get("pwm"));
        assertFalse((Boolean) ((Map<?, ?>) feedback.get("vibration")).get("enabled"));
    }

    @Test
    void parsesConfigurationSettingsDeserializedByLsp4j() {
        String notificationSettings = """
                {
                  "activeProfile": "mouse",
                  "profiles": {
                    "mouse": {
                      "simple": {
                        "thermal": {"enabled": false},
                        "vibration": {"enabled": false},
                        "mouseSpeed": {"enabled": true, "factor": 1}
                      }
                    }
                  }
                }
                """;
        DidChangeConfigurationParams params = new MessageJsonHandler(Map.of()).getGson()
                .fromJson("{\"settings\":" + notificationSettings + "}",
                        DidChangeConfigurationParams.class);

        assertInstanceOf(JsonObject.class, params.getSettings());
        CyclomaticLanguageServer server = new CyclomaticLanguageServer();
        server.initialize(new InitializeParams()).join();
        server.getWorkspaceService().didChangeConfiguration(params);

        Map<String, Object> feedback = server.getFeedbackSettings().toPayload(3);
        assertEquals("mouse", feedback.get("activeProfile"));
        assertTrue((Boolean) ((Map<?, ?>) feedback.get("mouseSpeed")).get("enabled"));
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
        assertFalse(modality(levels, "moderate", "vibration").containsKey("pulseCount"));
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
    void parsesProfilesWrappedInTheExtensionSection() {
        Map<String, Object> settings = Map.of(
                "cyclomaticLsp", Map.of(
                        "activeProfile", "mouse",
                        "profiles", Map.of(
                                "mouse", Map.of(
                                        "high", Map.of(
                                                "mouseSpeed", Map.of("factor", 0.55)
                                        )
                                )
                        )
                )
        );
        Map<?, ?> payload = FeedbackSettings.fromSettings(settings).toPayload();
        Map<?, ?> levels = (Map<?, ?>) payload.get("levels");

        assertEquals("mouse", payload.get("activeProfile"));
        assertEquals(0.55, modality(levels, "high", "mouseSpeed").get("factor"));
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

    @Test
    void rejectsUnknownActiveProfiles() {
        assertThrows(IllegalArgumentException.class,
                () -> FeedbackSettings.fromSettings(Map.of("activeProfile", "unknown")));
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> modality(Map<?, ?> levels, String level, String modality) {
        return (Map<String, Object>) ((Map<?, ?>) levels.get(level)).get(modality);
    }
}
