# UniswaPyV3

A small library for emulating a UniswapV3 liquidity pool and liquidity positions in it.


## Code

The code is structured in the following way:

uniswaPyv3/pool.py is the pool class that implements all the functions and calculations that are supposed to be handled by the uniswapV3 pool. Things like accordingly distributing the taxes, updating the price of the assets, and redistributing providers assets along the price curve;

uniswaPyv3/position.py is the pool class that represents an open position in the pool, with a price range and the initial and current value of the assets in the pool. The position is responsible for knowing and calculating its own statistics, like impermanent losses, past and current values, and assets;

uniswaPyv3/utils.py contains some useful functions to perform simulations and arithmetic calculations;

## Examples of usage

Some examples of use are available in the examples folder. There are instructions on how to initialize and use the pool class and open positions. Also, a proper Monte Carlo simulation is implemented to compare different positions.

This library provides functionality to simulate and manage liquidity positions in a Uniswap V3-like liquidity pool. Follow the steps below to use the library in your projects.

### 1. Initialize a Liquidity Pool

First, create an instance of the `LiquidityPool` class by providing the necessary parameters:

```python
from your_module import LiquidityPool

# Initialize the pool with tick space, fee, and initial price
pool = LiquidityPool(tick_space=60, fee=0.003, tick_size=1.0001, initial_price=3000)
```

### 2. Open a Liquidity Position
You can open a liquidity position within a specific price range using the open_position method:

```python
# Open a new position in the pool
position = pool.open_position(min_price=2500, max_price=3500, V=1000)

```

### 3. Update the Pool Price
To update the price in the liquidity pool and distribute fees accordingly, use the update_price method:

```python
# Update the pool price
pool.update_price(new_price=3100)
```

### 4. Manage and Retrieve Liquidity Position Data
After opening a position, you can manage it and retrieve important data, such as current value, impermanent loss, and total return:

```python
# Update reserves based on the current price
position.update_reserves()

# Calculate the current value of the position
current_value = position.calculate_value()

# Calculate impermanent loss (IL)
il = position.calculate_il()

# Calculate total return, including fees
total_return = position.calculate_total_return()
```

### 5. Collect Fees
Fees accumulated during price updates can be collected using the collect_taxes method within the LiquidityPosition class:

```python
# Collect fees from the position
position.collect_taxes(fees_received=np.array([10.0, 5.0]))
```


## Potential applications

- Simulate the perfomance of different price intervals

- Risk analysis of impermanent loss

- Educational purposes for understanding how liquidity provision works in DeFi

- Compare different strategies of provisioning

- Analyze the effects of multilpe fee's levels and their impacts


## Contributions

Possible contributions are the following

- Implement operations to buy and sell specific ammounts of tokens ( only available way to change the pool is by setting a new price and letting the pool adjust accordingly )

- Cleanup and optimization of the code, e.g, changing tick calculation directly to use the sqrt of tick_size instead of powering the price every time

- Add more trackalbe informations to the pool and the position class

- New features like token naming, liquidity shares calculations, modifying price ranges on the fly, etc ...

- Develop tests and documentation

## Credits and Disclaimers

This library is being developed in order to support current academic research going on at the Universidade Federal do Rio de Janeiro (UFRJ). The main purpose of the library will be to provide the necessary tools for research. That being said, it would be of immense pleasure if this library also evolved into something useful for the whole community.
<!-- ### Citing

```
@software{UniswaPyV3,
  author = {Bruno L. Trotti},
  doi = {10.5281/zenodo.6536395},
  license = {MIT License},
  month = {6},
  title = {{UniswaPyV3}},
  url = {https://github.com/brunoCCOS/UniswaPyV3},
  version = {0.1.0},
  year = {2024}
}
``` -->
