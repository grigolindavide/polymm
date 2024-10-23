import os
import dotenv
import py_clob_client as ClobClient
import OrderManager
from py_clob_client.constants import POLYGON
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds,  OrderBookSummary, BookParams, TradeParams, OrderArgs
from py_clob_client.order_builder.constants import BUY,SELL

def main():
    dotenv.load_dotenv()
    KEY= os.getenv("APIKEY")
    SECRET= os.getenv("APISECRET")
    PASSPHRASE= os.getenv("APIPASSPHRASE") 
    BROWSER_WALLET= os.getenv("BROWSER_WALLET")

    host = "https://clob.polymarket.com"

    creds = ApiCreds(
        api_key=KEY,
        api_secret=SECRET,
        api_passphrase=PASSPHRASE)
    client = ClobClient(host, key=KEY, chain_id=POLYGON,funder=BROWSER_WALLET,signature_type=1,creds=creds)

    ordermanager= OrderManager.OrderManager(client)

    sol_market = client.get_market(os.getenv("SOLANA_MARKET"))

    sol_y_token=sol_market['tokens'][0]['token_id']
    sol_n_token=sol_market['tokens'][1]['token_id']

    sol_orderbooks=client.get_order_books([BookParams(token_id=sol_y_token),BookParams(token_id=sol_n_token)])

    mid_buy_sol=client.get_midpoint(sol_y_token)
    mid_sell_sol=client.get_midpoint(sol_n_token)

    spread_buy_sol=client.get_spread(sol_y_token)
    spread_sell_sol=client.get_spread(sol_n_token)

    price_y = calculate_y_price()
    price_n = calculate_n_price()
    size_y = calculate_y_size()
    size_n = calculate_n_size()

    buy_y_order=ordermanager.send_order(price_y[0],size_y[0],BUY,sol_y_token)
    sell_y_order=ordermanager.send_order(price_y[0],size_y[1],SELL,sol_y_token)
    buy_n_order=ordermanager.send_order(price_n[0],size_n[0],BUY,sol_n_token)
    sell_n_order=ordermanager.send_order(price_n[0],size_n[1],SELL,sol_n_token)
    
if __name__=="__main__":
    main()


# print(client.get_tick_size(token_id=""))

# client.get_trades(TradeParams(maker_address=client.get_address(),market="0xbc7669a91c6bcff77f64bbb28828827c1100b1fb83c60bf7622e1f1811884b73"))

# p=client.calculate_market_price(token_id="66986042915704659405667249936404738251540443890148695955274896115759200257900",side="buy",amount=10000)
# print(p)
