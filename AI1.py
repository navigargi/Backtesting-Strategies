import yfinance as yf
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd

class CryptoAI:
    def __init__(self, dataScraper, date):
        self.date = date
        self.dataScraper = dataScraper
        self.model = LinearRegression()
        self.trained = False
        self.train_length = 0

    def train(self):
        curr_date = pd.Timestamp(self.date)
        start_date = curr_date - pd.DateOffset(years=5)

        # Filter data from dataScraper between start_date and curr_date
        data = self.dataScraper.data.loc[
            (self.dataScraper.data.index >= start_date) & (self.dataScraper.data.index <= curr_date)
        ]

        closes = data["Close"].values.astype(float)
        X = np.arange(len(closes)).reshape(-1, 1)
        y = closes

        self.model.fit(X, y)
        self.trained = True
        self.train_length = len(closes)

    def predict_next(self):
        if not self.trained:
            self.train()

        next_index = np.array([[self.train_length]])
        return self.model.predict(next_index)[0]

    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        curr_close = float(self.dataScraper.getNumData(curr_index, "Close"))
        predicted = self.predict_next()
        return predicted > curr_close

    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        curr_close = float(self.dataScraper.getNumData(curr_index, "Close"))
        predicted = self.predict_next()
        return predicted < curr_close

    def setDate(self, date):
        self.date = date
        self.trained = False  # retrain for new date

    def getType(self):
        return "Close"