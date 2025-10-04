#!/usr/bin/env bash
set -e
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m nltk.downloader vader_lexicon
cp -n .env.example .env || true
python3 -m src.main --symbols-file sample_symbols.txt --once --no-telegram
echo "Edit .env with your tokens, then remove --no-telegram to send alerts."
