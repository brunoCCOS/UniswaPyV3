import numpy as np
from .position import LiquidityPosition
from .utils import smallest_divisor

class LiquidityPool:
    """
    Represents a liquidity pool which manages liquidity providers, prices, and ticks.
    """

    def __init__(self, tick_space: int, fee: float, tick_size: float = 1.0001, initial_price: float = 3000):
        """
        Initializes a new instance of the LiquidityPool class.

        :param tick_space: The spacing between ticks in the pool.
        :param fee: The transaction fee percentage.
        :param tick_size: The multiplicative factor between successive price ticks.
        :param initial_price: The initial price level in the pool.
        """
        self.sqrt_tick_size: float = np.sqrt(tick_size)  # Price multiplier per tick
        self.tick_space: int = tick_space
        self.fee: float = fee
        self.providers: list[LiquidityPosition] = []  # List to store liquidity providers
        self.lower_tick: int = self._price_to_tick(initial_price / 2)
        self.upper_tick: int = self._price_to_tick(initial_price * 2)  # Tracks the min and max ticks currently available in the pool
        self.ticks_liquidity: np.ndarray = np.zeros((self.upper_tick - self.lower_tick) // self.tick_space + 1)  # Array to store liquidity at each tick
        # Cumulative fees earned per unit of liquidity in each tick's band, for
        # tokens (X, Y). Positions read this lazily instead of being pushed fees
        # on every tick crossing (see LiquidityPosition._accrue_fees).
        self.fee_growth: np.ndarray = np.zeros((self.ticks_liquidity.shape[0], 2))
        self.sqrt_price: float = np.sqrt(initial_price)  # Current price level in the pool
        self.current_tick: int = self._price_to_tick(self.sqrt_price**2)  # Current tick in the pool
        self.liquidity:float = 0

    @staticmethod
    def _calc_delta_x(liquidity: float, current_price: float, future_price: float) -> float:
        return liquidity * (1 / current_price  - 1 / future_price)

    @staticmethod
    def _calc_delta_y(liquidity: float, current_price: float, future_price: float) -> float:
        return liquidity * (current_price - future_price)

    def _fee_amount(self, volume: float, token_index: int) -> np.ndarray:
        """
        Builds the fee vector charged on a traded volume.

        `volume` is the net (post-fee) amount of the input token that flowed
        through a tick. Fees are taken on the gross input, so the fee equals
        volume * fee / (1 - fee). The result is placed in `token_index`
        (0 for token X, 1 for token Y).
        """
        fee = abs(volume) * self.fee / (1 - self.fee)
        fees = np.zeros(2)
        fees[token_index] = fee
        return fees

    @staticmethod
    def _calc_future_price(liquidity: float, current_price: float, tokens: float) -> float:
        if tokens > 0:
            return current_price - liquidity/tokens
        else:
            return current_price - tokens/liquidity

    def open_position(self, min_price: float, max_price: float, V: float) -> LiquidityPosition:
        """
        Opens a new liquidity position within the specified price range.

        :param min_price: The minimum price to offer resources.
        :param max_price: The maximum price to offer resources.
        :param V: The total value in terms of token y, of the resources provided.
        :return: The new open position object.
        """
        max_sqrt_price = np.sqrt(max_price)
        min_sqrt_price = np.sqrt(min_price)

        liquidity = V * ( 1 / (2 * self.sqrt_price - (self.sqrt_price ** 2) / max_sqrt_price  - min_sqrt_price)) # Using the relation V = x * S + y = L( 1/sqrt(S) - 1/sqrt(Su))S + L(sqrt(S) - sqrt(Sl))
        lower_tick, upper_tick = self._initialize_ticks(min_price, max_price)


        position: LiquidityPosition = LiquidityPosition(
            min_tick=lower_tick,
            max_tick=upper_tick,
            liquidity=liquidity,
            pool=self
        )
        self._add_position(position)
        return position

    def _add_position(self, position: LiquidityPosition):
        """
        Adds a new liquidity provider to the pool.

        :param position: The LiquidityPosition object to add to the pool.
        """
        self.providers.append(position)

        lower_idx: int = self._get_tick_index(position.min_tick)
        upper_idx: int = self._get_tick_index(position.max_tick)

        self.ticks_liquidity[lower_idx:upper_idx + 1] += position.liquidity
        self.liquidity += position.liquidity

    def swap(self, token):
        """
        Swap a token ammount

        :param token: Number of tokens to exchange, if positive then exchange token X for Y, if negative, token Y for X
        """
        if token == 0:
            print("Total ammount of tokens must be non-zero")
            return

        current_tick = self.current_tick
        current_price = self.sqrt_price

        # Extracts the fees and the amount of token avaible for swap
        token = token*(1-self.fee)

        # Define the direction of thw swap
        if token > 0:
            direction = 1
        else:
            direction = -1

        # Dict to store ammount of fees paid in each tick
        fees_dict = {}
        # Define future price as the actual price initially 
        future_price = current_price

        # Deplete all ticks until the swap is fullfilled
        while token > 0:
            current_liquidity = self.ticks_liquidity[current_tick]
            if current_liquidity == 0:
                print("Not enough resources to fullfill the swap")
                return

            
            # If buying token X, price goes UP
            if direction == 1:
                # Get the max betwen the price inside the tick and the target price
                # of the swap, if the target price is below, that means that the Swap
                # does not cross any tick, otherwise we need to make the swap within
                # the current tick and then waste the rest in next tick
                future_price = max(
                    self._tick_to_sqrt_price(current_tick + self.tick_space),
                    self._calc_future_price(current_liquidity,current_price,token)
                    )
                delta = self._calc_delta_y(current_liquidity,current_price,future_price)
                fees_dict[current_tick] = np.array([0,delta / (delta*(1-self.fee))])
            # Else if buying token Y, price goes down
            else:
                # Get the min betwen the price inside the tick and the target price
                # of the swap, if the target price is above, that means that the Swap
                # does not cross any tick_space
                future_price = min(
                    self._tick_to_sqrt_price(current_tick),
                    self._calc_future_price(current_liquidity,current_price,token)
                    )
                delta = self._calc_delta_x(current_liquidity,current_price,future_price)
                fees_dict[current_tick] = np.array([delta / (delta*(1-self.fee)),0])

            # Remove the amount of tokens already swaped from the remaining total
            token -= delta

        # IF the entire trade succeed then modify the values of the pool
        
        #Distribute the fees in each tick
        for tick,fees_paid in fees_dict.items():
            self._distribute_fees(self.current_tick, fees_paid, self.ticks_liquidity[tick])
        self.sqrt_price = future_price

    def update_price(self, new_price: float):
        """
        Updates the price in the pool and triggers fee collection based on price movement.

        :param new_price: The new price to update in the pool.
        """
        new_tick = self._price_to_tick(new_price)

        # The target tick must lie inside the currently tracked tick range,
        # otherwise the swap would walk off the end of the liquidity array.
        if not (self.lower_tick <= new_tick <= self.upper_tick):
            print("Not enough resources to fullfill the trade")
            print("The desired price is outside the range with liquidity")
            return

        # Check that every tick between the current price and the target has
        # liquidity; a gap means the trade cannot be completed.
        lo_idx = self._get_tick_index(min(self.current_tick, new_tick))
        hi_idx = self._get_tick_index(max(self.current_tick, new_tick))
        if np.any(self.ticks_liquidity[lo_idx:hi_idx + 1] == 0):
            print("Not enough resources to fullfill the trade")
            print("One of the ticks betwen the current price and the desired spot are wihtout liquidity")
            return

        current_sqrt_price = self.sqrt_price
        target_sqrt_price = np.sqrt(new_price)
        direction = 1 if new_price > current_sqrt_price ** 2 else -1
        fee_factor = self.fee / (1 - self.fee)

        # Every band between the current and target ticks is (partially) crossed.
        # The fee earned per unit of liquidity in a band is
        #     fee/(1-fee) * (sqrt-price width traversed in that band),
        # because the tick's liquidity cancels between the fee (~L*width) and
        # the per-liquidity normalisation. This lets us update all crossed
        # bands with vectorised numpy operations instead of a Python loop.
        low_tick = min(self.current_tick, new_tick)
        high_tick = max(self.current_tick, new_tick)
        band_ticks = np.arange(low_tick, high_tick + self.tick_space, self.tick_space)
        indices = (band_ticks - self.lower_tick) // self.tick_space

        lower_edges = self.sqrt_tick_size ** band_ticks
        upper_edges = self.sqrt_tick_size ** (band_ticks + self.tick_space)

        lo_price = min(current_sqrt_price, target_sqrt_price)
        hi_price = max(current_sqrt_price, target_sqrt_price)
        seg_lo = np.maximum(lower_edges, lo_price)
        seg_hi = np.minimum(upper_edges, hi_price)
        mask = seg_hi > seg_lo  # bands actually traversed

        if direction == 1:
            # Price up: swappers pay token Y; fee growth ~ width in sqrt-price.
            self.fee_growth[indices[mask], 1] += fee_factor * (seg_hi[mask] - seg_lo[mask])
        else:
            # Price down: swappers pay token X; fee growth ~ width in 1/sqrt-price.
            self.fee_growth[indices[mask], 0] += fee_factor * (1.0 / seg_lo[mask] - 1.0 / seg_hi[mask])

        self.current_tick = new_tick
        self.sqrt_price = target_sqrt_price




    def _distribute_fees(self, tick: int, fees_paid: np.ndarray, tick_liquidity: float) -> None:
        """
        Distributes fees to the liquidity providers based on their participation in the pool.

        :param tick: The current tick.
        :param fees_paid: The total fees collected.
        :param tick_liquidity: The liquidity at the current tick.
        """
        for provider in self.providers:
            if provider.check_tick_range(tick):
                participation = provider.liquidity / tick_liquidity
                provider.collect_taxes(participation * fees_paid)

    def _get_tick_index(self, tick: int) -> int:
        """
        Calculates the index of a tick in the ticks_liquidity array.

        :param tick: The tick to find the index for.
        :return: The index of the tick.
        """
        return abs((tick - self.lower_tick)) // self.tick_space

    def _get_index_tick(self, index: int) -> int:
        """
        Calculates the tick based on the index in the ticks_liquidity array.

        :param index: The index to convert to a tick.
        :return: The corresponding tick.
        """
        return self.lower_tick + index * self.tick_space

    def _initialize_ticks(self, lower_price: float, upper_price: float) -> tuple[int, int]:
        """
        Initializes ticks for a new liquidity provider based on their price range.

        :param lower_price: The lower bound of the price range.
        :param upper_price: The upper bound of the price range.
        :return: A tuple containing the lower and upper ticks.
        """
        lower_tick: int = self._price_to_tick(lower_price)
        upper_tick: int = self._price_to_tick(upper_price)

        # Extend the ticks_liquidity array to accommodate new ticks if necessary.
        # fee_growth is grown in lockstep so a tick's index maps to the same
        # entry in both arrays.
        if upper_tick > self.upper_tick:
            pad = (upper_tick - self.upper_tick) // self.tick_space
            self.ticks_liquidity = np.append(self.ticks_liquidity, np.zeros(pad))
            self.fee_growth = np.vstack([self.fee_growth, np.zeros((pad, 2))])
            self.upper_tick = upper_tick
        if lower_tick < self.lower_tick:
            pad = (self.lower_tick - lower_tick) // self.tick_space
            self.ticks_liquidity = np.append(np.zeros(pad), self.ticks_liquidity)
            self.fee_growth = np.vstack([np.zeros((pad, 2)), self.fee_growth])
            self.lower_tick = lower_tick

        return lower_tick, upper_tick

    def _tick_to_sqrt_price(self, tick: int) -> float:
        """
        Converts a tick value to a price.

        :param tick: The tick to convert.
        :return: The price corresponding to the tick.
        """
        return self.sqrt_tick_size ** tick

    def _price_to_tick(self, price: float) -> int:
        """
        Converts a price to the nearest tick.

        :param price: The price to convert.
        :return: The nearest tick corresponding to the price.
        """
        power_value = np.log(price) / np.log(self.sqrt_tick_size) / 2
        return smallest_divisor(power_value, self.tick_space)

    def _get_tick_liquidity(self, tick: int) -> float:
        """
        Retrieves the liquidity at a specific tick.

        :param tick: The tick to check.
        :return: The liquidity at the specified tick.
        """
        tick_idx = self._get_tick_index(tick)
        return self.ticks_liquidity[tick_idx]        
