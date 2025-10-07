# --- Example Usage ---
if __name__ == "__main__":
    test_symbol = "BTC-USD"
    df = fetch_price_history(test_symbol)
    if df is not None:
        print(df.tail())
    else:
        print("No data found.")
