import pandas as pd
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
from VWAPDrift import VWAPDrift
from LatencyArbitrage import LatencyArbitrage
from OptionSkewArbitrage import OptionSkewArbitrage
from ADRLocalSharesArb import ADRLocalSharesArb
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
from VolatilityExpansion import VolatilityExpansion
from LiquidityWavefrontScanning import LiquidityWavefrontScanning
from SpectralFractualStrategy import IntradayFractalStrategy
from QuantumEntropyStrategy import QuantumEntropyStrategy
from SuperiorAdaptiveSpreadStrategy import SuperiorAdaptiveSpreadStrategy
csv_path = input("Enter the path to your CSV file: ")
dataScraper = DataScraping()
dataScraper.printData()

strategies = [
    (BasketTrading, {}),
    (SMA_Cross, {}),
    (RSI_Strategy, {}),
    (EMA_Cross, {}),
    (CryptoAI, {}),
    (MeanReversion, {}),
    (AdaptiveSpreadStrategy, {}),
    (LatencyArbitrage, {}),
    (OptionSkewArbitrage, {}),
    (ADRLocalSharesArb, {}),
    (BidAskSpreadCapture, {}),
    (CalendarSpread, {}),
    (ClosingAuctionMomentum, {}),
    (CointegrationTrading, {}),
    (DividendArbitrage, {}),
    (ETFConstituentArb, {}),
    (ETFFuturesArb, {}),
    (FadingLargeOrders, {}),
    (FlashEventResponse, {}),
    (FuturesSpotArb, {}),
    (HiddenMarkovModels, {}),
    (IcebergDetection, {}),
    (LiquidityDetection, {}),
    (MeanReversionSpreads, {}),
    (OpeningRangeBreakout, {}),
    (OrderBookFeatureModels, {}),
    (OrderBookImbalance, {}),
    (OrderFlowMomentum, {}),
    (PairsTrading, {}),
    (PeggedOrders, {}),
    (PricePredictionML, {}),
    (QueuePositioning, {}),
    (ReinforcementLearningExecution, {}),
    (ShortTermMomentum, {}),
    (TriangularArbitrage, {}),
    (VWAPDrift, {}),
    (Alpha1, {}),
    # Add other strategies here as needed
]

strategies = [
    (SuperiorAdaptiveSpreadStrategy, {}),
    (AdaptiveSpreadStrategy, {})
]
import matplotlib.pyplot as plt
import threading

results = []
results_lock = threading.Lock()

def run_strategy(strategy_class, extra_args):
    print(f"\nRunning {strategy_class.__name__}...")
    i = 1
    backTesting = None
    while i < len(dataScraper.data):
        date = dataScraper.getIndex(i)
        strategy = strategy_class(dataScraper, date)
        if backTesting is None:
            backTesting = BackTesting(strategy, 1000, dataScraper, 0, dataScraper.getIndex(20), 900, 0, .02, .50)
        if backTesting.bankrupt():
            print(f"You are broke in {strategy_class.__name__}")
            break
        backTesting.update(date)
        i += 1
    if backTesting:
        with results_lock:
            results.append({
                'name': strategy_class.__name__,
                'portfolio': backTesting.portfolio.copy(),
                'dates': list(dataScraper.data.index)[:len(backTesting.portfolio)]
            })

threads = []
for strategy_class, extra_args in strategies:
    t = threading.Thread(target=run_strategy, args=(strategy_class, extra_args))
    t.start()
    threads.append(t)
for t in threads:
    t.join()

import numpy as np

# Calculate uniform buy-and-hold curve and return
initial_amount = 1000
close_prices = dataScraper.data['Close']
first_price = close_prices.iloc[0]
buy_and_hold_curve = close_prices * (initial_amount / first_price)
buy_and_hold_return = (close_prices.iloc[-1] / close_prices.iloc[0]) - 1

# Plot all strategies on one graph
plt.figure(figsize=(12, 7))
for result in results:
    plt.plot(result['dates'], result['portfolio'], label=result['name'])
plt.plot(close_prices.index, buy_and_hold_curve, label='Buy & Hold', linestyle='--', color='black')
plt.xlabel('Date')
plt.ylabel('Portfolio Value')
plt.title('Strategy Portfolio Comparison')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Create a summary table
summary = []
for result in results:
    portfolio = np.array(result['portfolio'])
    portfolio_series = pd.Series(portfolio)
    daily_returns = portfolio_series.pct_change().dropna()
    avg_daily_return = daily_returns.mean()
    annualized_return = avg_daily_return * 252
    daily_volatility = daily_returns.std()
    annualized_volatility = daily_volatility * np.sqrt(252)
    sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility != 0 else np.nan
    total_return = portfolio[-1] / portfolio[0] - 1
    summary.append({
        'Strategy': result['name'],
        'Final Value': portfolio[-1],
        'Total Return (%)': total_return * 100,
        'Annualized Return (%)': annualized_return * 100,
        'Annualized Volatility (%)': annualized_volatility * 100,
        'Sharpe Ratio': sharpe_ratio,
        'Buy & Hold Return (%)': buy_and_hold_return * 100
    })
    # Print final cash value with strategy name aligned right
    print(f"Final portfolio value: ${portfolio[-1]:,.2f}   |   Strategy: {result['name']}")

summary_df = pd.DataFrame(summary)
if not summary_df.empty and 'Total Return (%)' in summary_df.columns:
    summary_df = summary_df.sort_values(by='Total Return (%)', ascending=False)
    print("\n==== Strategy Performance Summary Table (Sorted by Total Return %) ====")
    print(summary_df.to_string(index=False, float_format='%.2f'))
    print("===========================================\n")
else:
    print("\n==== No strategy results to summarize. ====")




