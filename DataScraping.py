import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
class DataScraping:
    def __init__(self, ticker, startDate, endDate):
        self.ticker = ticker
        self.startDate = startDate
        self.endDate = endDate
        self.data = yf.download(tickers=ticker, start=startDate, end=endDate)
    def printData(self):
        print(self.data)
    def graphData(self, type):
        plt.figure(figsize = (10,6))
        y = self.data[type].values.flatten()
        sns.lineplot(x=self.data.index, y=y)

        plt.xlabel("Date")
        plt.ylabel(type)
        plt.title(type + " Prices vs Time")

        plt.grid(True)
        plt.xticks(rotation = 45)
        plt.show()
    def getDateData(self, date, type):
        return self.data.loc[date, type]

    def getNumData(self, num, type):
        return self.data.iloc[num][type]

    def getRow(self, date):
        return self.data.index.get_loc(pd.Timestamp(date))

    def getIndex(self, num):
        return self.data.index[num]






