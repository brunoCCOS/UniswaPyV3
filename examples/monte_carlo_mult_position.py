import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from uniswapyv3.utils import generate_poisson_arrivals
from uniswapyv3.pool import LiquidityPool
# import pool


NUM_SIMULATIONS = 1000

# Initialize parameters
INITIAL_PRICE = 3000
FEE_RATE = 0.0005

# Create liquidity providers with initial reserves and prices
PRICE_RANGES = [
    (INITIAL_PRICE/1.5, INITIAL_PRICE*1.5),
    (INITIAL_PRICE/2, INITIAL_PRICE*2),
    (INITIAL_PRICE/3, INITIAL_PRICE*3),
]
PORTFOLIO_VALUE = 100
TIME = 24*7
LAMBDA_PARAM = 222
MU = 0.00005
SIGMA = 0.07



keys = [f'{pr[0]}-{pr[1]}' for pr in PRICE_RANGES]

# Initialize lists to store results
impermanent_losses = {key : [] for key in keys}
fees_collected = {key : [] for key in keys}
total_return = {key : [] for key in keys}

all_prices = []


for _ in range(NUM_SIMULATIONS):
    arrival_times = generate_poisson_arrivals(LAMBDA_PARAM, TIME)
    price = INITIAL_PRICE

    # Create a liquidity pool with specified parameters
    pool = LiquidityPool(
        tick_space = 2,
        fee = 0.003,
        tick_size = 1.0001,
        initial_price = INITIAL_PRICE,
    )

    # Add the provider to the liquidity pool
    positions = [
            pool.open_position(*price_range,V = PORTFOLIO_VALUE) for price_range in PRICE_RANGES
    ]

    for t in range(1, len(arrival_times)):
        dt = arrival_times[t] - arrival_times[t-1]
        dW = np.random.normal(0, np.sqrt(dt))
        price =  price * (1 + MU * dt + SIGMA * dW)
        pool.update_price(new_price=price)

    for idx, key in enumerate(keys):
        impermanent_losses[key].append(positions[idx].calculate_il())
        total_return[key].append(positions[idx].calculate_total_return())
        fees_collected[key].append(positions[idx].fees_withdraw)


# Set the ggplot style
plt.style.use('fast')
sns.set_palette("muted")

# Create the first set of histograms
fig, axes = plt.subplots(1, 2, figsize=(14, 10))
fig.suptitle('Simulation Results', fontsize=18, weight='bold')

# Histogram of Impermanent Losses
sns.histplot(impermanent_losses, bins=100, kde=True, color='darkblue', ax=axes[0], alpha=0.7)
axes[0].set_title('Impermanent Loss Distribution', fontsize=14)
axes[0].set_xlabel('Prices', fontsize=12)
axes[0].set_ylabel('Frequency', fontsize=12)

# Histogram of Fees Collected
sns.histplot(fees_collected, bins=100, kde=False, color='darkgreen', ax=axes[1], alpha=0.7)
axes[1].set_title('Fees Distribution', fontsize=14)
axes[1].set_xlabel('Fees Collected', fontsize=12)
axes[1].set_ylabel('Frequency', fontsize=12)

# Adjust layout for better spacing
plt.tight_layout(rect=(0, 0, 1, 0.96))

# Save the first figure with high resolution
plt.savefig(f'figures/il_taxes_T={TIME}_sigma={SIGMA}_mu={MU}.png', dpi=300)
plt.show()

# Plot Total Return Distribution
fig, axes = plt.subplots(1, 1, figsize=(14, 10))
sns.histplot(total_return, bins=100, kde=False, color='purple', ax=axes, alpha=0.7)
axes.set_title('Total Return Distribution', fontsize=14)
axes.set_xlabel('Total Return', fontsize=12)
axes.set_ylabel('Frequency', fontsize=12)

# Adjust layout and save the second figure
plt.tight_layout(rect=(0, 0, 1, 0.96))
plt.savefig(f'figures/results_T={TIME}_sigma={SIGMA}_mu={MU}.png', dpi=300)
plt.show()