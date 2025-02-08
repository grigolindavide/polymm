from py_clob_client.order_builder.constants import BUY,SELL
import SharedState
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
        print(f'position updated to price: {self.avg_price} size: {self.size} token: {self.token}')
 
    def close_position(self, ids):
        if self.isInPosition:
            SharedState.client.cancel_orders(ids)
            print(f'Position closed')
        else:
            print('There are no open positions\n ')