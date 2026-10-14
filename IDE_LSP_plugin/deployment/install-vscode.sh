#!/usr/bin/env bash
# Package et installe l'extension VS Code (JAR embarqué).
set -euo pipefail
cd "$(dirname "$0")"

JAR="cyclomatic-lsp.jar"
[ -f "$JAR" ] || { echo "Absent : $JAR (lancer 'mvn clean package' puis le copier ici)"; exit 1; }

mkdir -p vscode-extension/server
cp "$JAR" vscode-extension/server/

cd vscode-extension
npm install
npx --yes @vscode/vsce package --allow-missing-repository --skip-license -o cyclomatic-complexity-lsp.vsix
code --install-extension cyclomatic-complexity-lsp.vsix --force
echo "OK : redémarrer VS Code puis ouvrir un fichier .java"
