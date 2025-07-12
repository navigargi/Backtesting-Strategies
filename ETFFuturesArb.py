class ETFFuturesArb:
    def __init__(self, dataScraper, date, window=20, z_threshold=2.0, futures_lag=1):
        self.date = date
        self.dataScraper = dataScraper
        self.window = window  # Window for calculating the spread's mean and standard deviation
        self.z_threshold = z_threshold  # Z-score threshold for trading signals
        self.futures_lag = futures_lag  # Lag to simulate futures data
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the window and to simulate futures
        if curr_index < self.window + self.futures_lag:
            return False
            
        # In a real ETF vs Futures arbitrage strategy, we would have data for both the ETF and its futures
        # Since we only have one asset, we'll simulate by comparing the asset to a lagged version of itself
        # with a slight premium (simulating futures premium)
        
        # Get current price (simulating ETF price)
        etf_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Get lagged price with premium (simulating futures price)
        futures_price = float(self.dataScraper.getNumData(curr_index - self.futures_lag, "Close")) * 1.001
        
        # Calculate the "basis" (difference between futures and ETF)
        basis = futures_price - etf_price
        
        # Calculate the mean and standard deviation of the basis over the window
        bases = []
        for i in range(curr_index - self.window + 1, curr_index + 1):
            if i - self.futures_lag >= 0:  # Ensure we don't go out of bounds
                etf_price_i = float(self.dataScraper.getNumData(i, "Close"))
                futures_price_i = float(self.dataScraper.getNumData(i - self.futures_lag, "Close")) * 1.001
                bases.append(futures_price_i - etf_price_i)
            
        mean_basis = sum(bases) / len(bases)
        std_basis = (sum((b - mean_basis) ** 2 for b in bases) / len(bases)) ** 0.5
        
        # Calculate z-score
        if std_basis > 0:
            z_score = (basis - mean_basis) / std_basis
        else:
            z_score = 0
            
        # Buy signal: z-score is significantly negative (ETF is overpriced relative to futures)
        # In a real arbitrage, we would short the ETF and buy the futures
        # Since we can only trade one asset, we'll simulate by selling when the ETF is overpriced
        return z_score < -self.z_threshold
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the window and to simulate futures
        if curr_index < self.window + self.futures_lag:
            return False
            
        # Get current price (simulating ETF price)
        etf_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Get lagged price with premium (simulating futures price)
        futures_price = float(self.dataScraper.getNumData(curr_index - self.futures_lag, "Close")) * 1.001
        
        # Calculate the "basis" (difference between futures and ETF)
        basis = futures_price - etf_price
        
        # Calculate the mean and standard deviation of the basis over the window
        bases = []
        for i in range(curr_index - self.window + 1, curr_index + 1):
            if i - self.futures_lag >= 0:  # Ensure we don't go out of bounds
                etf_price_i = float(self.dataScraper.getNumData(i, "Close"))
                futures_price_i = float(self.dataScraper.getNumData(i - self.futures_lag, "Close")) * 1.001
                bases.append(futures_price_i - etf_price_i)
            
        mean_basis = sum(bases) / len(bases)
        std_basis = (sum((b - mean_basis) ** 2 for b in bases) / len(bases)) ** 0.5
        
        # Calculate z-score
        if std_basis > 0:
            z_score = (basis - mean_basis) / std_basis
        else:
            z_score = 0
            
        # Sell signal: z-score is significantly positive (ETF is underpriced relative to futures)
        # In a real arbitrage, we would buy the ETF and short the futures
        # Since we can only trade one asset, we'll simulate by buying when the ETF is underpriced
        return z_score > self.z_threshold
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"