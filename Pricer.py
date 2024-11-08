import SharedState
import numpy as np
import scipy.stats as stats
from py_clob_client.clob_types import OrderBookSummary, BookParams, TradeParams, OrderArgs

class Pricer:
    def __init__(self, client):
        self.client = client

    def calculate_price(self, market_token):
        ba=float(SharedState.orderbook.get_best_ask()["price"])
        bb=float(SharedState.orderbook.get_best_bid()["price"])

        bias = self.calculateBias(bb,ba,market_token)

        buy = bb + bias
        sell= ba + bias
        return [buy,(1-sell)]
    
    def calculate_size(self,book,y_token):
        size_buy= 10
        size_sell= 10
        return [size_buy,size_sell]
    
    def calculateBias(self,bb,ba,market_token):
        '''
        returns: bias
        '''
        tick_size = self.client.get_market(market_token)['minimum_tick_size']
        b=0
        if SharedState.position.size > 0:
            b = bb - tick_size*2
        elif SharedState.position.size < 0:
            b = ba - tick_size*2 
        return b
    
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

