import SharedState
from Order import Order
import numpy as np
import scipy.stats as stats

class Pricer:
        
    def calculate_price(self, market_token):
        ba=float(SharedState.orderbook_y.get_best_ask()["price"])
        bb=float(SharedState.orderbook_y.get_best_bid()["price"])
        bias = self.calculateBias(bb,ba,market_token)
        buy = bb + bias
        sell= ba + bias
        return [buy,(1-sell)]
    
    def calculate_size(self):
        size_buy= 10
        size_sell= 10
        return [size_buy,size_sell]
    
    def calculateBias(self,bb,ba,market_token):
        '''
        returns: bias
        '''
        tick_size = SharedState.client.get_market(market_token)['minimum_tick_size']
        b=0
        if SharedState.position_y.size > 0:
            b = bb - tick_size*2
        elif SharedState.position_n.size < 0:
            b = ba - tick_size*2 
        print(f'Current bias: {b}')
        return b
    
    def make_spread(self):
        price = self.calculate_price(SharedState.SOLANA_MARKET)
        size = self.calculate_size()

        if not SharedState.position_y.isInPosition and not SharedState.position_n.isInPosition:
            if SharedState.ordermanager.bid_y_orders or SharedState.ordermanager.ask_y_orders:
                best_bid_y_order = max(SharedState.ordermanager.bid_y_orders) 
                best_ask_y_order = min(SharedState.ordermanager.ask_y_orders)
                best_bid_n_order = max(SharedState.ordermanager.bid_n_orders)
                best_ask_n_order = min(SharedState.ordermanager.ask_n_orders)
                if best_bid_y_order.price != self.shared_state.orderbook_y.get_best_bid()["price"]:
                    SharedState.client.cancel(best_bid_y_order.id)
                    SharedState.ordermanager.bid_y_orders.remove(best_bid_y_order)
                    id = SharedState.ordermanager.send_order(price[0], size[0], "BUY", SharedState.sol_y_token)

                elif best_bid_n_order.price != SharedState.orderbook_n.get_best_ask()["price"]:
                    SharedState.client.cancel(best_bid_n_order.id)
                    SharedState.ordermanager.bid_n_orders.remove(best_bid_n_order)
                    id = SharedState.ordermanager.send_order(price[1], size[1], "BUY", SharedState.sol_n_token)           
            else:
                idy = SharedState.ordermanager.send_order(price[0], size[0], "BUY", SharedState.sol_y_token)
                idn = SharedState.ordermanager.send_order(price[1], size[1], "BUY", SharedState.sol_n_token)
                
        elif SharedState.position_y.isInPosition:
            best_ask_y_order = min(SharedState.ordermanager.ask_y_orders)
            if best_ask_y_order.price != SharedState.orderbook_y.get_best_ask()["price"]:
                SharedState.client.cancel(best_ask_y_order.id)
                SharedState.ordermanager.ask_y_orders.remove(best_ask_y_order)
                id = SharedState.ordermanager.send_order(price[1], size[1], "SELL", SharedState.sol_y_token)
            else:
                SharedState.client.cancel(best_bid_y_order.id)
                id = SharedState.ordermanager.send_order(price[1], size[1], "SELL", SharedState.sol_y_token)

        elif SharedState.position_n.isInPosition:
            best_ask_n_order = min(SharedState.ordermanager.ask_n_orders)
            if best_ask_n_order.price != SharedState.orderbook_n.get_best_ask()["price"]:
                SharedState.client.cancel(best_ask_n_order.id)
                SharedState.ordermanager.ask_n_orders.remove(best_ask_n_order)
                id = SharedState.ordermanager.send_order(price[1], size[1], "SELL", SharedState.sol_n_token)
            else:
                SharedState.client.cancel(best_bid_n_order.id)
                id = SharedState.ordermanager.send_order(price[1], size[1], "SELL", SharedState.sol_n_token)

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

