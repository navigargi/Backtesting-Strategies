class TriangularArbitrage:
    def __init__(self, dataScraper, date, window=20, arb_threshold=0.001, lag1=1, lag2=2):
        self.date = date
        self.dataScraper = dataScraper
        self.window = window  # Window for calculating the average arbitrage opportunity
        self.arb_threshold = arb_threshold  # Minimum arbitrage opportunity to trade
        self.lag1 = lag1  # Lag to simulate second currency pair
        self.lag2 = lag2  # Lag to simulate third currency pair
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the window and to simulate all currency pairs
        if curr_index < self.window + max(self.lag1, self.lag2):
            return False
            
        # In a real triangular arbitrage strategy, we would have data for three currency pairs
        # Since we only have one asset, we'll simulate by using the current price and two lagged prices
        # with slight adjustments to simulate different currency pairs
        
        # Get current price (simulating first currency pair, e.g., USD/EUR)
        pair1 = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Get lagged prices with adjustments (simulating second and third currency pairs)
        pair2 = float(self.dataScraper.getNumData(curr_index - self.lag1, "Close")) * 1.002  # e.g., EUR/GBP
        pair3 = float(self.dataScraper.getNumData(curr_index - self.lag2, "Close")) * 0.998  # e.g., GBP/USD
        
        # Calculate the triangular arbitrage opportunity
        # In a real scenario: USD/EUR * EUR/GBP * GBP/USD should equal 1
        # Any deviation from 1 represents an arbitrage opportunity
        triangular_rate = pair1 * pair2 * pair3
        arbitrage_opportunity = abs(triangular_rate - 1.0)
        
        # Calculate the average arbitrage opportunity over the window
        avg_opportunity = 0.0
        count = 0
        
        for i in range(curr_index - self.window + 1, curr_index + 1):
            if i - max(self.lag1, self.lag2) >= 0:  # Ensure we don't go out of bounds
                p1 = float(self.dataScraper.getNumData(i, "Close"))
                p2 = float(self.dataScraper.getNumData(i - self.lag1, "Close")) * 1.002
                p3 = float(self.dataScraper.getNumData(i - self.lag2, "Close")) * 0.998
                
                tri_rate = p1 * p2 * p3
                opp = abs(tri_rate - 1.0)
                avg_opportunity += opp
                count += 1
                
        if count > 0:
            avg_opportunity /= count
        
        # Buy signal: arbitrage opportunity is significantly larger than average
        # and the triangular rate is greater than 1 (profitable to buy the base currency)
        return (arbitrage_opportunity > avg_opportunity + self.arb_threshold and 
                triangular_rate > 1.0)
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the window and to simulate all currency pairs
        if curr_index < self.window + max(self.lag1, self.lag2):
            return False
            
        # Get current price (simulating first currency pair, e.g., USD/EUR)
        pair1 = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Get lagged prices with adjustments (simulating second and third currency pairs)
        pair2 = float(self.dataScraper.getNumData(curr_index - self.lag1, "Close")) * 1.002  # e.g., EUR/GBP
        pair3 = float(self.dataScraper.getNumData(curr_index - self.lag2, "Close")) * 0.998  # e.g., GBP/USD
        
        # Calculate the triangular arbitrage opportunity
        triangular_rate = pair1 * pair2 * pair3
        arbitrage_opportunity = abs(triangular_rate - 1.0)
        
        # Calculate the average arbitrage opportunity over the window
        avg_opportunity = 0.0
        count = 0
        
        for i in range(curr_index - self.window + 1, curr_index + 1):
            if i - max(self.lag1, self.lag2) >= 0:  # Ensure we don't go out of bounds
                p1 = float(self.dataScraper.getNumData(i, "Close"))
                p2 = float(self.dataScraper.getNumData(i - self.lag1, "Close")) * 1.002
                p3 = float(self.dataScraper.getNumData(i - self.lag2, "Close")) * 0.998
                
                tri_rate = p1 * p2 * p3
                opp = abs(tri_rate - 1.0)
                avg_opportunity += opp
                count += 1
                
        if count > 0:
            avg_opportunity /= count
        
        # Sell signal: arbitrage opportunity is significantly larger than average
        # and the triangular rate is less than 1 (profitable to sell the base currency)
        return (arbitrage_opportunity > avg_opportunity + self.arb_threshold and 
                triangular_rate < 1.0)
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"