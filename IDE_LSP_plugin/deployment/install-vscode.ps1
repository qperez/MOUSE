# Package et installe l'extension VS Code (JAR embarqué) sous Windows.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

function Invoke-Checked {
    param([string]$Cmd, [string[]]$CmdArgs)
    & $Cmd @CmdArgs
    if ($LASTEXITCODE -ne 0) { throw "Échec : $Cmd $($CmdArgs -join ' ') (code $LASTEXITCODE)" }
}

$jar = 'cyclomatic-lsp.jar'
if (-not (Test-Path $jar)) {
    throw "Absent : $jar (lancer 'mvn clean package' puis le copier ici)"
}
foreach ($tool in 'java', 'node', 'npm', 'code') {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        throw "Commande introuvable dans le PATH : $tool"
    }
}

New-Item -ItemType Directory -Force -Path 'vscode-extension\server' | Out-Null
Copy-Item $jar 'vscode-extension\server\' -Force

Push-Location 'vscode-extension'
try {
    Invoke-Checked 'npm' @('install')
    Invoke-Checked 'npx' @('--yes', '@vscode/vsce', 'package', '--allow-missing-repository', '--skip-license', '-o', 'cyclomatic-complexity-lsp.vsix')
    Invoke-Checked 'code' @('--install-extension', 'cyclomatic-complexity-lsp.vsix', '--force')
}
finally { Pop-Location }

Write-Host 'OK : redémarrer VS Code puis ouvrir un fichier .java'
