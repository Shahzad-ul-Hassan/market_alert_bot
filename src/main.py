sed -i '' '1i\
def info(msg): print(f"✅ {msg}")\ndef warn(msg): print(f"⚠️ {msg}")\ndef err(msg): print(f"❌ {msg}")\
' main.py
def analyze_symbol(symbol):
    """
    Full market analysis with:
    - Decision, Risk, Trend, Confidence
    - ATR-based Entry/Stops/Targets
    - Trailing Stop + Reversal Probability
    Returns: (message_str, decision_text, confidence_pct)
    """
    info(f"Analyzing {symbol}...")

    # Price Data
    df = ds.fetch_price_history(symbol)
    if df is None:
        warn(f"No price data for {symbol}.")
        return None

    tech = sg.compute_technicals(df)
    tech_signal = float(tech.get("signal", 0.0))
    rsi = tech.get("rsi", None)
    macd_hist = tech.get("macd_hist", 0.0)
    sma_trend = tech.get("sma_trend", 0.0)

    sentiment = an.sentiment_from_texts(an.get_recent_news_and_tweets(symbol))
    fund = float(sg.fundamentals_to_score(symbol))

    score = sg.aggregate_scores(tech_signal, sentiment, fund)
    decision = sg.decision_from_score(score)
    risk = sg.risk_level_from_factors(tech_signal, sentiment, fund)

    # Trend
    if sma_trend > 0.02 and macd_hist > 0:
        trend_summary = "📊 Uptrend forming — buyers in control 💪"
        trend_agree = 1
    elif sma_trend < -0.02 and macd_hist < 0:
        trend_summary = "📊 Downtrend likely — sellers dominating 📉"
        trend_agree = 1
    else:
        trend_summary = "⚖️ Sideways / Consolidation"
        trend_agree = 0

    # Confidence %
    strength = min(1.0, abs(score))
    base_conf = 60.0 * strength
    trend_bonus = 20.0 * trend_agree
    rows = len(df)
    data_bonus = 10.0 if rows >= 120 else (5.0 if rows >= 60 else 0.0)
    confidence = max(0.0, min(100.0, round(base_conf + trend_bonus + data_bonus, 1)))

    # Trade Levels + trailing + reversal prob
    trade = sg.compute_trade_levels(df, decision)
    levels = []
    if trade:
        trail = sg.compute_trailing_stop(float(df["Close"].iloc[-1]), trade)
        rev_prob = sg.compute_reversal_probability(df, decision)
        levels += [
            f"🎯 Entry: {trade['entry']}",
            f"🛡️ Stop: {trade['stop']}",
            f"🎯 TP1: {trade['tp1']} | 🎯 TP2: {trade['tp2']}",
            f"🧮 ATR(14): {trade['atr']} | {trade['direction']} | R:R {trade['rr']}",
        ]
        if trail:
            levels.append(f"📉 Trailing Stop (live): {trail}")
        if rev_prob is not None:
            levels.append(f"🔄 *Reversal Probability:* {rev_prob:.1f}%")

    msg = "\n".join([
        f"📈 *{symbol}*",
        f"Tech Signal: {tech_signal:+.2f} | RSI: {rsi} | MACD: {macd_hist:.4f}",
        f"Sentiment: {sentiment:+.2f} | Fundamentals: {fund:+.2f}",
        f"👉 Decision: {decision}",
        f"⚖️ Risk: {risk}",
        f"{trend_summary}",
        f"✅ Confidence: {confidence:.1f}%",
        "",
        *levels
    ])
    return msg, decision, confidence
