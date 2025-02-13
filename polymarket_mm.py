import asyncio
import SharedState
async def run_trading_bot():
    
    try:
        await SharedState.clientws.run(channel_type="user")   
        await SharedState.clientws.run(channel_type="market", asset_ids=[SharedState.sol_y_token, SharedState.sol_n_token])
    except Exception as e:
        print(f"EXCEPTION: {e}")
        SharedState.client.cancel_all()
        print("--- Deleted ALL orders ---")

if __name__ == "__main__":
    asyncio.run(run_trading_bot())