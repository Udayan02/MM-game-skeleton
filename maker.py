from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, Literal
from collections import deque
import numpy as np

@dataclass
class OrderType:
    """
    Data class to represent the order type, which can be either "limit" or "market"
    """
    type: Literal["limit", "market"]
    from_time: int
    to_time: int

    def __init__(self, type: Literal["limit", "market"], from_time: int, to_time: int):
        self.type = type
        self.from_time = from_time
        self.to_time = to_time

    def __str__(self):
        return f"OrderType(type={self.type}, from_time={self.from_time}, to_time={self.to_time})"

    def new_limit_order(from_time: int, to_time: int):
        """
        Create a new limit order with the given from_time and to_time
        """
        return OrderType("limit", from_time, to_time)

    def new_market_order(timestamp: int):
        """
        Create a new market order with the given timestamp
        """
        return OrderType("market", timestamp, timestamp)


class MarketMaker(ABC):
    """
    Abstract class for market maker, where each player will use previous interval data to make decisions
    to buy or sell stocks. The market maker will return the bid and ask prices, and the volume to buy and sell.
    The bid price represents the highest amount a buyer is willing to pay for a stock, 
    while the ask price describes the lowest level at which a seller is willing to sell their shares
    """
    @abstractmethod
    def update(self, prev_bid_price, prev_ask_price, holding, money, timestamp) -> Tuple[float, int, float, int, OrderType]:
        """
        Update the market maker with the previous bid and ask prices, and the timestamp of the current interval,
        and return the new bid and ask prices, and the volume to buy and sell

        There are two type of order you can make each time interval: market order and limit order.

        Market order: an order to buy or sell a stock at the current market price. The buy and sell price
        is determined by the market (not you). Market order doesn't have a time frame. If you are setting the
        next bid price and next ask price for a market order, it will be defaulted to the market bid and ask price.

        Limit order: an order to buy or sell a stock at a specific price or better. 
        A buy limit order can only be executed at the limit price or lower (compare to market ask/sell price), 
        and a sell limit order can only be executed at the limit price or higher (compare to market bid/buy price). 
        Limit order have a time frame, from_time and to_time, which specifies the time interval in which the
        order is valid.

        Market order have higher priority than limit order. If you are setting both market order and limit order
        in a given time interval, the market order will be executed first.

        :param prev_bid_price: the previous bid price
        :param prev_ask_price: the previous ask price
        :param holding: the number of stocks you are holding from previous interval
        :param money: the amount of money you have from previous interval
        :param timestamp: the timestamp of the current (not previous) interval

        :return: a tuple containing the new bid price limit, the volume to buy, the new ask price limit, 
        the volume to sell, and the order type as OrderType object
        """
        pass


class SimpleMarketMaker(MarketMaker):

    def __init__(self, risk_aversion: float = 0.1, base_spread_factor: float = 0.01, volatility_window: int = 10,
                 num_simulations: int = 1000, forecast_horizon: int = 10):
        """
        :param risk_aversion: Adjusts bid and ask prices based on inventory levels.
        :param base_spread_factor: Base factor for determining spread size as a percentage of the mid-price.
        :param volatility_window: Number of recent mid-prices used for volatility calculation.
        :param num_simulations: Number of Monte Carlo simulations to run.
        :param forecast_horizon: Number of future steps for price forecasting.
        """
        self.risk_aversion = risk_aversion
        self.base_spread_factor = base_spread_factor
        self.volatility_window = volatility_window
        self.num_simulations = num_simulations
        self.forecast_horizon = forecast_horizon
        self.mid_prices = deque(maxlen=volatility_window)

    def simulate_price_paths(self, current_price: float, volatility: float) -> np.ndarray:
        """
        Simulate future price paths using Geometric Brownian Motion (GBM).
        """
        dt = 1  # Time step
        drift = 0  # Assumes no drift
        random_shocks = np.random.normal(
            0, 1, (self.forecast_horizon, self.num_simulations))
        price_paths = np.zeros(
            (self.forecast_horizon + 1, self.num_simulations))
        price_paths[0] = current_price

        for t in range(1, self.forecast_horizon + 1):
            price_paths[t] = price_paths[t - 1] * np.exp(
                (drift - 0.5 * volatility**2) * dt + volatility * np.sqrt(dt) * random_shocks[t - 1])

        return price_paths

    def update(self, prev_bid_price, prev_ask_price, holding, money, timestamp) -> Tuple[float, int, float, int, OrderType]:
        """
        Update the bid and ask prices using Monte Carlo simulations with safeguards for invalid values.

        :param prev_bid_price: Previous bid price.
        :param prev_ask_price: Previous ask price.
        :param holding: Current inventory.
        :param money: Current cash.
        :param timestamp: Current time step.
        :return: Tuple of bid price, bid size, ask price, ask size, and order type.
        """
        # Ensure valid inputs
        prev_bid_price = max(0.01, prev_bid_price)
        prev_ask_price = max(0.01, prev_ask_price)

        # Calculate mid-price and update history
        mid_price = (prev_bid_price + prev_ask_price) / 2
        self.mid_prices.append(mid_price)

        # Calculate volatility
        if len(self.mid_prices) > 1:
            volatility = max(0.0001, np.std(self.mid_prices))
        else:
            volatility = 0.01

        # Simulate future price paths
        price_paths = self.simulate_price_paths(mid_price, volatility)
        simulated_bid = np.percentile(price_paths[-1], 10)
        simulated_ask = np.percentile(price_paths[-1], 90)

        # Ensure reasonable bid and ask prices
        simulated_bid = max(0.01, simulated_bid)
        simulated_ask = max(simulated_bid + 0.01, simulated_ask)

        # Adjust for inventory and risk
        inventory_adjustment = self.risk_aversion * holding
        new_bid_price = max(0.01, simulated_bid - inventory_adjustment)
        new_ask_price = max(new_bid_price + 0.01,
                            simulated_ask - inventory_adjustment)

        # Validate plus cap order sizes
        bid_size = max(1, int(money / max(new_bid_price, 0.01)
                       * 0.1)) if new_bid_price > 0 else 0
        ask_size = max(1, abs(holding)) if holding > 0 else 0

        order_type = OrderType.new_limit_order(
            from_time=timestamp, to_time=timestamp + 1)

        return new_bid_price, bid_size, new_ask_price, ask_size, order_type
