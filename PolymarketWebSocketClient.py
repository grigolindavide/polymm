import json
import websockets
import asyncio
import os
import dotenv
from py_clob_client.clob_types import ApiCreds
class PolymarketWebSocketClient:
    def __init__(self, api_key=None, secret=None, passphrase=None):
        self.api_key = api_key
        self.secret = secret
        self.passphrase = passphrase
        self.websocket_url = "wss://ws-subscriptions-clob.polymarket.com/ws/market"  
        self.connection = None

    async def connect(self):
        """Establishes a connection to the WebSocket."""
        self.connection = await websockets.connect(self.websocket_url)
        print("Connected to WebSocket")

    async def subscribe(self, channel_type, markets=None, assets_ids=None):
        """
        Subscribes to a specified channel.

        :param channel_type: 'user' or 'market'
        :param markets: List of market condition IDs for user channel
        :param assets_ids: List of asset IDs for market channel
        """
        if channel_type not in ["user", "market"]:
            raise ValueError("Invalid channel type. Use 'user' or 'market'.")

        subscribe_message = {
            "type": channel_type,
        }

        if channel_type == "user" and self.api_key and self.secret and self.passphrase:
            subscribe_message["auth"] = {
                "apiKey": self.api_key,
                "secret": self.secret,
                "passphrase": self.passphrase,
            }
            subscribe_message["markets"] = markets or []

        if channel_type == "market":
            subscribe_message["assets_ids"] = assets_ids or []

        await self.connection.send(json.dumps(subscribe_message)) 
        print(f"Subscribed to {channel_type} channel")

    async def listen(self):
        """Listens for incoming messages from the WebSocket."""
        try:
            async for message in self.connection:
                data = json.loads(message)
                self.handle_message(data)
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed: {e}")

    def handle_message(self, message):
        """
        Handles incoming WebSocket messages.

        :param message: Parsed JSON message
        """
        event_type = message.get("event_type")

        if event_type == "trade":
            self.handle_trade_message(message)
        elif event_type == "order":
            self.handle_order_message(message)
        elif event_type == "book":
            self.handle_book_message(message)
        elif event_type == "price_change":
            self.handle_price_change_message(message)
        else:
            print("Unknown message type:", message)

    def handle_trade_message(self, message):
        print("Trade Message:", message)

    def handle_order_message(self, message):
        print("Order Message:", message)

    def handle_book_message(self, message):
        print("Book Message:", message)

    def handle_price_change_message(self, message):
        print("Price Change Message:", message)

    async def close(self):
        """Closes the WebSocket connection."""
        if self.connection:
            await self.connection.close()
            print("WebSocket connection closed")

async def main():
    
    dotenv.load_dotenv()
    KEY= os.getenv("APIKEY")
    SECRET= os.getenv("APISECRET")
    PASSPHRASE= os.getenv("APIPASSPHRASE") 
    creds = ApiCreds(
        api_key=KEY,
        api_secret=SECRET,
        api_passphrase=PASSPHRASE)
    clientws = PolymarketWebSocketClient(creds)
    await clientws.connect()
    await clientws.subscribe(channel_type="market", assets_ids=["21742633143463906290569050155826241533067272736897614950488156847949938836455"])
    await clientws.listen()
    print("Running async code")

if __name__ == "__main__":
    asyncio.run(main())