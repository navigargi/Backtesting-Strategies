class OrderBookFeatureModels:
    def __init__(self, dataScraper, date, lookback=10, depth_window=3):
        self.date = date
        self.dataScraper = dataScraper
        self.lookback = lookback  # Window for feature calculation
        self.depth_window = depth_window  # Window for simulated order book depth
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for feature calculation
        if curr_index < self.lookback:
            return False
            
        # In a real order book feature model, we would:
        # 1. Extract features from the order book (depth, imbalance, cancel rates, etc.)
        # 2. Feed these features into a trained ML model
        # 3. Get a prediction for the next price movement
        # 4. Make a trading decision based on the prediction
        
        # Since we don't have actual order book data, we'll simulate order book features
        # using available price and volume data
        
        # 1. Simulated order book imbalance
        imbalance = self.simulate_order_book_imbalance(curr_index)
        
        # 2. Simulated order book depth
        depth = self.simulate_order_book_depth(curr_index)
        
        # 3. Simulated order flow (using volume changes)
        order_flow = self.simulate_order_flow(curr_index)
        
        # 4. Price volatility as a proxy for order cancellation rates
        # (higher volatility often correlates with higher cancel rates)
        volatility = self.calculate_volatility(curr_index)
        
        # 5. Spread estimate
        spread = self.estimate_spread(curr_index)
        
        # Simulate ML model prediction (in reality, this would be the output of a trained model)
        # A weighted combination of order book features
        prediction = (
            0.4 * imbalance +  # Positive imbalance suggests buying pressure
            0.2 * depth +      # Higher depth might indicate stronger support/resistance
            0.2 * order_flow + # Positive order flow suggests buying momentum
            -0.1 * volatility + # Higher volatility might reduce prediction confidence
            -0.1 * spread      # Wider spread might indicate less liquidity
        )
        
        # Buy signal: positive prediction above a threshold
        return prediction > 0.2
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for feature calculation
        if curr_index < self.lookback:
            return False
            
        # Calculate the same features as in buy()
        imbalance = self.simulate_order_book_imbalance(curr_index)
        depth = self.simulate_order_book_depth(curr_index)
        order_flow = self.simulate_order_flow(curr_index)
        volatility = self.calculate_volatility(curr_index)
        spread = self.estimate_spread(curr_index)
        
        # Simulate ML model prediction for sell signal
        prediction = (
            0.4 * imbalance +
            0.2 * depth +
            0.2 * order_flow +
            -0.1 * volatility +
            -0.1 * spread
        )
        
        # Sell signal: negative prediction below a threshold
        return prediction < -0.2
    
    def simulate_order_book_imbalance(self, end_index):
        """Simulate order book imbalance using price movement and volume"""
        # In a real order book, imbalance would be (bid_volume - ask_volume) / (bid_volume + ask_volume)
        # We'll simulate this using recent price changes and volume
        
        # Get recent price changes
        price_changes = []
        for i in range(end_index - self.depth_window + 1, end_index + 1):
            current_price = float(self.dataScraper.getNumData(i, "Close"))
            prev_price = float(self.dataScraper.getNumData(i - 1, "Close"))
            price_changes.append(current_price - prev_price)
        
        # Get recent volumes
        volumes = []
        for i in range(end_index - self.depth_window + 1, end_index + 1):
            volumes.append(float(self.dataScraper.getNumData(i, "Volume")))
        
        # Calculate volume-weighted price change
        weighted_change = sum(pc * v for pc, v in zip(price_changes, volumes)) / sum(volumes) if sum(volumes) > 0 else 0
        
        # Normalize to [-1, 1] range
        max_change = max(abs(weighted_change), 0.01)  # Avoid division by zero
        return weighted_change / max_change
    
    def simulate_order_book_depth(self, end_index):
        """Simulate order book depth using volume relative to average"""
        current_volume = float(self.dataScraper.getNumData(end_index, "Volume"))
        
        # Calculate average volume over lookback period
        avg_volume = 0.0
        for i in range(end_index - self.lookback + 1, end_index):
            avg_volume += float(self.dataScraper.getNumData(i, "Volume"))
        avg_volume /= (self.lookback - 1)
        
        # Normalize: higher relative volume suggests deeper order book
        return min(3.0, current_volume / avg_volume) / 3.0  # Cap at 3x average, normalize to [0, 1]
    
    def simulate_order_flow(self, end_index):
        """Simulate order flow using recent volume trend and price direction"""
        # Calculate recent volume trend
        recent_volumes = []
        for i in range(end_index - self.depth_window + 1, end_index + 1):
            recent_volumes.append(float(self.dataScraper.getNumData(i, "Volume")))
        
        volume_trend = 0
        for i in range(1, len(recent_volumes)):
            if recent_volumes[i] > recent_volumes[i-1]:
                volume_trend += 1
            else:
                volume_trend -= 1
        
        # Normalize to [-1, 1]
        volume_trend = volume_trend / self.depth_window
        
        # Get price direction
        current_price = float(self.dataScraper.getNumData(end_index, "Close"))
        prev_price = float(self.dataScraper.getNumData(end_index - 1, "Close"))
        price_direction = 1 if current_price > prev_price else -1
        
        # Combine: positive when volume is increasing and price is rising
        return volume_trend * price_direction
    
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
        std_dev = (sum_squared_diff / len(returns)) ** 0.5
        
        # Normalize to [0, 1] range (assuming max volatility of 5%)
        return min(std_dev / 0.05, 1.0)
    
    def estimate_spread(self, end_index):
        """Estimate bid-ask spread using high-low range and volume"""
        # In a real market, lower volume often correlates with wider spreads
        current_high = float(self.dataScraper.getNumData(end_index, "High"))
        current_low = float(self.dataScraper.getNumData(end_index, "Low"))
        current_volume = float(self.dataScraper.getNumData(end_index, "Volume"))
        
        # Calculate average volume
        avg_volume = 0.0
        for i in range(end_index - self.lookback + 1, end_index + 1):
            avg_volume += float(self.dataScraper.getNumData(i, "Volume"))
        avg_volume /= self.lookback
        
        # Estimate spread as a function of price range and relative volume
        price_range_pct = (current_high - current_low) / current_low
        volume_ratio = min(current_volume / avg_volume, 1.0)  # Cap at 1.0
        
        # Higher range and lower volume suggest wider spread
        estimated_spread = price_range_pct * (2.0 - volume_ratio) / 2.0
        
        # Normalize to [0, 1] range (assuming max spread of 2%)
        return min(estimated_spread / 0.02, 1.0)
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"