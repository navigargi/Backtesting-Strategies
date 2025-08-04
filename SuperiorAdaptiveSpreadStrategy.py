import math
import numpy as np


class SuperiorAdaptiveSpreadStrategy:
    def __init__(self, dataScraper, date,
                 base_spread=0.0002, volatility_window=10,
                 vol_multiplier=2.5, max_spread=0.005,
                 min_volume_ratio=0.7, order_imbalance_threshold=0.3,
                 vwap_deviation_threshold=0.0005):
        """
        Enhanced intraday spread strategy for 1-minute data with 10-minute lookback

        Parameters:
        dataScraper: Data source with OHLCV + order book data
        date: Current datetime (minute granularity)
        base_spread: Base spread percentage (0.02%)
        volatility_window: Minutes for volatility calculation (10 min)
        vol_multiplier: Volatility sensitivity multiplier
        max_spread: Maximum allowable spread (0.5%)
        min_volume_ratio: Minimum volume vs 10-min average
        order_imbalance_threshold: Minimum order book imbalance
        vwap_deviation_threshold: Price deviation from VWAP for entry
        """
        self.date = date
        self.dataScraper = dataScraper
        self.base_spread = base_spread
        self.volatility_window = volatility_window
        self.vol_multiplier = vol_multiplier
        self.max_spread = max_spread
        self.min_volume_ratio = min_volume_ratio
        self.imb_threshold = order_imbalance_threshold
        self.vwap_threshold = vwap_deviation_threshold

    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)

        # Need enough data for calculations
        if curr_index < self.volatility_window:
            return False

        # Calculate Parkinson volatility using 10-minute high-low
        volatility = self.calculate_volatility(curr_index)

        # Adaptive spread with cap
        adaptive_spread = min(
            self.base_spread * (1 + self.vol_multiplier * math.sqrt(volatility)),
            self.max_spread
        )

        # Get current prices
        high_price = float(self.dataScraper.getDateData(self.date, "High"))
        low_price = float(self.dataScraper.getDateData(self.date, "Low"))
        current_close = float(self.dataScraper.getDateData(self.date, "Close"))

        # Calculate market spread
        market_spread = (high_price - low_price) / low_price

        # Volume sufficiency check
        volume_ok = self._check_volume_sufficiency(curr_index)

        # Order imbalance check
        imbalance_ok = self._check_order_imbalance()

        # VWAP deviation check
        vwap_dev_ok = self._check_vwap_deviation("buy", current_close)

        # Buy signal conditions
        return (
                market_spread > adaptive_spread and
                current_close < (low_price + (high_price - low_price) * 0.35) and
                volume_ok and
                imbalance_ok and
                vwap_dev_ok
        )

    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)

        # Need enough data for calculations
        if curr_index < self.volatility_window:
            return False

        # Calculate Parkinson volatility using 10-minute high-low
        volatility = self.calculate_volatility(curr_index)

        # Adaptive spread with cap
        adaptive_spread = min(
            self.base_spread * (1 + self.vol_multiplier * math.sqrt(volatility)),
            self.max_spread
        )

        # Get current prices
        high_price = float(self.dataScraper.getDateData(self.date, "High"))
        low_price = float(self.dataScraper.getDateData(self.date, "Low"))
        current_close = float(self.dataScraper.getDateData(self.date, "Close"))

        # Calculate market spread
        market_spread = (high_price - low_price) / low_price

        # Volume sufficiency check
        volume_ok = self._check_volume_sufficiency(curr_index)

        # Order imbalance check
        imbalance_ok = self._check_order_imbalance(side="sell")

        # VWAP deviation check
        vwap_dev_ok = self._check_vwap_deviation("sell", current_close)

        # Sell signal conditions
        return (
                market_spread > adaptive_spread and
                current_close > (low_price + (high_price - low_price) * 0.55) and
                volume_ok and
                imbalance_ok and
                vwap_dev_ok
        )

    def calculate_volatility(self, end_index):
        """Calculate Parkinson volatility using high-low prices"""
        sum_log_sq = 0.0
        valid_count = 0
        start_index = end_index - self.volatility_window + 1

        for i in range(start_index, end_index + 1):
            high = float(self.dataScraper.getNumData(i, "High"))
            low = float(self.dataScraper.getNumData(i, "Low"))

            if low > 0 and high > low:
                log_hl = math.log(high / low)
                sum_log_sq += log_hl ** 2
                valid_count += 1

        if valid_count < 5:  # Minimum 5 valid bars
            return 0.0

        return math.sqrt(sum_log_sq / (4 * valid_count * math.log(2)))

    def _check_volume_sufficiency(self, curr_index):
        """Ensure sufficient volume relative to recent average"""
        current_vol = float(self.dataScraper.getDateData(self.date, "Volume"))
        volumes = []
        start_index = curr_index - self.volatility_window + 1

        for i in range(start_index, curr_index + 1):
            vol = float(self.dataScraper.getNumData(i, "Volume"))
            volumes.append(vol)

        avg_volume = np.mean(volumes) if volumes else 0
        return current_vol >= avg_volume * self.min_volume_ratio

    def _check_order_imbalance(self, side="buy"):
        """Check order book imbalance condition"""
        try:
            bid_size = float(self.dataScraper.getDateData(self.date, "BidSize"))
            ask_size = float(self.dataScraper.getDateData(self.date, "AskSize"))
            total_size = bid_size + ask_size

            if total_size == 0:
                return False

            imbalance = (bid_size - ask_size) / total_size

            if side == "buy":
                return imbalance > self.imb_threshold
            else:
                return imbalance < -self.imb_threshold
        except:
            # Fallback if order book data not available
            return True

    def _check_vwap_deviation(self, side, close_price):
        """Check VWAP deviation condition"""
        try:
            vwap = float(self.dataScraper.getDateData(self.date, "VWAP"))
            deviation = (close_price - vwap) / vwap

            if side == "buy":
                return deviation < -self.vwap_threshold
            else:
                return deviation > self.vwap_threshold
        except:
            # Fallback if VWAP not available
            return True

    def setDate(self, date):
        self.date = date

    def getType(self):
        return "Close"