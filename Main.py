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


userTicker = input("Enter a valid Ticker: ")
userStart = input("Enter a valid start date: ")
userEnd = input("Enter a valid end date: ")

dataScraper = DataScraping(userTicker, userStart, userEnd)
dataScraper.printData()

strategy = BasketTrading(dataScraper, userStart)
backTesting = BackTesting(strategy, 1000, dataScraper, 0, dataScraper.getIndex(20), 900,0,.02,.50)

i = 1

while(i < len(dataScraper.data)):

    if(backTesting.bankrupt()):
        print("you are broke")
        break

    date = dataScraper.getIndex(i)
    backTesting.update(date)
    i+=1




print(backTesting.portfolio)


backTesting.displayData()




