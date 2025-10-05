from __future__ import annotations
import os, time
from src.analysis import analyze_symbol
from src.whatsapp_alert import send_whatsapp_alert
from src.data_sources import load_symbols

def run_once(symbols, notify=True):
    for sym in symbols:
        print(f"\n🔍 Analyzing {sym} ...")
        try:
            result = analyze_symbol(sym)
            msg = (
                f"📊 *Market Alert*\n"
                f"Symbol: {sym}\n"
                f"Decision: {result['decision']}\n"
                f"Confidence: {result['confidence']}%\n"
                f"Entry: {result.get('entry')}\n"
                f"Stop-Loss: {result.get('stop_loss')}\n"
                f"Target: {result.get('target')}"
            )
            if notify:
                send_whatsapp_alert(msg)
        except Exception as e:
            print(f"❌ Error analyzing {sym}: {e}")

def main():
    symbols_file = os.getenv("SYMBOLS_FILE", "sample_symbols.txt")
    interval = int(os.getenv("INTERVAL", "1800"))
    notify = not bool(os.getenv("NO_TELEGRAM", False))

    if not os.path.exists(symbols_file):
        print(f"⚠️  Symbols file not found: {symbols_file}")
        return

    with open(symbols_file) as f:
        symbols = [s.strip() for s in f if s.strip()]

    while True:
        run_once(symbols, notify=notify)
        print(f"\n⏱ Waiting {interval} s before next run…\n")
        time.sleep(interval)

if __name__ == "__main__":
    main()
