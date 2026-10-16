package fr.irisa.diversexrainbow.server;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonPrimitive;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Immutable feedback profile settings synchronized from the VS Code extension.
 */
public final class FeedbackSettings {

    private static final String[] PROFILES = {"vibration", "thermal", "mouse", "custom"};
    private static final String[] LEVELS = {"simple", "moderate", "high", "veryHigh"};

    private final String activeProfile;
    private final Map<String, Object> profiles;

    private FeedbackSettings(String activeProfile, Map<String, Object> profiles) {
        this.activeProfile = activeProfile;
        this.profiles = Collections.unmodifiableMap(profiles);
    }

    public static FeedbackSettings defaults() {
        Map<String, Object> profiles = new LinkedHashMap<>();
        profiles.put("vibration", createProfile(false, true, false));
        profiles.put("thermal", createProfile(true, false, false));
        profiles.put("mouse", createProfile(false, false, true));
        profiles.put("custom", profiles.get("vibration"));
        return new FeedbackSettings("vibration", profiles);
    }

    public static FeedbackSettings fromSettings(Object rawSettings) {
        Map<String, Object> root = asMap(rawSettings, "settings", true);
        if (root.containsKey("cyclomaticLsp")) {
            root = asMap(root.get("cyclomaticLsp"), "cyclomaticLsp", false);
        }

        FeedbackSettings defaults = defaults();
        String activeProfile = root.containsKey("activeProfile")
                ? stringValue(root.get("activeProfile"), "activeProfile")
                : defaults.activeProfile;
        if (!contains(PROFILES, activeProfile)) {
            throw new IllegalArgumentException(
                    "activeProfile must be one of vibration, thermal, mouse, or custom");
        }

        Map<String, Object> configuredProfiles = root.containsKey("profiles")
                ? asMap(root.get("profiles"), "profiles", false)
                : Collections.emptyMap();
        boolean hasProfiles = root.containsKey("profiles");
        Map<String, Object> legacyLevels = hasProfiles
                ? Collections.emptyMap()
                : legacyLevels(root);

        Map<String, Object> parsedProfiles = new LinkedHashMap<>();
        for (String profileName : PROFILES) {
            Map<String, Object> defaultProfile =
                    asMap(defaults.profiles.get(profileName), "default profile", false);
            Map<String, Object> configuredProfile = configuredProfiles.containsKey(profileName)
                    ? asMap(configuredProfiles.get(profileName),
                            "profiles." + profileName, false)
                    : Collections.emptyMap();
            if (profileName.equals("vibration") && !legacyLevels.isEmpty()) {
                configuredProfile = legacyLevels;
            }
            parsedProfiles.put(profileName,
                    parseProfile(profileName, configuredProfile, defaultProfile));
        }
        return new FeedbackSettings(activeProfile, parsedProfiles);
    }

    public Map<String, Object> toPayload() {
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("activeProfile", activeProfile);
        Map<String, Object> profile =
                asMap(profiles.get(activeProfile), "active profile", false);
        Map<String, Object> levels = new LinkedHashMap<>();
        for (String levelName : LEVELS) {
            Map<String, Object> configuredLevel =
                    asMap(profile.get(levelName), "active profile level", false);
            Map<String, Object> level = new LinkedHashMap<>();
            level.put("thermal", payloadModality(configuredLevel.get("thermal")));
            level.put("vibration", payloadModality(configuredLevel.get("vibration")));
            level.put("mouseSpeed", payloadModality(configuredLevel.get("mouseSpeed")));
            levels.put(levelName, Collections.unmodifiableMap(level));
        }
        payload.put("levels", Collections.unmodifiableMap(levels));
        return Collections.unmodifiableMap(payload);
    }

    public String getActiveProfile() {
        return activeProfile;
    }

    public Map<String, Object> toPayload(int complexity) {
        String levelName;
        if (complexity <= 5) {
            levelName = "simple";
        } else if (complexity <= 10) {
            levelName = "moderate";
        } else if (complexity <= 20) {
            levelName = "high";
        } else {
            levelName = "veryHigh";
        }

        Map<String, Object> active = asMap(profiles.get(activeProfile), "active profile", false);
        Map<String, Object> configuredLevel =
                asMap(active.get(levelName), "active profile level", false);
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("activeProfile", activeProfile);
        payload.put("level", levelName);
        payload.put("thermal", payloadModality(configuredLevel.get("thermal")));
        payload.put("vibration", payloadModality(configuredLevel.get("vibration")));
        payload.put("mouseSpeed", payloadModality(configuredLevel.get("mouseSpeed")));
        return Collections.unmodifiableMap(payload);
    }

