def run_once(symbols, send_whatsapp=True):
    info(f"Symbols: {', '.join(symbols)}")
    for sym in symbols:
        try:
            result = analyze_symbol(sym)
            if not result:
                continue
            msg, decision, conf = result
            print(msg)

            if send_whatsapp and should_alert(decision, conf, MIN_CONF):
                try:
                    send_whatsapp_alert(msg)
                except Exception as e:
                    err(f"WhatsApp send failed: {e}")
            else:
                print(f"ℹ️ Skipping {sym}: decision='{decision[:12]}...', confidence={conf:.1f}% (< {MIN_CONF:.1f}% یا neutral)")
        except KeyboardInterrupt:
            raise
        except Exception as e:
            err(f"Error analyzing {sym}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbols", default="", help="Comma-separated e.g. BTC-USD,ETH-USD")
    parser.add_argument("--symbols-file", default="sample_symbols.txt")
    parser.add_argument("--interval", type=int, default=1800)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    symbols = []
    if args.symbols_file and os.path.exists(args.symbols_file):
        with open(args.symbols_file) as f:
            symbols = [l.strip() for l in f if l.strip() and not l.strip().startswith("#")]
    if not symbols and args.symbols:
        symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    if not symbols:
        warn("No symbols found — using defaults BTC-USD,ETH-USD")
        symbols = ["BTC-USD", "ETH-USD"]

    if args.once:
        run_once(symbols, send_whatsapp=True)
    else:
        while True:
            run_once(symbols, send_whatsapp=True)
            time.sleep(max(60, args.interval))
