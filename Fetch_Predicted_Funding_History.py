# run a virtual environment with these commands:
# python3 -m venv venv
# source venv/bin/activate
# pip install requests
# Save this file as `Predicted_Funding_Rate.py` and run it with

import requests
import time
import csv
from datetime import datetime

API_KEY = "xxx"  # Replace with your actual API key
BASE_URL = "https://api.coinalyze.net/v1"
HEADERS = {"api_key": API_KEY}

# LIST OF SUPPORTED EXCHANGES
EXCHANGE_CODES = {
    "A": "binance",
    "B": "bitstamp",
    "C": "coinbase",
    "D": "bitforex",
    "E": "mercadobitcoin",
    "F": "bitfinex",
    "G": "gemini",
    "H": "hyperliquid",
    "I": "bit2c",
    "J": "luno",
    "K": "kraken",
    "L": "bitflyer",
    "M": "btcmarkets",
    "N": "independentreserve",
    "P": "poloniex",
    "U": "bithumb",
    "V": "vertex",
    "W": "woo",
    "Y": "gateio",
    "0": "bitmex",
    "2": "deribit",
    "3": "okx",
    "4": "huobi",
    "6": "bybit",
    "7": "phemex",
    "8": "dydx"
}

# BTC Perpetual Futures: stablecoin + inverse
symbols = [
    "BTCUSDT_PERP.A",   # Binance (USDT)
    "BTCUSDC_PERP.A",   # Binance (USDC)
    "BTCUSD_PERP.0",    # BitMEX (BTC)
    "BTCUSDT_PERP.0",   # BitMEX (USDT)
    "BTCUSDT_PERP.F",   # Bitfinex (USDT)
    "BTCUSD_PERP.F",    # Bitfinex (BTC)
    "BTCUSDT.6",        # Bybit (USDT) ✅ correct now
    "BTCUSD.6",         # Bybit (BTC)
    "BTCUSDT_PERP.4",   # Huobi (USDT)
    "BTCUSD_PERP.4",    # Huobi (BTC)
    "BTCUSDT_PERP.3",   # OKX (USDT)
    "BTCUSDC_PERP.3",   # OKX (USDC)
    "BTCUSD_PERP.3",    # OKX (BTC)
    "PERP_BTC_USDT.W",  # WOO X (USDT)
    "BTC_USDT.Y",       # Gate.io (USDT)
    "BTC.H"             # Hyperliquid (USD)
]

# FUNCTION TO CONVERT DATE TO UNIX TIMESTAMP 
def to_unix(year, month, day):
    return int(datetime(year, month, day).timestamp())

# FUNCTION TO PARSE SYMBOLS AND EXTRACT BASE, EXCHANGE, AND MARGIN
def parse_symbol(symbol_str):
    exchange_code = symbol_str.split(".")[-1]
    exchange_name = EXCHANGE_CODES.get(exchange_code, exchange_code)

    # Special case: Hyperliquid "BTC.H"
    if symbol_str == "BTC.H":
        return "BTCUSD", exchange_name, "USD"

    # Special case: WOO format "PERP_BTC_USDT.W"
    if "PERP_" in symbol_str and "_" in symbol_str:
        parts = symbol_str.split("_")
        if len(parts) == 3:
            base = parts[1].upper()
            quote = parts[2].split(".")[0].upper()
            sym = f"{base}{quote}"
            margin = quote
            return sym, exchange_name, margin

    # Special case: Bybit format "BTCUSDT.6" or "BTCUSD.6"
    if exchange_code == "6" and "." in symbol_str and "_" not in symbol_str:
        base_quote = symbol_str.split(".")[0]
        if "USD" in base_quote:
            base = "BTC"
            if "USDT" in base_quote:
                margin = "USDT"
                sym = "BTCUSD"
            elif "USDC" in base_quote:
                margin = "USDC"
                sym = "BTCUSD"
            elif "USD" in base_quote:
                margin = "BTC"
                sym = "BTCUSD"
            else:
                margin = "UNKNOWN"
                sym = base_quote
            return sym, exchange_name, margin

    # Standard case
    base = symbol_str.split("_")[0].replace("PERP", "").replace("PERPETUAL", "").upper()

    if "USDT" in symbol_str:
        margin = "USDT"
    elif "USDC" in symbol_str:
        margin = "USDC"
    elif "USD" in symbol_str:
        margin = "BTC"
    else:
        margin = "UNKNOWN"

    return base, exchange_name, margin

# CALL API
def get_predicted_funding_rate_history(symbols, interval, from_ts, to_ts):
    url = f"{BASE_URL}/predicted-funding-rate-history"
    params = {
        "symbols": ",".join(symbols),
        "interval": interval,
        "from": from_ts,
        "to": to_ts
    }
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

# MAIN LOGIC
if __name__ == "__main__":
    interval = "daily"      # "1min" "5min" "15min" "30min" "1hour" "2hour" "4hour" "6hour" "12hour" "daily"
    from_ts = to_unix(2021, 1, 1)
    to_ts = to_unix(2025, 5, 27)
    output_file = "BTC_Predicted_Funding_Rate_History.csv"

    print(f"📡 Fetching predicted funding rate history for: {symbols}")
    data = get_predicted_funding_rate_history(symbols, interval, from_ts, to_ts)

    with open(output_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["date", "sym", "ecn", "margin", "open", "high", "low", "close", "raw_symbol"])

        for market in data:
            raw_symbol = market["symbol"]
            sym, ecn, margin = parse_symbol(raw_symbol)
            for row in market["history"]:
                date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row["t"]))
                writer.writerow([date, sym, ecn, margin, row["o"], row["h"], row["l"], row["c"], raw_symbol])

    print(f"\n✅ CSV file written to {output_file}")