    private static Map<String, Object> payloadModality(Object configured) {
        Map<String, Object> modality = asMap(configured, "configured modality", false);
        if (!booleanValue(modality.get("enabled"), "configured modality.enabled")) {
            return Collections.singletonMap("enabled", false);
        }
        return modality;
    }

    private static Map<String, Object> createProfile(
            boolean thermalEnabled, boolean vibrationEnabled, boolean mouseSpeedEnabled) {
        int[] thermalPwm = {50, 100, 150, 200};
        int[] vibrationPwm = {30, 50, 70, 90};
        int[] pulseCounts = {1, 2, 3, 3};
        double[] mouseSpeedFactors = {1.0, 0.8, 0.6, 0.4};
        Map<String, Object> profile = new LinkedHashMap<>();
        for (int index = 0; index < LEVELS.length; index++) {
            Map<String, Object> thermal = new LinkedHashMap<>();
            thermal.put("enabled", thermalEnabled);
            thermal.put("durationMs", 5000);
            thermal.put("pwm", thermalPwm[index]);

            Map<String, Object> vibration = new LinkedHashMap<>();
            vibration.put("enabled", vibrationEnabled);
            vibration.put("durationMs", 200);
            vibration.put("pwm", vibrationPwm[index]);
            vibration.put("pulseCount", pulseCounts[index]);
            vibration.put("pulseDelayMs", 200);

            Map<String, Object> mouseSpeed = new LinkedHashMap<>();
            mouseSpeed.put("enabled", mouseSpeedEnabled);
            mouseSpeed.put("factor", mouseSpeedFactors[index]);

            Map<String, Object> level = new LinkedHashMap<>();
            level.put("thermal", Collections.unmodifiableMap(thermal));
            level.put("vibration", Collections.unmodifiableMap(vibration));
            level.put("mouseSpeed", Collections.unmodifiableMap(mouseSpeed));
            profile.put(LEVELS[index], Collections.unmodifiableMap(level));
        }
        return Collections.unmodifiableMap(profile);
    }

    private static Map<String, Object> parseProfile(
            String profileName, Map<String, Object> configured, Map<String, Object> defaults) {
        Map<String, Object> result = new LinkedHashMap<>();
        for (String levelName : LEVELS) {
            Map<String, Object> defaultLevel =
                    asMap(defaults.get(levelName), "default level", false);
            Map<String, Object> configuredLevel = configured.containsKey(levelName)
                    ? asMap(configured.get(levelName),
                            "profiles." + profileName + "." + levelName, false)
                    : Collections.emptyMap();
            result.put(levelName, parseLevel(
                    profileName, levelName, configuredLevel, defaultLevel));
        }
        return Collections.unmodifiableMap(result);
    }

