# Cyclomatic Complexity LSP — Java + PMD + VSCode

Un serveur LSP écrit en Java qui calcule la **complexité cyclomatique** de vos méthodes Java via **PMD**, et l'affiche directement dans VSCode au survol de la souris.

## Prérequis

- Java 21+
- Maven 3.8+
- VSCode avec l'extension Java (optionnel mais recommandé)
- Node.js (pour packager l'extension)

## Build & Installation

### 1. Compiler le serveur LSP

```bash
cd cyclomatic-lsp
mvn clean package
```

Cela génère `target/cyclomatic-lsp.jar` (fat jar avec toutes les dépendances).

### 2. Tester le serveur

```bash
mvn test
```

### 3. Installer l'extension VSCode

#### Option A — Mode développement (recommandé pour tester)

1. Ouvrir VSCode dans le dossier `.vscode-extension/` :
   ```bash
   cd .vscode-extension
   npm install
   code .
   ```

2. Appuyer sur `F5` pour lancer une instance de VSCode avec l'extension chargée.

3. Dans la nouvelle fenêtre VSCode, configurer le chemin du JAR dans les settings :
   ```json
   // .vscode/settings.json
   {
     "cyclomaticLsp.serverJar": "/chemin/absolu/vers/target/cyclomatic-lsp.jar",
     "cyclomaticLsp.javaPath": "java"
   }
   ```

#### Option B — Packager en `.vsix`

```bash
cd .vscode-extension
npm install
npm install -g @vscode/vsce
vsce package
# Génère cyclomatic-complexity-lsp-1.0.0.vsix
```

Installer dans VSCode :
```bash
code --install-extension cyclomatic-complexity-lsp-1.0.0.vsix
```

## Utilisation

1. Ouvrir un fichier `.java` dans VSCode.
2. **Survoler** n'importe quelle méthode avec la souris → une infobulle apparaît avec :
   - Le nom et la signature de la méthode
   - La complexité cyclomatique (entier)
   - Un niveau de risque coloré
3. Les méthodes avec complexité > 10 apparaissent aussi dans le panneau **Problèmes**.

## Niveaux de complexité (McCabe)

| Complexité | Niveau       | Icône | Signification                              |
|-----------|--------------|-------|--------------------------------------------|
| 1–5       | Simple       | ✅    | Facile à tester et maintenir               |
| 6–10      | Modéré       | ⚠️    | Acceptable, à surveiller                   |
| 11–20     | Élevé        | 🔴    | Difficile à tester, refactoring conseillé  |
| 21+       | Très élevé   | ☠️    | Impossible à tester correctement           |

## Configuration VSCode

```json
{
  "cyclomaticLsp.serverJar": "",        // Chemin vers le JAR (auto-détecté si vide)
  "cyclomaticLsp.javaPath": "java",     // Chemin vers l'exécutable Java
  "cyclomaticLsp.feedback.levels.moderate.vibration.enabled": true,
  "cyclomaticLsp.feedback.levels.moderate.vibration.pwm": 50,
  "cyclomaticLsp.feedback.levels.high.mouseSpeed.enabled": true,
  "cyclomaticLsp.feedback.levels.high.mouseSpeed.factor": 0.8
}
```

Les réglages `cyclomaticLsp.feedback.levels` couvrent les bandes existantes :
`simple` (1–5), `moderate` (6–10), `high` (11–20) et `veryHigh` (21+).
Chaque bande permet d'activer/désactiver séparément le retour thermique,
vibratoire et de vitesse de souris. Les paramètres thermiques et vibratoires
utilisent une durée en millisecondes et une valeur PWM de 0 à 255 ; la vibration
ajoute le nombre d'impulsions et leur délai. Le facteur de souris est un
multiplicateur (1 est neutre). Par défaut, la vibration conserve les valeurs
historiques (PWM 30/50/70/90, 1/2/3/3 impulsions) et les deux autres modalités
sont désactivées.
