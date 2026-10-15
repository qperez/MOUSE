package fr.irisa.diversexrainbow.server;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Immutable feedback settings synchronized from the VS Code extension.
 */
public final class FeedbackSettings {

    private static final String[] LEVELS = {"simple", "moderate", "high", "veryHigh"};
    private final Map<String, Object> levels;

    private FeedbackSettings(Map<String, Object> levels) {
        this.levels = Collections.unmodifiableMap(levels);
    }

    public static FeedbackSettings defaults() {
        Map<String, Object> levels = new LinkedHashMap<>();
        levels.put("simple", level(false, 1000, 100, 30, 1));
        levels.put("moderate", level(false, 1000, 100, 50, 2));
        levels.put("high", level(false, 1000, 100, 70, 3));
        levels.put("veryHigh", level(false, 1000, 100, 90, 3));
        return new FeedbackSettings(levels);
    }

    public static FeedbackSettings fromSettings(Object rawSettings) {
        Map<String, Object> root = asMap(rawSettings, "settings", true);
        if (root.containsKey("cyclomaticLsp")) {
            root = asMap(root.get("cyclomaticLsp"), "cyclomaticLsp", false);
        }
        boolean hasFeedback = root.containsKey("feedback")
                || root.keySet().stream().anyMatch(key -> key.startsWith("feedback."));
        if (!hasFeedback) {
            return defaults();
        }

        Map<String, Object> feedback = root.containsKey("feedback")
                ? new LinkedHashMap<>(asMap(root.get("feedback"), "feedback", false))
                : new LinkedHashMap<>();
        for (Map.Entry<String, Object> entry : root.entrySet()) {
            if (entry.getKey().startsWith("feedback.")) {
                putNested(feedback, entry.getKey().substring("feedback.".length()), entry.getValue());
            }
        }
        Map<String, Object> configuredLevels = feedback.containsKey("levels")
                ? asMap(feedback.get("levels"), "feedback.levels", false)
                : Collections.emptyMap();
        FeedbackSettings defaults = defaults();
        Map<String, Object> parsedLevels = new LinkedHashMap<>();

        for (String levelName : LEVELS) {
            Map<String, Object> defaultLevel =
                    asMap(defaults.levels.get(levelName), "default level", false);
            Map<String, Object> configuredLevel = configuredLevels.containsKey(levelName)
                    ? asMap(configuredLevels.get(levelName), "feedback.levels." + levelName, false)
                    : Collections.emptyMap();
            parsedLevels.put(levelName, parseLevel(levelName, configuredLevel, defaultLevel));
        }
        return new FeedbackSettings(parsedLevels);
    }

    public Map<String, Object> toPayload() {
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("levels", levels);
        return Collections.unmodifiableMap(payload);
    }

    private static Map<String, Object> level(
            boolean thermalEnabled, int thermalDurationMs, int thermalPwm,
            int vibrationPwm, int vibrationPulseCount) {
        Map<String, Object> thermal = new LinkedHashMap<>();
        thermal.put("enabled", thermalEnabled);
        thermal.put("durationMs", thermalDurationMs);
        thermal.put("pwm", thermalPwm);

        Map<String, Object> vibration = new LinkedHashMap<>();
        vibration.put("enabled", true);
        vibration.put("durationMs", 200);
        vibration.put("pwm", vibrationPwm);
        vibration.put("pulseCount", vibrationPulseCount);
        vibration.put("pulseDelayMs", 200);

        Map<String, Object> mouseSpeed = new LinkedHashMap<>();
        mouseSpeed.put("enabled", false);
        mouseSpeed.put("factor", 1.0);

        Map<String, Object> profile = new LinkedHashMap<>();
        profile.put("thermal", Collections.unmodifiableMap(thermal));
        profile.put("vibration", Collections.unmodifiableMap(vibration));
        profile.put("mouseSpeed", Collections.unmodifiableMap(mouseSpeed));
        return Collections.unmodifiableMap(profile);
    }

