const path = require('path');
const fs = require('fs');
const http = require('http');
const vscode = require('vscode');
const { LanguageClient } = require('vscode-languageclient/node');

let client;
let configurationListener;

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

function enableComplexityGuiMode() {
  return new Promise((resolve) => {
    const request = http.get('http://localhost:5000/metric/gui?start=1', (response) => {
      response.resume();
      if (response.statusCode < 200 || response.statusCode >= 300) {
        showGuiModeRetryWarning(
          `Cyclomatic LSP started, but M5 complexity mode could not be enabled (HTTP ${response.statusCode}).`
        );
      }
      resolve();
    });

    request.setTimeout(5000, () => {
      request.destroy(new Error('Request timed out'));
    });
    request.on('error', (error) => {
      showGuiModeRetryWarning(
        `Cyclomatic LSP started, but M5 complexity mode could not be enabled: ${error.message}`
      );
      resolve();
    });
  });
}

function showGuiModeRetryWarning(message) {
  vscode.window.showWarningMessage(message, 'Retry').then((action) => {
    if (action === 'Retry') {
      enableComplexityGuiMode();
    }
  });
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
  configurationListener = vscode.workspace.onDidChangeConfiguration(event => {
    if (event.affectsConfiguration('cyclomaticLsp')) {
      const settings = getFeedbackSettings(vscode.workspace.getConfiguration('cyclomaticLsp'));
      if (client.isRunning()) {
        client.sendNotification('workspace/didChangeConfiguration', { settings })
          .catch(error => {
            vscode.window.showWarningMessage(
              `Cyclomatic LSP could not apply updated feedback settings: ${error.message}`
            );
          });
      } else {
        pendingSettings = settings;
      }
    }
  });
  ctx.subscriptions.push(configurationListener);
  client.start().then(() => {
    if (pendingSettings) {
      client.sendNotification('workspace/didChangeConfiguration', { settings: pendingSettings })
        .catch(error => {
          vscode.window.showWarningMessage(
            `Cyclomatic LSP could not apply updated feedback settings: ${error.message}`
          );
        });
      pendingSettings = undefined;
    }
    return enableComplexityGuiMode();
  }).catch(error => {
    vscode.window.showErrorMessage(`Cyclomatic LSP failed to start: ${error.message}`);
  });
};

exports.deactivate = async () => {
  if (configurationListener) {
    configurationListener.dispose();
    configurationListener = undefined;
  }
  if (client && client.isRunning()) {
    try { await client.stop(); } catch (_) { /* arrêt déjà en cours */ }
  }
};
