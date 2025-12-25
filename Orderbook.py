"""
Orderbook: Maintains the current state of the order book for a token.

Tracks bid/ask levels and provides best bid/ask access.
"""
from enums import OrderSide
import logging


class Orderbook:
    """Maintains order book state for a single token."""

    def __init__(self):
        self.buy_orders = {}   # price -> size
        self.sell_orders = {}  # price -> size

    def populate_orderbook(self, buys: list, sells: list):
        """
        Initialize orderbook from a snapshot.
        
        Args:
            buys: List of {'price': x, 'size': y} dicts
            sells: List of {'price': x, 'size': y} dicts
        """
        logging.info("Populating orderbook from snapshot")
        self.buy_orders.clear()
        self.sell_orders.clear()

        for b in buys:
            price = float(b.get('price', 0))
            size = float(b.get('size', 0))
            if size > 0:
                self.buy_orders[price] = size

        for s in sells:
            price = float(s.get('price', 0))
            size = float(s.get('size', 0))
            if size > 0:
                self.sell_orders[price] = size

        logging.info(f"Orderbook: {len(self.buy_orders)} bids, {len(self.sell_orders)} asks")

    def update_orderbook(self, price: float, side: OrderSide, size: float):
        """
        Update a single price level.
        If size is 0, remove the level.
        """
        if isinstance(side, OrderSide):
            side_value = side.value
        else:
            side_value = side

        if side_value == OrderSide.BUY.value or side_value == "BUY":
            if size <= 0:
                self.buy_orders.pop(price, None)
            else:
                self.buy_orders[price] = size
        elif side_value == OrderSide.SELL.value or side_value == "SELL":
            if size <= 0:
                self.sell_orders.pop(price, None)
            else:
                self.sell_orders[price] = size

    def get_best_bid(self) -> dict:
        """Get the best (highest) bid price and size."""
        if not self.buy_orders:
            raise ValueError("No bids in orderbook")
        best_price = max(self.buy_orders.keys())
        return {"price": best_price, "size": self.buy_orders[best_price]}

    def get_best_ask(self) -> dict:
        """Get the best (lowest) ask price and size."""
        if not self.sell_orders:
            raise ValueError("No asks in orderbook")
        best_price = min(self.sell_orders.keys())
        return {"price": best_price, "size": self.sell_orders[best_price]}

    def get_mid_price(self) -> float:
        """Calculate mid price."""
        best_bid = self.get_best_bid()['price']
        best_ask = self.get_best_ask()['price']
        return (best_bid + best_ask) / 2

    def get_spread(self) -> float:
        """Calculate spread."""
        best_bid = self.get_best_bid()['price']
        best_ask = self.get_best_ask()['price']
        return best_ask - best_bid
