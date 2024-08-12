import numpy as np

class LiquidityPosition:
    """
    A class to represent a liquidity position in a Uniswap V3 pool.

    Attributes:
    -----------
    min_range : float
        The minimum price range for the position.
    max_range : float
        The maximum price range for the position.
    fees : float
        The fees earned in terms of both tokens.
    current_value : float
        The current value of the portfolio.
    x : float
        The reserve of token X provided by the liquidity provider.
    y : float
        The reserve of token Y provided by the liquidity provider.
    initial_x : float
        The initial reserve of token X.
    initial_y : float
        The initial reserve of token Y.
    liquidity : float
        The amount of liquidity provided by the position.
    pool : LiquidityPool
        The Uniswap V3 pool associated with the position.
    min_tick : int
        The minimum tick range for the position.
    max_tick : int
        The maximum tick range for the position.
    """

    def __init__(self, max_range: float, min_range: float,pool, liquidity: float = 100):
        """
        Initialize a new LiquidityPosition.

        Parameters:
        -----------
        max_range : float
            The maximum price range for the position.
        min_range : float
            The minimum price range for the position.
        pool : LiquidityPool
            The Uniswap V3 pool associated with the position.
        liquidity : float, optional
            The amount of liquidity provided by the position (default is 100).
        """
        self.pool = pool
        self.min_range: float = min_range
        self.max_range: float = max_range
        self.liquidity: float = liquidity
        self.update_reserves()
        self.initial_x: float = self.x
        self.initial_y: float = self.y
        self.fees: np.ndarray = np.array([0.0,0.0])
        self.fees_withdraw: float = 0.0

    def update_reserves(self):
        """
        Update the reserves of token X and Y based on the new price in the pool.
        """
        new_price = self.pool.sqrt_price**2
        if new_price < self.min_range:
            self.x = self.liquidity / np.sqrt(self.min_range) - self.liquidity / np.sqrt(self.max_range)
            self.y = 0
        elif new_price > self.max_range:
            self.x = 0
            self.y = self.liquidity * np.sqrt(self.max_range) - self.liquidity * np.sqrt(self.min_range)
        else:
            self.x = self.liquidity * (1 / np.sqrt(new_price) - 1 / np.sqrt(self.max_range))
            self.y = self.liquidity * (np.sqrt(new_price) - np.sqrt(self.min_range))

    def calculate_value(self) -> float:
        """
        Calculate the current value of the portfolio based on the current price.

        Returns:
        --------
        float
            The current value of the portfolio.
        """
        self.current_value = self.x * self.pool.sqrt_price**2 + self.y
        return self.current_value

    def calculate_initial_value(self) -> float:
        """
        Calculate the initial value of the portfolio based on the initial reserves.

        Returns:
        --------
        float
            The initial value of the portfolio.
        """
        current_price = self.pool.sqrt_price**2
        return self.initial_x * current_price + self.initial_y

    def calculate_il(self) -> float:
        """
        Calculate the impermanent loss for the position.

        Returns:
        --------
        float
            The impermanent loss (IL) of the position.
        """
        self.update_reserves()
        current_value: float = self.calculate_value()
        hodl_value: float = self.calculate_initial_value()
        self.il: float =  (current_value - hodl_value)
        return self.il / hodl_value

    def calculate_total_return(self) -> float:
        """
        Calculate the total return of the position.

        Returns:
        --------
        float
            The total return of the position.
        """
        self.calculate_il()
        hodl_value = self.calculate_initial_value()
        fees = self._withdraw_taxes()
        return ( self.il + fees ) / hodl_value


    def check_tick_range(self, tick: int) -> bool:
        """
        Check if the current price tick is within the acceptable range.

        Parameters:
        -----------
        tick : int
            The current price tick.

        Returns:
        --------
        bool
            True if the tick is within the range, False otherwise.
        """
        return self.min_tick <= tick <= self.max_tick

    def collect_taxes(self, fees_received: np.ndarray):
        """
        Collect fees received and add them to the accumulated fees.

        Parameters:
        -----------
        fees_received : float
            The amount of fees received.
        """
        self.fees += fees_received

    def _withdraw_taxes(self) -> float:
        """
        Withdraw taxes from the current pool.
        """
        self.fees_withdraw = self.fees[0] * self.pool.sqrt_price ** 2 + self.fees[1]
        self.fees = np.array([0.0, 0.0])
        return self.fees_withdraw

    def set_tick_range(self, min_tick: int, max_tick: int):
        """
        Set the acceptable tick range for the position.

        Parameters:
        -----------
        min_tick : int
            The minimum tick range.
        max_tick : int
            The maximum tick range.
        """
        self.min_tick: int = min_tick
        self.max_tick: int = max_tick
        # Update max and min range for the exaclty tick
        self.max_range = self.pool.tick_size ** (max_tick + 1)
        self.min_range = self.pool.tick_size ** min_tick
