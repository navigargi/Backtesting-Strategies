class IcebergDetection:
    def __init__(self, dataScraper, date, lookback=10, volume_threshold=2.0, consecutive_trades=3):
        self.date = date
        self.dataScraper = dataScraper
        self.lookback = lookback  # Window for pattern detection
        self.volume_threshold = volume_threshold  # Threshold for significant volume
        self.consecutive_trades = consecutive_trades  # Number of consecutive trades to confirm pattern
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for calculations
        if curr_index < self.lookback:
            return False
            
        # In a real iceberg detection strategy, we would:
        # 1. Monitor the order book for repeated orders at the same price level
        # 2. Detect when visible orders are quickly replenished after being filled
        # 3. Identify patterns suggesting a large buyer is hiding their true size
        # 4. Position alongside the iceberg order to benefit from its price impact
        
        # Since we don't have actual order book data, we'll simulate by:
        # - Looking for patterns of consistent buying with minimal price impact
        # - Detecting repeated volume spikes at similar price levels
        # - Identifying directional bias in trading activity
        
        # Detect potential buy-side iceberg orders
        buy_iceberg = self.detect_buy_iceberg(curr_index)
        
        # Buy signal: We've detected a buy-side iceberg order
        return buy_iceberg
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for calculations
        if curr_index < self.lookback:
            return False
            
        # Detect potential sell-side iceberg orders
        sell_iceberg = self.detect_sell_iceberg(curr_index)
        
        # Sell signal: We've detected a sell-side iceberg order
        return sell_iceberg
    
    def detect_buy_iceberg(self, end_index):
        """Detect potential buy-side iceberg orders based on volume and price patterns"""
        # In real markets, buy-side iceberg orders might be inferred from:
        # 1. Repeated buying at the same price level
        # 2. Consistent volume that exceeds visible orders
        # 3. Price stability or upward bias despite large volume
        
        # Calculate average volume
        avg_volume = self.calculate_average_volume(end_index)
        
        # Check for consistent buying pressure
        consistent_buying = self.check_consistent_buying(end_index)
        
        # Check for repeated volume spikes at similar price levels
        repeated_volume_spikes = self.check_repeated_volume_spikes(end_index)
        
        # Check for price stability despite large volume (suggesting absorption)
        price_stability = self.check_price_stability(end_index)
        
        # Buy-side iceberg is likely when:
        # 1. There's consistent buying pressure
        # 2. We see repeated volume spikes at similar price levels
        # 3. Price remains stable or has an upward bias despite large volume
        return consistent_buying and (repeated_volume_spikes or price_stability)
    
    def detect_sell_iceberg(self, end_index):
        """Detect potential sell-side iceberg orders based on volume and price patterns"""
        # Similar to buy-side detection, but looking for selling patterns
        
        # Calculate average volume
        avg_volume = self.calculate_average_volume(end_index)
        
        # Check for consistent selling pressure
        consistent_selling = self.check_consistent_selling(end_index)
        
        # Check for repeated volume spikes at similar price levels
        repeated_volume_spikes = self.check_repeated_volume_spikes(end_index)
        
        # Check for price stability despite large volume (suggesting absorption)
        price_stability = self.check_price_stability(end_index)
        
        # Sell-side iceberg is likely when:
        # 1. There's consistent selling pressure
        # 2. We see repeated volume spikes at similar price levels
        # 3. Price remains stable or has a downward bias despite large volume
        return consistent_selling and (repeated_volume_spikes or price_stability)
    
    def calculate_average_volume(self, end_index):
        """Calculate average volume over the lookback period"""
        total_volume = 0.0
        for i in range(end_index - self.lookback, end_index):
            total_volume += float(self.dataScraper.getNumData(i, "Volume"))
        return total_volume / self.lookback
    
    def check_consistent_buying(self, end_index):
        """Check for consistent buying pressure over recent periods"""
        # Count how many of the recent periods show buying pressure
        buying_periods = 0
        
        for i in range(end_index - self.consecutive_trades, end_index + 1):
            if i < 0:
                continue
                
            # Get open, close, and volume
            open_price = float(self.dataScraper.getNumData(i, "Open"))
            close_price = float(self.dataScraper.getNumData(i, "Close"))
            volume = float(self.dataScraper.getNumData(i, "Volume"))
            
            # Calculate average volume
            avg_volume = self.calculate_average_volume(i)
            
            # Buying pressure: close > open and volume is significant
            if close_price > open_price and volume > avg_volume:
                buying_periods += 1
        
        # Consistent buying: most recent periods show buying pressure
        return buying_periods >= self.consecutive_trades - 1
    
    def check_consistent_selling(self, end_index):
        """Check for consistent selling pressure over recent periods"""
        # Count how many of the recent periods show selling pressure
        selling_periods = 0
        
        for i in range(end_index - self.consecutive_trades, end_index + 1):
            if i < 0:
                continue
                
            # Get open, close, and volume
            open_price = float(self.dataScraper.getNumData(i, "Open"))
            close_price = float(self.dataScraper.getNumData(i, "Close"))
            volume = float(self.dataScraper.getNumData(i, "Volume"))
            
            # Calculate average volume
            avg_volume = self.calculate_average_volume(i)
            
            # Selling pressure: close < open and volume is significant
            if close_price < open_price and volume > avg_volume:
                selling_periods += 1
        
        # Consistent selling: most recent periods show selling pressure
        return selling_periods >= self.consecutive_trades - 1
    
    def check_repeated_volume_spikes(self, end_index):
        """Check for repeated volume spikes at similar price levels"""
        # Get volumes for recent periods
        volumes = []
        for i in range(end_index - self.lookback, end_index + 1):
            if i >= 0:
                volumes.append(float(self.dataScraper.getNumData(i, "Volume")))
        
        if not volumes:
            return False
            
        # Calculate average volume
        avg_volume = sum(volumes) / len(volumes)
        
        # Count volume spikes (periods with volume significantly above average)
        spike_count = 0
        for volume in volumes:
            if volume > self.volume_threshold * avg_volume:
                spike_count += 1
        
        # Repeated volume spikes: multiple periods with high volume
        return spike_count >= 3  # At least 3 spikes in the lookback window
    
    def check_price_stability(self, end_index):
        """Check for price stability despite large volume"""
        # Get prices and volumes for recent periods
        prices = []
        volumes = []
        
        for i in range(end_index - self.lookback, end_index + 1):
            if i >= 0:
                prices.append(float(self.dataScraper.getNumData(i, "Close")))
                volumes.append(float(self.dataScraper.getNumData(i, "Volume")))
        
        if not prices or not volumes:
            return False
            
        # Calculate average volume
        avg_volume = sum(volumes) / len(volumes)
        
        # Calculate price volatility (standard deviation of returns)
        returns = []
        for i in range(1, len(prices)):
            returns.append((prices[i] - prices[i-1]) / prices[i-1])
        
        if not returns:
            return False
            
        # Calculate standard deviation of returns
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_dev = variance ** 0.5
        
        # Check if recent volume is high but price volatility is low
        recent_volume = volumes[-1]
        
        # Price stability: high volume with low volatility
        return recent_volume > self.volume_threshold * avg_volume and std_dev < 0.01  # 1% volatility threshold
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"