def analyze_symbol(symbol: str) -> Optional[tuple[str, str, float]]:
    """
    Analyze one symbol and return tuple:
      (pretty_message, decision_text, confidence_pct)
    Includes Decision, Risk, Trend, Confidence, and ATR-based Trade Levels.
    """
    info(f"Analyzing {symbol}...")

    # 1) Price data
    df = ds.fetch_price_history(symbol)
    if df is None:
        warn(f"No price data for {symbol}. Skipping.")
        return None

    # 2) Technicals
    tech = sg.compute_technicals(df)
    tech_signal = float(tech.get("signal", 0.0))
    rsi = tech.get("rsi", None)
    macd_hist = tech.get("macd_hist", 0.0)
    sma_trend = tech.get("sma_trend", 0.0)

    # 3) Sentiment
    sentiment = an.sentiment_from_texts(an.get_recent_news_and_tweets(symbol))

    # 4) Fundamentals
    fund = float(sg.fundamentals_to_score(symbol))

    # 5) Aggregate → Decision
    score = sg.aggregate_scores(
        tech_signal=tech_signal,
        sentiment=sentiment,
        fundamentals=fund,
    )
    decision = sg.decision_from_score(score)

    # 6) Risk
    risk = sg.risk_level_from_factors(
        tech_signal=tech_signal,
        sentiment=sentiment,
        fundamentals=fund,
    )

    # 7) Trend Summary
    try:
        if sma_trend > 0.02 and macd_hist > 0:
            trend_summary = "📊 *Trend:* Uptrend forming — buyers in control 💪"
            trend_agree = 1
        elif sma_trend < -0.02 and macd_hist < 0:
            trend_summary = "📊 *Trend:* Downtrend likely — sellers dominating 📉"
            trend_agree = 1
        else:
            trend_summary = "📊 *Trend:* Sideways / Consolidation — wait for breakout ⚖️"
            trend_agree = 0
    except Exception as e:
        trend_summary = f"⚠️ Trend analysis error: {e}"
        trend_agree = 0

    # 8) Confidence % (0–100)
    try:
        strength = min(1.0, abs(score))
        base_conf = 60.0 * strength
        trend_bonus = 20.0 * trend_agree
        sent_align = 1.0 if (score * sentiment) > 0 else 0.0
        sent_bonus = 15.0 * (sent_align * min(1.0, abs(sentiment)))
        rows = len(df)
        data_bonus = 10.0 if rows >= 120 else (5.0 if rows >= 60 else 0.0)
        confidence = max(0.0, min(100.0), round(base_conf + trend_bonus + sent_bonus + data_bonus, 1))
        conf_line = f"✅ *Confidence:* {confidence:.1f}%"
    except Exception as e:
        confidence = 0.0
        conf_line = f"⚠️ Confidence calc error: {e}"

    # 9) ATR-based Trade Levels (only for BUY/SELL, not for neutral)
    trade_levels = sg.compute_trade_levels(df, decision)
    if trade_levels:
        tl_lines = [
            f"🎯 *Entry:* {trade_levels['entry']}",
            f"🛡️ *Stop:* {trade_levels['stop']}",
            f"🎯 *TP1:* {trade_levels['tp1']} | 🎯 *TP2:* {trade_levels['tp2']}",
            f"🧮 ATR(14): {trade_levels['atr']} | R:R = {trade_levels['rr']} | {trade_levels['direction']}",
        ]
    else:
        tl_lines = []

    # 10) Build WhatsApp message
    lines = [
        f"📈 *{symbol}*",
        f"Tech Signal: {tech_signal:+.2f}",
        f"RSI: {rsi} | MACD Hist: {macd_hist} | SMA Trend: {sma_trend:+.2f}",
        f"Sentiment: {sentiment:+.2f} | Fundamentals: {fund:+.2f}",
        "",
        f"👉 Decision: {decision}",
        f"⚖️ Risk: {risk}",
        f"{trend_summary}",
        f"{conf_line}",
    ]
    if tl_lines:
        lines.append("")  # blank line
        lines.extend(tl_lines)

    return ("\n".join(lines), decision, confidence)
