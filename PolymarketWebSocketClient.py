import json, websockets, asyncio, os, dotenv
from py_clob_client.clob_types import ApiCreds
import Pricer, WebSocketHandler

class PolymarketWebSocketClient:
    def __init__(self, api_key=None, secret=None, passphrase=None):
        self.api_key = api_key
        self.secret = secret
        self.passphrase = passphrase
        self.websocket_url = "wss://ws-subscriptions-clob.polymarket.com/ws/"  
        self.connection = None

    async def connect(self,channel_type):
        """Establishes a connection to the WebSocket."""
        self.connection = await websockets.connect(f"{self.websocket_url}{channel_type}")
        print("Connected to WebSocket")

    async def subscribe(self, channel_type, markets=None, assets_ids=None):
        """
        Subscribes to a specified channel.

        :param channel_type: 'user' or 'market'
        :param markets: LIST/ARRAY of market condition IDs ONLY  for user channel
        :param assets_ids: LIST/ARRAY of asset IDs ONLY for market channel
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

    async def listen(self,channel_type, markets=None, assets_ids=None):
        """Listens for incoming messages from the WebSocket."""
        try:
            async for message in self.connection:
                data = json.loads(message)
                self.handle_message(data)
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed: {e}")
            await self.reconnect(channel_type, markets, assets_ids)

    async def reconnect(self, channel_type,markets = None, assets_ids = None):
        """Attempts to reconnect to the WebSocket after an unexpected closure."""
        print("Attempting to reconnect...")
        await asyncio.sleep(1) 
        await self.connect(channel_type)
        await self.subscribe(channel_type ,markets, assets_ids)
        await self.listen(channel_type,markets, assets_ids)

    def handle_message(self, message):
        """
        Handles incoming WebSocket messages.

        :param message: Parsed JSON message
        """
        event_type = message.get("event_type")

        if event_type == "trade":
            WebSocketHandler.handle_trade_message(message)
        elif event_type == "order":
            WebSocketHandler.handle_order_message(message)
        elif event_type == "book":
            WebSocketHandler.handle_book_message(message)
        elif event_type == "price_change":
            WebSocketHandler.handle_price_change_message(message) 
        else:
            print("Unknown message type:", message)

    async def close(self):
        """Closes the WebSocket connection."""
        if self.connection:
            await self.connection.close()
            print("WebSocket connection closed")

    async def keep_alive(self, interval=1):
        """Send ping messages every `interval` seconds to keep the connection alive."""
        while self.connection.open:
            await self.connection.ping()
            await asyncio.sleep(interval)
