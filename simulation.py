from maker import SimpleMarketMaker as MarketMaker
from mm_game import MarketData
from typing import Tuple
from logger import Logger
from datetime import datetime
from math import floor


INTERVAL = 60
INIT_BUY = 100.5
INIT_SELL = 99.5
START_MONEY = 100*1000

class Simulation():
    def __init__(self, maker: MarketMaker):
        self.mm = MarketData(INIT_BUY, INIT_SELL)
        self.start_time = datetime.now()
        log_filename = f"log/{self.start_time.strftime('%Y%m%d_%H%M%S')}.log"
        self.logger = Logger(log_filename)
        self.market_maker = maker
        self.buy = []
        self.mmBuy = [INIT_BUY]
        self.mmSell = [INIT_SELL]
        self.buyVolume = []
        self.sellVolume = []
        self.sell = []
        self.profit = []
        self.holding = 0
        self.money = START_MONEY

    def checkAndUpdate(self, prevBuy, prevSell, logging = False)  -> Tuple[float, int, float, int]:
        buy, vb, sell, vs = self.market_maker.update(prevBuy, prevSell)
        if(buy < 0):
            if(logging):
                self.logger.warning("Buy price is negative, setting volume to 0")
            vb = 0
        if(sell < 0):
            if(logging):
                self.logger.warning("Sell price is negative, setting volume to 0")
            vs = 0
        if(vb < 0):
            if(logging):
                self.logger.warning("Buying negative volume, setting volume to 0")
            vb = 0
        if(vs < 0):
            if(logging):
                self.logger.warning("Selling negative volume, setting volume to 0")
            vs = 0
        if(vs > self.holding):
            if(logging):
                self.logger.warning("Selling more than holding, setting volume to holding")
            vs = self.holding
        return buy, vb, sell, vs
    
    def reset(self):
        self.start_time = datetime.now()
        log_filename = f"log/{self.start_time.strftime('%Y%m%d_%H%M%S')}.log"
        self.logger = Logger(log_filename)
        self.mm = MarketData(INIT_BUY, INIT_SELL)
        self.buy = []
        self.mmBuy = [INIT_BUY]
        self.mmSell = [INIT_SELL]
        self.buyVolume = []
        self.sellVolume = []
        self.sell = []
        self.profit = []
        self.holding = 0

    def run(self, logging = False):

        i = 0
        mmBuy = self.mmBuy[0]
        mmSell = self.mmSell[0]

        if(logging):
            self.logger.log("Simulation Start")
            self.logger.log(f"Start time: {self.start_time}")
            self.logger.log(f"Initial Market: Buy: {mmBuy} Sell: {mmSell}")
            self.logger.spacing()

        while(i < INTERVAL):
            mb, vb, mS, vs = self.checkAndUpdate(mmBuy, mmSell)
            if(logging):
                self.logger.log(f"Interval: {i}")
                self.logger.log(f"Market: Buy: {mmBuy} Sell: {mmSell}")
                self.logger.log(f"Buy: {mb} Volume: {vb} Sell: {mS} Volume: {vs}")

            [mmBuy, mmSell] = self.mm.getNextPrices(mb, vb, mS, vs)

            self.mmBuy.append(mmBuy)
            self.mmSell.append(mmSell)
            
            self.buy.append(mb)
            self.buyVolume.append(vb)
            self.sell.append(mS)
            self.sellVolume.append(vs)

            profit = 0.0
            # buy high selll low
            if mmSell <= mb:
                max_buyable_volume = floor(self.money / mmSell)
                if vb > max_buyable_volume:
                    vb = max_buyable_volume
                    if(logging):
                        self.logger.warning(f"Buying more than available money, setting volume to {vb}") 
                if(logging and vb > 0):
                    self.logger.info(f"Buying at {mb} for {vb}")
                profit += -mmSell * vb
                self.money -= mmSell *vb
                self.holding += vb
            # sell high buy low
            if mmBuy <= mS:
                if(logging and vs > 0):
                    self.logger.info(f"Selling at {mS} with market price at for {vs}")
                profit += (mS - mmBuy) * vs
                self.money += mS * vs
                self.holding -= vs

            self.profit.append(profit)
            if(logging):
                self.logger.log(f"Profit: {self.holding * (self.mmSell[-1]) + self.money - START_MONEY} Current profit: {profit} Holding: {self.holding}")
                self.logger.log(f"Cash: {self.money}")
                self.logger.spacing()
            i += 1
    
    def summarize(self, logging = False):
        print(f"Total profit: {self.holding * (self.mmSell[-1]) + self.money - START_MONEY}")
        print(f"Total holding: {self.holding} at price {self.mmSell[-1]} for a total of {self.holding * self.mmSell[-1]}")
        print(f"Total cash: {self.money}")

        if(logging):
            self.logger.log("Simulation End")
            self.logger.log(f"Total profit: {self.holding * (self.mmSell[-1]) + self.money - START_MONEY}")
            self.logger.log(f"Total cash: {self.money}")
            self.logger.log(f"Total holding: {self.holding} at price {self.mmSell[-1]} for a total of {self.holding * self.mmSell[-1]}")
            self.logger.spacing()

        final = self.holding * (self.mmSell[-1]) + self.money
        print(f"Final Revenue: {final}")
        if(logging):
            self.logger.log(f"Final Revenue: {final}")
            self.logger.spacing()

        self.reset()