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
  "cyclomaticLsp.serverJar": "",
  "cyclomaticLsp.javaPath": "java",
  "cyclomaticLsp.activeProfile": "vibration",
  "cyclomaticLsp.profiles": {
    "vibration": {
      "simple": {
        "thermal": { "enabled": false },
        "vibration": {
          "enabled": true,
          "durationMs": 200,
          "pwm": 30,
          "pulseCount": 1,
          "pulseDelayMs": 200
        },
        "mouseSpeed": { "enabled": false }
      },
      "moderate": {
        "thermal": { "enabled": false },
        "vibration": {
          "enabled": true,
          "durationMs": 200,
          "pwm": 50,
          "pulseCount": 2,
          "pulseDelayMs": 200
        },
        "mouseSpeed": { "enabled": false }
      },
      "high": {
        "thermal": { "enabled": false },
        "vibration": {
          "enabled": true,
          "durationMs": 200,
          "pwm": 70,
          "pulseCount": 3,
          "pulseDelayMs": 200
        },
        "mouseSpeed": { "enabled": false }
      },
      "veryHigh": {
        "thermal": { "enabled": false },
        "vibration": {
          "enabled": true,
          "durationMs": 200,
          "pwm": 90,
          "pulseCount": 3,
          "pulseDelayMs": 200
        },
        "mouseSpeed": { "enabled": false }
      }
    }
  }
}
```

`cyclomaticLsp.activeProfile` selects `vibration`, `thermal`, `mouse`, or `custom`.
Each profile has the four complexity bands: `simple` (1–5), `moderate` (6–10),
`high` (11–20), and `veryHigh` (21+). The complete JSON for all four profiles
is available as the default value of `cyclomaticLsp.profiles`; edit the profile
objects there to customize them independently.

The default `thermal` profile enables thermal feedback at 5 seconds per band,
with PWM values 50/100/150/200. The `mouse` profile enables mouse speed factors
1.0/0.8/0.6/0.4. The `custom` profile starts as a copy of `vibration`. Disabled
modalities only need their `enabled` flag; enabled thermal/vibration modalities
accept `durationMs` and `pwm` (0–255), vibration also accepts `pulseCount`
and `pulseDelayMs`, and mouse speed accepts a finite `factor` of at least 0.1.

On hover, the extension posts `feedbackSettings.activeProfile`, the matched
complexity `feedbackSettings.level`, and only that band's thermal, vibration,
and mouse-speed settings. Disabled modalities carry only `enabled: false`;
enabled modalities include their parameters. The method/class/signature/
complexity fields remain available to the GUI. Changing the selected profile
or its settings refreshes the current hover feedback. Existing
`cyclomaticLsp.feedback.levels.*` values continue to act as a fallback when no
profile JSON is configured.
