# Import necessary libraries
from uniswapyv3.pool import LiquidityPool

# Assuming the classes LiquidityPool and LiquidityProvider have already been defined as provided

# Create a liquidity pool with specified parameters
pool = LiquidityPool(tick_space=10, fee=0.003, tick_size=1.0001,initial_price=15)

# Add the provider to the liquidity pool
position = pool.open_position(13,17,100)

position2 = pool.open_position(13,30,100)

print('--------------------------------')
print(f'Initial price in pool: {pool.sqrt_price**2}\n')

# Print initial state of the pool
print(f"Initial liquidity in pool: {pool.liquidity}")
print(f"Position 1 liquidity: {position.liquidity}")
print(f"Position 2 liquidity: {position2.liquidity}")

print(f"Initial price in pool: {pool.sqrt_price**2}")
print(f"Initial x y for provider 1: {position.x, position.y}")
print(f"Initial x y for provider 2: {position2.x, position2.y}")



# Update the price in the pool to simulate market movement
pool.update_price(new_price=30)
print('--------------------------------')
print(f'New price in pool: {pool.sqrt_price**2} \n')
# Calculate impermanent loss after the price update
impermanent_loss = position.calculate_il()
impermanent_loss2 = position2.calculate_il()

print(f"Final x y for provider 1: {position.x, position.y}")
print(f"Final x y for provider 2: {position2.x, position2.y}")
print(f"Impermanent loss for the provider 1: {impermanent_loss}")
print(f"Impermanent loss for the provider 2: {impermanent_loss2}")
print(f"Taxes for the provider 1: {position.fees}")
print(f"Taxes for the provider 2: {position2.fees}")
