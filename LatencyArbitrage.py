class LatencyArbitrage:
    def __init__(self, dataScraper, date, price_diff_threshold=0.001, reaction_delay=1):
        self.date = date
        self.dataScraper = dataScraper
        self.price_diff_threshold = price_diff_threshold  # Minimum price difference to consider for arbitrage
        self.reaction_delay = reaction_delay  # Simulated delay in reacting to price changes (in data points)
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the reaction delay
        if curr_index < self.reaction_delay + 1:
            return False
            
        # In a real latency arbitrage strategy, we would compare prices between exchanges
        # Since we don't have multi-exchange data, we'll simulate by comparing current price
        # with a slightly delayed price to simulate the latency advantage
        
        # Current price (representing the "fast" exchange)
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Delayed price (representing the "slow" exchange)
        delayed_index = curr_index - self.reaction_delay
        delayed_price = float(self.dataScraper.getNumData(delayed_index, "Close"))
        
        # Calculate price difference as a percentage
        price_diff = (current_price - delayed_price) / delayed_price
        
        # Buy signal: current price is significantly higher than the delayed price
        # This simulates buying on the "slow" exchange when we know the price will soon rise
        # based on what we've already seen on the "fast" exchange
        return price_diff > self.price_diff_threshold
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the reaction delay
        if curr_index < self.reaction_delay + 1:
            return False
            
        # Current price (representing the "fast" exchange)
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Delayed price (representing the "slow" exchange)
        delayed_index = curr_index - self.reaction_delay
        delayed_price = float(self.dataScraper.getNumData(delayed_index, "Close"))
        
        # Calculate price difference as a percentage
        price_diff = (delayed_price - current_price) / current_price
        
        # Sell signal: current price is significantly lower than the delayed price
        # This simulates selling on the "slow" exchange when we know the price will soon fall
        # based on what we've already seen on the "fast" exchange
        return price_diff > self.price_diff_threshold
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"