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

    def get_best_bid(self):
        bb = max(self.buy_orders.keys())
        return {"price":bb,"size":self.buy_orders.get(bb)}
    
    def get_best_ask(self):
        ba = min(self.sell_orders.keys())
        return {"price":ba,"size":self.sell_orders.get(ba)}
