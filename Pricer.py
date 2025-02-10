import SharedState
import numpy as np
import scipy.stats as stats

class Pricer:
        
    def calculate_price(self, market_token):
        ba=float(SharedState.orderbook_n.get_best_bid()["price"])
        bb=float(SharedState.orderbook_y.get_best_bid()["price"])
        tick_size = SharedState.client.get_market(market_token)['minimum_tick_size']

        if abs(tick_size - (ba - bb)) < 1e-6:
            print("Spread is equal to 1 tick")
            if SharedState.position_y.isInPosition:
                return [ (bb + tick_size),  ba - tick_size]
            elif SharedState.position_n.isInPosition:
                return [bb - tick_size,  (ba + tick_size) ] 
            else:
                return [bb, ba]
        elif (ba-bb) > tick_size*2:
            print("Spread is greater than 2 ticks")
            if SharedState.position_y.isInPosition:
                return [SharedState.orderbook_y.get_best_ask()["price"] - tick_size,  ba]
            elif SharedState.position_n.isInPosition:
                return [bb, SharedState.orderbook_n.get_best_ask()["price"] - tick_size] 
            else:
                return [bb + tick_size,  ba - tick_size]
        else:
            print("Spread is less than 2 ticks")
            if SharedState.position_y.isInPosition:
                return [SharedState.orderbook_y.get_best_ask()["price"] - tick_size,  ba - tick_size] 
            elif SharedState.position_n.isInPosition:
                return [bb - tick_size,  SharedState.orderbook_n.get_best_ask()["price"]- tick_size] 
            else:
                return [bb + tick_size,  ba] #
    
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

