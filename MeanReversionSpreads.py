class MeanReversionSpreads:
    def __init__(self, dataScraper, date, window=50, half_life=10, z_threshold=2.0, lag=1):
        self.date = date
        self.dataScraper = dataScraper
        self.window = window  # Window for estimating OU process parameters
        self.half_life = half_life  # Half-life of mean reversion
        self.z_threshold = z_threshold  # Z-score threshold for trading signals
        self.lag = lag  # Lag to simulate second asset for spread
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the window and to simulate spread
        if curr_index < self.window + self.lag:
            return False
            
        # In a real mean reversion on spreads strategy, we would have data for two assets
        # Since we only have one asset, we'll simulate by comparing the asset to a lagged version of itself
        
        # Get current price and lagged price
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        lagged_price = float(self.dataScraper.getNumData(curr_index - self.lag, "Close"))
        
        # Calculate the spread
        spread = current_price - lagged_price
        
        # Estimate Ornstein-Uhlenbeck process parameters
        spreads = []
        for i in range(curr_index - self.window + 1, curr_index + 1):
            if i - self.lag >= 0:  # Ensure we don't go out of bounds
                price_i = float(self.dataScraper.getNumData(i, "Close"))
                lagged_price_i = float(self.dataScraper.getNumData(i - self.lag, "Close"))
                spreads.append(price_i - lagged_price_i)
        
        # Calculate mean and standard deviation of the spread
        mean_spread = sum(spreads) / len(spreads)
        std_spread = (sum((s - mean_spread) ** 2 for s in spreads) / len(spreads)) ** 0.5
        
        # Calculate the speed of mean reversion (lambda)
        # In a real OU process, lambda = -ln(2) / half_life
        lambda_param = 0.693 / self.half_life  # ln(2) ≈ 0.693
        
        # Calculate the expected spread based on OU process
        # In a real OU process, E[S_t+1] = S_t * e^(-lambda) + mean * (1 - e^(-lambda))
        exp_factor = 2.718 ** (-lambda_param)  # e^(-lambda)
        expected_spread = spread * exp_factor + mean_spread * (1 - exp_factor)
        
        # Calculate the z-score of the current spread
        if std_spread > 0:
            z_score = (spread - mean_spread) / std_spread
        else:
            z_score = 0
            
        # Buy signal: z-score is significantly negative (spread is below mean and expected to revert upward)
        # This means we expect the current price to increase relative to the lagged price
        return z_score < -self.z_threshold and spread < expected_spread
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the window and to simulate spread
        if curr_index < self.window + self.lag:
            return False
            
        # Get current price and lagged price
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        lagged_price = float(self.dataScraper.getNumData(curr_index - self.lag, "Close"))
        
        # Calculate the spread
        spread = current_price - lagged_price
        
        # Estimate Ornstein-Uhlenbeck process parameters
        spreads = []
        for i in range(curr_index - self.window + 1, curr_index + 1):
            if i - self.lag >= 0:  # Ensure we don't go out of bounds
                price_i = float(self.dataScraper.getNumData(i, "Close"))
                lagged_price_i = float(self.dataScraper.getNumData(i - self.lag, "Close"))
                spreads.append(price_i - lagged_price_i)
        
        # Calculate mean and standard deviation of the spread
        mean_spread = sum(spreads) / len(spreads)
        std_spread = (sum((s - mean_spread) ** 2 for s in spreads) / len(spreads)) ** 0.5
        
        # Calculate the speed of mean reversion (lambda)
        lambda_param = 0.693 / self.half_life  # ln(2) ≈ 0.693
        
        # Calculate the expected spread based on OU process
        exp_factor = 2.718 ** (-lambda_param)  # e^(-lambda)
        expected_spread = spread * exp_factor + mean_spread * (1 - exp_factor)
        
        # Calculate the z-score of the current spread
        if std_spread > 0:
            z_score = (spread - mean_spread) / std_spread
        else:
            z_score = 0
            
        # Sell signal: z-score is significantly positive (spread is above mean and expected to revert downward)
        # This means we expect the current price to decrease relative to the lagged price
        return z_score > self.z_threshold and spread > expected_spread
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"