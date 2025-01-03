import SharedState
class WebSocketHandler:

    def handle_trade_message(message):
        """
        user: emitted when:

            when a market order is matched (”MATCHED”)
            when a limit order for a user is included in a trade (”MATCHED”)
            subsequent status changes for trade (”MINED”, “CONFIRMED”, “RETRYING”, “FAILED”)
        """
        if message['market']==SharedState.SOLANA_MARKET:
            print(message)
            if message['asset_id']==SharedState.sol_y_token:
                SharedState.position_y.update_position(message['price'],message['side'],message['side'],message['outcome'])
            elif message['asset_id']==SharedState.sol_n_token:
                SharedState.position_n.update_position(message['price'],message['side'],message['side'],message['outcome'])
            SharedState.ordermanager.update_orders()
        else:
            raise Exception(f"received a message from an unexpected market: {message['market']} at time {message['timestamp']}\n message: \n{message}")
        
        return 0
    
    def handle_order_message(message):
        """
        user: emitted when:

            When an order is placed (PLACEMENT)
            When an order is updated (some of it is matched) (UPDATE)
            When an order is cancelled (CANCELLATION)
        """
        if message['market'] == SharedState.SOLANA_MARKET:
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
        if message['market'] == SharedState.SOLANA_MARKET:
            if message['asset_id']==SharedState.sol_y_token:
                print('populating orderbook yes')
                SharedState.orderbook_y.populate_orderbook(message['bids'],message['asks'])
            elif message['asset_id']==SharedState.sol_n_token:
                print('populating orderbook no')
                SharedState.orderbook_n.populate_orderbook(message['bids'],message['asks'])
            else:
                raise Exception(f"Error with the asset ids: {message['asset_id']}")
            #make the spread
            if all([
                SharedState.orderbook_n.buy_orders, 
                SharedState.orderbook_n.sell_orders, 
                SharedState.orderbook_y.buy_orders, 
                SharedState.orderbook_y.sell_orders
            ]):
                    SharedState.pricer.make_spread()
        else:
            raise Exception(f"received a message from an unexpected market: {message['market']} at time {message['timestamp']}\n message: \n{message}")

    def handle_price_change_message(message):
        """
        market: emitted When:

            A new order is placed
            An order is cancelled
        """
        if message['asset_id'] == SharedState.sol_y_token:
            print('updating orderbook yes')
            for i in message['changes']:
                SharedState.orderbook_y.update_orderbook(i['price'],i['side'],i['size'])
        elif message['asset_id'] == SharedState.sol_n_token:
            print('updating orderbook no')
            for i in message['changes']:
                SharedState.orderbook_n.update_orderbook(i['price'],i['side'],i['size'])
        else:
            raise Exception(f"Error with price change message unrecognized asset id {message['asset_id']}\n message: \n{message}")