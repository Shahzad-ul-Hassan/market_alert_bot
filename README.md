# Market Next-Move Alert Bot (Python)

An end-to-end **alert bot** that blends **Fundamental**, **Sentiment (Twitter/News)**, and **Technical** signals to send **actionable alerts to Telegram**.

> ⚠️ You must provide your own API keys/tokens in a `.env` file (see `.env.example`).

## Features
- **Technical**: RSI, MACD, moving averages with `pandas` + `yfinance` + `ta`.
- **Sentiment**: News + Twitter text scored with VADER (or transformers, optional).
- **Fundamentals**: Simple valuation snapshot via `yfinance` (fallbacks included).
- **Aggregation**: Weighted scoring → Buy / Sell / Neutral.
- **Alerts**: Auto-send to Telegram chats.
- **Scheduler**: Run at intervals using APScheduler (or simple loop).

## Quick Start

1) **Python 3.10+** recommended. Create & activate a virtualenv:

```bash
python3 -m venv venv
source venv/bin/activate
```

2) **Install dependencies**

```bash
pip install -r requirements.txt
python -m nltk.downloader vader_lexicon
```

3) **Configure environment**

Copy `.env.example` → `.env` and fill values:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `NEWSAPI_KEY` *(optional but recommended)*
- `TWITTER_BEARER_TOKEN` *(optional)*

4) **Run**

```bash
python -m src.main --symbols-file sample_symbols.txt --interval-min 30
```
or
```bash
python -m src.main --symbols AAPL,MSFT,GOOG --once
```

## Notes
- Twitter/X API requires a **Bearer Token** for v2 endpoints.
- News requires a provider (e.g., **NewsAPI.org**). You can extend `data_sources.py` for other providers (GDELT, Finnhub, etc.).
- Fundamentals from `yfinance` can be spotty; code handles graceful fallbacks.
- Adjust weights/thresholds in `signals.py` to fit your strategy.
