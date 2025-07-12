class BidAskSpreadCapture:
    def __init__(self, dataScraper, date, spread_threshold=0.001):
        self.date = date
        self.dataScraper = dataScraper
        self.spread_threshold = spread_threshold  # Minimum spread to consider for trading
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need at least one previous data point
        if curr_index < 1:
            return False
            
        # In a real market making strategy, we would place buy orders at the bid
        # Since we don't have bid-ask data, we'll simulate by using high/low prices
        
        # Get current high and low prices to estimate the spread
        high_price = float(self.dataScraper.getDateData(self.date, "High"))
        low_price = float(self.dataScraper.getDateData(self.date, "Low"))
        
        # Calculate estimated spread
        estimated_spread = (high_price - low_price) / low_price
        
        # Previous day's close
        prev_close = float(self.dataScraper.getNumData(curr_index - 1, "Close"))
        
        # Current close
        current_close = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Buy signal: spread is wide enough and price is near the low (simulating buying at the bid)
        return (estimated_spread > self.spread_threshold and 
                current_close < (low_price + (high_price - low_price) * 0.3))
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need at least one previous data point
        if curr_index < 1:
            return False
            
        # Get current high and low prices to estimate the spread
        high_price = float(self.dataScraper.getDateData(self.date, "High"))
        low_price = float(self.dataScraper.getDateData(self.date, "Low"))
        
        # Calculate estimated spread
        estimated_spread = (high_price - low_price) / low_price
        
        # Current close
        current_close = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Sell signal: spread is wide enough and price is near the high (simulating selling at the ask)
        return (estimated_spread > self.spread_threshold and 
                current_close > (low_price + (high_price - low_price) * 0.7))
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"