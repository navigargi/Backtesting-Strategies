from DataScraping import DataScraping
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


class BackTesting:
    def __init__(self, strategy, amount, dataScraper, transactionCost, date, buyAmount, extraCosts, drawDown, drawUp):
        self.initialAmount = amount
        self.stocks = 0
        self.dataScraper = dataScraper
        self.strategy = strategy
        self.cash = amount
        self.transactionCost = transactionCost
        self.date = date
        self.portfolio = []
        self.i = 0
        self.listBuy = []
        self.closePrice = []
        self.numStocks = []
        self.numCash = []
        self.buyAmount = buyAmount
        self.extraCosts = extraCosts
        self.initialBuyAmount = buyAmount
        self.drawDown = drawDown
        self.drawUp = drawUp
        self.buyHold = []

    def checkCash(self, amount):
        return self.cash >= amount
    def buy(self):

        price = self.dataScraper.getDateData(self.date, self.strategy.getType()).iloc[0]
        if self.strategy.buy() and self.cash > self.buyAmount + self.extraCosts*self.buyAmount:
            print("                                               TRUE BUY")
            self.i = 1
            self.cash -= self.buyAmount + self.extraCosts * self.buyAmount
            self.stocks += self.buyAmount/(float(self.dataScraper.getDateData(self.date, self.strategy.getType()).iloc[0]))
    def sell(self):
        if(self.strategy.sell() and self.stocks > 0):
            print("                                               TRUE SELL")
            self.i = 2
            self.cash += float(self.dataScraper.getDateData(self.date, self.strategy.getType()).iloc[0]) * self.stocks - self.extraCosts * float(self.dataScraper.getDateData(self.date, self.strategy.getType()).iloc[0])
            self.stocks = 0

    def sellA(self):
        print("                                               TRUE SELL")
        self.i = 2
        self.cash += float(self.dataScraper.getDateData(self.date, self.strategy.getType()).iloc[
                               0]) * self.stocks - self.extraCosts * float(
            self.dataScraper.getDateData(self.date, self.strategy.getType()).iloc[0])
        self.stocks = 0

    def update(self, date):
        if(self.cash >= self.initialBuyAmount):
            self.buyAmount = self.initialBuyAmount
        while(self.cash < (self.buyAmount + self.buyAmount*self.extraCosts)):
            self.buyAmount -= 1
        self.date = date
        self.strategy.setDate(date)
        self.buy()
        self.sell()
        print("cash: " + str(self.cash))
        if not self.portfolio:
            pass
        else:
            if (self.cash + self.stocks * float(self.dataScraper.getDateData(self.date, self.strategy.getType()).iloc[0])) < ((1-self.drawDown)*(self.portfolio[-1])):
                print("                                    LOSS")
                self.sellA()
            elif (self.cash + self.stocks * float(self.dataScraper.getDateData(self.date, self.strategy.getType()).iloc[0])) > ((1+self.drawUp)*(self.portfolio[-1])):
                print("                                     PROFIT")
                self.sellA()

        self.portfolio.append(self.cash + self.stocks * float(self.dataScraper.getDateData(self.date, self.strategy.getType()).iloc[0]))
        print(date)
        if(self.i == 1):
            self.listBuy.append("Buy")
        elif(self.i == 2):
            self.listBuy.append("Sell")
        else:
            self.listBuy.append("Nothing")
        self.i = 0
        self.closePrice.append(float(self.dataScraper.getDateData(self.date, self.strategy.getType()).iloc[0]))
        self.numStocks.append(self.stocks)
        self.numCash.append(self.cash)


    def bankrupt(self):
        return self.cash <= 0

    def displayData(self):
        pd.set_option('display.max_rows', None)
        index_list = list(self.dataScraper.data.index)
        combined_list = list(zip(index_list, self.portfolio))
        df = pd.DataFrame(combined_list, columns=['Date', 'Portfolio'])
        df['Action'] = self.listBuy
        df['Price'] = self.closePrice
        df['Num Prices'] = self.numStocks
        df['Cash'] = self.numCash

        first_price = df['Price'].iloc[0]
        factor = self.initialAmount/first_price

        df["Buy and Hold"] = df["Price"] * factor

        print(df)

        portfolio_series = pd.Series(self.portfolio)

        daily_returns = portfolio_series.pct_change().dropna()

        avg_daily_return = daily_returns.mean()

        annualized_return = avg_daily_return * 252

        daily_volatility = daily_returns.std()

        annualized_volatility = daily_volatility * np.sqrt(252)


        buyAndHoldReturns = df["Buy and Hold"].iloc[-1] / df["Buy and Hold"].iloc[0] - 1

        if annualized_volatility != 0:
            sharpe_ratio = annualized_return / annualized_volatility
        else:
            sharpe_ratio = np.nan



        # Print summary
        print("==== Strategy Performance Summary ====")
        print("Profits $" + str(self.portfolio[-1] - self.portfolio[0]))
        print(f"Total Return: {portfolio_series.iloc[-1] / portfolio_series.iloc[0] - 1:.2%}")
        print(f"Annualized Return: {annualized_return:.2%}")
        print(f"Annualized Volatility: {annualized_volatility:.2%}")
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
        print("=====================================")



        plt.figure(figsize=(10, 6))
        textstr = '\n'.join((
            f'Profits: ${self.portfolio[-1] - self.portfolio[0]:.2f}',
            f'Total Return: {portfolio_series.iloc[-1] / portfolio_series.iloc[0] - 1:.2%}',
            f'Annualized Return: {annualized_return:.2%}',
            f'Annualized Volatility: {annualized_volatility:.2%}',
            f'Sharpe Ratio: {sharpe_ratio:.2f}',
            f'Buy and Hold vs Strategy: {buyAndHoldReturns:.2%}'
        ))

        # place the text box in the upper left corner
        plt.gca().text(
            0.02, 0.98, textstr,
            transform=plt.gca().transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
        )

        listC = [self.initialAmount] + self.portfolio
        plt.plot(df["Date"].tolist(), df['Portfolio'].tolist())
        plt.plot(df["Date"].tolist(), df['Buy and Hold'].tolist())



        buy_mask = df['Action'] == 'Buy'
        sell_mask = df['Action'] == 'Sell'

        plt.scatter(df.loc[buy_mask, 'Date'], df.loc[buy_mask, 'Portfolio'], color='green', s=20, label='Buy')
        plt.scatter(df.loc[sell_mask, 'Date'], df.loc[sell_mask, 'Portfolio'], color='red', s=20, label='Sell')
        plt.show()





