import asyncio
import json, websockets, asyncio
import WebSocketHandler
import SharedState
#async def main():
    #tasks = [
        #asyncio.create_task(sharedsrate.clientws.connect(channel_type="user")),
        #asyncio.create_task(sharedsrate.clientws.connect(channel_type="market")),
        #asyncio.create_task(sharedsrate.clientws.run(channel_type="market", markets=[sharedsrate.sol_y_token, sharedsrate.sol_n_token])),
        #asyncio.create_task(sharedsrate.clientws.subscribe(channel_type="market", markets=[sharedsrate.sol_y_token, sharedsrate.sol_n_token])),
        #asyncio.create_task(sharedsrate.clientws.listen(channel_type="market", markets=[sharedsrate.sol_y_token, sharedsrate.sol_n_token])),
        #asyncio.create_task(sharedsrate.clientws.subscribe(channel_type="user", markets=[sharedsrate.SOLANA_MARKET])),
        #asyncio.create_task(sharedsrate.clientws.listen(channel_type="user", markets=[sharedsrate.SOLANA_MARKET]))
    #]
    # Wait for all tasks to finish
    #await asyncio.gather(*tasks)

async def run_trading_bot():
    
    try:
        # await main()
        await SharedState.clientws.run(channel_type="market", asset_ids=[SharedState.sol_y_token, SharedState.sol_n_token])
    except Exception as e:
        print(f"EXCEPTION: {e}")
        await SharedState.client.cancel_all()
        print("--- Deleted ALL orders ---")

if __name__ == "__main__":
    asyncio.run(run_trading_bot())

