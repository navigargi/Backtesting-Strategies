import pandas as pd
import matplotlib.pyplot as plt

from DataScraping import DataScraping
from BackTesting import BackTesting
from Close import Close
from SMACross import SMA_Cross
from RSI_Strategy import RSI_Strategy
from Alpha1 import Alpha1
from EMACross import EMA_Cross
from AI1 import CryptoAI
from MeanReversion import MeanReversion
from AdaptiveSpreadStrategy import AdaptiveSpreadStrategy
from BasketTrading import BasketTrading
from LatencyArbitrage import LatencyArbitrage
from OptionSkewArbitrage import OptionSkewArbitrage
from ADRLocalSharesArb import ADRLocalSharesArb
from Alpha1 import Alpha1
from BidAskSpreadCapture import BidAskSpreadCapture
from CalendarSpread import CalendarSpread
from ClosingAuctionMomentum import ClosingAuctionMomentum
from CointegrationTrading import CointegrationTrading
from DividendArbitrage import DividendArbitrage
from ETFConstituentArb import ETFConstituentArb
from ETFFuturesArb import ETFFuturesArb
from FadingLargeOrders import FadingLargeOrders
from FlashEventResponse import FlashEventResponse
from FuturesSpotArb import FuturesSpotArb
from HiddenMarkovModels import HiddenMarkovModels
from IcebergDetection import IcebergDetection
from LiquidityDetection import LiquidityDetection
from MeanReversionSpreads import MeanReversionSpreads
from OpeningRangeBreakout import OpeningRangeBreakout
from OrderBookFeatureModels import OrderBookFeatureModels
from OrderBookImbalance import OrderBookImbalance
from OrderFlowMomentum import OrderFlowMomentum
from PairsTrading import PairsTrading
from PeggedOrders import PeggedOrders
from PricePredictionML import PricePredictionML
from QueuePositioning import QueuePositioning
from ReinforcementLearningExecution import ReinforcementLearningExecution
from ShortTermMomentum import ShortTermMomentum
from TriangularArbitrage import TriangularArbitrage
from VWAPDrift import VWAPDrift

# Step 1: get user input
userTicker = input("Enter a valid Ticker: ")
userStart = input("Enter a valid start date (YYYY-MM-DD): ")
userEnd = input("Enter a valid end date (YYYY-MM-DD): ")

# Step 2: scrape data
dataScraper = DataScraping(userTicker, userStart, userEnd)
dataScraper.printData()

# Step 3: list of strategies to test
strategy_classes = [
    BasketTrading, SMA_Cross, RSI_Strategy,
    EMA_Cross, CryptoAI, MeanReversion, AdaptiveSpreadStrategy, LatencyArbitrage, OptionSkewArbitrage,
    ADRLocalSharesArb, BidAskSpreadCapture, CalendarSpread,
    ClosingAuctionMomentum, CointegrationTrading, DividendArbitrage,
    ETFConstituentArb, ETFFuturesArb, FadingLargeOrders, FlashEventResponse, FuturesSpotArb,
    HiddenMarkovModels, IcebergDetection, LiquidityDetection, MeanReversionSpreads,
    OpeningRangeBreakout, OrderBookFeatureModels, OrderBookImbalance, OrderFlowMomentum,
    PairsTrading, PeggedOrders, PricePredictionML, QueuePositioning,
    ReinforcementLearningExecution, ShortTermMomentum, TriangularArbitrage, VWAPDrift
]

# Dictionary to store results
all_results = {}

# Step 4: loop over each strategy
for strat_class in strategy_classes:
    print(f"\n=== Running strategy: {strat_class.__name__} ===")

    # Create strategy instance
    strategy = strat_class(dataScraper, userStart)

    # Create backtesting instance
    backTesting = BackTesting(
        strategy,
        1000,  # initial cash
        dataScraper,
        0,
        dataScraper.getIndex(20),  # you can adjust this lookahead window if needed
        900,
        0,
        0.02,
        0.50
    )

    # Run backtest loop
    i = 1
    while i < len(dataScraper.data):
        if backTesting.bankrupt():
            print(f"{strat_class.__name__} went bankrupt")
            break
        date = dataScraper.getIndex(i)
        backTesting.update(date)
        i += 1

    # Save the portfolio (equity curve)
    all_results[strat_class.__name__] = backTesting.portfolio

    # (Optional) show final portfolio value
    print(f"Final portfolio value for {strat_class.__name__}: {backTesting.portfolio[-1]}")

# Step 5: plot all equity curves
plt.figure(figsize=(12, 7))
for name, portfolio in all_results.items():
    plt.plot(portfolio, label=name)
plt.title(f"Equity Curves for {userTicker} ({userStart} to {userEnd})")
plt.xlabel("Time Step (index)")
plt.ylabel("Portfolio Value")
plt.legend()
plt.grid(True)
plt.show()