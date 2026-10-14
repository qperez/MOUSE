# Désinstalle l'extension VS Code et nettoie les artefacts de packaging (Windows).
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

$extId = 'irisa.cyclomatic-complexity-lsp'

if (Get-Command code -ErrorAction SilentlyContinue) {
    $installed = & code --list-extensions
    if ($installed -contains $extId) {
        & code --uninstall-extension $extId
        if ($LASTEXITCODE -ne 0) { throw "Échec de la désinstallation (code $LASTEXITCODE)" }
    } else {
        Write-Host "Extension $extId non installée."
    }
} else {
    Write-Host "Commande 'code' introuvable : désinstaller l'extension depuis VS Code."
}

$ext = 'vscode-extension'
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue `
    "$ext\server", "$ext\node_modules", "$ext\package-lock.json"
Remove-Item -Force -ErrorAction SilentlyContinue "$ext\*.vsix"

Write-Host "OK : redémarrer VS Code. Retirer aussi les settings 'cyclomaticLsp.*' si besoin."
