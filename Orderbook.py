class Orderbook:
    def __init__(self):
        self.buy_orders = {}
        self.sell_orders = {}

    def populate_orderbook(self, buys, sells):
        print("populating orderbook")
        for i in buys:
            self.buy_orders[float(i['price'])] = float(i['size'])
        for i in sells:
            self.sell_orders[float(i['price'])] = float(i['size'])    
    
    def update_orderbook(self, price, side, size):
        print("updating orderbook")
        if side == 'buy':
            self.buy_orders[float(price)] = float(size)
        else:
            self.sell_orders[float(price)] = float(size)

    def get_best_bid(self):
        bb = max(self.buy_orders)
        return {"price":bb,"size":self.buy_orders.get(bb)}
    
    def get_best_ask(self):
        ba = min(self.sell_orders)
        return {"price":ba,"size":self.sell_orders.get(ba)}
