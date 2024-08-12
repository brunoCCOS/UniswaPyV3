# Import necessary libraries
from uniswapyv3.pool import LiquidityPool
PRICES = (15,30,22,25)
# Assuming the classes LiquidityPool and LiquidityProvider have already been defined as provided

# Create a liquidity pool with specified parameters
pool = LiquidityPool(tick_space=10, fee=0.003, tick_size=1.01,initial_price=13)

# Add the provider to the liquidity pool
position = pool.open_position(10,22,100)

print(f'Lower tick {position.min_tick}, upper tick {position.max_tick}')
print(f'Lower price {position.min_range}, upper price {position.max_range}')
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
    print(f"x y: {position.x, position.y}")
