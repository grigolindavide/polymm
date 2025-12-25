"""
Position: Tracks trading position for a single token.

Provides position size, average price, and USD value calculations.
"""
from enums import OrderSide
import logging


class Position:
    """Represents a trading position for a single token."""

    def __init__(self, price: float, size: float, token: str):
        """
        Initialize a position.

        Args:
            price: Initial average price (0 if no position)
            size: Initial position size in contracts
            token: Token ID for this position
        """
        self.avg_price = price
        self.size = size
        self.token = token

    def is_in_position(self) -> bool:
        """Check if we have any position."""
        return self.size > 0

    def get_value_usd(self) -> float:
        """
        Get position value in USD.
        Value = size * avg_price
        """
        if self.size <= 0:
            return 0.0
        return self.size * self.avg_price

    def update_position(self, price: float, size: float, side: str):
        """
        Update position based on a fill.

        Args:
            price: Fill price
            size: Fill size (always positive)
            side: The side of the TAKER order (BUY means we sold, SELL means we bought)
        """
        # When taker is BUY, we are the maker on SELL side (we sold)
        # When taker is SELL, we are the maker on BUY side (we bought)
        if side == OrderSide.BUY.value:
            # Taker bought, we sold - reduce position
            self._reduce_position(price, size)
        else:
            # Taker sold, we bought - increase position
            self._increase_position(price, size)

        logging.info(
            f"Position updated: avg_price={self.avg_price:.4f}, "
            f"size={self.size:.2f}, token={self.token[:8]}..."
        )

    def _increase_position(self, price: float, size: float):
        """Add to position with new average price calculation."""
        if self.size <= 0:
            # New position
            self.avg_price = price
            self.size = size
        else:
            # Average into existing position
            total_value = (self.size * self.avg_price) + (size * price)
            self.size += size
            self.avg_price = total_value / self.size

    def _reduce_position(self, price: float, size: float):
        """Reduce position size. Average price stays the same for remaining."""
        self.size -= size
        if self.size <= 0:
            self.reset()

    def reset(self):
        """Clear the position."""
        self.avg_price = 0.0
        self.size = 0.0
        logging.info(f"Position reset for token {self.token[:8]}...")

    def __repr__(self):
        return f"Position(size={self.size:.2f}, avg_price={self.avg_price:.4f}, token={self.token[:8]}...)"