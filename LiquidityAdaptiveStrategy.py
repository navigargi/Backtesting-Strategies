import numpy as np
import math

import numpy as np
import math


class LiquidAd:
    def __init__(self, dataScraper, date,
                 entanglement_window=14,
                 tunneling_window=10,
                 volatility_window=8,
                 trend_window=20,
                 max_risk_per_trade=0.01,  # Max 1% risk per trade
                 profit_target_multiplier=1.5):
        self.date = date
        self.dataScraper = dataScraper
        self.entanglement_window = entanglement_window
        self.tunneling_window = tunneling_window
        self.volatility_window = volatility_window
        self.trend_window = trend_window
        self.max_risk_per_trade = max_risk_per_trade
        self.profit_target_multiplier = profit_target_multiplier

        # State variables
        self.position = 0
        self.entry_price = 0
        self.stop_loss = 0
        self.take_profit = 0
        self.last_trade_index = -100

    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)

        # Check data sufficiency and trade cooldown
        if not self._valid_trade_conditions(curr_index):
            return False

        # Calculate quantum metrics
        entanglement = self.calculate_entanglement(curr_index)
        tunneling_prob = self.calculate_tunneling_probability(curr_index, direction="up")
        volatility = self.calculate_volatility(curr_index)
        trend_strength = self.calculate_trend_strength(curr_index)

        # Additional filters
        volume_ok = self.volume_spike_confirmation(curr_index)
        risk_ok = self.position_size_ok(volatility)

        # Buy conditions
        conditions = (
                entanglement > 0.4 and  # Stronger entanglement requirement
                tunneling_prob > 0.7 and  # Higher tunneling probability
                volatility > 0.003 and  # Minimum volatility
                trend_strength > 0.6 and  # Strong uptrend
                volume_ok and  # Volume confirmation
                risk_ok and  # Risk management
                self.position == 0 and  # Not in position
                curr_index > self.last_trade_index + 5  # Trade cooldown
        )

        if conditions:
            self._enter_long_position(curr_index, volatility)
            return True
        return False

    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)

        # Exit if we're in a position and conditions are met
        if self.position > 0:
            current_price = float(self.dataScraper.getNumData(curr_index, "Close"))

            # Exit conditions
            profit_target_hit = current_price >= self.take_profit
            stop_loss_hit = current_price <= self.stop_loss
            volatility_spike = self.calculate_volatility(curr_index) > 1.5 * self.entry_volatility
            time_exit = curr_index >= self.entry_index + 15  # Max 15 minutes in trade

            if profit_target_hit or stop_loss_hit or volatility_spike or time_exit:
                self.position = 0
                self.last_trade_index = curr_index
                return True
        return False

    def _enter_long_position(self, curr_index, volatility):
        """Execute long position with proper risk management"""
        entry_price = float(self.dataScraper.getNumData(curr_index, "Close"))

        # Calculate position size based on volatility
        atr = self.calculate_atr(curr_index)
        risk_per_share = atr * 1.5  # Stop at 1.5x ATR

        # Position sizing
        position_size = min(
            int(self.max_risk_per_trade / risk_per_share),
            10  # Max position size
        )

        # Set orders
        self.position = position_size
        self.entry_price = entry_price
        self.entry_volatility = volatility
        self.entry_index = curr_index
        self.stop_loss = entry_price - risk_per_share
        self.take_profit = entry_price + risk_per_share * self.profit_target_multiplier

    def _valid_trade_conditions(self, curr_index):
        """Check basic trade validity"""
        min_data = max(self.entanglement_window, self.tunneling_window,
                       self.volatility_window, self.trend_window) + 5
        return curr_index >= min_data

    def calculate_entanglement(self, curr_index):
        """Enhanced entanglement measurement with volume confirmation"""
        # ... (same as previous implementation) ...

    def calculate_tunneling_probability(self, curr_index, direction="up"):
        """More conservative tunneling probability"""
        # ... (same as previous implementation) ...
        # But with adjusted formula:
        if direction == "up":
            # More conservative tunneling probability
            return math.exp(-distance / (volatility * current_price * 2 + 1e-8))
        else:
            return math.exp(-distance / (volatility * current_price * 2 + 1e-8))

    def calculate_volatility(self, curr_index):
        """ATR-based volatility"""
        # ... (same as previous implementation) ...

    def calculate_atr(self, curr_index, window=10):
        """Calculate Average True Range"""
        # ... (same as volatility calculation but returns ATR value) ...

    def calculate_trend_strength(self, curr_index):
        """Measure trend strength using linear regression"""
        prices = []
        for i in range(curr_index - self.trend_window + 1, curr_index + 1):
            prices.append(float(self.dataScraper.getNumData(i, "Close")))

        x = np.arange(len(prices))
        slope, _, r_value, _, _ = linregress(x, prices)

        # Normalize to 0-1 range
        trend_strength = min(1.0, abs(r_value) * 2)  # R² scaled
        return trend_strength if slope > 0 else 0  # Only positive for long trades

    def volume_spike_confirmation(self, curr_index):
        """Confirm with volume spike"""
        volumes = []
        for i in range(curr_index - 5, curr_index + 1):
            volumes.append(float(self.dataScraper.getNumData(i, "Volume")))

        current_vol = volumes[-1]
        avg_vol = np.mean(volumes[:-1])
        return current_vol > 1.8 * avg_vol

    def position_size_ok(self, volatility):
        """Check if volatility allows safe position size"""
        min_atr = 0.002  # Minimum ATR for trading
        max_atr = 0.015  # Maximum ATR for trading
        return min_atr <= volatility <= max_atr

    def setDate(self, date):
        self.date = date

    def getType(self):
        return "Close"