import numpy as np
import math
from scipy.stats import linregress
from scipy.fft import fft
from scipy.signal import argrelextrema, savgol_filter


class IntradayFractalStrategy:
    def __init__(self, dataScraper, date,
                 fractal_window=15,
                 volatility_window=5,
                 entropy_window=3,
                 max_position=10):
        self.date = date
        self.dataScraper = dataScraper
        self.fractal_window = fractal_window  # Minutes for fractal calculation
        self.volatility_window = volatility_window  # Minutes for volatility
        self.entropy_window = entropy_window  # Minutes for entropy calculation
        self.max_position = max_position  # Max position size

        # State variables
        self.position = 0
        self.last_signal_time = 0
        self.entry_price = 0
        self.stop_loss = 0

    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)

        # Minimum data requirement
        if curr_index < max(self.fractal_window, self.volatility_window, self.entropy_window) + 5:
            return False

        # Calculate core micro-structure features
        fd = self.compute_fractal_dimension(curr_index)
        volatility = self.compute_volatility(curr_index)
        entropy = self.compute_entropy(curr_index)
        pressure = self.orderbook_pressure(curr_index)

        # Micro-regime detection
        explosive_regime = (fd > 1.25) and (entropy < 0.8) and (volatility > 0.002)
        squeeze_regime = (fd < 1.05) and (pressure > 0.7) and (volatility < 0.005)

        # Position sizing based on regime strength
        position_size = self.calculate_position_size(fd, volatility, entropy)

        # Entry conditions
        if (explosive_regime or squeeze_regime) and self.position < self.max_position:
            if self.position == 0:
                self.entry_price = float(self.dataScraper.getNumData(curr_index, "Close"))
                self.stop_loss = self.calculate_stop_loss(curr_index)
            self.position += position_size
            self.last_signal_time = curr_index
            return True
        return False

    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        if curr_index <= self.last_signal_time + 1:  # Prevent immediate reversal
            return False

        current_price = float(self.dataScraper.getNumData(curr_index, "Close"))

        # Exit conditions
        stop_hit = current_price <= self.stop_loss
        profit_target = current_price >= self.entry_price * 1.003
        volatility_spike = self.compute_volatility(curr_index) > 0.01
        entropy_shift = self.compute_entropy(curr_index) > 0.9

        if self.position > 0 and (stop_hit or profit_target or volatility_spike or entropy_shift):
            self.position = 0
            self.last_signal_time = curr_index
            return True
        return False

    # ------------------- 1-Minute Micro-Structure Indicators ------------------- #
    def compute_fractal_dimension(self, curr_index, method='box'):
        """High-frequency fractal dimension calculation"""
        prices = []
        for i in range(curr_index - self.fractal_window + 1, curr_index + 1):
            prices.append(float(self.dataScraper.getNumData(i, "Close")))

        if method == 'hurst':
            # Higuchi method for short time series
            k_max = min(8, len(prices) // 2)
            L = []
            for k in range(1, k_max + 1):
                Lk = 0
                for m in range(0, k):
                    idx = np.arange(m, len(prices), k)
                    if len(idx) > 1:
                        Lkm = np.sum(np.abs(np.diff(np.take(prices, idx))))
                        Lk += Lkm * (len(prices) - 1) / (len(idx) - 1) / k
                L.append(np.log(Lk / k))
            H, _ = linregress(np.log(range(1, k_max + 1)), L)
            return 2 - H

        else:  # Box-counting method
            # Normalize prices
            min_p, max_p = min(prices), max(prices)
            if max_p - min_p == 0:
                return 1.0
            norm_prices = [(p - min_p) / (max_p - min_p) for p in prices]

            # High-resolution box counting
            box_sizes = [2, 3, 4, 5]
            counts = []
            for size in box_sizes:
                box_count = 0
                for i in range(0, len(norm_prices), size):
                    segment = norm_prices[i:i + size]
                    if segment:
                        min_seg, max_seg = min(segment), max(segment)
                        box_count += math.ceil((max_seg - min_seg) * len(norm_prices) / size)
                counts.append(box_count)

            logs = np.log(np.array([box_sizes, counts]))
            slope, _, _, _, _ = linregress(logs[0], logs[1])
            return slope

    def compute_volatility(self, curr_index):
        """Micro-volatility calculation"""
        prices = []
        for i in range(curr_index - self.volatility_window + 1, curr_index + 1):
            prices.append(float(self.dataScraper.getNumData(i, "Close")))

        returns = np.abs(np.diff(np.log(prices)))
        return np.mean(returns) if len(returns) > 0 else 0

    def compute_entropy(self, curr_index):
        """Sample entropy for market disorder measurement"""
        prices = []
        for i in range(curr_index - self.entropy_window + 1, curr_index + 1):
            prices.append(float(self.dataScraper.getNumData(i, "Close")))

        if len(prices) < 4:
            return 0.5

        # Normalize
        prices = (prices - np.mean(prices)) / np.std(prices)
        m = 2  # Embedding dimension
        r = 0.2 * np.std(prices)  # Tolerance

        # Pattern counts
        patterns = []
        for i in range(len(prices) - m + 1):
            patterns.append(prices[i:i + m])

        # Similarity counts
        B, A = 0, 0
        for i in range(len(patterns)):
            for j in range(i + 1, len(patterns)):
                if np.max(np.abs(patterns[i] - patterns[j])) <= r:
                    B += 1
                if m > 1 and np.max(np.abs(patterns[i][:-1] - patterns[j][:-1])) <= r:
                    A += 1

        if A == 0:
            return 0
        return -np.log(B / A) if B > 0 else 0

    def orderbook_pressure(self, curr_index):
        """Simulated order book pressure (requires L2 data)"""
        # Fallback to volume/price relationship if no order book
        volume_change = []
        price_change = []

        for i in range(curr_index - 3, curr_index + 1):
            if i > 0:
                vol = float(self.dataScraper.getNumData(i, "Volume"))
                prev_vol = float(self.dataScraper.getNumData(i - 1, "Volume"))
                price = float(self.dataScraper.getNumData(i, "Close"))
                prev_price = float(self.dataScraper.getNumData(i - 1, "Close"))

                volume_change.append(vol / prev_vol if prev_vol > 0 else 1)
                price_change.append(price - prev_price)

        if len(price_change) == 0:
            return 0.5

        # Calculate volume-pressure correlation
        corr = np.corrcoef(volume_change, price_change)[0, 1]
        return (corr + 1) / 2  # Normalize to [0,1]

    def calculate_position_size(self, fd, vol, entropy):
        """Dynamic position sizing based on regime strength"""
        # Fractal dimension strength
        fd_strength = min(1.0, max(0, (fd - 1.0) * 5))

        # Entropy confidence
        entropy_confidence = 1 - entropy

        # Combined signal strength
        strength = (fd_strength + entropy_confidence) / 2

        # Volatility scaler (reduce size in high vol)
        vol_scaler = 1.0 / (1 + 100 * vol)

        return max(1, round(strength * vol_scaler * self.max_position))

    def calculate_stop_loss(self, curr_index):
        """Adaptive volatility-based stop loss"""
        prices = []
        for i in range(curr_index - 5, curr_index + 1):
            prices.append(float(self.dataScraper.getNumData(i, "Close")))

        atr = np.mean(np.abs(np.diff(prices)))
        return prices[-1] - 3 * atr

    # ------------------- Utility Methods ------------------- #
    def setDate(self, date):
        self.date = date

    def getType(self):
        return "Close"