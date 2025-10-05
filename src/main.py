from __future__ import annotations
import os
try:
    from .logger import info, warn, err
except Exception:
    def info(msg): print(f"✅ {msg}")
    def warn(msg): print(f"⚠️ {msg}")
    def err(msg):  print(f"❌ {msg}")
MIN_CONF = float(os.getenv('CONFIDENCE_MIN', '70'))

from src.main import run_once as _run_once
_run_once(syms, send_whatsapp=True)
