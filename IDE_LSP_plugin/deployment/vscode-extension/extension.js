const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const { LanguageClient } = require('vscode-languageclient/node');

let client;

const feedbackDefaults = {
  simple: {
    thermal: { enabled: false, durationMs: 1000, pwm: 100 },
    vibration: { enabled: true, durationMs: 200, pwm: 30, pulseCount: 1, pulseDelayMs: 200 },
    mouseSpeed: { enabled: false, factor: 1 }
  },
  moderate: {
    thermal: { enabled: false, durationMs: 1000, pwm: 100 },
    vibration: { enabled: true, durationMs: 200, pwm: 50, pulseCount: 2, pulseDelayMs: 200 },
    mouseSpeed: { enabled: false, factor: 1 }
  },
  high: {
    thermal: { enabled: false, durationMs: 1000, pwm: 100 },
    vibration: { enabled: true, durationMs: 200, pwm: 70, pulseCount: 3, pulseDelayMs: 200 },
    mouseSpeed: { enabled: false, factor: 1 }
  },
  veryHigh: {
    thermal: { enabled: false, durationMs: 1000, pwm: 100 },
    vibration: { enabled: true, durationMs: 200, pwm: 90, pulseCount: 3, pulseDelayMs: 200 },
    mouseSpeed: { enabled: false, factor: 1 }
  }
};

function getFeedbackSettings(configuration) {
  const levels = {};
  for (const [levelName, defaults] of Object.entries(feedbackDefaults)) {
    const profile = {};
    for (const [modalityName, parameters] of Object.entries(defaults)) {
      profile[modalityName] = {};
      for (const [parameterName, defaultValue] of Object.entries(parameters)) {
        const setting = `feedback.levels.${levelName}.${modalityName}.${parameterName}`;
        profile[modalityName][parameterName] = configuration.get(setting, defaultValue);
      }
    }
    levels[levelName] = profile;
  }
  return { levels };
}

exports.activate = (ctx) => {
  const cfg = vscode.workspace.getConfiguration('cyclomaticLsp');
  const java = cfg.get('javaPath') || 'java';
  const jar = cfg.get('serverJar') || path.join(ctx.extensionPath, 'server', 'cyclomatic-lsp.jar');

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
      initializationOptions: { feedback: getFeedbackSettings(cfg) },
      synchronize: { configurationSection: 'cyclomaticLsp' }
    }
  );
  client.start();
};

exports.deactivate = async () => {
  if (client && client.isRunning()) {
    try { await client.stop(); } catch (_) { /* arrêt déjà en cours */ }
  }
};
