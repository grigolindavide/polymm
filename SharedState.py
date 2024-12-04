import dotenv, os
import Orderbook, PolymarketWebSocketClient
from py_clob_client.constants import POLYGON
from py_clob_client.clob_types import ApiCreds
from py_clob_client.client import ClobClient
from Position import Position
from Pricer import Pricer
from OrderManager import OrderManager

dotenv.load_dotenv("C:\\Users\\farma\\Desktop\\python1\\polymm\\variable.env.txt")
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


orderbook_y = Orderbook.Orderbook()
orderbook_n = Orderbook.Orderbook()
ordermanager = OrderManager()
pricer = Pricer()
position_y = Position(price=0,size=0, token=sol_y_token)
position_n = Position(price=0,size=0, token=sol_n_token)
