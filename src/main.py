def analyze_symbol(symbol: str) -> Optional[str]:
    """
    One-symbol analysis → returns a pretty WhatsApp-friendly message
    including Decision, Risk, and Trend summary.
    """
    info(f"Analyzing {symbol}...")

    # 1) Fetch data
    df = ds.fetch_price_history(symbol)
    if df is None:
        warn(f"No price data for {symbol}. Skipping.")
        return None

    # 2) Technicals (RSI, MACD, SMA trend)
    tech = sg.compute_technicals(df)
    tech_signal = float(tech.get("signal", 0.0))

    # 3) Sentiment (from news & twitter)
    sentiment = an.sentiment_from_texts(an.get_recent_news_and_tweets(symbol))

    # 4) Fundamentals (mock or API-based)
    fund = float(sg.fundamentals_to_score(symbol))

    # 5) Aggregate overall score → Decision
    score = sg.aggregate_scores(
        tech_signal=tech_signal,
        sentiment=sentiment,
        fundamentals=fund,
    )
    decision = sg.decision_from_score(score)

    # 6) Risk level
    risk = sg.risk_level_from_factors(
        tech_signal=tech_signal,
        sentiment=sentiment,
        fundamentals=fund,
    )

    # 7) Trend Summary logic
    try:
        sma_trend = tech.get("sma_trend", 0.0)
        macd_hist = tech.get("macd_hist", 0.0)
        if sma_trend > 0.02 and macd_hist > 0:
            trend_summary = "📊 *Trend:* Uptrend forming — buyers in control 💪"
        elif sma_trend < -0.02 and macd_hist < 0:
            trend_summary = "📊 *Trend:* Downtrend likely — sellers dominating 📉"
        else:
            trend_summary = "📊 *Trend:* Sideways / Consolidation — wait for breakout ⚖️"
    except Exception as e:
        trend_summary = f"⚠️ Trend analysis error: {e}"

    # 8) Build WhatsApp message
    lines = [
        f"📈 *{symbol}*",
        f"Tech Signal: {tech_signal:+.2f}",
        f"RSI: {tech.get('rsi', None)} | MACD Hist: {tech.get('macd_hist', None)} | SMA Trend: {tech.get('sma_trend', 0.0):+.2f}",
        f"Sentiment: {sentiment:+.2f} | Fundamentals: {fund:+.2f}",
        "",
        f"👉 Decision: {decision}",
        f"⚖️ Risk: {risk}",
        f"{trend_summary}",
    ]
    return "\n".join(lines)
