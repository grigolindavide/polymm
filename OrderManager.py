from py_clob_client.clob_types import OrderArgs
from Order import Order
import SharedState

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
    
    def make_spread(self):
        print("making spread")
        price = SharedState.pricer.calculate_price(SharedState.SOLANA_MARKET)
        size = SharedState.pricer.calculate_size()

        if not SharedState.position_y.isInPosition and not SharedState.position_n.isInPosition:
            print("not in position--> price: ", price[0], "size: ", price[1])
            SharedState.ordermanager.send_order(price[0], size[0], "BUY", SharedState.sol_y_token)
            SharedState.ordermanager.send_order(price[1], size[1], "BUY", SharedState.sol_n_token)
                
        elif SharedState.position_y.isInPosition:
            SharedState.client.cancel_all()
            print("canceled all orders we are in position yes")
            SharedState.ordermanager.send_order(price[0], size[1], "SELL", SharedState.sol_y_token)
            SharedState.ordermanager.send_order(price[1], size[1], "BUY", SharedState.sol_n_token)

        elif SharedState.position_n.isInPosition:
            SharedState.client.cancel_all()
            print("canceled all orders we are in position no")
            SharedState.ordermanager.send_order(price[0], size[0], "BUY", SharedState.sol_y_token)
            SharedState.ordermanager.send_order(price[1], size[0], "SELL", SharedState.sol_n_token)

    def update_orders(self):
        print("updating orders")
        if SharedState.position_y.isInPosition:
            print("we are in position yes")
            best_ask_y_order = min(self.ask_y_orders)
            
            if best_ask_y_order.price > SharedState.orderbook_y.get_best_ask()["price"]:
                SharedState.client.cancel(best_ask_y_order.id)
                self.send_order(SharedState.orderbook_y.get_best_ask()["price"], best_ask_y_order.size, "SELL", SharedState.sol_y_token)
                self.ask_y_orders.remove(best_ask_y_order)
        
        elif SharedState.position_n.isInPosition:
            print("we are in position no")
            best_ask_n_order = min(self.ask_n_orders)
            
            if best_ask_n_order.price > SharedState.orderbook_n.get_best_ask()["price"]:
                self.send_order(SharedState.orderbook_n.get_best_ask()["price"], best_ask_n_order.size, "SELL", SharedState.sol_n_token)
                self.ask_n_orders.remove(best_ask_n_order)
        else:
            best_bid_n_order = max(self.bid_n_orders)
            best_bid_y_order = max(self.bid_y_orders)
            if best_bid_y_order.price < SharedState.orderbook_y.get_best_bid()["price"]:
                print("not best bid order anymore-> updating")
                print("best bid order: ", best_bid_y_order.price, "best bid order in orderbook: ", SharedState.orderbook_y.get_best_bid()["price"])
                SharedState.client.cancel(best_bid_y_order.id)
                self.send_order(SharedState.orderbook_y.get_best_bid()["price"], best_bid_y_order.size, "BUY", SharedState.sol_y_token)
                self.bid_y_orders.remove(best_bid_y_order)

            elif best_bid_n_order.price < SharedState.orderbook_n.get_best_bid()["price"]:
                print("not best ask order anymore-> updating")
                print("best ask order: ", best_bid_n_order.price, "best ask order in orderbook: ", SharedState.orderbook_n.get_best_bid()["price"])
                SharedState.client.cancel(best_bid_n_order.id)
                self.send_order(SharedState.orderbook_n.get_best_bid()['price'], best_bid_n_order.size, "BUY", SharedState.sol_n_token)
                self.bid_n_orders.remove(best_bid_n_order)