    private static Map<String, Object> parseLevel(
            String levelName, Map<String, Object> configured, Map<String, Object> defaults) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("thermal", parseModality(levelName, "thermal", configured, defaults));
        result.put("vibration", parseModality(levelName, "vibration", configured, defaults));
        result.put("mouseSpeed", parseModality(levelName, "mouseSpeed", configured, defaults));
        return Collections.unmodifiableMap(result);
    }

    private static Map<String, Object> parseModality(
            String levelName, String modalityName,
            Map<String, Object> configuredLevel, Map<String, Object> defaultLevel) {
        Map<String, Object> defaults = asMap(defaultLevel.get(modalityName), "default modality", false);
        Map<String, Object> configured = configuredLevel.containsKey(modalityName)
                ? asMap(configuredLevel.get(modalityName),
                        "feedback.levels." + levelName + "." + modalityName, false)
                : Collections.emptyMap();
        Map<String, Object> result = new LinkedHashMap<>(defaults);
        for (Map.Entry<String, Object> entry : configured.entrySet()) {
            result.put(entry.getKey(), entry.getValue());
        }

        result.put("enabled", booleanValue(result.get("enabled"),
                levelName + "." + modalityName + ".enabled"));
        if (modalityName.equals("mouseSpeed")) {
            double factor = numberValue(result.get("factor"),
                    levelName + ".mouseSpeed.factor").doubleValue();
            if (!Double.isFinite(factor) || factor < 0.1) {
                throw new IllegalArgumentException(
                        levelName + ".mouseSpeed.factor must be a finite number >= 0.1");
            }
            result.put("factor", factor);
        } else {
            int duration = integerValue(result.get("durationMs"),
                    levelName + "." + modalityName + ".durationMs");
            int pwm = integerValue(result.get("pwm"),
                    levelName + "." + modalityName + ".pwm");
            if (duration < 0) {
                throw new IllegalArgumentException(
                        levelName + "." + modalityName + ".durationMs must be >= 0");
            }
            if (pwm < 0 || pwm > 255) {
                throw new IllegalArgumentException(
                        levelName + "." + modalityName + ".pwm must be between 0 and 255");
            }
            result.put("durationMs", duration);
            result.put("pwm", pwm);
            if (modalityName.equals("vibration")) {
                int pulseCount = integerValue(result.get("pulseCount"),
                        levelName + ".vibration.pulseCount");
                int pulseDelayMs = integerValue(result.get("pulseDelayMs"),
                        levelName + ".vibration.pulseDelayMs");
                if (pulseCount < 1) {
                    throw new IllegalArgumentException(
                            levelName + ".vibration.pulseCount must be >= 1");
                }
                if (pulseDelayMs < 0) {
                    throw new IllegalArgumentException(
                            levelName + ".vibration.pulseDelayMs must be >= 0");
                }
                result.put("pulseCount", pulseCount);
                result.put("pulseDelayMs", pulseDelayMs);
            }
        }
        return Collections.unmodifiableMap(result);
    }

    private static Map<String, Object> asMap(Object value, String name, boolean allowNull) {
        if (value == null && allowNull) {
            return Collections.emptyMap();
        }
        if (!(value instanceof Map<?, ?>)) {
            throw new IllegalArgumentException(name + " must be an object");
        }
        Map<String, Object> result = new LinkedHashMap<>();
        for (Map.Entry<?, ?> entry : ((Map<?, ?>) value).entrySet()) {
            if (!(entry.getKey() instanceof String)) {
                throw new IllegalArgumentException(name + " contains a non-string key");
            }
            result.put((String) entry.getKey(), entry.getValue());
        }
        return result;
    }

    private static void putNested(Map<String, Object> root, String path, Object value) {
        String[] parts = path.split("\\.");
        Map<String, Object> current = root;
        for (int index = 0; index < parts.length - 1; index++) {
            Object child = current.get(parts[index]);
            if (child == null) {
                Map<String, Object> next = new LinkedHashMap<>();
                current.put(parts[index], next);
                current = next;
            } else {
                Map<String, Object> next = asMap(child, "feedback." + path, false);
                current.put(parts[index], next);
                current = next;
            }
        }
        current.put(parts[parts.length - 1], value);
    }

    private static boolean booleanValue(Object value, String name) {
        if (!(value instanceof Boolean)) {
            throw new IllegalArgumentException(name + " must be a boolean");
        }
        return (Boolean) value;
    }

    private static Number numberValue(Object value, String name) {
        if (!(value instanceof Number)) {
            throw new IllegalArgumentException(name + " must be a number");
        }
        return (Number) value;
    }

    private static int integerValue(Object value, String name) {
        Number number = numberValue(value, name);
        double doubleValue = number.doubleValue();
        if (!Double.isFinite(doubleValue) || doubleValue != Math.rint(doubleValue)
                || doubleValue < Integer.MIN_VALUE || doubleValue > Integer.MAX_VALUE) {
            throw new IllegalArgumentException(name + " must be an integer");
        }
        return (int) doubleValue;
    }
}
