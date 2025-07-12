class OpeningRangeBreakout:
    def __init__(self, dataScraper, date, lookback=3, breakout_factor=1.2):
        self.date = date
        self.dataScraper = dataScraper
        self.lookback = lookback  # Number of periods to define the opening range
        self.breakout_factor = breakout_factor  # Factor to determine breakout threshold
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the lookback
        if curr_index < self.lookback:
            return False
            
        # In a real opening range breakout strategy, we would use intraday data to define the opening range
        # Since we only have daily data, we'll simulate by using the high/low range of the past few days
        
        # Calculate the opening range high and low
        range_high = float('-inf')
        range_low = float('inf')
        
        for i in range(curr_index - self.lookback, curr_index):
            high = float(self.dataScraper.getNumData(i, "High"))
            low = float(self.dataScraper.getNumData(i, "Low"))
            
            range_high = max(range_high, high)
            range_low = min(range_low, low)
        
        # Calculate the range size
        range_size = range_high - range_low
        
        # Calculate breakout levels
        breakout_level = range_high + (range_size * (self.breakout_factor - 1))
        
        # Get current price
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Get previous price
        prev_price = float(self.dataScraper.getNumData(curr_index - 1, "Close"))
        
        # Buy signal: price breaks above the upper breakout level with momentum
        return current_price > breakout_level and current_price > prev_price
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the lookback
        if curr_index < self.lookback:
            return False
            
        # Calculate the opening range high and low
        range_high = float('-inf')
        range_low = float('inf')
        
        for i in range(curr_index - self.lookback, curr_index):
            high = float(self.dataScraper.getNumData(i, "High"))
            low = float(self.dataScraper.getNumData(i, "Low"))
            
            range_high = max(range_high, high)
            range_low = min(range_low, low)
        
        # Calculate the range size
        range_size = range_high - range_low
        
        # Calculate breakout levels
        breakdown_level = range_low - (range_size * (self.breakout_factor - 1))
        
        # Get current price
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Get previous price
        prev_price = float(self.dataScraper.getNumData(curr_index - 1, "Close"))
        
        # Sell signal: price breaks below the lower breakdown level with momentum
        return current_price < breakdown_level and current_price < prev_price
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"