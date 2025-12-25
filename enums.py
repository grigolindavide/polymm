from enum import Enum

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class ChannelType(Enum):
    USER = "user"
    MARKET = "market"
