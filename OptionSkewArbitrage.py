class OptionSkewArbitrage:
    def __init__(self, dataScraper, date, lookback=30, vol_window=10, skew_threshold=0.2):
        self.date = date
        self.dataScraper = dataScraper
        self.lookback = lookback  # Window for historical skew calculation
        self.vol_window = vol_window  # Window for volatility calculation
        self.skew_threshold = skew_threshold  # Threshold for skew deviation signals
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for calculations
        if curr_index < self.lookback + self.vol_window:
            return False
            
        # In a real option skew arbitrage strategy, we would:
        # 1. Calculate implied volatility for different strike prices
        # 2. Measure the volatility skew (difference between OTM puts and calls)
        # 3. Identify when the skew is abnormally steep or flat compared to historical patterns
        # 4. Execute trades to exploit the mispricing (e.g., buy underpriced options, sell overpriced ones)
        
        # Since we don't have actual options data, we'll simulate by:
        # - Using historical price movements to estimate realized volatility
        # - Simulating implied volatility skew based on recent price behavior
        # - Identifying abnormal skew patterns that suggest potential mispricing
        
        # Calculate current simulated skew
        current_skew = self.simulate_volatility_skew(curr_index)
        
        # Calculate historical average skew and standard deviation
        historical_skews = []
        for i in range(curr_index - self.lookback, curr_index):
            historical_skews.append(self.simulate_volatility_skew(i))
        
        avg_skew = sum(historical_skews) / len(historical_skews)
        std_dev = (sum((s - avg_skew) ** 2 for s in historical_skews) / len(historical_skews)) ** 0.5
        
        # Calculate z-score of current skew
        z_score = (current_skew - avg_skew) / std_dev if std_dev > 0 else 0
        
        # Buy signal: skew is abnormally flat (z-score < -2)
        # In options markets, this would suggest OTM puts are underpriced relative to OTM calls
        # Since we can only go long the underlying, we'll use this as a buy signal
        # (flat skew often occurs in bullish markets)
        return z_score < -2 and current_skew < avg_skew - self.skew_threshold
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for calculations
        if curr_index < self.lookback + self.vol_window:
            return False
            
        # Calculate current simulated skew
        current_skew = self.simulate_volatility_skew(curr_index)
        
        # Calculate historical average skew and standard deviation
        historical_skews = []
        for i in range(curr_index - self.lookback, curr_index):
            historical_skews.append(self.simulate_volatility_skew(i))
        
        avg_skew = sum(historical_skews) / len(historical_skews)
        std_dev = (sum((s - avg_skew) ** 2 for s in historical_skews) / len(historical_skews)) ** 0.5
        
        # Calculate z-score of current skew
        z_score = (current_skew - avg_skew) / std_dev if std_dev > 0 else 0
        
        # Sell signal: skew is abnormally steep (z-score > 2)
        # In options markets, this would suggest OTM puts are overpriced relative to OTM calls
        # Since we can only go long the underlying, we'll use this as a sell signal
        # (steep skew often occurs in bearish markets or when downside protection is expensive)
        return z_score > 2 and current_skew > avg_skew + self.skew_threshold
    
    def simulate_volatility_skew(self, end_index):
        """Simulate option volatility skew using price behavior"""
        # In real options markets, volatility skew is the difference in implied volatility
        # between out-of-the-money puts and calls. Typically, OTM puts have higher IV than OTM calls,
        # creating a negative skew (or "smirk").
        
        # We'll simulate this by:
        # 1. Calculating realized volatility
        # 2. Estimating downside vs upside volatility
        # 3. Using the ratio as a proxy for volatility skew
        
        # Calculate overall realized volatility
        overall_vol = self.calculate_volatility(end_index)
        
        # Calculate downside volatility (only negative returns)
        downside_vol = self.calculate_downside_volatility(end_index)
        
        # Calculate upside volatility (only positive returns)
        upside_vol = self.calculate_upside_volatility(end_index)
        
        # Calculate skew as the ratio of downside to upside volatility
        # Higher values indicate steeper skew (more expensive OTM puts)
        if upside_vol == 0:
            return 3.0  # Cap at a high value if upside vol is zero
            
        skew = downside_vol / upside_vol
        
        # Normalize to a reasonable range
        return min(skew, 3.0)
    
    def calculate_volatility(self, end_index):
        """Calculate overall realized volatility"""
        returns = []
        for i in range(end_index - self.vol_window + 1, end_index + 1):
            if i <= 0:
                continue
                
            current_price = float(self.dataScraper.getNumData(i, "Close"))
            prev_price = float(self.dataScraper.getNumData(i - 1, "Close"))
            returns.append((current_price - prev_price) / prev_price)
            
        # Calculate standard deviation
        if not returns:
            return 0
            
        mean_return = sum(returns) / len(returns)
        sum_squared_diff = sum((r - mean_return) ** 2 for r in returns)
        std_dev = (sum_squared_diff / len(returns)) ** 0.5
        
        # Annualize (assuming daily data)
        return std_dev * (252 ** 0.5)
    
    def calculate_downside_volatility(self, end_index):
        """Calculate volatility of only negative returns"""
        negative_returns = []
        for i in range(end_index - self.vol_window + 1, end_index + 1):
            if i <= 0:
                continue
                
            current_price = float(self.dataScraper.getNumData(i, "Close"))
            prev_price = float(self.dataScraper.getNumData(i - 1, "Close"))
            ret = (current_price - prev_price) / prev_price
            
            if ret < 0:
                negative_returns.append(ret)
                
        # Calculate standard deviation
        if not negative_returns:
            return 0
            
        mean_return = sum(negative_returns) / len(negative_returns)
        sum_squared_diff = sum((r - mean_return) ** 2 for r in negative_returns)
        std_dev = (sum_squared_diff / len(negative_returns)) ** 0.5
        
        # Annualize (assuming daily data)
        return std_dev * (252 ** 0.5)
    
    def calculate_upside_volatility(self, end_index):
        """Calculate volatility of only positive returns"""
        positive_returns = []
        for i in range(end_index - self.vol_window + 1, end_index + 1):
            if i <= 0:
                continue
                
            current_price = float(self.dataScraper.getNumData(i, "Close"))
            prev_price = float(self.dataScraper.getNumData(i - 1, "Close"))
            ret = (current_price - prev_price) / prev_price
            
            if ret > 0:
                positive_returns.append(ret)
                
        # Calculate standard deviation
        if not positive_returns:
            return 0.001  # Small non-zero value to avoid division by zero
            
        mean_return = sum(positive_returns) / len(positive_returns)
        sum_squared_diff = sum((r - mean_return) ** 2 for r in positive_returns)
        std_dev = (sum_squared_diff / len(positive_returns)) ** 0.5
        
        # Annualize (assuming daily data)
        return std_dev * (252 ** 0.5)
    
    def estimate_implied_volatility(self, end_index):
        """Estimate implied volatility using historical realized volatility and a premium"""
        # In real markets, implied volatility typically includes a premium over realized volatility
        realized_vol = self.calculate_volatility(end_index)
        
        # Calculate recent price trend
        current_price = float(self.dataScraper.getNumData(end_index, "Close"))
        past_price = float(self.dataScraper.getNumData(end_index - self.vol_window, "Close"))
        price_change = (current_price - past_price) / past_price
        
        # Add a premium based on recent price action
        # Falling markets tend to have higher IV premium (fear premium)
        if price_change < -0.05:  # Significant drop
            premium = 0.05  # 5% premium
        elif price_change < 0:  # Mild drop
            premium = 0.03  # 3% premium
        else:  # Flat or rising market
            premium = 0.02  # 2% premium
            
        return realized_vol * (1 + premium)
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"