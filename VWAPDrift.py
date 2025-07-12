class VWAPDrift:
    def __init__(self, dataScraper, date, window=5, threshold=0.01):
        self.date = date
        self.dataScraper = dataScraper
        self.window = window  # Window for calculating VWAP
        self.threshold = threshold  # Minimum deviation from VWAP to consider for trading
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the window
        if curr_index < self.window:
            return False
            
        # Calculate VWAP over the window
        vwap = self.calculate_vwap(curr_index)
        
        # Get current price
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Calculate deviation from VWAP as a percentage
        deviation = (vwap - current_price) / vwap
        
        # Get previous price
        prev_price = float(self.dataScraper.getNumData(curr_index - 1, "Close"))
        
        # Calculate price change
        price_change = (current_price - prev_price) / prev_price
        
        # Buy signal: price is significantly below VWAP and starting to move up towards it
        return deviation > self.threshold and price_change > 0
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the window
        if curr_index < self.window:
            return False
            
        # Calculate VWAP over the window
        vwap = self.calculate_vwap(curr_index)
        
        # Get current price
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Calculate deviation from VWAP as a percentage
        deviation = (current_price - vwap) / vwap
        
        # Get previous price
        prev_price = float(self.dataScraper.getNumData(curr_index - 1, "Close"))
        
        # Calculate price change
        price_change = (current_price - prev_price) / prev_price
        
        # Sell signal: price is significantly above VWAP and starting to move down towards it
        return deviation > self.threshold and price_change < 0
    
    def calculate_vwap(self, end_index):
        """Calculate the Volume-Weighted Average Price over the specified window"""
        sum_price_volume = 0.0
        sum_volume = 0.0
        
        for i in range(end_index - self.window + 1, end_index + 1):
            # Use typical price (high + low + close) / 3 for VWAP calculation
            high = float(self.dataScraper.getNumData(i, "High"))
            low = float(self.dataScraper.getNumData(i, "Low"))
            close = float(self.dataScraper.getNumData(i, "Close"))
            typical_price = (high + low + close) / 3
            
            volume = float(self.dataScraper.getNumData(i, "Volume"))
            
            sum_price_volume += typical_price * volume
            sum_volume += volume
            
        if sum_volume > 0:
            return sum_price_volume / sum_volume
        else:
            return 0.0
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"