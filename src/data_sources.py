# src/data_sources.py
import yfinance as yf
import pandas as pd

# --- Robust Price Fetch Helper ---
def fetch_price_history(symbol: str,
                        periods=("6mo", "3mo", "1mo", "5d"),
                        interval="1d") -> pd.DataFrame | None:
    """
    مختلف periods سے price history fetch کرے گا۔
    اگر ایک empty ہو تو اگلا period ٹرائی کرے گا۔
    """
    for p in periods:
        try:
            df = yf.Ticker(symbol).history(period=p, interval=interval, auto_adjust=True, actions=False)
            if df is not None and not df.empty and "Close" in df.columns:
                df = df.rename(columns=str.lower)  # Close → close, Volume → volume
                return df
            else:
                print(f"[WARN] Empty history for {symbol} period={p}, trying next…")
        except Exception as e:
            print(f"[WARN] yfinance error for {symbol} period={p}: {e}. Trying next…")
    print(f"[WARN] No price data found for {symbol} after all fallbacks.")
    return None


# --- Example Usage ---
if __name__ == "__main__":
    test_symbol = "BTC-USD"
    df = fetch_price_history(test_symbol)
    if df is not None:
        print(df.tail())
    else:
        print("No data found.")
