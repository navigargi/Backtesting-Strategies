class FadingLargeOrders:
    def __init__(self, dataScraper, date, volume_spike_threshold=3.0, price_reversal_threshold=0.005):
        self.date = date
        self.dataScraper = dataScraper
        self.volume_spike_threshold = volume_spike_threshold  # Volume spike threshold as multiple of average
        self.price_reversal_threshold = price_reversal_threshold  # Price reversal threshold
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need at least 10 days of data
        if curr_index < 10:
            return False
            
        # In a real fading large orders strategy, we would identify large visible orders and trade against them
        # Since we don't have order book data, we'll simulate by looking for volume spikes followed by price reversals
        
        # Calculate average volume over the last 10 days
        avg_volume = 0
        for i in range(curr_index - 10, curr_index):
            avg_volume += float(self.dataScraper.getNumData(i, "Volume"))
        avg_volume /= 10
        
        # Check if previous day had a volume spike
        prev_volume = float(self.dataScraper.getNumData(curr_index - 1, "Volume"))
        volume_spike = prev_volume > self.volume_spike_threshold * avg_volume
        
        # Check if previous day had a significant price drop
        prev_close = float(self.dataScraper.getNumData(curr_index - 1, "Close"))
        prev_prev_close = float(self.dataScraper.getNumData(curr_index - 2, "Close"))
        price_drop = (prev_prev_close - prev_close) / prev_prev_close > self.price_reversal_threshold
        
        # Get current price
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Buy signal: previous day had a volume spike and price drop, and current price is starting to reverse
        # This simulates fading a large sell order that pushed the price down but is now being absorbed
        return volume_spike and price_drop and current_price > prev_close
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need at least 10 days of data
        if curr_index < 10:
            return False
            
        # Calculate average volume over the last 10 days
        avg_volume = 0
        for i in range(curr_index - 10, curr_index):
            avg_volume += float(self.dataScraper.getNumData(i, "Volume"))
        avg_volume /= 10
        
        # Check if previous day had a volume spike
        prev_volume = float(self.dataScraper.getNumData(curr_index - 1, "Volume"))
        volume_spike = prev_volume > self.volume_spike_threshold * avg_volume
        
        # Check if previous day had a significant price rise
        prev_close = float(self.dataScraper.getNumData(curr_index - 1, "Close"))
        prev_prev_close = float(self.dataScraper.getNumData(curr_index - 2, "Close"))
        price_rise = (prev_close - prev_prev_close) / prev_prev_close > self.price_reversal_threshold
        
        # Get current price
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Sell signal: previous day had a volume spike and price rise, and current price is starting to reverse
        # This simulates fading a large buy order that pushed the price up but is now being absorbed
        return volume_spike and price_rise and current_price < prev_close
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"