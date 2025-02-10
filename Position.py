from py_clob_client.order_builder.constants import SELL
import SharedState

class Position:
    """
    A class to represent a trading position.

    Attributes:
    avg_price (float): The average price of the position.
    size (float): The size of the position.
    isInPosition (bool): A flag indicating if the position is active.
    token (str): The token associated with the position.
    """

    def __init__(self, price: float, size: float, token: str):
        """
        Initializes a new Position instance.

        Args:
        price (float): The initial price of the position.
        size (float): The initial size of the position.
        token (str): The token associated with the position.
        """
        self.avg_price = price
        self.size = size
        self.isInPosition = False
        self.token = token

    def update_position(self, price: float, size: float, side: str):
        """
        Updates the position with a new trade.

        Args:
        price (float): The price of the new trade.
        size (float): The size of the new trade.
        side (str): The side of the trade, either 'BUY' or 'SELL'.
        """
        if not self.isInPosition:
            self.isInPosition = True

        if side == SELL:
            size = size * (-1)
            if size == 0:
                self.isInPosition = False

        new_value = self.size * self.avg_price + size * price
        self.size += size
        self.avg_price = new_value / self.size
        print(f'position updated to price: {self.avg_price} size: {self.size} token: {self.token}')

    def close_position(self, ids):
        """
        Closes the current position by canceling orders.

        Args:
        ids (list): A list of order IDs to cancel.
        """
        if self.isInPosition:
            SharedState.client.cancel_orders(ids)
            print(f'Position closed')
        else:
            print('There are no open positions\n')