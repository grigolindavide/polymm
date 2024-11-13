class Order:
    def __init__(self, id: str, size: float, price: float, side: str, token: str, status: str):

        self.id = id
        self.size = size
        self.price = price
        self.side = side
        self.token = token
        self.status = status
