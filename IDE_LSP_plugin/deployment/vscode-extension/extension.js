const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const { LanguageClient } = require('vscode-languageclient/node');

let client;

const profileDefaults = {
  vibration: {
    simple: {
      thermal: { enabled: false },
      vibration: { enabled: true, durationMs: 200, pwm: 30, pulseCount: 1, pulseDelayMs: 200 },
      mouseSpeed: { enabled: false }
    },
    moderate: {
      thermal: { enabled: false },
      vibration: { enabled: true, durationMs: 200, pwm: 50, pulseCount: 2, pulseDelayMs: 200 },
      mouseSpeed: { enabled: false }
    },
    high: {
      thermal: { enabled: false },
      vibration: { enabled: true, durationMs: 200, pwm: 70, pulseCount: 3, pulseDelayMs: 200 },
      mouseSpeed: { enabled: false }
    },
    veryHigh: {
      thermal: { enabled: false },
      vibration: { enabled: true, durationMs: 200, pwm: 90, pulseCount: 3, pulseDelayMs: 200 },
      mouseSpeed: { enabled: false }
    }
  },
  thermal: {
    simple: {
      thermal: { enabled: true, durationMs: 5000, pwm: 50 },
      vibration: { enabled: false },
      mouseSpeed: { enabled: false }
    },
    moderate: {
      thermal: { enabled: true, durationMs: 5000, pwm: 100 },
      vibration: { enabled: false },
      mouseSpeed: { enabled: false }
    },
    high: {
      thermal: { enabled: true, durationMs: 5000, pwm: 150 },
      vibration: { enabled: false },
      mouseSpeed: { enabled: false }
    },
    veryHigh: {
      thermal: { enabled: true, durationMs: 5000, pwm: 200 },
      vibration: { enabled: false },
      mouseSpeed: { enabled: false }
    }
  },
  mouse: {
    simple: {
      thermal: { enabled: false },
      vibration: { enabled: false },
      mouseSpeed: { enabled: true, factor: 1 }
    },
    moderate: {
      thermal: { enabled: false },
      vibration: { enabled: false },
      mouseSpeed: { enabled: true, factor: 0.8 }
    },
    high: {
      thermal: { enabled: false },
      vibration: { enabled: false },
      mouseSpeed: { enabled: true, factor: 0.6 }
    },
    veryHigh: {
      thermal: { enabled: false },
      vibration: { enabled: false },
      mouseSpeed: { enabled: true, factor: 0.4 }
    }
  },
  custom: {
    simple: {
      thermal: { enabled: false },
      vibration: { enabled: true, durationMs: 200, pwm: 30, pulseCount: 1, pulseDelayMs: 200 },
      mouseSpeed: { enabled: false }
    },
    moderate: {
      thermal: { enabled: false },
      vibration: { enabled: true, durationMs: 200, pwm: 50, pulseCount: 2, pulseDelayMs: 200 },
      mouseSpeed: { enabled: false }
    },
    high: {
      thermal: { enabled: false },
      vibration: { enabled: true, durationMs: 200, pwm: 70, pulseCount: 3, pulseDelayMs: 200 },
      mouseSpeed: { enabled: false }
    },
    veryHigh: {
      thermal: { enabled: false },
      vibration: { enabled: true, durationMs: 200, pwm: 90, pulseCount: 3, pulseDelayMs: 200 },
      mouseSpeed: { enabled: false }
    }
  }
};

function getLegacyFeedbackDefaults(levelName) {
  return {
    thermal: { enabled: false, durationMs: 1000, pwm: 100 },
    vibration: profileDefaults.vibration[levelName].vibration,
    mouseSpeed: { enabled: false, factor: 1 }
  };
}

function hasConfiguredValue(configuration, setting) {
  const inspected = configuration.inspect(setting);
  return inspected && [
    'globalValue',
    'workspaceValue',
    'workspaceFolderValue',
    'globalLanguageValue',
    'workspaceLanguageValue',
    'workspaceFolderLanguageValue'
  ].some(key => inspected[key] !== undefined);
}

function hasLegacyFeedback(configuration) {
  for (const levelName of Object.keys(profileDefaults.vibration)) {
    const modalities = getLegacyFeedbackDefaults(levelName);
    for (const [modalityName, parameters] of Object.entries(modalities)) {
      for (const parameterName of Object.keys(parameters)) {
        const setting = `feedback.levels.${levelName}.${modalityName}.${parameterName}`;
        if (hasConfiguredValue(configuration, setting)) {
          return true;
        }
      }
    }
  }
  return false;
}

function getFeedbackSettings(configuration) {
  const activeProfile = configuration.get('activeProfile', 'vibration');
  const profiles = configuration.get('profiles', profileDefaults);
  if (hasConfiguredValue(configuration, 'profiles') || !hasLegacyFeedback(configuration)) {
    return { activeProfile, profiles };
  }

  const legacyLevels = {};
  for (const levelName of Object.keys(profileDefaults.vibration)) {
    const defaults = getLegacyFeedbackDefaults(levelName);
    const level = {};
    for (const [modalityName, parameters] of Object.entries(defaults)) {
      level[modalityName] = {};
      for (const [parameterName, defaultValue] of Object.entries(parameters)) {
        const setting = `feedback.levels.${levelName}.${modalityName}.${parameterName}`;
        level[modalityName][parameterName] = configuration.get(setting, defaultValue);
      }
    }
    legacyLevels[levelName] = level;
  }
  return {
    activeProfile,
    profiles: { ...profiles, vibration: legacyLevels }
  };
}

exports.activate = (ctx) => {
  const cfg = vscode.workspace.getConfiguration('cyclomaticLsp');
  const java = cfg.get('javaPath') || 'java';
  const jar = cfg.get('serverJar') || path.join(ctx.extensionPath, 'server', 'cyclomatic-lsp.jar');
  let pendingSettings;

  if (!fs.existsSync(jar)) {
    vscode.window.showErrorMessage(`Cyclomatic LSP : JAR introuvable (${jar}). Voir cyclomaticLsp.serverJar.`);
    return;
  }

  client = new LanguageClient(
    'cyclomaticLsp',
    'Cyclomatic LSP',
    { command: java, args: ['-jar', jar] },
    {
      documentSelector: [{ scheme: 'file', language: 'java' }],
      initializationOptions: getFeedbackSettings(cfg)
    }
  );
  ctx.subscriptions.push(vscode.workspace.onDidChangeConfiguration(event => {
    if (event.affectsConfiguration('cyclomaticLsp')) {
      const settings = getFeedbackSettings(vscode.workspace.getConfiguration('cyclomaticLsp'));
      if (client.isRunning()) {
        client.sendNotification('workspace/didChangeConfiguration', { settings });
      } else {
        pendingSettings = settings;
      }
    }
  }));
  client.start().then(() => {
    if (pendingSettings) {
      client.sendNotification('workspace/didChangeConfiguration', { settings: pendingSettings });
      pendingSettings = undefined;
    }
  });
};

exports.deactivate = async () => {
  if (client && client.isRunning()) {
    try { await client.stop(); } catch (_) { /* arrêt déjà en cours */ }
  }
};
