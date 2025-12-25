import os
import dotenv

dotenv.load_dotenv(r"C:\Users\farma\Desktop\python1\polymm\variable.env.txt")

PK = os.getenv("PK")
API_KEY = os.getenv("APIKEY")
API_SECRET = os.getenv("APISECRET")
API_PASSPHRASE = os.getenv("APIPASSPHRASE")
BROWSER_WALLET = os.getenv("BROWSER_WALLET")
BITCOIN_MARKET = os.getenv("BITCOIN_MARKET")
ETHEREUM_MARKET = os.getenv("ETHEREUM_MARKET")
SOLANA_MARKET = os.getenv("SOLANA_MARKET")
FUNDER = os.getenv("FUNDER")

# You can set the market here
MARKET = ETHEREUM_MARKET

HOST = "https://clob.polymarket.com"
CHAIN_ID = 137  # Polygon

# Trading Parameters
MAX_INVENTORY_USD = 20.0      # Max position value in USD before entering unwind mode
BASE_ORDER_SIZE = 5.0         # Base order size in contracts
MIN_TICK_SIZE = 0.01          # Minimum price tick (will be overridden by market data)
QUOTE_SIDE = "YES"            # Which side to quote: "YES" or "NO"
