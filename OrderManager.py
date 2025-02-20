from py_clob_client.clob_types import OrderArgs
from Order import Order
import SharedState

class OrderManager:
    def __init__(self):
        self.bid_y_orders = []
        self.ask_y_orders = []
        self.bid_n_orders = []
        self.ask_n_orders = [] 

    def clear_all_orders(self):
        self.bid_y_orders.clear()
        self.ask_y_orders.clear()
        self.bid_n_orders.clear()
        self.ask_n_orders.clear()
    def remove_order(self, order_id, token_id, side):
        '''
        :param order_id: id of the order to remove
        :param token_id: token id of the token to trade
        :param side: BUY or SELL
        '''
        if token_id==SharedState.y_token:
            if side == "BUY":
                self.bid_y_orders = [o for o in self.bid_y_orders if o.id != order_id]
            elif side == "SELL":
                self.ask_y_orders = [o for o in self.ask_y_orders if o.id != order_id]
        elif token_id==SharedState.n_token:
            if side == "BUY":
                self.bid_n_orders = [o for o in self.bid_n_orders if o.id != order_id]
            elif side == "SELL":
                self.ask_n_orders = [o for o in self.ask_n_orders if o.id != order_id]
        else:
            raise Exception(f'Wrong token id when trying to remove an order: {token_id}')
            
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
            if token_id==SharedState.y_token:
                if side == "BUY":
                    self.bid_y_orders.append(Order(resp['orderID'], size, price, side, token_id, "open"))
                else:
                    self.ask_y_orders.append(Order(resp['orderID'], size, price, side, token_id, "open"))

            elif token_id== SharedState.n_token:
                if side == "BUY":
                    self.bid_n_orders.append(Order(resp['orderID'], size, price, side, token_id, "open"))
                else:
                    self.ask_n_orders.append(Order(resp['orderID'], size, price, side, token_id, "open"))   
            else:
                raise Exception(f'Wrong token id when trying to send an order: {token_id}')             
            return resp['orderID']
    
    def make_spread(self):
        print("making spread")
        price = SharedState.pricer.calculate_price(SharedState.MARKET)
        size = SharedState.pricer.calculate_size()
        
        if not SharedState.position_y.isInPosition and not SharedState.position_n.isInPosition:
            SharedState.client.cancel_all()
            self.clear_all_orders()
            print("canceled all precedent orders")
            print("making spread: not in position--> price y: ", price[0], "price n: ", price[1])
            SharedState.ordermanager.send_order(price[0], size[0], "BUY", SharedState.y_token)
            SharedState.ordermanager.send_order(price[1], size[1], "BUY", SharedState.n_token)
        
        elif SharedState.position_y.isInPosition:
            SharedState.client.cancel_all()
            self.clear_all_orders()
            print("canceled all orders we are in position yes")
            SharedState.ordermanager.send_order(price[0], SharedState.position_y.size, "SELL", SharedState.y_token)
            SharedState.ordermanager.send_order(price[1], size[1], "BUY", SharedState.n_token)

        elif SharedState.position_n.isInPosition:
            SharedState.client.cancel_all()
            self.clear_all_orders()
            print("canceled all orders we are in position no")
            SharedState.ordermanager.send_order(price[0], size[0], "BUY", SharedState.y_token)
            SharedState.ordermanager.send_order(price[1], SharedState.position_n.size, "SELL", SharedState.n_token)

    def update_orders(self):
        print("updating orders")

        if SharedState.position_y.isInPosition:
            print("we are in position yes")
            if self.ask_y_orders:  # Check if list is non-empty
                best_ask_y_order = min(self.ask_y_orders, key=lambda order: order.price)
                best_ask_price = SharedState.orderbook_y.get_best_ask()["price"]
                
                if best_ask_y_order.price > best_ask_price:
                    SharedState.client.cancel(best_ask_y_order.id)
                    self.send_order(best_ask_price, best_ask_y_order.size, "SELL", SharedState.y_token)
                    self.ask_y_orders.remove(best_ask_y_order)

        elif SharedState.position_n.isInPosition:
            print("we are in position no")
            if self.ask_n_orders:
                best_ask_n_order = min(self.ask_n_orders, key=lambda order: order.price)
                best_ask_price = SharedState.orderbook_n.get_best_ask()["price"]
                
                if best_ask_n_order.price > best_ask_price:
                    SharedState.client.cancel(best_ask_n_order.id)
                    new_order = self.send_order(best_ask_price, best_ask_n_order.size, "SELL", SharedState.n_token)
                    self.ask_n_orders.remove(best_ask_n_order)
        else:
            if self.bid_y_orders and self.bid_n_orders:  # Both lists must be non-empty
                best_bid_y_order = max(self.bid_y_orders, key=lambda order: order.price)
                best_bid_n_order = max(self.bid_n_orders, key=lambda order: order.price)
                
                best_bid_y_price = SharedState.orderbook_y.get_best_bid()["price"]
                best_bid_n_price = SharedState.orderbook_n.get_best_bid()["price"]
                
                if best_bid_y_order.price < best_bid_y_price:
                    print("not best bid_yes order anymore -> updating")
                    print(f"best bid_yes order: {best_bid_y_order.price}, best bid order in orderbook yes: {best_bid_y_price}")
                    SharedState.client.cancel(best_bid_y_order.id)
                    self.send_order(best_bid_y_price, best_bid_y_order.size, "BUY", SharedState.y_token)
                    self.bid_y_orders.remove(best_bid_y_order)
                
                elif best_bid_n_order.price < best_bid_n_price:
                    print("not best bid_no order anymore -> updating")
                    print(f"best bid_no order: {best_bid_n_order.price}, best bid order in orderbook_no: {best_bid_n_price}")
                    SharedState.client.cancel(best_bid_n_order.id)
                    self.bid_n_orders.remove(best_bid_n_order)
                    self.send_order(best_bid_n_price, best_bid_n_order.size, "BUY", SharedState.n_token)
                    self.bid_n_orders.remove(best_bid_n_order)