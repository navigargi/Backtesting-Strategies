class PeggedOrders:
    def __init__(self, dataScraper, date, peg_offset=0.001, min_spread=0.002):
        self.date = date
        self.dataScraper = dataScraper
        self.peg_offset = peg_offset  # Offset from midpoint as a fraction of price
        self.min_spread = min_spread  # Minimum spread required to trade
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need at least one previous data point
        if curr_index < 1:
            return False
            
        # In a real pegged orders strategy, we would place orders pegged to the midpoint or best bid/ask
        # Since we don't have order book data, we'll simulate by using high/low prices to estimate the spread
        
        # Get current high and low prices to estimate the spread
        high_price = float(self.dataScraper.getDateData(self.date, "High"))
        low_price = float(self.dataScraper.getDateData(self.date, "Low"))
        
        # Calculate estimated spread
        estimated_spread = (high_price - low_price) / low_price
        
        # Calculate midpoint
        midpoint = (high_price + low_price) / 2
        
        # Calculate our buy price (midpoint - offset)
        buy_price = midpoint * (1 - self.peg_offset)
        
        # Current close
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Previous close
        prev_close = float(self.dataScraper.getNumData(curr_index - 1, "Close"))
        
        # Buy signal: spread is wide enough and current price is at or below our buy price
        # This simulates our pegged buy order getting filled
        return (estimated_spread > self.min_spread and 
                current_price <= buy_price and
                current_price < prev_close)  # Downward momentum
    
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
        
        # Calculate midpoint
        midpoint = (high_price + low_price) / 2
        
        # Calculate our sell price (midpoint + offset)
        sell_price = midpoint * (1 + self.peg_offset)
        
        # Current close
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Previous close
        prev_close = float(self.dataScraper.getNumData(curr_index - 1, "Close"))
        
        # Sell signal: spread is wide enough and current price is at or above our sell price
        # This simulates our pegged sell order getting filled
        return (estimated_spread > self.min_spread and 
                current_price >= sell_price and
                current_price > prev_close)  # Upward momentum
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"