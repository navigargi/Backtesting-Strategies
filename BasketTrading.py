class BasketTrading:
    def __init__(self, dataScraper, date, window=20, z_threshold=2.0, basket_size=3):
        self.date = date
        self.dataScraper = dataScraper
        self.window = window  # Window for calculating the spread's mean and standard deviation
        self.z_threshold = z_threshold  # Z-score threshold for trading signals
        self.basket_size = basket_size  # Number of assets in the simulated basket
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the window and to simulate multiple assets
        if curr_index < self.window + self.basket_size:
            return False
            
        # In a real basket trading strategy, we would have data for multiple correlated assets
        # Since we only have one asset, we'll simulate by comparing the asset to multiple lagged versions of itself
        
        # Get current price
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Calculate the "basket" as the average of lagged prices
        basket_value = 0.0
        for lag in range(1, self.basket_size + 1):
            lagged_price = float(self.dataScraper.getNumData(curr_index - lag, "Close"))
            basket_value += lagged_price
        basket_value /= self.basket_size
        
        # Calculate the "spread" as the difference between current price and the basket value
        spread = current_price - basket_value
        
        # Calculate the mean and standard deviation of the spread over the window
        spreads = []
        for i in range(curr_index - self.window + 1, curr_index + 1):
            price_i = float(self.dataScraper.getNumData(i, "Close"))
            
            # Calculate basket value for this point
            basket_i = 0.0
            for lag in range(1, self.basket_size + 1):
                if i - lag >= 0:  # Ensure we don't go out of bounds
                    lagged_price_i = float(self.dataScraper.getNumData(i - lag, "Close"))
                    basket_i += lagged_price_i
            basket_i /= self.basket_size
            
            spreads.append(price_i - basket_i)
            
        mean_spread = sum(spreads) / len(spreads)
        std_spread = (sum((s - mean_spread) ** 2 for s in spreads) / len(spreads)) ** 0.5
        
        # Calculate z-score
        if std_spread > 0:
            z_score = (spread - mean_spread) / std_spread
        else:
            z_score = 0
            
        # Buy signal: z-score is significantly negative (asset is undervalued relative to the basket)
        return z_score < -self.z_threshold
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the window and to simulate multiple assets
        if curr_index < self.window + self.basket_size:
            return False
            
        # Get current price
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Calculate the "basket" as the average of lagged prices
        basket_value = 0.0
        for lag in range(1, self.basket_size + 1):
            lagged_price = float(self.dataScraper.getNumData(curr_index - lag, "Close"))
            basket_value += lagged_price
        basket_value /= self.basket_size
        
        # Calculate the "spread" as the difference between current price and the basket value
        spread = current_price - basket_value
        
        # Calculate the mean and standard deviation of the spread over the window
        spreads = []
        for i in range(curr_index - self.window + 1, curr_index + 1):
            price_i = float(self.dataScraper.getNumData(i, "Close"))
            
            # Calculate basket value for this point
            basket_i = 0.0
            for lag in range(1, self.basket_size + 1):
                if i - lag >= 0:  # Ensure we don't go out of bounds
                    lagged_price_i = float(self.dataScraper.getNumData(i - lag, "Close"))
                    basket_i += lagged_price_i
            basket_i /= self.basket_size
            
            spreads.append(price_i - basket_i)
            
        mean_spread = sum(spreads) / len(spreads)
        std_spread = (sum((s - mean_spread) ** 2 for s in spreads) / len(spreads)) ** 0.5
        
        # Calculate z-score
        if std_spread > 0:
            z_score = (spread - mean_spread) / std_spread
        else:
            z_score = 0
            
        # Sell signal: z-score is significantly positive (asset is overvalued relative to the basket)
        return z_score > self.z_threshold
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"