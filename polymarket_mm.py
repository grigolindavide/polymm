import asyncio
import SharedState

async def main():
    asyncio.create_task(SharedState.clientws.connect(channel_type="user"))
    asyncio.create_task(SharedState.clientws.subscribe(channel_type="markets", markets=[SharedState.sol_y_token,SharedState.sol_n_token]))
    asyncio.create_task(SharedState.clientws.listen(channel_type="markets", markets=[SharedState.sol_y_token,SharedState.sol_n_token]))
    asyncio.create_task(SharedState.clientws.subscribe(channel_type="user", markets=[SharedState.SOLANA_MARKET]))
    asyncio.create_task(SharedState.clientws.listen(channel_type="user", markets=[SharedState.SOLANA_MARKET]))

    #sol_orderbooks = client.get_order_books([BookParams(token_id=sol_y_token), BookParams(token_id=sol_n_token)])

    #price = pricer.calculate_price(sol_orderbooks[0], position_y, SOLANA_MARKET)
    #size = pricer.calculate_size(sol_orderbooks[0], position_y)

    #buy_orders = ordermanager.send_order(price[0], size[0], BUY, sol_y_token)
    #print(f"Sent order buy at price: {price[0]} with size {size[0]}")
    #sell_orders = ordermanager.send_order(price[1], size[1], BUY, sol_n_token)
    #print(f"Sent order buy at price: {price[1]} with size {size[1]}")

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
