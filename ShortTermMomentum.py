class ShortTermMomentum:
    def __init__(self, dataScraper, date, lookback=3, threshold=0.005):
        self.date = date
        self.dataScraper = dataScraper
        self.lookback = lookback  # Number of periods to look back for momentum
        self.threshold = threshold  # Minimum price change to consider as momentum
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the lookback
        if curr_index < self.lookback:
            return False
            
        # Get current price
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Get price from lookback periods ago
        past_price = float(self.dataScraper.getNumData(curr_index - self.lookback, "Close"))
        
        # Calculate price change as a percentage
        price_change = (current_price - past_price) / past_price
        
        # Calculate recent momentum (last period)
        recent_price = float(self.dataScraper.getNumData(curr_index - 1, "Close"))
        recent_change = (current_price - recent_price) / recent_price
        
        # Buy signal: positive momentum exceeding threshold and accelerating
        return price_change > self.threshold and recent_change > 0
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the lookback
        if curr_index < self.lookback:
            return False
            
        # Get current price
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Get price from lookback periods ago
        past_price = float(self.dataScraper.getNumData(curr_index - self.lookback, "Close"))
        
        # Calculate price change as a percentage
        price_change = (current_price - past_price) / past_price
        
        # Calculate recent momentum (last period)
        recent_price = float(self.dataScraper.getNumData(curr_index - 1, "Close"))
        recent_change = (current_price - recent_price) / recent_price
        
        # Sell signal: negative momentum exceeding threshold and accelerating
        return price_change < -self.threshold and recent_change < 0
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"