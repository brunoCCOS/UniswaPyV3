import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from uniswapyv3.utils import generate_poisson_arrivals,simulate_stochastic_process
from uniswapyv3.pool import LiquidityPool

NUM_SIMULATIONS = 1000

# Initialize parameters
INITIAL_PRICE = 3000
FEE_RATE = 0.0005

# Create liquidity providers with initial reserves and prices
PRICE_RANGES = [
    (2800, 3000),
    (2500, 3500),
    (1000, 5000),
]
X_TOKENS = 100
TIME = 24
LAMBDA_PARAM = 222
MU = 0.00005
SIGMA = 0.007



keys = [f'{pr[0]}-{pr[1]}' for pr in PRICE_RANGES]

# Initialize lists to store results
impermanent_losses = {key : [] for key in keys}
fees_collected = {key : [] for key in keys}
all_prices = []


for _ in range(NUM_SIMULATIONS):
    arrival_times = generate_poisson_arrivals(LAMBDA_PARAM, TIME)
    prices = simulate_stochastic_process(MU, SIGMA, INITIAL_PRICE, arrival_times)

    # Create a liquidity pool with specified parameters
    pool = LiquidityPool(
        tick_space = 2,
        fee = 0.003,
        tick_size = 1.01,
        initial_price = INITIAL_PRICE,
    )

    # Add the provider to the liquidity pool
    positions = [
            pool.open_position(*price_range,X_TOKENS) for price_range in PRICE_RANGES
    ]

    for t in range(1, len(arrival_times)):
        new_price = prices[t]
        pool.update_price(new_price=new_price)

    for idx, key in enumerate(keys):
        impermanent_losses[key].append(positions[idx].calculate_il())
        fees_collected[key].append(positions[idx].fees)


total_return = {key: np.array(fees_collected[key]) + np.array(impermanent_losses[key]) for key in keys}

# Set the style and plot as originally planned
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Simulation Results', fontsize=16)

# Histogram of Prices
sns.histplot(prices, bins=50, kde=False, color='blue', ax=axes[0, 0])
axes[0, 0].set_title('Histogram of Prices')
axes[0, 0].set_xlabel('Prices')
axes[0, 0].set_ylabel('Frequency')

# Histogram of Impermanent Losses
sns.histplot(impermanent_losses, bins=100, kde=True, ax=axes[0, 1])
axes[0, 1].set_title('Impermanent loss distribution')
axes[0, 1].set_xlabel('Prices')

# Histograms of fees collected, and total returns
sns.histplot(fees_collected, bins=100, kde=False, ax=axes[1, 0])
axes[1, 0].set_title('Fees distribution')
axes[1, 0].set_xlabel('Fees Collected')

sns.histplot(total_return, bins=100, kde=True, ax=axes[1, 1])
axes[1, 1].set_title('Total Return distribution')
axes[1, 1].set_xlabel('Total return')

plt.tight_layout(rect=(0, 0, 1, 0.96))
# plt.savefig(f'figures/results_T={TIME}_sigma={SIGMA}_mu={MU}.png', dpi=300)
plt.show()