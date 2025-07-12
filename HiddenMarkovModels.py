class HiddenMarkovModels:
    def __init__(self, dataScraper, date, lookback=20, regime_threshold=0.6):
        self.date = date
        self.dataScraper = dataScraper
        self.lookback = lookback  # Window for regime detection
        self.regime_threshold = regime_threshold  # Threshold for regime classification
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for regime detection
        if curr_index < self.lookback:
            return False
            
        # In a real Hidden Markov Model implementation, we would:
        # 1. Train an HMM on historical data to identify different market regimes
        # 2. Use the trained model to determine the current regime
        # 3. Apply regime-specific trading rules
        
        # Since we can't actually train an HMM here, we'll simulate one by
        # using statistical properties to identify different market regimes
        
        # Detect the current market regime
        regime = self.detect_regime(curr_index)
        
        # Apply regime-specific trading rules
        if regime == "trending_up":
            # In an uptrend, buy on pullbacks
            return self.is_pullback(curr_index)
        elif regime == "trending_down":
            # In a downtrend, don't buy
            return False
        elif regime == "mean_reverting":
            # In mean-reverting regime, buy when price is below mean
            return self.is_below_mean(curr_index)
        elif regime == "high_volatility":
            # In high volatility, buy only on strong signals
            return self.is_strong_buy_signal(curr_index)
        else:  # "low_volatility"
            # In low volatility, use smaller thresholds for buy signals
            return self.is_mild_buy_signal(curr_index)
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for regime detection
        if curr_index < self.lookback:
            return False
            
        # Detect the current market regime
        regime = self.detect_regime(curr_index)
        
        # Apply regime-specific trading rules
        if regime == "trending_up":
            # In an uptrend, sell only on trend reversal signals
            return self.is_trend_reversal(curr_index)
        elif regime == "trending_down":
            # In a downtrend, sell on rallies
            return self.is_rally(curr_index)
        elif regime == "mean_reverting":
            # In mean-reverting regime, sell when price is above mean
            return self.is_above_mean(curr_index)
        elif regime == "high_volatility":
            # In high volatility, sell on any weakness
            return self.is_weakness(curr_index)
        else:  # "low_volatility"
            # In low volatility, use smaller thresholds for sell signals
            return self.is_mild_sell_signal(curr_index)
    
    def detect_regime(self, end_index):
        """Simulate HMM regime detection using statistical properties"""
        # Calculate key statistical properties
        trend = self.calculate_trend(end_index)
        volatility = self.calculate_volatility(end_index)
        mean_reversion = self.calculate_mean_reversion(end_index)
        
        # Classify the regime based on these properties
        if volatility > self.regime_threshold:
            return "high_volatility"
        elif volatility < 0.5 * self.regime_threshold:
            return "low_volatility"
        elif trend > self.regime_threshold:
            return "trending_up"
        elif trend < -self.regime_threshold:
            return "trending_down"
        elif mean_reversion > self.regime_threshold:
            return "mean_reverting"
        else:
            # Default to low volatility if no clear regime is detected
            return "low_volatility"
    
    def calculate_trend(self, end_index):
        """Calculate the strength of the trend"""
        # Use linear regression slope as a measure of trend strength
        prices = []
        for i in range(end_index - self.lookback + 1, end_index + 1):
            prices.append(float(self.dataScraper.getNumData(i, "Close")))
        
        # Simple linear regression slope calculation
        n = len(prices)
        x = list(range(n))
        mean_x = sum(x) / n
        mean_y = sum(prices) / n
        
        numerator = sum((x[i] - mean_x) * (prices[i] - mean_y) for i in range(n))
        denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0
            
        slope = numerator / denominator
        
        # Normalize by the average price to get a relative trend measure
        normalized_slope = slope * n / mean_y
        
        # Return a value between -1 and 1
        return max(min(normalized_slope, 1.0), -1.0)
    
    def calculate_volatility(self, end_index):
        """Calculate the volatility (normalized standard deviation)"""
        returns = []
        for i in range(end_index - self.lookback + 1, end_index):
            price_t = float(self.dataScraper.getNumData(i, "Close"))
            price_t_1 = float(self.dataScraper.getNumData(i + 1, "Close"))
            returns.append((price_t - price_t_1) / price_t_1)
            
        # Calculate standard deviation
        mean_return = sum(returns) / len(returns)
        sum_squared_diff = sum((r - mean_return) ** 2 for r in returns)
        std_dev = (sum_squared_diff / len(returns)) ** 0.5
        
        # Normalize to [0, 1] range (assuming max volatility of 5%)
        return min(std_dev / 0.05, 1.0)
    
    def calculate_mean_reversion(self, end_index):
        """Calculate the strength of mean reversion"""
        # Use autocorrelation of returns as a measure of mean reversion
        returns = []
        for i in range(end_index - self.lookback + 1, end_index):
            price_t = float(self.dataScraper.getNumData(i, "Close"))
            price_t_1 = float(self.dataScraper.getNumData(i + 1, "Close"))
            returns.append((price_t - price_t_1) / price_t_1)
        
        # Calculate lag-1 autocorrelation
        n = len(returns)
        if n <= 1:
            return 0
            
        mean_return = sum(returns) / n
        
        numerator = sum((returns[i] - mean_return) * (returns[i-1] - mean_return) for i in range(1, n))
        denominator = sum((r - mean_return) ** 2 for r in returns)
        
        if denominator == 0:
            return 0
            
        autocorr = numerator / denominator
        
        # Negative autocorrelation suggests mean reversion
        # Return a value between 0 and 1, where 1 is strong mean reversion
        return max(min(-autocorr, 1.0), 0.0)
    
    def is_pullback(self, end_index):
        """Check if current price is a pullback in an uptrend"""
        current_price = float(self.dataScraper.getNumData(end_index, "Close"))
        
        # Calculate short-term and long-term moving averages
        short_ma = self.calculate_ma(end_index, 5)
        long_ma = self.calculate_ma(end_index, self.lookback)
        
        # Pullback: price is below short MA but long MA is still rising
        prev_long_ma = self.calculate_ma(end_index - 1, self.lookback)
        
        return current_price < short_ma and long_ma > prev_long_ma
    
    def is_rally(self, end_index):
        """Check if current price is a rally in a downtrend"""
        current_price = float(self.dataScraper.getNumData(end_index, "Close"))
        
        # Calculate short-term and long-term moving averages
        short_ma = self.calculate_ma(end_index, 5)
        long_ma = self.calculate_ma(end_index, self.lookback)
        
        # Rally: price is above short MA but long MA is still falling
        prev_long_ma = self.calculate_ma(end_index - 1, self.lookback)
        
        return current_price > short_ma and long_ma < prev_long_ma
    
    def is_below_mean(self, end_index):
        """Check if price is below the mean in a mean-reverting regime"""
        current_price = float(self.dataScraper.getNumData(end_index, "Close"))
        mean_price = self.calculate_ma(end_index, self.lookback)
        
        # Calculate standard deviation
        sum_squared_diff = 0.0
        for i in range(end_index - self.lookback + 1, end_index + 1):
            price = float(self.dataScraper.getNumData(i, "Close"))
            sum_squared_diff += (price - mean_price) ** 2
        std_dev = (sum_squared_diff / self.lookback) ** 0.5
        
        # Price is significantly below mean (more than 1 std dev)
        return current_price < mean_price - 0.8 * std_dev
    
    def is_above_mean(self, end_index):
        """Check if price is above the mean in a mean-reverting regime"""
        current_price = float(self.dataScraper.getNumData(end_index, "Close"))
        mean_price = self.calculate_ma(end_index, self.lookback)
        
        # Calculate standard deviation
        sum_squared_diff = 0.0
        for i in range(end_index - self.lookback + 1, end_index + 1):
            price = float(self.dataScraper.getNumData(i, "Close"))
            sum_squared_diff += (price - mean_price) ** 2
        std_dev = (sum_squared_diff / self.lookback) ** 0.5
        
        # Price is significantly above mean (more than 1 std dev)
        return current_price > mean_price + 0.8 * std_dev
    
    def is_strong_buy_signal(self, end_index):
        """Check for a strong buy signal in high volatility regime"""
        # In high volatility, we want multiple confirming signals
        
        # Check if price is near recent lows
        current_price = float(self.dataScraper.getNumData(end_index, "Close"))
        min_price = float('inf')
        for i in range(end_index - 5, end_index):
            min_price = min(min_price, float(self.dataScraper.getNumData(i, "Low")))
        
        near_lows = current_price < min_price * 1.03  # Within 3% of recent lows
        
        # Check for volume spike
        current_volume = float(self.dataScraper.getNumData(end_index, "Volume"))
        avg_volume = 0.0
        for i in range(end_index - 5, end_index):
            avg_volume += float(self.dataScraper.getNumData(i, "Volume"))
        avg_volume /= 5
        
        volume_spike = current_volume > 1.5 * avg_volume
        
        # Check for bullish candle
        current_open = float(self.dataScraper.getNumData(end_index, "Open"))
        bullish_candle = current_price > current_open
        
        # Need at least 2 out of 3 signals
        signals = [near_lows, volume_spike, bullish_candle]
        return sum(signals) >= 2
    
    def is_weakness(self, end_index):
        """Check for weakness in high volatility regime"""
        # Check for bearish candle
        current_price = float(self.dataScraper.getNumData(end_index, "Close"))
        current_open = float(self.dataScraper.getNumData(end_index, "Open"))
        bearish_candle = current_price < current_open
        
        # Check for lower high
        prev_high = float(self.dataScraper.getNumData(end_index - 1, "High"))
        current_high = float(self.dataScraper.getNumData(end_index, "High"))
        lower_high = current_high < prev_high
        
        # Either signal is enough in high volatility
        return bearish_candle or lower_high
    
    def is_trend_reversal(self, end_index):
        """Check for trend reversal in uptrend"""
        # Calculate short-term and medium-term momentum
        short_momentum = self.calculate_momentum(end_index, 3)
        medium_momentum = self.calculate_momentum(end_index, 10)
        
        # Reversal: short-term momentum turns negative while medium-term is still positive
        return short_momentum < -0.01 and medium_momentum > 0.01
    
    def is_mild_buy_signal(self, end_index):
        """Check for mild buy signal in low volatility regime"""
        # In low volatility, smaller price movements are significant
        
        # Check for two consecutive up days
        current_price = float(self.dataScraper.getNumData(end_index, "Close"))
        prev_price = float(self.dataScraper.getNumData(end_index - 1, "Close"))
        prev_prev_price = float(self.dataScraper.getNumData(end_index - 2, "Close"))
        
        two_up_days = current_price > prev_price and prev_price > prev_prev_price
        
        # Check if price is above short-term MA
        short_ma = self.calculate_ma(end_index, 5)
        above_ma = current_price > short_ma
        
        # Either signal is enough in low volatility
        return two_up_days or above_ma
    
    def is_mild_sell_signal(self, end_index):
        """Check for mild sell signal in low volatility regime"""
        # Check for two consecutive down days
        current_price = float(self.dataScraper.getNumData(end_index, "Close"))
        prev_price = float(self.dataScraper.getNumData(end_index - 1, "Close"))
        prev_prev_price = float(self.dataScraper.getNumData(end_index - 2, "Close"))
        
        two_down_days = current_price < prev_price and prev_price < prev_prev_price
        
        # Check if price is below short-term MA
        short_ma = self.calculate_ma(end_index, 5)
        below_ma = current_price < short_ma
        
        # Either signal is enough in low volatility
        return two_down_days or below_ma
    
    def calculate_ma(self, end_index, window):
        """Calculate moving average for the specified window"""
        sum_prices = 0.0
        for i in range(end_index - window + 1, end_index + 1):
            sum_prices += float(self.dataScraper.getNumData(i, "Close"))
        return sum_prices / window
    
    def calculate_momentum(self, end_index, window):
        """Calculate price momentum over the specified window"""
        current_price = float(self.dataScraper.getNumData(end_index, "Close"))
        past_price = float(self.dataScraper.getNumData(end_index - window, "Close"))
        return (current_price - past_price) / past_price
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"