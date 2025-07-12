import yfinance as yf
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
import numpy as np
import pandas as pd

class CryptoAI:
    def __init__(self, dataScraper, date):
        self.date = date
        self.dataScraper = dataScraper
        self.model = GaussianProcessRegressor(
            kernel=C(1.0, (1e-3, 1e3)) * RBF(10, (1e-2, 1e2)),
            n_restarts_optimizer=10,
            random_state=42
        )
        self.trained = False
        self.train_length = 0
        self.lag_periods = 5

    def train(self):
        curr_date = pd.Timestamp(self.date)
        start_date = curr_date - pd.DateOffset(years=5)
        data = self.dataScraper.data.loc[
            (self.dataScraper.data.index >= start_date) & (self.dataScraper.data.index <= curr_date)
        ]
        closes = data["Close"].values.astype(float)

        effective_lags = min(self.lag_periods, max(1, len(closes) - 1))
        if effective_lags < 1 or len(closes) <= effective_lags:
            self.trained = False
            return

        X = []
        y = []
        for i in range(effective_lags, len(closes)):
            X.append(closes[i - effective_lags:i])
            y.append(closes[i])

        X = np.array(X)
        # Ensure X is always 2D for sklearn
        if X.ndim > 2:
            X = X.reshape((X.shape[0], X.shape[-1]))
        y = np.array(y)

        self.model.fit(X, y)
        self.trained = True
        self.train_length = len(closes)
        self.current_lags = effective_lags

    def predict_next(self):
        if not self.trained:
            self.train()
        if not self.trained:
            return None

        curr_date = pd.Timestamp(self.date)
        start_date = curr_date - pd.DateOffset(years=5)
        data = self.dataScraper.data.loc[
            (self.dataScraper.data.index >= start_date) & (self.dataScraper.data.index <= curr_date)
        ]
        closes = data["Close"].values.astype(float)

        if len(closes) < self.current_lags:
            return None

        last_lags = closes[-self.current_lags:].reshape(1, -1)
        predicted, _ = self.model.predict(last_lags, return_std=True)
        return predicted[0]

    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        curr_close = self.dataScraper.getNumData(curr_index, "Close").item()
        predicted = self.predict_next()
        if predicted is None:
            return False
        return predicted > curr_close

    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        curr_close = self.dataScraper.getNumData(curr_index, "Close").item()
        predicted = self.predict_next()
        if predicted is None:
            return False
        return predicted < curr_close

    def setDate(self, date):
        self.date = date
        self.trained = False

    def getType(self):
        return "Close"