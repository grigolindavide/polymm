"""
InventoryManager: Centralized inventory tracking and skew calculations.

Manages position sizing and price skewing based on current inventory levels.
"""
import config
from shared import shared_state
import logging


class InventoryManager:
    """Manages inventory tracking and calculates skew parameters for market making."""

    def __init__(self):
        self.position = None  # Will be set to the active position (YES or NO)

    def set_position(self, position):
        """Set the position object to track."""
        self.position = position

    def get_inventory_size(self) -> float:
        """Get current inventory size in contracts."""
        if self.position is None:
            return 0.0
        return self.position.size

    def get_inventory_usd(self) -> float:
        """Get current inventory value in USD."""
        if self.position is None:
            return 0.0
        return self.position.get_value_usd()

    def get_inventory_ratio(self) -> float:
        """
        Get inventory ratio from 0 to 1.
        0 = no inventory, 1 = at max inventory.
        """
        inventory_usd = self.get_inventory_usd()
        if inventory_usd <= 0:
            return 0.0
        ratio = inventory_usd / config.MAX_INVENTORY_USD
        return min(ratio, 1.0)  # Cap at 1.0

    def should_unwind(self) -> bool:
        """Check if we've hit max inventory and should enter unwind mode."""
        return self.get_inventory_usd() >= config.MAX_INVENTORY_USD

    def is_flat(self) -> bool:
        """Check if position is flat (no inventory)."""
        return self.get_inventory_size() <= 0

    def calculate_bid_size(self) -> float:
        """
        Calculate bid size based on inventory.
        Reduces as inventory grows to slow accumulation.
        """
        ratio = self.get_inventory_ratio()
        size = config.BASE_ORDER_SIZE * (1.0 - ratio)
        return max(size, 0.0)  # Don't go negative

    def calculate_ask_size(self) -> float:
        """
        Calculate ask size based on inventory.
        Increases as inventory grows to speed up unwinding.
        """
        ratio = self.get_inventory_ratio()
        size = config.BASE_ORDER_SIZE * (1.0 + ratio)
        return size

    def get_unwind_size(self) -> float:
        """Get the full position size for aggressive unwinding."""
        return self.get_inventory_size()

    def log_status(self):
        """Log current inventory status."""
        logging.info(
            f"Inventory: size={self.get_inventory_size():.2f}, "
            f"usd=${self.get_inventory_usd():.2f}, "
            f"ratio={self.get_inventory_ratio():.2%}, "
            f"should_unwind={self.should_unwind()}"
        )
