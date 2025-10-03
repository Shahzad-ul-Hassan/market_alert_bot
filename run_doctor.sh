#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
# activate venv if present
if [ -d "venv" ]; then
  source venv/bin/activate || true
fi

# update pairs before doctor
python tools/update_pairs.py || true
echo "Pairs updated ✅"
echo "--------------------------------------------"

# run doctor (health + fix + optional online)
python tools/bot_doctor.py "$@"
