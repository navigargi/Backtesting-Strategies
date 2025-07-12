class FlashEventResponse:
    def __init__(self, dataScraper, date, gap_threshold=0.03, reversion_factor=0.5):
        self.date = date
        self.dataScraper = dataScraper
        self.gap_threshold = gap_threshold  # Minimum price gap to consider as a flash event
        self.reversion_factor = reversion_factor  # Expected reversion factor (0-1)
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need at least one previous data point
        if curr_index < 1:
            return False
            
        # In a real flash event response strategy, we would react to sudden price gaps or news
        # We'll simulate by looking for significant overnight gaps down
        
        # Get current open price
        current_open = float(self.dataScraper.getDateData(self.date, "Open"))
        
        # Get previous close price
        prev_close = float(self.dataScraper.getNumData(curr_index - 1, "Close"))
        
        # Calculate overnight gap as a percentage
        overnight_gap = (current_open - prev_close) / prev_close
        
        # Current close
        current_close = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Calculate intraday recovery
        intraday_move = (current_close - current_open) / current_open
        
        # Buy signal: significant gap down and price is starting to recover
        # This simulates buying after a flash crash when prices are likely to revert
        return (overnight_gap < -self.gap_threshold and 
                intraday_move > 0 and  # Price is recovering
                intraday_move < -overnight_gap * self.reversion_factor)  # But hasn't fully recovered yet
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need at least one previous data point
        if curr_index < 1:
            return False
            
        # Get current open price
        current_open = float(self.dataScraper.getDateData(self.date, "Open"))
        
        # Get previous close price
        prev_close = float(self.dataScraper.getNumData(curr_index - 1, "Close"))
        
        # Calculate overnight gap as a percentage
        overnight_gap = (current_open - prev_close) / prev_close
        
        # Current close
        current_close = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Calculate intraday reversal
        intraday_move = (current_close - current_open) / current_open
        
        # Sell signal: significant gap up and price is starting to reverse
        # This simulates selling after a flash spike when prices are likely to revert
        return (overnight_gap > self.gap_threshold and 
                intraday_move < 0 and  # Price is reversing
                intraday_move > -overnight_gap * self.reversion_factor)  # But hasn't fully reversed yet
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"