    private static Map<String, Object> parseLevel(
            String profileName,
            String levelName,
            Map<String, Object> configured,
            Map<String, Object> defaults) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("thermal", parseModality(
                profileName, levelName, "thermal", configured, defaults));
        result.put("vibration", parseModality(
                profileName, levelName, "vibration", configured, defaults));
        result.put("mouseSpeed", parseModality(
                profileName, levelName, "mouseSpeed", configured, defaults));
        return Collections.unmodifiableMap(result);
    }

    private static Map<String, Object> parseModality(
            String profileName,
            String levelName,
            String modalityName,
            Map<String, Object> configuredLevel,
            Map<String, Object> defaultLevel) {
        String prefix = "profiles." + profileName + "." + levelName + "." + modalityName;
        Map<String, Object> defaultModality =
                asMap(defaultLevel.get(modalityName), "default modality", false);
        Map<String, Object> configuredModality = configuredLevel.containsKey(modalityName)
                ? asMap(configuredLevel.get(modalityName), prefix, false)
                : Collections.emptyMap();
        Map<String, Object> result = new LinkedHashMap<>(defaultModality);
        result.putAll(configuredModality);

        result.put("enabled", booleanValue(result.get("enabled"), prefix + ".enabled"));
        if (modalityName.equals("mouseSpeed")) {
            double factor = numberValue(result.get("factor"), prefix + ".factor").doubleValue();
            if (!Double.isFinite(factor) || factor < 0.1) {
                throw new IllegalArgumentException(prefix + ".factor must be a finite number >= 0.1");
            }
            result.put("factor", factor);
        } else {
            int duration = integerValue(result.get("durationMs"), prefix + ".durationMs");
            int pwm = integerValue(result.get("pwm"), prefix + ".pwm");
            if (duration < 0) {
                throw new IllegalArgumentException(prefix + ".durationMs must be >= 0");
            }
            if (pwm < 0 || pwm > 255) {
                throw new IllegalArgumentException(prefix + ".pwm must be between 0 and 255");
            }
            result.put("durationMs", duration);
            result.put("pwm", pwm);
            if (modalityName.equals("vibration")) {
                int pulseCount = integerValue(result.get("pulseCount"), prefix + ".pulseCount");
                int pulseDelayMs =
                        integerValue(result.get("pulseDelayMs"), prefix + ".pulseDelayMs");
                if (pulseCount < 1) {
                    throw new IllegalArgumentException(prefix + ".pulseCount must be >= 1");
                }
                if (pulseDelayMs < 0) {
                    throw new IllegalArgumentException(prefix + ".pulseDelayMs must be >= 0");
                }
                result.put("pulseCount", pulseCount);
                result.put("pulseDelayMs", pulseDelayMs);
            }
        }
        return Collections.unmodifiableMap(result);
    }

    private static Map<String, Object> legacyLevels(Map<String, Object> root) {
        boolean hasFeedback = root.containsKey("feedback")
                || root.keySet().stream().anyMatch(key -> key.startsWith("feedback."));
        if (!hasFeedback) {
            return Collections.emptyMap();
        }

        Map<String, Object> feedback = root.containsKey("feedback")
                ? new LinkedHashMap<>(asMap(root.get("feedback"), "feedback", false))
                : new LinkedHashMap<>();
        for (Map.Entry<String, Object> entry : root.entrySet()) {
            if (entry.getKey().startsWith("feedback.")) {
                putNested(feedback, entry.getKey().substring("feedback.".length()), entry.getValue());
            }
        }
        if (!feedback.containsKey("levels")) {
            return Collections.emptyMap();
        }
        return asMap(feedback.get("levels"), "feedback.levels", false);
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

    private static Map<String, Object> asMap(Object value, String name, boolean allowNull) {
        if (value instanceof JsonElement) {
            value = fromJsonElement((JsonElement) value);
        }
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

    private static Object fromJsonElement(JsonElement value) {
        if (value == null || value.isJsonNull()) {
            return null;
        }
        if (value.isJsonObject()) {
            Map<String, Object> result = new LinkedHashMap<>();
            JsonObject object = value.getAsJsonObject();
            for (Map.Entry<String, JsonElement> entry : object.entrySet()) {
                result.put(entry.getKey(), fromJsonElement(entry.getValue()));
            }
            return result;
        }
        if (value.isJsonArray()) {
            List<Object> result = new ArrayList<>();
            JsonArray array = value.getAsJsonArray();
            for (JsonElement element : array) {
                result.add(fromJsonElement(element));
            }
            return result;
        }
        JsonPrimitive primitive = value.getAsJsonPrimitive();
        if (primitive.isBoolean()) {
            return primitive.getAsBoolean();
        }
        if (primitive.isNumber()) {
            return primitive.getAsNumber();
        }
        return primitive.getAsString();
    }

    private static boolean booleanValue(Object value, String name) {
        if (!(value instanceof Boolean)) {
            throw new IllegalArgumentException(name + " must be a boolean");
        }
        return (Boolean) value;
    }

    private static String stringValue(Object value, String name) {
        if (!(value instanceof String)) {
            throw new IllegalArgumentException(name + " must be a string");
        }
        return (String) value;
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

    private static boolean contains(String[] values, String candidate) {
        for (String value : values) {
            if (value.equals(candidate)) {
                return true;
            }
        }
        return false;
    }
}
