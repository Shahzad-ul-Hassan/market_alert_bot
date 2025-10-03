#!/bin/bash
cd ~/Desktop/market_alert_bot
source venv/bin/activate
python3 -m src.main --symbols-file sample_symbols.txt --once

