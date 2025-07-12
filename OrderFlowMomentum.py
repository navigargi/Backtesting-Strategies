class OrderFlowMomentum:
    def __init__(self, dataScraper, date, window=5, volume_threshold=1.5):
        self.date = date
        self.dataScraper = dataScraper
        self.window = window  # Window for analyzing order flow
        self.volume_threshold = volume_threshold  # Volume threshold as multiple of average
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the window
        if curr_index < self.window:
            return False
            
        # In a real order flow momentum strategy, we would analyze tick-by-tick data and order book changes
        # Since we only have daily OHLCV data, we'll simulate by looking at volume and price movement
        
        # Calculate average volume over the window
        avg_volume = 0.0
        for i in range(curr_index - self.window + 1, curr_index + 1):
            avg_volume += float(self.dataScraper.getNumData(i, "Volume"))
        avg_volume /= self.window
        
        # Get current volume and price data
        current_volume = float(self.dataScraper.getDateData(self.date, "Volume"))
        current_close = float(self.dataScraper.getDateData(self.date, "Close"))
        current_open = float(self.dataScraper.getDateData(self.date, "Open"))
        
        # Calculate price change
        price_change = current_close - current_open
        
        # Calculate volume-weighted price movement for recent days
        volume_weighted_movement = 0.0
        total_volume = 0.0
        
        for i in range(curr_index - self.window + 1, curr_index + 1):
            close = float(self.dataScraper.getNumData(i, "Close"))
            open_price = float(self.dataScraper.getNumData(i, "Open"))
            volume = float(self.dataScraper.getNumData(i, "Volume"))
            
            # Weight price movement by volume
            volume_weighted_movement += (close - open_price) * volume
            total_volume += volume
            
        if total_volume > 0:
            volume_weighted_movement /= total_volume
        
        # Buy signal: high volume with positive price movement and positive volume-weighted momentum
        return (current_volume > self.volume_threshold * avg_volume and 
                price_change > 0 and 
                volume_weighted_movement > 0)
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the window
        if curr_index < self.window:
            return False
            
        # Calculate average volume over the window
        avg_volume = 0.0
        for i in range(curr_index - self.window + 1, curr_index + 1):
            avg_volume += float(self.dataScraper.getNumData(i, "Volume"))
        avg_volume /= self.window
        
        # Get current volume and price data
        current_volume = float(self.dataScraper.getDateData(self.date, "Volume"))
        current_close = float(self.dataScraper.getDateData(self.date, "Close"))
        current_open = float(self.dataScraper.getDateData(self.date, "Open"))
        
        # Calculate price change
        price_change = current_close - current_open
        
        # Calculate volume-weighted price movement for recent days
        volume_weighted_movement = 0.0
        total_volume = 0.0
        
        for i in range(curr_index - self.window + 1, curr_index + 1):
            close = float(self.dataScraper.getNumData(i, "Close"))
            open_price = float(self.dataScraper.getNumData(i, "Open"))
            volume = float(self.dataScraper.getNumData(i, "Volume"))
            
            # Weight price movement by volume
            volume_weighted_movement += (close - open_price) * volume
            total_volume += volume
            
        if total_volume > 0:
            volume_weighted_movement /= total_volume
        
        # Sell signal: high volume with negative price movement and negative volume-weighted momentum
        return (current_volume > self.volume_threshold * avg_volume and 
                price_change < 0 and 
                volume_weighted_movement < 0)
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"