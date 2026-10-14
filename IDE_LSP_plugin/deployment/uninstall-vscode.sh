#!/usr/bin/env bash
# Désinstalle l'extension VS Code et nettoie les artefacts de packaging.
set -euo pipefail
cd "$(dirname "$0")"

EXT_ID="irisa.cyclomatic-complexity-lsp"

if command -v code >/dev/null 2>&1; then
  if code --list-extensions | grep -qix "$EXT_ID"; then
    code --uninstall-extension "$EXT_ID"
  else
    echo "Extension $EXT_ID non installée."
  fi
else
  echo "Commande 'code' introuvable : désinstaller l'extension depuis VS Code."
fi

rm -rf vscode-extension/server vscode-extension/node_modules \
       vscode-extension/package-lock.json vscode-extension/*.vsix
echo "OK : redémarrer VS Code. Retirer aussi les settings 'cyclomaticLsp.*' si besoin."
