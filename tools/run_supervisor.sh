#!/usr/bin/env bash
set -euo pipefail

SYMS_FILE="${SYMBOLS_FILE:-sample_symbols.txt}"
INTERVAL_SEC="${INTERVAL:-1800}"

echo "[supervisor] Starting bot with SYMS_FILE=$SYMS_FILE, INTERVAL=$INTERVAL_SEC"

# Exponential backoff (max 5min)
backoff=5
while true; do
  echo "[supervisor] Launching bot at $(date -u '+%Y-%m-%d %H:%M:%S') UTC"
  set +e
  python3 -m src.main --symbols-file "$SYMS_FILE" --interval "$INTERVAL_SEC"
  exit_code=$?
  set -e

  echo "[supervisor] Bot exited with code $exit_code"
  # If it exited cleanly, restart after normal interval; else backoff
  if [ "$exit_code" -eq 0 ]; then
    sleep "$INTERVAL_SEC"
    backoff=5
  else
    echo "[supervisor] Crash detected, sleeping $backoff sec then retry…"
    sleep "$backoff"
    # grow backoff until 300s
    backoff=$(( backoff < 300 ? backoff*2 : 300 ))
  fi
done
