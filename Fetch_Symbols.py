# _______________________________________________________________________________________________________________________________________
# #######################        FUNCTION THAT CALLS THE API TO GET SUPPORTED EXCHANGES AND FUTURE MARKETS        #######################
# _______________________________________________________________________________________________________________________________________

import requests
import time
import csv
from datetime import datetime

API_KEY = "xxx"  # Replace with your actual API key
BASE_URL = "https://api.coinalyze.net/v1"
HEADERS = {"api_key": API_KEY}

def get_supported_future_markets():
    url = f"{BASE_URL}/future-markets"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    # Fetch filtered future markets
    futures = get_supported_future_markets()

    print("✅ BTC / ETH / SOL Futures Markets:\n")
    count = 0
    for market in futures:
        if market["base_asset"] in {"BTC", "ETH", "SOL"}:
            print(f"{market['symbol']} | Exchange: {market['exchange']} | Pair: {market['base_asset']}/{market['quote_asset']} | Perpetual: {market['is_perpetual']}")
            count += 1

    print(f"\nTotal Matches: {count}")
