from py_clob_client.clob_types import OrderArgs
from Order import Order
import SharedState
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
        resp = SharedState.client.create_and_post_order(OrderArgs(
            price=price,
            size=size,
            side=side,
            token_id=token_id
        ))
        print(f'Order {side} sent at price: {price} size: {size} token id: {token_id}')
        if not resp['success']:
            raise Exception(f"Error with the order at price:{price}, size:{size}, side:{side}, token_id:{token_id} message:\n{resp['errorMsg']}")
        else:
            if token_id==SharedState.sol_y_token:
                if side == "BUY":
                    self.bid_y_orders.append(Order(resp['orderID'], size, price, side, token_id, "open"))
                else:
                    self.ask_y_orders.append(Order(resp['orderID'], size, price, side, token_id, "open"))

            elif token_id== SharedState.sol_n_token:
                if side == "BUY":
                    self.bid_n_orders.append(Order(resp['orderID'], size, price, side, token_id, "open"))
                else:
                    self.ask_n_orders.append(Order(resp['orderID'], size, price, side, token_id, "open"))   
            else:
                raise Exception(f'Wrong token id when trying to send an order: {token_id}')             
            return resp['orderID']
    
           

