import SharedState
import numpy as np
import scipy.stats as stats

class Pricer:
        
    def calculate_price(self, market_token):

        best_bid_n=float(SharedState.orderbook_n.get_best_bid()["price"])
        best_bid_y=float(SharedState.orderbook_y.get_best_bid()["price"])
        best_ask_n=float(SharedState.orderbook_n.get_best_ask()["price"])
        best_ask_y=float(SharedState.orderbook_y.get_best_ask()["price"])

        tick_size = SharedState.client.get_market(market_token)['minimum_tick_size']

        if abs(tick_size - (best_ask_y - best_bid_y)) < 1e-6:
            print("Spread yes is equal to 1 tick")
            price_y = best_ask_y 
        else:
            print("Spread yes is greater than 2 ticks")
            price_y = best_bid_y + tick_size

        if abs(tick_size - (best_ask_n - best_bid_n)) < 1e-6:
            print("Spread no is equal to 1 tick")
            price_n = best_ask_n
        else:   
            print("Spread no is greater than 2 ticks")
            price_n = best_bid_n + tick_size
        
        if SharedState.position_y.isInPosition:
            return [price_y, best_bid_n - tick_size]
        elif SharedState.position_n.isInPosition:
            return [best_bid_y - tick_size, price_n]
        else:
            return [price_y, price_n]
        
    
    def calculate_size(self):
        size_buy= 5
        size_sell= 5
        return [size_buy,size_sell]
    

    def isSpreadEqualMinTick(self,bb,ba,market_token):
        '''
        bb: best bid 
        ba: best ask
        market_token: market token
        returns: True if the spread is equal to the min tick
        '''
        return SharedState.client.get_market(market_token)['minimum_tick_size'] == (ba-bb)
    
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

