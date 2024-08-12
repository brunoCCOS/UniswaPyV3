# UniswaPyV3

A small library for emulating a UniswapV3 liquidity pool and liquidity positions in it.


## Code

The code is structured in the following way:

uniswaPyv3/pool.py is the pool class that implements all the functions and calculations that are supposed to be handled by the uniswapV3 pool. Things like accordingly distribute the taxes, update price of the assets, and redistributing providers assets along the price curve;

uniswaPyv3/position.py is the pool class that represents a open position in the pool, with a price range and initial and current value of the assets on the pool. The positions is responsable for knowing and calculating it's own statistics, like impermanent loss, past and current values and assets;

uniswaPyv3/utils.py contains some useful functions to perform simulations and arithmetic calculations;

## Examples of usage

Some examples of use are available in examples folder, there is shown how to initialize and use the pool class and open positions. Also a proper monte carlo simulation is imlemented to compare different positions.


### Potential applications

- Simulate the perfomance of different price intervals

- Risk analysis of impermanent loss

- Educational purposes for understanding how liquidity provision works in DeFi

- Compare different strategies of provisioning

- Analyze the effects of multilpe fee's levels and the impacts caused by


## Contributions

Possible contributions are the following

- Implement operations to buy and sell specific ammounts of tokens ( only available way to change the pool is by setting a new price and letting the pool adjust accordingly )

- Cleanup and optimization of the code, e.g, changing tick calculation directly to use the sqrt of tick_size instead of powering the price every time

- Add more trackalbe informations to the pool and the position class

- New features like token naming, liquidity shares calculations, modifying price ranges on the fly, etc ...


## Credits and Disclaimers

This library is being developed in order to support current academical research going on in Universidade Federal do Rio de Janeiro(UFRJ), the main purpose of the library will be to provide the necessay tools to the research, that being sad, it would be of immense pleasure if this library also evolve into something useful for the hole community.

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