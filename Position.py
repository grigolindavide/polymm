import SharedState
from py_clob_client.order_builder.constants import BUY,SELL

class Position:
    def __init__(self, price, size, token):
        self.avg_price = price
        self.size = size
        self.isInPosition = False
        self.token = token

    def update_position(self, price, size, side):
        if not self.inPosition:
            self.isInPosition = True

        if side == SELL:
            size =  size * (-1)
            if size == 0:
                self.inPosition = False

        new_value = self.size * self.avg_price + size * price
        self.size += size
        self.avg_price = new_value / self.size

    def close_position(self):
        if self.isInPosition:
            if self.size > 0:
                SharedState.ordermanager.send_order(SharedState.orderbook.get_best_bid()["price"],self.size,SELL,self.token)
            else:
                SharedState.ordermanager.send_order(SharedState.orderbook.get_best_ask()["price"],self.size,BUY,self.token)
