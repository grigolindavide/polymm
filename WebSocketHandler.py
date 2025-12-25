"""
WebSocketHandler: Handles WebSocket messages for the market making bot.

Processes:
- Trade messages (fills)
- Order book messages (initial snapshot)
- Price change messages (orderbook updates)
- Last trade price messages
"""
from enums import OrderSide
from shared import shared_state
import logging


class WebSocketHandler:
    """Handles incoming WebSocket messages."""

    @staticmethod
    def handle_trade_message(message):
        """
        Handle a trade message - this means an order was filled.
        """
        if message.get("market") != shared_state.market:
            logging.debug(f"Ignoring trade from different market: {message.get('market')}")
            return

        logging.info(f"Trade message received: {message}")

        ordermanager = shared_state.ordermanager
        if ordermanager is None:
            logging.error("OrderManager not initialized")
            return

        # Get our active order IDs
        our_order_ids = set()
        if ordermanager.active_bid:
            our_order_ids.add(ordermanager.active_bid.id)
        if ordermanager.active_ask:
            our_order_ids.add(ordermanager.active_ask.id)

        if not our_order_ids:
            logging.debug("No active orders to match")
            return

        # Check if any of our orders were filled
        maker_orders = message.get("maker_orders", [])
        my_fills = [
            order for order in maker_orders
            if order.get("order_id") in our_order_ids
        ]

        if not my_fills:
            logging.debug("Trade did not involve our orders")
            return

        # Process each fill
        for fill in my_fills:
            order_id = fill.get("order_id")
            filled_amount = float(fill.get("matched_amount", 0))
            price = float(fill.get("price", 0))
            # The 'side' in the message is the TAKER's side
            taker_side = message.get("side", "")

            logging.info(
                f"Our order filled: id={order_id[:8]}..., "
                f"size={filled_amount}, price={price}, taker_side={taker_side}"
            )

            # Handle the fill
            ordermanager.handle_fill(order_id, filled_amount, price, taker_side)

    @staticmethod
    def handle_order_message(message):
        """Handle order status messages."""
        if message.get("market") != shared_state.market:
            return
        logging.debug(f"Order message: {message}")

    @staticmethod
    def handle_book_message(message):
        """
        Handle orderbook snapshot message.
        This is received when first subscribing to a market.
        """
        if message.get("market") != shared_state.market:
            logging.debug(f"Ignoring book from different market")
            return

        asset_id = message.get("asset_id")
        
        # Determine which orderbook to update
        if asset_id == shared_state.y_token:
            orderbook = shared_state.orderbook_y
        elif asset_id == shared_state.n_token:
            orderbook = shared_state.orderbook_n
        else:
            logging.warning(f"Unknown asset_id in book message: {asset_id}")
            return

        # Populate the orderbook
        bids = message.get("bids", [])
        asks = message.get("asks", [])
        orderbook.populate_orderbook(bids, asks)
        
        logging.info(f"Orderbook populated for asset {asset_id[:8]}...")

        # Check if this is our active token and start quoting
        if asset_id == shared_state.active_token:
            if orderbook.buy_orders and orderbook.sell_orders:
                logging.info("Active orderbook ready, starting to quote")
                shared_state.ordermanager.quote_market()
            else:
                logging.warning("Orderbook incomplete, waiting for more data")

    @staticmethod
    def handle_price_change_message(message):
        """
        Handle orderbook price change (delta update).
        This is the main trigger for requoting.
        """
        asset_id = message.get("asset_id")
        
        # Only care about our active token
        if asset_id != shared_state.active_token:
            return

        orderbook = shared_state.active_orderbook
        if orderbook is None:
            return

        # Apply the changes to the orderbook
        changes = message.get("changes", [])
        for change in changes:
            price = float(change.get("price", 0))
            side = change.get("side", "")
            size = float(change.get("size", 0))

            if side == "BUY":
                orderbook.update_orderbook(price, OrderSide.BUY, size)
            elif side == "SELL":
                orderbook.update_orderbook(price, OrderSide.SELL, size)

        # Check if best levels changed
        try:
            new_best_bid = orderbook.get_best_bid()['price']
            new_best_ask = orderbook.get_best_ask()['price']
        except (KeyError, ValueError) as e:
            logging.warning(f"Could not get best bid/ask: {e}")
            return

        # Check if we need to requote
        if shared_state.pricer.prices_changed(new_best_bid, new_best_ask):
            logging.info(
                f"Prices changed: bid {shared_state.last_best_bid} -> {new_best_bid}, "
                f"ask {shared_state.last_best_ask} -> {new_best_ask}"
            )
            shared_state.ordermanager.requote()
        else:
            logging.debug("No price change affecting our quotes")

    @staticmethod
    def handle_last_trade_price_message(message):
        """Handle last trade price updates."""
        if message.get("market") != shared_state.market:
            return

        asset_id = message.get("asset_id")
        price = float(message.get("price", 0))

        if asset_id == shared_state.y_token:
            logging.debug(f"Last trade YES: {price}")
        elif asset_id == shared_state.n_token:
            logging.debug(f"Last trade NO: {price}")
