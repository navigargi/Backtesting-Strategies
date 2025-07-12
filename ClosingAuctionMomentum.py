class ClosingAuctionMomentum:
    def __init__(self, dataScraper, date, lookback=5, momentum_threshold=0.01):
        self.date = date
        self.dataScraper = dataScraper
        self.lookback = lookback  # Number of periods to analyze momentum
        self.momentum_threshold = momentum_threshold  # Threshold for significant momentum
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the lookback
        if curr_index < self.lookback:
            return False
            
        # In a real closing auction momentum strategy, we would analyze intraday data
        # leading into the close. Since we only have daily data, we'll simulate by
        # looking at recent price action and volume patterns
        
        # Calculate recent momentum (rate of change)
        current_close = float(self.dataScraper.getDateData(self.date, "Close"))
        lookback_close = float(self.dataScraper.getNumData(curr_index - self.lookback, "Close"))
        momentum = (current_close - lookback_close) / lookback_close
        
        # Check if close is higher than open (bullish candle)
        current_open = float(self.dataScraper.getDateData(self.date, "Open"))
        is_bullish = current_close > current_open
        
        # Check if volume is increasing (suggesting strong auction interest)
        current_volume = float(self.dataScraper.getDateData(self.date, "Volume"))
        prev_volume = float(self.dataScraper.getNumData(curr_index - 1, "Volume"))
        volume_increasing = current_volume > prev_volume
        
        # Buy signal: positive momentum above threshold, bullish candle, and increasing volume
        return momentum > self.momentum_threshold and is_bullish and volume_increasing
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the lookback
        if curr_index < self.lookback:
            return False
            
        # Calculate recent momentum (rate of change)
        current_close = float(self.dataScraper.getDateData(self.date, "Close"))
        lookback_close = float(self.dataScraper.getNumData(curr_index - self.lookback, "Close"))
        momentum = (current_close - lookback_close) / lookback_close
        
        # Check if close is lower than open (bearish candle)
        current_open = float(self.dataScraper.getDateData(self.date, "Open"))
        is_bearish = current_close < current_open
        
        # Check if volume is increasing (suggesting strong auction interest)
        current_volume = float(self.dataScraper.getDateData(self.date, "Volume"))
        prev_volume = float(self.dataScraper.getNumData(curr_index - 1, "Volume"))
        volume_increasing = current_volume > prev_volume
        
        # Sell signal: negative momentum below negative threshold, bearish candle, and increasing volume
        return momentum < -self.momentum_threshold and is_bearish and volume_increasing
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"