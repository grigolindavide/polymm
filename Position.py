from py_clob_client.order_builder.constants import BUY,SELL
class Position:
    def __init__(self, price, size, token_id):
        self.avg_price = price
        self.size = size
        self.token_id = token_id

    def update_position(self, price, size, side):
        if side == SELL:
            size =  size * (-1)

        new_value = self.size * self.avg_price + size * price
        self.size += size
        self.avg_price = new_value / self.size
