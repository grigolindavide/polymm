"""
OrderManager: Manages order lifecycle for market making.

Handles:
- Sending orders to the exchange
- Tracking active orders
- Requoting when market conditions change
- Canceling orders
"""
from py_clob_client.clob_types import OrderArgs
from enums import OrderSide
from Order import Order
from shared import shared_state
import logging


class OrderManager:
    """Manages order placement, tracking, and updates for market making."""

    def __init__(self):
        # Track orders by side: {'BUY': Order or None, 'SELL': Order or None}
        self.active_bid = None
        self.active_ask = None

    def clear_all_orders(self):
        """Clear internal order tracking."""
        self.active_bid = None
        self.active_ask = None

    def quote_market(self):
        """
        Main entry point for quoting.
        Gets quotes from Pricer and places orders.
        """
        quotes = shared_state.pricer.calculate_quotes()
        if quotes is None:
            logging.warning("No quotes calculated, skipping")
            return

        # Cancel existing orders first
        self._cancel_existing_orders()

        # Place new orders
        self._place_orders(quotes)

        # Update last known prices
        orderbook = shared_state.active_orderbook
        if orderbook:
            try:
                shared_state.last_best_bid = orderbook.get_best_bid()['price']
                shared_state.last_best_ask = orderbook.get_best_ask()['price']
            except (KeyError, ValueError):
                pass

        logging.info(f"Quoted market in {quotes['mode']} mode")

    def requote(self):
        """
        Requote the market. Called when orderbook changes.
        """
        logging.info("Requoting due to market change...")
        self.quote_market()

    def _cancel_existing_orders(self):
        """Cancel all existing orders."""
        orders_to_cancel = []

        if self.active_bid is not None:
            orders_to_cancel.append(self.active_bid.id)
        if self.active_ask is not None:
            orders_to_cancel.append(self.active_ask.id)

        if orders_to_cancel:
            try:
                shared_state.client.cancel_orders(orders_to_cancel)
                logging.info(f"Cancelled {len(orders_to_cancel)} orders")
            except Exception as e:
                logging.error(f"Error cancelling orders: {e}")

        self.clear_all_orders()

    def _place_orders(self, quotes: dict):
        """Place bid and/or ask orders based on calculated quotes."""
        token_id = shared_state.active_token

        # Place bid if we have one
        if quotes['bid_price'] is not None and quotes['bid_size'] > 0:
            self._send_order(
                price=quotes['bid_price'],
                size=quotes['bid_size'],
                side=OrderSide.BUY.value,
                token_id=token_id,
                is_bid=True
            )

        # Place ask if we have one
        if quotes['ask_price'] is not None and quotes['ask_size'] > 0:
            self._send_order(
                price=quotes['ask_price'],
                size=quotes['ask_size'],
                side=OrderSide.SELL.value,
                token_id=token_id,
                is_bid=False
            )

    def _send_order(self, price: float, size: float, side: str, token_id: str, is_bid: bool):
        """Send a single order to the exchange."""
        try:
            resp = shared_state.client.create_and_post_order(
                OrderArgs(price=price, size=size, side=side, token_id=token_id)
            )

            if not resp.get("success", False):
                logging.error(
                    f"Order failed: price={price}, size={size}, side={side}, "
                    f"error={resp.get('errorMsg', 'Unknown')}"
                )
                return None

            order = Order(
                id=resp["orderID"],
                size=size,
                price=price,
                side=side,
                token=token_id,
                status="open"
            )

            if is_bid:
                self.active_bid = order
            else:
                self.active_ask = order

            logging.info(f"Order placed: {side} {size:.2f} @ {price:.4f}")
            return resp["orderID"]

        except Exception as e:
            logging.error(f"Exception sending order: {e}")
            return None

    def handle_fill(self, order_id: str, filled_size: float, price: float, side: str):
        """
        Handle an order fill notification.
        Updates position and triggers requote.
        """
        # Update position
        position = shared_state.inventory_manager.position
        if position:
            position.update_position(price, filled_size, side)

        # Log inventory status
        shared_state.inventory_manager.log_status()

        # Check if we need to enter/exit unwind mode
        if shared_state.is_unwinding:
            if shared_state.inventory_manager.is_flat():
                logging.info("Position is flat, exiting unwind mode")
                shared_state.is_unwinding = False
        else:
            if shared_state.inventory_manager.should_unwind():
                logging.info("Max inventory reached, entering unwind mode")
                shared_state.is_unwinding = True

        # Clear the filled order from tracking
        if self.active_bid and self.active_bid.id == order_id:
            self.active_bid = None
        if self.active_ask and self.active_ask.id == order_id:
            self.active_ask = None

        # Requote
        self.quote_market()

    def cancel_all(self):
        """Emergency cancel all orders."""
        try:
            shared_state.client.cancel_all()
            self.clear_all_orders()
            logging.info("Cancelled all orders (emergency)")
        except Exception as e:
            logging.error(f"Error in emergency cancel: {e}")
