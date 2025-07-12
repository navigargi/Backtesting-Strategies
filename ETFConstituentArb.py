class ETFConstituentArb:
    def __init__(self, dataScraper, date, window=20, z_threshold=2.0, num_constituents=5):
        self.date = date
        self.dataScraper = dataScraper
        self.window = window  # Window for calculating the spread's mean and standard deviation
        self.z_threshold = z_threshold  # Z-score threshold for trading signals
        self.num_constituents = num_constituents  # Number of simulated constituent stocks
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the window and to simulate constituents
        if curr_index < self.window + self.num_constituents:
            return False
            
        # In a real ETF vs Constituent Stocks arbitrage strategy, we would have data for both the ETF and its constituents
        # Since we only have one asset, we'll simulate by comparing the asset to a weighted average of its past values
        # with different weights to simulate different constituent stocks
        
        # Get current price (simulating ETF price)
        etf_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Calculate the "basket" as a weighted average of past prices (simulating constituent stocks)
        basket_value = 0.0
        total_weight = 0.0
        
        for i in range(1, self.num_constituents + 1):
            # Use different weights for different "constituents"
            weight = 1.0 / i  # Higher weight for more recent prices
            price = float(self.dataScraper.getNumData(curr_index - i, "Close"))
            basket_value += weight * price
            total_weight += weight
            
        # Normalize the basket value
        basket_value /= total_weight
        
        # Calculate the "spread" as the difference between ETF and basket
        spread = etf_price - basket_value
        
        # Calculate the mean and standard deviation of the spread over the window
        spreads = []
        for i in range(curr_index - self.window + 1, curr_index + 1):
            if i - self.num_constituents >= 0:  # Ensure we don't go out of bounds
                etf_price_i = float(self.dataScraper.getNumData(i, "Close"))
                
                # Calculate basket value for this point
                basket_i = 0.0
                for j in range(1, self.num_constituents + 1):
                    weight = 1.0 / j
                    price = float(self.dataScraper.getNumData(i - j, "Close"))
                    basket_i += weight * price
                    
                basket_i /= total_weight
                spreads.append(etf_price_i - basket_i)
            
        mean_spread = sum(spreads) / len(spreads)
        std_spread = (sum((s - mean_spread) ** 2 for s in spreads) / len(spreads)) ** 0.5
        
        # Calculate z-score
        if std_spread > 0:
            z_score = (spread - mean_spread) / std_spread
        else:
            z_score = 0
            
        # Buy signal: z-score is significantly negative (ETF is underpriced relative to constituents)
        # In a real arbitrage, we would buy the ETF and short the constituents
        # Since we can only trade one asset, we'll simulate by buying when the ETF is underpriced
        return z_score < -self.z_threshold
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the window and to simulate constituents
        if curr_index < self.window + self.num_constituents:
            return False
            
        # Get current price (simulating ETF price)
        etf_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Calculate the "basket" as a weighted average of past prices (simulating constituent stocks)
        basket_value = 0.0
        total_weight = 0.0
        
        for i in range(1, self.num_constituents + 1):
            # Use different weights for different "constituents"
            weight = 1.0 / i  # Higher weight for more recent prices
            price = float(self.dataScraper.getNumData(curr_index - i, "Close"))
            basket_value += weight * price
            total_weight += weight
            
        # Normalize the basket value
        basket_value /= total_weight
        
        # Calculate the "spread" as the difference between ETF and basket
        spread = etf_price - basket_value
        
        # Calculate the mean and standard deviation of the spread over the window
        spreads = []
        for i in range(curr_index - self.window + 1, curr_index + 1):
            if i - self.num_constituents >= 0:  # Ensure we don't go out of bounds
                etf_price_i = float(self.dataScraper.getNumData(i, "Close"))
                
                # Calculate basket value for this point
                basket_i = 0.0
                for j in range(1, self.num_constituents + 1):
                    weight = 1.0 / j
                    price = float(self.dataScraper.getNumData(i - j, "Close"))
                    basket_i += weight * price
                    
                basket_i /= total_weight
                spreads.append(etf_price_i - basket_i)
            
        mean_spread = sum(spreads) / len(spreads)
        std_spread = (sum((s - mean_spread) ** 2 for s in spreads) / len(spreads)) ** 0.5
        
        # Calculate z-score
        if std_spread > 0:
            z_score = (spread - mean_spread) / std_spread
        else:
            z_score = 0
            
        # Sell signal: z-score is significantly positive (ETF is overpriced relative to constituents)
        # In a real arbitrage, we would short the ETF and buy the constituents
        # Since we can only trade one asset, we'll simulate by selling when the ETF is overpriced
        return z_score > self.z_threshold
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"