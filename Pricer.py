import SharedState
import numpy as np
import scipy.stats as stats

class Pricer:
        
    def calculate_price(self, market_token):
        ba=float(SharedState.orderbook_y.get_best_ask()["price"])
        bb=float(SharedState.orderbook_y.get_best_bid()["price"])
        tick_size = SharedState.client.get_market(market_token)['minimum_tick_size']

        if self.isSpreadEqualMinTick(bb,ba,market_token):
            return [bb,(1-ba)]
        else:
            if SharedState.position_y.isInPosition:
                return [bb - tick_size*2, (1 - ba) ]
            elif SharedState.position_n.isInPosition:
                return [bb, (1 - (ba - tick_size*2)) ] 
            else:
                return [ba, (1 - (ba+tick_size)) ]
    
    def calculate_size(self):
        size_buy= 10
        size_sell= 10
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

