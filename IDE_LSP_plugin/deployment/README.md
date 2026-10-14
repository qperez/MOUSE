# Déploiement du LSP Cyclomatic Complexity

Contenu :

| Fichier | Rôle |
|---|---|
| `cyclomatic-lsp.jar` | Serveur LSP (fat jar, Java 21+), communique en stdio |
| `vscode-extension/` | Client VS Code minimal qui lance le JAR |
| `install-vscode.sh` | Package + installation automatique de l'extension |
| `uninstall-vscode.sh` | Désinstalle l'extension et nettoie les artefacts |
| `install-vscode.ps1` / `.cmd` | Équivalent Windows de l'installation |
| `uninstall-vscode.ps1` / `.cmd` | Équivalent Windows de la désinstallation |
| `settings.example.windows.json` | Exemple de settings avec chemin Windows |
| `settings.example.json` | Exemple de settings VS Code |

## Prérequis
- Java 21+ (`java -version`)
- Node.js + npm
- VS Code avec la commande `code` dans le PATH

## 0. (Re)construire le JAR si besoin
```bash
cd ..            # racine IDE_LSP_plugin
mvn clean package
cp target/cyclomatic-lsp.jar deployment/
```

## 1. VS Code — installation automatique
```bash
cd deployment
./install-vscode.sh
```
Le script embarque le JAR dans l'extension (`server/cyclomatic-lsp.jar`), génère le `.vsix` et l'installe.
Redémarrer VS Code, ouvrir un `.java`, survoler une méthode.

## 2. VS Code — installation manuelle
```bash
cd deployment/vscode-extension
mkdir -p server && cp ../cyclomatic-lsp.jar server/
npm install
npx @vscode/vsce package --allow-missing-repository --skip-license
code --install-extension cyclomatic-complexity-lsp-1.0.0.vsix
```

## 3. VS Code — mode développement (sans packager)
```bash
cd deployment/vscode-extension
npm install
code .
```
Appuyer sur **F5** (config `Run Extension`), puis dans la nouvelle fenêtre mettre dans les settings
le contenu de `settings.example.json` (adapter le chemin du JAR).

## Windows
Prérequis : Java 21+, Node.js, VS Code (`code` dans le PATH), PowerShell 5.1+.
```powershell
cd deployment
.\install-vscode.cmd      # ou : powershell -ExecutionPolicy Bypass -File .\install-vscode.ps1
.\uninstall-vscode.cmd    # désinstallation
```
Les `.cmd` lancent les `.ps1` avec `-ExecutionPolicy Bypass` (évite le blocage des scripts non signés).

## Désinstallation
```bash
./uninstall-vscode.sh
```
Supprime l'extension (`irisa.cyclomatic-complexity-lsp`) et nettoie `server/`, `node_modules/` et les `.vsix`.

## Configuration
| Setting | Défaut | Description |
|---|---|---|
| `cyclomaticLsp.serverJar` | `""` | Chemin du JAR ; vide = JAR embarqué |
| `cyclomaticLsp.javaPath` | `java` | Exécutable Java (chemin complet si hors PATH) |

## Dépannage
- **« JAR introuvable »** : renseigner `cyclomaticLsp.serverJar` ou relancer `install-vscode.sh`.
- **Rien au survol** : *View → Output → Cyclomatic LSP* pour les logs ; vérifier `java -version` ≥ 21.
- **Test du JAR seul** : `java -jar cyclomatic-lsp.jar` doit rester en attente sur stdin (Ctrl+C pour quitter).
- Ne jamais écrire sur stdout dans le serveur (réservé au protocole LSP).

## IntelliJ (aperçu)
Installer le plugin **LSP4IJ** → *Language Servers* → **+** → commande
`java -jar /chemin/vers/deployment/cyclomatic-lsp.jar`, mapping `*.java` → languageId `java`.
