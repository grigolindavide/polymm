from py_clob_client.clob_types import OrderArgs
from Order import Order
import Pricer
from Position import Position

class OrderManager:
    def __init__(self):
        self.bid_y_orders = []
        self.ask_y_orders = []
        self.bid_n_orders = []
        self.ask_n_orders = [] 

    def send_order(self,price, size, side, token_id):
        '''
        :param price: price of the order
        :param size: size of the order
        :param side: BUY or SELL
        :param token_id: token id of the token to trade
        '''
        resp = self.shared_state.client.create_and_post_order(OrderArgs(
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
    
           

