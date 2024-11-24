import SharedState
import Pricer
class WebSocketHandler:

    def handle_trade_message(self,message):
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
            raise Exception(f"received a message from an unexpected market: {message['market']} at time {message['timestamp']}")
        
        return 0
    
    def handle_order_message(self, message):
        """
        user: emitted when:

            When an order is placed (PLACEMENT)
            When an order is updated (some of it is matched) (UPDATE)
            When an order is cancelled (CANCELLATION)
        """
        if message['market'] == SharedState.SOLANA_MARKET:
            print("Order Message:", message)
        else:
            raise Exception(f"received a message from an unexpected market: {message['market']} at time {message['timestamp']}")

    def handle_book_message(self, message):
        """
        market 
            emitted When:

            First subscribed to market/
            When there is a trade that affects the book
        """
        if message['market']=='book' and message['market'] == SharedState.SOLANA_MARKET:
            if message['asset_id']==SharedState.sol_y_token:
                SharedState.orderbook_y.populate_orderbook(message['buys'],message['sells'])
            elif message['asset_id']==SharedState.sol_n_token:
                SharedState.orderbook_n.populate_orderbook(message['buys'],message['sells'])
            else:
                raise Exception(f"Error with the asset ids: {message['asset_id']}")
            #make the spread
            SharedState.ordermanager.make_spread()

        else:
            raise Exception(f"received a message from an unexpected market: {message['market']} at time {message['timestamp']}")

    def handle_price_change_message(self, message):
        """
        market: emitted When:

            A new order is placed
            An order is cancelled
        """
        if message['asset_id'] == SharedState.sol_y_token:
            for i in message['changes']:
                SharedState.orderbook_y.update_orderbook(i['price'],i['side'],i['size'])
        elif message['asset_id'] == SharedState.sol_n_token:
            for i in message['changes']:
                SharedState.orderbook_n.update_orderbook(i['price'],i['side'],i['size'])
        else:
            raise Exception(f"Error with price change message unrecognized asset id {message['asset_id']}")