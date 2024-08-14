# Import necessary libraries
from uniswapyv3.pool import LiquidityPool

ALPHA = 1.1
INITIAL_PRICE = 1000
PRICES = [INITIAL_PRICE*10,INITIAL_PRICE*100,INITIAL_PRICE*0.1,INITIAL_PRICE*0.01]
# Assuming the classes LiquidityPool and LiquidityProvider have already been defined as provided

# Create a liquidity pool with specified parameters
pool = LiquidityPool(tick_space=10, fee=0.003, tick_size=1.0001,initial_price=INITIAL_PRICE)

# Add the provider to the liquidity pool
position = pool.open_position(INITIAL_PRICE/ALPHA,ALPHA*INITIAL_PRICE,100)

print(f'Lower tick {position.min_tick}, upper tick {position.max_tick}')
print(f'Lower price {position.min_range**2}, upper price {position.max_range**2}')
# Print initial state of the pool
print(f"Initial liquidity in pool: {pool.liquidity}")
print(f"Initial price in pool: {pool.sqrt_price**2}")
print(f"Initial x y: {position.x, position.y}")
print(f'Liqudity {position.liquidity}')


for price in PRICES:
    pool.update_price(new_price=price)
    print('----------------------------------------------------------------')
    print(f'Current price {price}')
    # Calculate the current value of the provider's portfolio at the new price
    current_value = position.calculate_value()
    print(f"Current value of provider's portfolio: {current_value}")

    # Calculate impermanent loss after the price update
    impermanent_loss = position.calculate_il()
    print(f"Taxes earned: {position.fees}")
    print(f"Impermanent loss for the provider: {impermanent_loss}")
    print(f'Total return {position.calculate_total_return()}')
    print(f"x y: {position.x, position.y}")
