import dotenv, os
import numpy as np
import scipy.stats as stats
import polymarket_mm
from py_clob_client.clob_types import OrderBookSummary, BookParams, TradeParams, OrderArgs

dotenv.load_dotenv()
SOLANA_MARKET= os.getenv("SOLANA_MARKET")

class Pricer:
    def __init__(self, client):
        self.client = client

    def calculate_price(self,book,position,market_token):
        ba=float(book.asks[-1].price)
        bb=float(book.bids[-1].price)

        bias = self.calculateBias(position,bb,ba,market_token)

        buy = bb + bias
        sell= ba + bias
        return [buy,(1-sell)]
    
    def calculate_size(self,book,y_token):
        size_buy= 10
        size_sell= 10
        return [size_buy,size_sell]
    
    def calculateBias(self,position,bb,ba,market_token):
        '''
        returns: bias
        '''
        tick_size = self.client.get_market(market_token)['minimum_tick_size']
        b=0
        if position.size > 0:
            b = bb - tick_size*2
        elif position.size < 0:
            b = ba - tick_size*2 
        return b
    
    def handle_trade_message(self,message):
        """
        message: trade message
        """
        if message['market']==SOLANA_MARKET:
            polymarket_mm.update_position(message['price'],message['side'],message['side'],message['outcome'])
        else:
            raise Exception(f"received a message from an unexpected market: {message['market']} at time {message['matchtime']}")
        
        return 0
    
    def digital_option_price(S,K, r,T,t,sigma,call=True):
        """
        params:
        S: Current price of the underlying asset
        K: Strike price of the option
        T: Expiry date
        t: Current date
        r: Risk-free interest rate (decimal)
        sigma: Volatility of the underlying asset (decimal)
        call: True if call else False
        """
        d2 = (np.log(S/K) + (r-0.5*sigma**2)*(T-t)) / (sigma*np.sqrt(T-t))
        price = np.exp(-r*(T-t))*stats.norm.cdf(d2)
        return price if call else (1-price)
    
    def isSpreadEqualMinTick(self,bb,ba,market_token):
        '''
        bb: best bid 
        ba: best ask
        market_token: market token
        returns: True if the spread is equal to the min tick
        '''
        return self.client.get_market(market_token)['minimum_tick_size'] == (ba-bb)

