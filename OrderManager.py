from py_clob_client.clob_types import OrderArgs
import SharedState
from Order import Order
import Pricer
class OrderManager:
    bid_y_orders = []
    ask_y_orders = []
    bid_n_orders = []
    ask_n_orders = [] 

    def send_order(self,price, size, side, token_id):
        '''
        :param price: price of the order
        :param size: size of the order
        :param side: BUY or SELL
        :param token_id: token id of the token to trade
        '''
        resp = SharedState.client.create_and_post_order(OrderArgs(
            price=price,
            size=size,
            side=side,
            token_id=token_id
        ))

        if not resp['success']:
            raise Exception(f"Error with the order at price:{price}, size:{size}, side:{side}, token_id:{token_id} message:{resp['errorMsg']}")
        else:
            if side == "BUY":
                self.bid_orders.append(Order(resp['orderID'], size, price, side, token_id, "open"))
            else:
                self.ask_orders.append(Order(resp['orderID'], size, price, side, token_id, "open"))
            return resp['orderID']
    
    def make_spread(self):
        #get bid order with the highest price
        best_bid_y_order = max(self.bid_y_orders, key=lambda x: x.price)
        best_ask_y_order = min(self.ask_y_orders, key=lambda x: x.price)
        best_bid_n_order = max(self.bid_n_orders, key=lambda x: x.price)
        best_ask_n_order = min(self.ask_n_orders, key=lambda x: x.price)

        price = Pricer.calculate_price(SharedState.SOLANA_MARKET)
        size = Pricer.calculate_size()

        if not SharedState.position_y.isInPosition and not SharedState.position_n.isInPosition:
            if best_bid_y_order.price != SharedState.orderbook_y.get_best_bid()["price"]:
                SharedState.client.cancel(best_bid_y_order.id)
                self.bid_y_orders.remove(best_bid_y_order)
                id = self.send_order(price[0], size[0], "BUY", SharedState.sol_y_token)
                self.bid_y_orders.append(Order(id, size[0], price[0], "BUY", SharedState.sol_y_token, "open"))
 
            elif best_bid_n_order.price != SharedState.orderbook_n.get_best_ask()["price"]:
                SharedState.client.cancel(best_bid_n_order.id)
                self.bid_n_orders.remove(best_bid_n_order)
                id = self.send_order(price[1], size[1], "BUY", SharedState.sol_n_token)
                self.bid_n_orders.append(Order(id, size[1], price[1], "BUY", SharedState.sol_n_token, "open"))
            
            else:
                idy = self.send_order(price[0], size[0], "BUY", SharedState.sol_y_token)
                self.bid_y_orders.append(Order(idy, size[0], price[0], "BUY", SharedState.sol_y_token, "open"))
                idn = self.send_order(price[1], size[1], "BUY", SharedState.sol_n_token)
                self.bid_n_orders.append(Order(idn, size[1], price[1], "BUY", SharedState.sol_n_token, "open"))
                
        elif SharedState.position_y.isInPosition:
            if best_ask_y_order.price != SharedState.orderbook_y.get_best_ask()["price"]:
                SharedState.client.cancel(best_ask_y_order.id)
                self.ask_y_orders.remove(best_ask_y_order)
                id = self.send_order(price[1], size[1], "SELL", SharedState.sol_y_token)
                self.ask_y_orders.append(Order(id, size[1], price[1], "SELL", SharedState.sol_y_token, "open"))
            else:
                SharedState.client.cancel(best_bid_y_order.id)
                id = self.send_order(price[1], size[1], "SELL", SharedState.sol_y_token)
                self.ask_y_orders.append(Order(id, size[1], price[1], "SELL", SharedState.sol_y_token, "open"))

        elif SharedState.position_n.isInPosition:
            if best_ask_n_order.price != SharedState.orderbook_n.get_best_ask()["price"]:
                SharedState.client.cancel(best_ask_n_order.id)
                self.ask_n_orders.remove(best_ask_n_order)
                id = self.send_order(price[1], size[1], "SELL", SharedState.sol_n_token)
                self.ask_n_orders.append(Order(id, size[1], price[1], "SELL", SharedState.sol_n_token, "open"))
            else:
                SharedState.client.cancel(best_bid_n_order.id)
                id = self.send_order(price[1], size[1], "SELL", SharedState.sol_n_token)
                self.ask_n_orders.append(Order(id, size[1], price[1], "SELL", SharedState.sol_n_token, "open"))
           

