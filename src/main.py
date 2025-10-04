def analyze_symbol(symbol: str) -> Optional[str]:
    """
    One-symbol analysis → returns a pretty WhatsApp-friendly message
    including Decision + Risk line.
    """
    info(f"Analyzing {symbol}...")

    # 1) Price data
    df = ds.fetch_price_history(symbol)
    if df is None:
        warn(f"No price data for {symbol}. Skipping.")
        return None

    # 2) Technicals (RSI/MACD/SMA trend + combined 'signal')
    tech = sg.compute_technicals(df)
    tech_signal = float(tech.get("signal", 0.0))

    # 3) News/Twitter sentiment (safe default 0.0 inside impl)
    sentiment = an.sentiment_from_texts(an.get_recent_news_and_tweets(symbol))

    # 4) Fundamentals mock/real (safe default inside)
    fund = float(sg.fundamentals_to_score(symbol))

    # 5) Aggregate final score → Decision
    score = sg.aggregate_scores(
        tech_signal=tech_signal,
        sentiment=sentiment,
        fundamentals=fund,
    )
    decision = sg.decision_from_score(score)

    # 6) Risk level (NEW)
    risk = sg.risk_level_from_factors(
        tech_signal=tech_signal,
        sentiment=sentiment,
        fundamentals=fund,
    )

    # 7) Build pretty message (WhatsApp friendly)
    lines = [
        f"📈 *{symbol}*",
        f"Tech Signal: {tech_signal:+.2f}",
        f"RSI: {tech.get('rsi', None)} | MACD Hist: {tech.get('macd_hist', None)} | SMA Trend: {tech.get('sma_trend', 0.0):+.2f}",
        f"Sentiment: {sentiment:+.2f} | Fundamentals: {fund:+.2f}",
        "",
        f"👉 Decision: {decision}",
        f"⚖️ Risk: {risk}",
    ]
    return "\n".join(lines)
