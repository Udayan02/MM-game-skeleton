from abc import ABC, abstractmethod
from typing import Tuple

class MarketMaker(ABC):
    @abstractmethod
    def update(self, prevBuy, prevSell) -> Tuple[float, int, float, int]:
        pass

class SimpleMarketMaker(MarketMaker):
        def __init__(self):
             pass

        def update(self, prevBuy, prevSell) -> Tuple[float, int, float, int]:
             return prevBuy, 100, prevSell, 100
