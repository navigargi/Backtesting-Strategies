class OrderBookImbalance:
    def __init__(self, dataScraper, date, imbalance_threshold=0.2, volume_window=5):
        self.date = date
        self.dataScraper = dataScraper
        self.imbalance_threshold = imbalance_threshold  # Threshold for significant imbalance
        self.volume_window = volume_window  # Window for volume analysis
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the volume window
        if curr_index < self.volume_window:
            return False
            
        # In a real order book imbalance strategy, we would analyze the order book depth
        # Since we don't have order book data, we'll simulate by using volume and price movement
        
        # Calculate volume-weighted price change over the window
        total_volume = 0
        buy_volume = 0  # Approximated by up-day volume
        
        for i in range(curr_index - self.volume_window + 1, curr_index + 1):
            volume = float(self.dataScraper.getNumData(i, "Volume"))
            close = float(self.dataScraper.getNumData(i, "Close"))
            prev_close = float(self.dataScraper.getNumData(i - 1, "Close"))
            
            total_volume += volume
            
            # If price went up, assume more buy volume
            if close > prev_close:
                buy_volume += volume
        
        # Calculate buy-side imbalance
        if total_volume > 0:
            buy_imbalance = buy_volume / total_volume - 0.5  # Normalized around 0
        else:
            buy_imbalance = 0
            
        # Current price
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Previous price
        prev_price = float(self.dataScraper.getNumData(curr_index - 1, "Close"))
        
        # Buy signal: significant buy imbalance and price hasn't moved up too much yet
        # This simulates detecting buying pressure in the order book before it fully impacts price
        return (buy_imbalance > self.imbalance_threshold and 
                (current_price - prev_price) / prev_price < buy_imbalance / 2)
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the volume window
        if curr_index < self.volume_window:
            return False
            
        # Calculate volume-weighted price change over the window
        total_volume = 0
        sell_volume = 0  # Approximated by down-day volume
        
        for i in range(curr_index - self.volume_window + 1, curr_index + 1):
            volume = float(self.dataScraper.getNumData(i, "Volume"))
            close = float(self.dataScraper.getNumData(i, "Close"))
            prev_close = float(self.dataScraper.getNumData(i - 1, "Close"))
            
            total_volume += volume
            
            # If price went down, assume more sell volume
            if close < prev_close:
                sell_volume += volume
        
        # Calculate sell-side imbalance
        if total_volume > 0:
            sell_imbalance = sell_volume / total_volume - 0.5  # Normalized around 0
        else:
            sell_imbalance = 0
            
        # Current price
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Previous price
        prev_price = float(self.dataScraper.getNumData(curr_index - 1, "Close"))
        
        # Sell signal: significant sell imbalance and price hasn't moved down too much yet
        # This simulates detecting selling pressure in the order book before it fully impacts price
        return (sell_imbalance > self.imbalance_threshold and 
                (prev_price - current_price) / prev_price < sell_imbalance / 2)
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"