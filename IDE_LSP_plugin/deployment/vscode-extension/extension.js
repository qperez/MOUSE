const path = require('path');
const fs = require('fs');
const http = require('http');
const vscode = require('vscode');
const { LanguageClient } = require('vscode-languageclient/node');

let client;
let configurationListener;

function getFeedbackSettings(configuration) {
  return {
    activeProfile: configuration.get('activeProfile'),
    profiles: configuration.get('profiles')
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
