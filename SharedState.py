import Position, Orderbook, OrderManager, PolymarketWebSocketClient
import dotenv, os
from py_clob_client.constants import POLYGON
from py_clob_client.clob_types import ApiCreds
from py_clob_client.client import ClobClient

dotenv.load_dotenv("path")

PK= os.getenv("PK")
KEY= os.getenv("APIKEY")
SECRET= os.getenv("APISECRET")
PASSPHRASE= os.getenv("APIPASSPHRASE") 
BROWSER_WALLET= os.getenv("BROWSER_WALLET")
SOLANA_MARKET=os.getenv("SOLANA_MARKET")
FUNDER=os.getenv("FUNDER")

host = "https://clob.polymarket.com"
creds = ApiCreds(api_key=KEY, api_secret=SECRET, api_passphrase=PASSPHRASE)
client = ClobClient(host, key=PK, chain_id=POLYGON,funder=FUNDER,signature_type=1,creds=creds)
clientws = PolymarketWebSocketClient.PolymarketWebSocketClient(api_key=KEY, secret=SECRET, passphrase=PASSPHRASE)

sol_market = client.get_market(SOLANA_MARKET)
sol_y_token=sol_market['tokens'][0]['token_id']
sol_n_token=sol_market['tokens'][1]['token_id']

orderbook = Orderbook.Orderbook()
ordermanager = OrderManager.OrderManager()
position = Position.Position(price=0,size=0)
