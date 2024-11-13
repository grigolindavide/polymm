import asyncio
import SharedState

async def main():
    asyncio.create_task(SharedState.clientws.connect(channel_type="user"))
    asyncio.create_task(SharedState.clientws.subscribe(channel_type="markets", markets=[SharedState.sol_y_token,SharedState.sol_n_token]))
    asyncio.create_task(SharedState.clientws.listen(channel_type="markets", markets=[SharedState.sol_y_token,SharedState.sol_n_token]))
    asyncio.create_task(SharedState.clientws.subscribe(channel_type="user", markets=[SharedState.SOLANA_MARKET]))
    asyncio.create_task(SharedState.clientws.listen(channel_type="user", markets=[SharedState.SOLANA_MARKET]))


async def run_trading_bot():
    while True:
        try:
            await main()
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"EXCEPTION: {e}")
            SharedState.client.cancel_all()
            print("--- Deleted ALL orders ---")
            break



if __name__ == "__main__":
    asyncio.run(run_trading_bot())
