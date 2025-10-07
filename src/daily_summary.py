"""
    enabled = os.getenv("DAILY_SUMMARY_ENABLED", "true").lower() in ("1","true","yes","on")
    if not enabled:
        return

    hour_pk = int(os.getenv("DAILY_SUMMARY_HOUR_PK", "21"))
    now = _now_pk()
    if now.hour != hour_pk:
        return

    guard = "/tmp/daily_summary_sent.txt"
    today = now.date().isoformat()
    try:
        if os.path.exists(guard):
            last = open(guard).read().strip()
            if last == today:
                return
    except Exception:
        pass

    msg, nb, ns, nn = build_daily_summary(symbols)
    try:
        send_func(msg)
        open(guard, "w").write(today)
    except Exception as e:
        print(f"❌ Daily summary send failed: {e}")
