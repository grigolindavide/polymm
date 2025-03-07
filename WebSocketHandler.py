import SharedState
class WebSocketHandler:

    def handle_trade_message(message):
        """
        user: emitted when:

            when a market order is matched (”MATCHED”)
            when a limit order for a user is included in a trade (”MATCHED”)
            subsequent status changes for trade (”MINED”, “CONFIRMED”, “RETRYING”, “FAILED”)
        """
        if message['market'] == SharedState.MARKET:
            print("Trade Message:", message)
            
            ordermanager = SharedState.ordermanager
            all_order_ids = {
                order.id for order_list in [
                    ordermanager.bid_y_orders,
                    ordermanager.ask_y_orders,
                    ordermanager.bid_n_orders,
                    ordermanager.ask_n_orders
                ] for order in order_list
            }
            
            my_orders = [order for order in message['maker_orders'] if order['order_id'] in all_order_ids]
            
            if not my_orders:
                print("No matching orders found for your order IDs.")
                return 0
            
            for matched_order in my_orders:
                order_id = matched_order['order_id']
                matched_amount = float(matched_order['matched_amount'])
                price = float(matched_order['price'])
                side = message['side']
                
                if matched_order['asset_id'] == SharedState.y_token:
                    SharedState.position_y.update_position(price, matched_amount, side)
                    ordermanager.remove_order(order_id, SharedState.y_token, side)
                    SharedState.ordermanager.make_spread()
                
                elif matched_order['asset_id'] == SharedState.n_token:
                    SharedState.position_n.update_position(price, matched_amount, side)
                    ordermanager.remove_order(order_id, SharedState.n_token, side)
                    SharedState.ordermanager.make_spread()
                
                print(f"Removed matched order ID: {order_id}")
            
        else:
            raise Exception(
                f"received a message from an unexpected market: {message['market']} at time {message['timestamp']}\n message: \n{message}"
            )
        
        return 0

    def handle_order_message(message):
        """
        user: emitted when:

            When an order is placed (PLACEMENT)
            When an order is updated (some of it is matched) (UPDATE)
            When an order is cancelled (CANCELLATION)
        """
        if message['market'] == SharedState.MARKET:
            print("Order Message:", message)
        else:
            raise Exception(f"received a message from an unexpected market: {message['market']} at time {message['timestamp']}\n message: \n{message}")

    def handle_book_message(message):
        """
        market 
            emitted When:
            First subscribed to market/
            When there is a trade that affects the book
        """
        if message['market'] == SharedState.MARKET:
            if message['asset_id']==SharedState.y_token:
                SharedState.orderbook_y.populate_orderbook(message['bids'],message['asks'])
            elif message['asset_id']==SharedState.n_token:
                SharedState.orderbook_n.populate_orderbook(message['bids'],message['asks'])
            else:
                raise Exception(f"Error with the asset ids: {message['asset_id']}")
            #make the spread
            if all([SharedState.orderbook_n.buy_orders, SharedState.orderbook_n.sell_orders, SharedState.orderbook_y.buy_orders, SharedState.orderbook_y.sell_orders]):
                SharedState.ordermanager.make_spread()
        else:
            raise Exception(f"received a message from an unexpected market: {message['market']} at time {message['timestamp']}\n message: \n{message}")

    def handle_price_change_message(message):
        """
        market: emitted When:

            A new order is placed
            An order is cancelled
        """
        if message['asset_id'] == SharedState.y_token:
            for i in message['changes']:
                SharedState.orderbook_y.update_orderbook(float(i['price']),i['side'],float(i['size']))
                SharedState.ordermanager.update_orders()
        elif message['asset_id'] == SharedState.n_token:
            for i in message['changes']:
                SharedState.orderbook_n.update_orderbook(float(i['price']),i['side'],float(i['size']))
                SharedState.ordermanager.update_orders()
        else:
            raise Exception(f"Error with price change message unrecognized asset id {message['asset_id']}\n message: \n{message}")
        
    def handle_last_trade_price_message(message):
        """
        market: emitted When:

            A new trade is executed
        """
        if message['market'] == SharedState.MARKET:
            if message['asset_id'] == SharedState.y_token:
                last_trade_y = float(message['price'])
                print("Last Trade Y: ", last_trade_y)
            elif message['asset_id'] == SharedState.n_token:
                last_trade_n = float(message['price'])
                print("Last Trade N: ", last_trade_n)
            else:
                raise Exception(f"Error with last trade price message unrecognized asset id {message['asset_id']}\n message: \n{message}")
        else:
            raise Exception(f"received a message from an unexpected market: {message['market']} at time {message['timestamp']}\n message: \n{message}")