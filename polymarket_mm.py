import os, time
import dotenv, asyncio
import py_clob_client as ClobClient
import OrderManager, Pricer, Position 
import PolymarketWebSocketClient
from py_clob_client.constants import POLYGON
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, BookParams
from py_clob_client.order_builder.constants import BUY,SELL

async def main():
    ordermanager = OrderManager.OrderManager(client)
    pricer = Pricer.Pricer(client)

    asyncio.create_task(clientws.connect(channel_type="user"))
    asyncio.create_task(clientws.subscribe(channel_type="user", markets=[SOLANA_MARKET]))
    asyncio.create_task(clientws.subscribe(channel_type="markets", markets=[sol_y_token,sol_n_token]))
    asyncio.create_task(clientws.listen(channel_type="user", markets=[SOLANA_MARKET]))
    asyncio.create_task(clientws.listen(channel_type="markets", markets=[sol_y_token,sol_n_token]))

    sol_orderbooks = client.get_order_books([BookParams(token_id=sol_y_token), BookParams(token_id=sol_n_token)])

    price = pricer.calculate_price(sol_orderbooks[0], position_y, SOLANA_MARKET)
    size = pricer.calculate_size(sol_orderbooks[0], position_y)

    buy_orders = ordermanager.send_order(price[0], size[0], BUY, sol_y_token)
    print(f"Sent order buy at price: {price[0]} with size {size[0]}")
    sell_orders = ordermanager.send_order(price[1], size[1], BUY, sol_n_token)
    print(f"Sent order buy at price: {price[1]} with size {size[1]}")

async def run_trading_bot():
    while True:
        try:
            await main()
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"EXCEPTION: {e}")
            client.cancel_all()
            print("--- Deleted ALL orders ---")
            break



if __name__ == "__main__":

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

    ordermanager = OrderManager.OrderManager(client)
    sol_market = client.get_market(SOLANA_MARKET)
    sol_y_token=sol_market['tokens'][0]['token_id']
    sol_n_token=sol_market['tokens'][1]['token_id']

    position_y = Position.Position(price=0,size=0,token_id=sol_y_token)

    position_n = Position.Position(price=0,size=0,token_id=sol_n_token)
    
    asyncio.run(run_trading_bot())
    

def update_position(price, size, side, outcome):

    if outcome=="YES":
        position_y.update_position(price,size,side)

    elif outcome=="NO":
        position_n.update_position(price,size,side)

    else:
        raise Exception("outcome not recognized")

