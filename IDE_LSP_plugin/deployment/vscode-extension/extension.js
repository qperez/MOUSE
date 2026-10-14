const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const { LanguageClient } = require('vscode-languageclient/node');

let client;

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
    { documentSelector: [{ scheme: 'file', language: 'java' }] }
  );
  client.start();
};

exports.deactivate = async () => {
  if (client && client.isRunning()) {
    try { await client.stop(); } catch (_) { /* arrêt déjà en cours */ }
  }
};
