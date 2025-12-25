"""
Polymarket Market Making Bot

Main entry point for the market making bot.
Initializes all components and runs the WebSocket connections.
"""
import asyncio
from enums import ChannelType
from logger import setup_logging
import logging
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
import config
from shared import shared_state
from Orderbook import Orderbook
from PolymarketWebSocketClient import PolymarketWebSocketClient
from Position import Position
from Pricer import Pricer
from OrderManager import OrderManager
from InventoryManager import InventoryManager


def initialize_dependencies():
    """Initialize all trading components."""
    logging.info("Initializing dependencies...")

    # Initialize API client
    creds = ApiCreds(
        api_key=config.API_KEY,
        api_secret=config.API_SECRET,
        api_passphrase=config.API_PASSPHRASE
    )
    shared_state.client = ClobClient(
        config.HOST,
        key=config.PK,
        chain_id=config.CHAIN_ID,
        funder=config.BROWSER_WALLET,
        signature_type=1,
        creds=creds
    )

    # Initialize WebSocket clients
    shared_state.clientws_user = PolymarketWebSocketClient(
        api_key=config.API_KEY,
        secret=config.API_SECRET,
        passphrase=config.API_PASSPHRASE
    )
    shared_state.clientws_market = PolymarketWebSocketClient(
        api_key=config.API_KEY,
        secret=config.API_SECRET,
        passphrase=config.API_PASSPHRASE
    )

    # Get market info
    current_market = shared_state.client.get_market(config.MARKET)
    shared_state.y_token = current_market['tokens'][0]['token_id']
    shared_state.n_token = current_market['tokens'][1]['token_id']
    shared_state.market = config.MARKET

    # Get tick size from market (use config default if not available)
    tick_size = current_market.get('minimum_tick_size')
    if tick_size:
        shared_state.tick_size = float(tick_size)
    else:
        shared_state.tick_size = config.MIN_TICK_SIZE
    logging.info(f"Tick size: {shared_state.tick_size}")

    # Determine which token to quote based on config
    if config.QUOTE_SIDE == "YES":
        shared_state.active_token = shared_state.y_token
        logging.info(f"Quoting YES token: {shared_state.active_token[:16]}...")
    else:
        shared_state.active_token = shared_state.n_token
        logging.info(f"Quoting NO token: {shared_state.active_token[:16]}...")

    # Initialize orderbooks (we still need both for market data)
    shared_state.orderbook_y = Orderbook()
    shared_state.orderbook_n = Orderbook()

    # Set active orderbook reference
    if config.QUOTE_SIDE == "YES":
        shared_state.active_orderbook = shared_state.orderbook_y
    else:
        shared_state.active_orderbook = shared_state.orderbook_n

    # Initialize positions
    shared_state.position_y = Position(price=0, size=0, token=shared_state.y_token)
    shared_state.position_n = Position(price=0, size=0, token=shared_state.n_token)

    # Initialize inventory manager with active position
    shared_state.inventory_manager = InventoryManager()
    if config.QUOTE_SIDE == "YES":
        shared_state.inventory_manager.set_position(shared_state.position_y)
    else:
        shared_state.inventory_manager.set_position(shared_state.position_n)

    # Initialize pricer and order manager
    shared_state.pricer = Pricer()
    shared_state.ordermanager = OrderManager()

    logging.info("All dependencies initialized")


async def run_trading_bot():
    """Main async entry point."""
    try:
        initialize_dependencies()

        logging.info(f"Starting market making bot for market: {config.MARKET}")
        logging.info(f"Max inventory: ${config.MAX_INVENTORY_USD}")
        logging.info(f"Base order size: {config.BASE_ORDER_SIZE}")
        logging.info(f"Quoting side: {config.QUOTE_SIDE}")

        # Run both WebSocket connections
        # - User channel for our order/trade updates
        # - Market channel for orderbook data (only subscribe to active token)
        await asyncio.gather(
            shared_state.clientws_user.run(
                channel_type=ChannelType.USER.value,
                markets=[config.MARKET]
            ),
            shared_state.clientws_market.run(
                channel_type=ChannelType.MARKET.value,
                asset_ids=[shared_state.active_token]
            )
        )

    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received, shutting down...")
    except Exception as e:
        logging.error(f"EXCEPTION: {e}", exc_info=True)
    finally:
        # Clean up - cancel all orders
        try:
            shared_state.client.cancel_all()
            logging.info("Cancelled all orders on shutdown")
        except Exception as e:
            logging.error(f"Error cancelling orders on shutdown: {e}")


if __name__ == "__main__":
    setup_logging()
    asyncio.run(run_trading_bot())