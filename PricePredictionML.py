class PricePredictionML:
    def __init__(self, dataScraper, date, lookback=10, feature_window=5):
        self.date = date
        self.dataScraper = dataScraper
        self.lookback = lookback  # Window for feature calculation
        self.feature_window = feature_window  # Window for shorter-term features
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for feature calculation
        if curr_index < self.lookback:
            return False
            
        # In a real ML-based strategy, we would:
        # 1. Extract features from price and volume data
        # 2. Feed these features into a trained ML model
        # 3. Get a prediction for the next price movement
        # 4. Make a trading decision based on the prediction
        
        # Since we can't actually train an ML model here, we'll simulate one
        # by using a combination of technical indicators that ML models often find useful
        
        # Calculate features that would typically be used in an ML model
        
        # 1. Recent momentum (short-term)
        short_momentum = self.calculate_momentum(curr_index, self.feature_window)
        
        # 2. Medium-term momentum
        medium_momentum = self.calculate_momentum(curr_index, self.lookback)
        
        # 3. Volatility
        volatility = self.calculate_volatility(curr_index)
        
        # 4. Volume trend
        volume_trend = self.calculate_volume_trend(curr_index)
        
        # 5. Price relative to recent range
        price_range_position = self.calculate_price_range_position(curr_index)
        
        # Simulate ML model prediction (in reality, this would be the output of a trained model)
        # A simple weighted combination of features
        prediction = (
            0.3 * short_momentum +
            0.2 * medium_momentum +
            -0.1 * volatility +  # Higher volatility might reduce prediction confidence
            0.2 * volume_trend +
            0.2 * price_range_position
        )
        
        # Buy signal: positive prediction above a threshold
        return prediction > 0.15
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for feature calculation
        if curr_index < self.lookback:
            return False
            
        # Calculate the same features as in buy()
        short_momentum = self.calculate_momentum(curr_index, self.feature_window)
        medium_momentum = self.calculate_momentum(curr_index, self.lookback)
        volatility = self.calculate_volatility(curr_index)
        volume_trend = self.calculate_volume_trend(curr_index)
        price_range_position = self.calculate_price_range_position(curr_index)
        
        # Simulate ML model prediction for sell signal
        prediction = (
            0.3 * short_momentum +
            0.2 * medium_momentum +
            -0.1 * volatility +
            0.2 * volume_trend +
            0.2 * price_range_position
        )
        
        # Sell signal: negative prediction below a threshold
        return prediction < -0.15
    
    def calculate_momentum(self, end_index, window):
        """Calculate price momentum over the specified window"""
        current_price = float(self.dataScraper.getNumData(end_index, "Close"))
        past_price = float(self.dataScraper.getNumData(end_index - window, "Close"))
        return (current_price - past_price) / past_price
    
    def calculate_volatility(self, end_index):
        """Calculate price volatility (standard deviation of returns)"""
        returns = []
        for i in range(end_index - self.lookback + 1, end_index + 1):
            price_t = float(self.dataScraper.getNumData(i, "Close"))
            price_t_1 = float(self.dataScraper.getNumData(i - 1, "Close"))
            returns.append((price_t - price_t_1) / price_t_1)
            
        # Calculate standard deviation
        mean_return = sum(returns) / len(returns)
        sum_squared_diff = sum((r - mean_return) ** 2 for r in returns)
        return (sum_squared_diff / len(returns)) ** 0.5
    
    def calculate_volume_trend(self, end_index):
        """Calculate the trend in trading volume"""
        current_volume = float(self.dataScraper.getNumData(end_index, "Volume"))
        avg_volume = 0.0
        
        for i in range(end_index - self.lookback + 1, end_index):
            avg_volume += float(self.dataScraper.getNumData(i, "Volume"))
            
        avg_volume /= (self.lookback - 1)
        
        # Return normalized volume trend
        return (current_volume - avg_volume) / avg_volume
    
    def calculate_price_range_position(self, end_index):
        """Calculate where the current price is within its recent range"""
        current_price = float(self.dataScraper.getNumData(end_index, "Close"))
        
        # Find high and low in the lookback period
        high_price = float('-inf')
        low_price = float('inf')
        
        for i in range(end_index - self.lookback + 1, end_index + 1):
            high = float(self.dataScraper.getNumData(i, "High"))
            low = float(self.dataScraper.getNumData(i, "Low"))
            
            high_price = max(high_price, high)
            low_price = min(low_price, low)
        
        # Calculate position in range from -1 (at low) to 1 (at high)
        range_size = high_price - low_price
        if range_size == 0:
            return 0
        
        position = (current_price - low_price) / range_size
        return 2 * position - 1  # Scale to [-1, 1]
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"