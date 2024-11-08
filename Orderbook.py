class Orderbook:
    def __init__(self):
        self.buy_orders = {}
        self.sell_orders = {}

    def populate_orderbook(self, buys, sells):
        for i in buys:
            self.buy_orders[i['price']] = i['size']
        for i in sells:
            self.sell_orders[i['price']] = i['size']    
    
    def update_orderbook(self, price, side, size):
        if side == 'buy':
            self.buy_orders[price] = size
        else:
            self.sell_orders[price] = size
