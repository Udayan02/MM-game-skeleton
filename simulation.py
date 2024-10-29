from maker import SimpleMarketMaker as MarketMaker
from build.Mmgame import MarketData
from typing import Tuple
from logger import Logger
from datetime import datetime


INTERVAL = 60
INIT_BUY = 100
INIT_SELL = 100

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
        
        i = 0;
        mmBuy = self.mm.getNextBuyPrice()
        mmSell = self.mm.getNextSellPrice()

        if(logging):
            self.logger.log("Simulation Start")
            self.logger.log(f"Start time: {self.start_time}")
            self.logger.log(f"Initial Market: Buy: {mmBuy} Sell: {mmSell}")
            self.logger.spacing()

        borrowed = 0
        while(i <INTERVAL):
            mb, vb, mS, vs = self.checkAndUpdate(mmBuy, mmSell)
            if(logging):
                self.logger.log(f"Interval: {i}")
                self.logger.log(f"Market: Buy: {mmBuy} Sell: {mmSell}")
                self.logger.log(f"Buy: {mb} Volume: {vb} Sell: {mS} Volume: {vs}")
            mmBuy = self.mm.getNextBuyPrice()
            mmSell = self.mm.getNextSellPrice()
            self.mmBuy.append(mmBuy)
            self.mmSell.append(mmSell)
            
            self.buy.append(mb)
            self.buyVolume.append(vb)
            self.sell.append(mS)
            self.sellVolume.append(vs)

            borrowed = self.mmBuy[0] * self.buyVolume[0]
            if(logging):
                if(i == 0):
                    self.logger.log(f"Borrowing initial volume: {borrowed}")

            profit = 0.0
            # buy high selll low
            if mmSell > mb:
                profit += (mmSell - mb) * vb
            # sell high buy low
            if mmBuy < mS:
                profit += (mS - mmBuy) * vs

            self.profit.append(profit)
            self.holding += vb - vs
            if(logging):
                self.logger.log(f"Profit: {sum(self.profit)} Current profit: {profit} Holding: {self.holding}")
                self.logger.spacing()
            i += 1
    
    def summarize(self, logging = False):
        print(f"Total profit: {sum(self.profit)}")
        print(f"Total holding: {self.holding}")

        if(logging):
            self.logger.log("Simulation End")
            self.logger.log(f"Total profit: {sum(self.profit)}")
            self.logger.log(f"Total holding: {self.holding}")
            self.logger.spacing()

        final = sum(self.profit) + self.holding * (self.mmSell[-1]) - self.mmBuy[0] * self.buyVolume[0]
        print(f"Final Profit: {final}")
        if(logging):
            self.logger.log(f"Final Profit: {final}")
            self.logger.spacing()

        self.reset()