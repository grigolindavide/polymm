import json, websockets, asyncio
from enums import ChannelType
import WebSocketHandler
import logging

class PolymarketWebSocketClient:
    def __init__(self, api_key=None, secret=None, passphrase=None):
        self.api_key = api_key
        self.secret = secret
        self.passphrase = passphrase
        self.websocket_url = "wss://ws-subscriptions-clob.polymarket.com/ws/"  
        self.connection = None

    async def connect(self, channel_type: ChannelType):
        """Establishes a connection to the WebSocket."""
        try:
            logging.info('Trying to establish connection')
            self.connection = await websockets.connect(f"{self.websocket_url}{channel_type}")
            logging.info("Connected to WebSocket")
        except Exception as e:
            logging.info(f"Failed to connect: {e}")
            self.connection = None

    async def subscribe(self, channel_type: ChannelType, markets: list[str] = None, assets_ids: list[str] = None):
        """
        Subscribes to a specified channel.

        :param channel_type: 'user' or 'market'
        :param markets: LIST/ARRAY of market condition IDs ONLY for user channel
        :param assets_ids: LIST/ARRAY of asset IDs ONLY for market channel
        """
        if not self.connection:
            logging.info("No connection established. Cannot subscribe.")
            return

        if channel_type not in [ChannelType.USER.value, ChannelType.MARKET.value]:
            raise ValueError("Invalid channel type. Use 'user' or 'market'.")

        subscribe_message = {
            "type": channel_type.value
        }

        if channel_type == ChannelType.USER.value and self.api_key and self.secret and self.passphrase:
            subscribe_message["auth"] = {
                "apiKey": self.api_key,
                "secret": self.secret,
                "passphrase": self.passphrase,
            }
            subscribe_message["markets"] = markets or []

        elif channel_type == ChannelType.MARKET.value:
            subscribe_message["assets_ids"] = assets_ids or []

        await self.connection.send(json.dumps(subscribe_message)) 
        logging.info(f"Subscribed to {channel_type} channel")


    async def listen(self, channel_type: ChannelType, markets: list[str] = None, assets_ids: list[str] = None):
        """Listens for incoming messages from the WebSocket."""
        try:
            async for message in self.connection:
                data = json.loads(message)
                self.handle_message(data)
                #logging.info(data)
        except websockets.exceptions.ConnectionClosed as e:
            logging.info(f"Connection closed: {e}")
            await self.reconnect(channel_type, markets, assets_ids)

    async def reconnect(self, channel_type: ChannelType, markets: list[str] = None, assets_ids: list[str] = None):
        """Attempts to reconnect to the WebSocket after an unexpected closure."""
        logging.info("Attempting to reconnect...")
        await asyncio.sleep(1) 
        await self.connect(channel_type)
        await self.subscribe(channel_type ,markets, assets_ids)
        await self.listen(channel_type,markets, assets_ids)

    def handle_message(self, message):
        """
        Handles incoming WebSocket messages.

        :param message: Parsed JSON message
        """
        for sms in message:
            event_type = sms.get("event_type")
            if event_type == "trade":
                WebSocketHandler.WebSocketHandler.handle_trade_message(sms)
            elif event_type == "last_trade_price":
                WebSocketHandler.WebSocketHandler.handle_last_trade_price_message(sms)
            elif event_type == "order":
                WebSocketHandler.WebSocketHandler.handle_order_message(sms)
            elif event_type == "book":
                WebSocketHandler.WebSocketHandler.handle_book_message(sms)
            elif event_type == "price_change":
                WebSocketHandler.WebSocketHandler.handle_price_change_message(sms) 
            else:
                raise Exception("Unknown message type:", sms)

    async def close(self):
        """Closes the WebSocket connection."""
        if self.connection:
            await self.connection.close()
            logging.info("WebSocket connection closed")

    async def keep_alive(self, interval=1):
        """Send ping messages every `interval` seconds to keep the connection alive."""
        try:
            while self.connection and self.connection.open:
                await self.connection.ping()
                logging.info("Ping sent to keep connection alive")
                await asyncio.sleep(interval)
        except Exception as e:
            logging.info(f"Error during keep-alive: {e}")
    
    async def run(self, channel_type: ChannelType, markets: list[str] = None, asset_ids: list[str] = None):
        """Run the WebSocket client."""
        await self.connect(channel_type)
        await self.subscribe(channel_type, markets, asset_ids)
        await self.listen(channel_type, markets, asset_ids)
