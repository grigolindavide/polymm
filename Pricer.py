"""
Pricer: Calculates quote prices and sizes based on market conditions and inventory.

Implements the core market making logic:
- Neutral quoting at best bid/ask when flat
- Price skewing based on inventory (improve inside to unwind)
- Size skewing based on inventory ratio
- Unwind mode with aggressive pricing
"""
import config
from shared import shared_state
import logging


class Pricer:
    """Calculates bid/ask prices and sizes for market making."""

    def calculate_quotes(self) -> dict:
        """
        Calculate the quotes to place based on current market and inventory state.

        Returns:
            dict with keys:
                - bid_price: float or None (None = don't quote bid)
                - bid_size: float
                - ask_price: float or None (None = don't quote ask)
                - ask_size: float
                - mode: 'normal' | 'unwind'
        """
        orderbook = shared_state.active_orderbook
        inventory_mgr = shared_state.inventory_manager

        if orderbook is None:
            logging.warning("Orderbook not available, skipping quote calculation")
            return None

        try:
            best_bid = orderbook.get_best_bid()['price']
            best_ask = orderbook.get_best_ask()['price']
        except (KeyError, ValueError) as e:
            logging.warning(f"Could not get best bid/ask: {e}")
            return None

        tick_size = shared_state.tick_size
        spread = best_ask - best_bid

        # Check for unwind mode
        if shared_state.is_unwinding:
            return self._calculate_unwind_quotes(best_bid, tick_size, inventory_mgr)

        # Check if we should enter unwind mode
        if inventory_mgr.should_unwind():
            logging.info("Entering UNWIND mode - max inventory reached")
            shared_state.is_unwinding = True
            return self._calculate_unwind_quotes(best_bid, tick_size, inventory_mgr)

        # Normal quoting mode
        return self._calculate_normal_quotes(
            best_bid, best_ask, spread, tick_size, inventory_mgr
        )

    def _calculate_normal_quotes(
        self, best_bid: float, best_ask: float, spread: float, 
        tick_size: float, inventory_mgr
    ) -> dict:
        """Calculate quotes for normal trading mode."""
        
        inventory_ratio = inventory_mgr.get_inventory_ratio()
        is_one_tick_spread = abs(spread - tick_size) < 1e-9

        if inventory_ratio <= 0:
            # Neutral - no inventory, quote at best levels
            bid_price = best_bid
            ask_price = best_ask
            logging.info(f"Neutral quoting: bid={bid_price:.4f}, ask={ask_price:.4f}")
        elif is_one_tick_spread:
            # Tight spread - can't improve, just copy
            bid_price = best_bid
            ask_price = best_ask
            logging.info(f"Tight spread (1 tick), copying: bid={bid_price:.4f}, ask={ask_price:.4f}")
        else:
            # Wide spread with inventory - skew to unwind
            # We're long, so improve ask to sell faster
            bid_price = best_bid  # Don't improve bid (slow accumulation)
            ask_price = best_ask - tick_size  # Improve ask (faster unwind)
            logging.info(
                f"Wide spread with inventory, skewing: bid={bid_price:.4f}, "
                f"ask={ask_price:.4f} (improved by 1 tick)"
            )

        # Calculate sizes with skew
        bid_size = inventory_mgr.calculate_bid_size()
        ask_size = inventory_mgr.calculate_ask_size()

        # If bid size is 0, don't quote bid
        if bid_size <= 0:
            bid_price = None
            bid_size = 0

        logging.info(f"Calculated sizes: bid_size={bid_size:.2f}, ask_size={ask_size:.2f}")

        return {
            'bid_price': bid_price,
            'bid_size': bid_size,
            'ask_price': ask_price,
            'ask_size': ask_size,
            'mode': 'normal'
        }

    def _calculate_unwind_quotes(
        self, best_bid: float, tick_size: float, inventory_mgr
    ) -> dict:
        """
        Calculate quotes for unwind mode.
        - No bids (stop accumulating)
        - Aggressive ask at best_bid + tick (one tick inside the bid)
        """
        # Check if we're flat and should exit unwind mode
        if inventory_mgr.is_flat():
            logging.info("Position is flat, exiting UNWIND mode")
            shared_state.is_unwinding = False
            return self.calculate_quotes()  # Recalculate in normal mode

        # Aggressive ask: one tick above best bid to get filled
        aggressive_ask_price = best_bid + tick_size
        unwind_size = inventory_mgr.get_unwind_size()

        logging.info(
            f"UNWIND mode: aggressive ask at {aggressive_ask_price:.4f} "
            f"(best_bid + tick), size={unwind_size:.2f}"
        )

        return {
            'bid_price': None,  # No bids in unwind mode
            'bid_size': 0,
            'ask_price': aggressive_ask_price,
            'ask_size': unwind_size,
            'mode': 'unwind'
        }

    def prices_changed(self, new_best_bid: float, new_best_ask: float) -> bool:
        """
        Check if best bid/ask have changed from last known values.
        Used to determine if we need to requote.
        """
        old_bid = shared_state.last_best_bid
        old_ask = shared_state.last_best_ask

        if old_bid is None or old_ask is None:
            return True  # First time, always quote

        bid_changed = abs(new_best_bid - old_bid) > 1e-9
        ask_changed = abs(new_best_ask - old_ask) > 1e-9

        return bid_changed or ask_changed
