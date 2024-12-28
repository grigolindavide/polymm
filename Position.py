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
        print(f'position updated')
 
    def close_position(self, ordermanager, orderbook):
        if self.isInPosition:
            ordermanager.send_order(orderbook.get_best_ask()["price"], self.size, "BUY", self.token)
            print(f'Position closed')
        else:
            print('There are no open positions\n ')