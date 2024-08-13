import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from uniswapyv3.utils import generate_poisson_arrivals
from uniswapyv3.pool import LiquidityPool

NUM_SIMULATIONS = 3000

# Initialize parameters
INITIAL_PRICE = 3000
FEE_RATE = 0.0005

# Create liquidity providers with initial reserves and prices
PRICE_RANGES = [
    (2800, 3000),
    (2500, 3500),
    (1000, 5000),
]
PORTFOLIO_VALUE = 100
TIME = 24
LAMBDA_PARAM = 222
MU = 0.00005
SIGMA = 0.0007



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
        tick_size = 1.001,
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


# Set the style and plot as originally planned
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(1, 2, figsize=(14, 10))
fig.suptitle('Simulation Results', fontsize=16)

# # Histogram of Prices
# sns.histplot(prices, bins=50, kde=False, color='blue', ax=axes[0, 0])
# axes[0, 0].set_title('Histogram of Prices')
# axes[0, 0].set_xlabel('Prices')
# axes[0, 0].set_ylabel('Frequency')

# Histogram of Impermanent Losses
sns.histplot(impermanent_losses, bins=100, kde=True, ax=axes[0])
axes[0].set_title('Impermanent loss distribution')
axes[0].set_xlabel('Prices')

# Histograms of fees collected, and total returns
sns.histplot(fees_collected, bins=100, kde=False, ax=axes[1])
axes[1].set_title('Fees distribution')
axes[1].set_xlabel('Fees Collected')

plt.tight_layout(rect=(0, 0, 1, 0.96))
plt.savefig(f'figures/il_taxes_T={TIME}_sigma={SIGMA}_mu={MU}.png', dpi=300)
plt.show()

fig, axes = plt.subplots(1, 1, figsize=(14, 10))
sns.histplot(total_return, bins=100, kde=True, ax=axes)
axes.set_title('Total Return distribution')
axes.set_xlabel('Total return')

plt.tight_layout(rect=(0, 0, 1, 0.96))
plt.savefig(f'figures/results_T={TIME}_sigma={SIGMA}_mu={MU}.png', dpi=300)
plt.show()