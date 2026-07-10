#!/usr/bin/env python3
"""
Script de charge sysbench avec phases :
  1. Attente initiale    : 15s
  2. Phase 1 (1/2 threads) : 15s de charge
  3. Pause              : 30s
  4. Phase 2 (tous les threads) : 15s de charge
  5. Pause              : 30s
  6. Phase 3 (1/3 threads) : 15s de charge
  7. Pause              : 30s
  8. Fin
"""

import subprocess
import time
import os
import multiprocessing

# ── Détection du nombre de threads disponibles ──────────────────────────────
TOTAL_THREADS = multiprocessing.cpu_count()

HALF_THREADS  = max(1, TOTAL_THREADS // 2)
THIRD_THREADS = max(1, TOTAL_THREADS // 3)

# ── Helpers ──────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def wait(seconds: int, reason: str = "") -> None:
    label = f" ({reason})" if reason else ""
    log(f"Attente de {seconds}s{label}...")
    for remaining in range(seconds, 0, -1):
        print(f"\r  → {remaining:3d}s restantes ", end="", flush=True)
        time.sleep(1)
    print()


def run_sysbench(threads: int, duration: int, label: str) -> None:
    """Lance sysbench cpu en mode non-interactif."""
    log(f"[{label}] Démarrage — {threads} thread(s), durée {duration}s")
    cmd = [
        "sysbench",
        "cpu",
        f"--threads={threads}",
        f"--time={duration}",
        "run",
    ]
    log(f"  Commande : {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False, text=True)
    if result.returncode != 0:
        log(f"  ⚠  sysbench a retourné le code {result.returncode}")
    else:
        log(f"[{label}] Terminé.")


# ── Séquence principale ───────────────────────────────────────────────────────

def main() -> None:
    log("=" * 60)
    log("Script de charge sysbench")
    log(f"  Cœurs détectés      : {TOTAL_THREADS}")
    log(f"  Threads phase 1 (1/2) : {HALF_THREADS}")
    log(f"  Threads phase 2 (tout) : {TOTAL_THREADS}")
    log(f"  Threads phase 3 (1/3) : {THIRD_THREADS}")
    log("=" * 60)

    # ── 1. Attente initiale ──────────────────────────────────────────────────
    wait(15, "attente initiale")

    # ── 2. Phase 1 : moitié des threads, 15s ────────────────────────────────
    run_sysbench(HALF_THREADS, 30, "Phase 1 — moitié des threads")

    # ── 3. Pause 30s ────────────────────────────────────────────────────────
    wait(30, "pause")

    # ── 4. Phase 2 : tous les threads, 15s ──────────────────────────────────
    run_sysbench(TOTAL_THREADS, 30, "Phase 2 — tous les threads")

    # ── 5. Pause 30s ────────────────────────────────────────────────────────
    wait(30, "pause")

    # ── 6. Phase 3 : un tiers des threads, 15s ──────────────────────────────
    run_sysbench(THIRD_THREADS, 30, "Phase 3 — un tiers des threads")

    # ── 7. Pause finale 30s ─────────────────────────────────────────────────
    wait(30, "pause finale")

    log("=" * 60)
    log("Séquence terminée. Bonne journée !")
    log("=" * 60)


if __name__ == "__main__":
    main()