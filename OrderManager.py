from py_clob_client.clob_types import OrderArgs

class OrderManager:
    def __init__(self, client):
        self.client = client

    def send_order(self,price, size, side, token_id):
        '''
        :param price: price of the order
        :param size: size of the order
        :param side: BUY or SELL
        :param token_id: token id of the token to trade
        '''
        resp = self.client.create_and_post_order(OrderArgs(
            price=price,
            size=size,
            side=side,
            token_id=token_id
        ))

        if not resp['success']:
            print(resp['errorMsg'])
        return resp['orderID']