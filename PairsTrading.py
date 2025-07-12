class PairsTrading:
    def __init__(self, dataScraper, date, window=20, z_threshold=2.0):
        self.date = date
        self.dataScraper = dataScraper
        self.window = window  # Window for calculating the spread's mean and standard deviation
        self.z_threshold = z_threshold  # Z-score threshold for trading signals
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the window
        if curr_index < self.window:
            return False
            
        # In a real pairs trading strategy, we would have data for two correlated assets
        # Since we only have one asset, we'll simulate by comparing the asset to a moving average
        
        # Calculate the "spread" as the difference between current price and its moving average
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        ma = self.calculate_ma(curr_index)
        spread = current_price - ma
        
        # Calculate the mean and standard deviation of the spread over the window
        spreads = []
        for i in range(curr_index - self.window + 1, curr_index + 1):
            price = float(self.dataScraper.getNumData(i, "Close"))
            ma_i = self.calculate_ma(i)
            spreads.append(price - ma_i)
            
        mean_spread = sum(spreads) / len(spreads)
        std_spread = (sum((s - mean_spread) ** 2 for s in spreads) / len(spreads)) ** 0.5
        
        # Calculate z-score
        if std_spread > 0:
            z_score = (spread - mean_spread) / std_spread
        else:
            z_score = 0
            
        # Buy signal: z-score is significantly negative (asset is undervalued relative to its pair)
        return z_score < -self.z_threshold
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the window
        if curr_index < self.window:
            return False
            
        # Calculate the "spread" as the difference between current price and its moving average
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        ma = self.calculate_ma(curr_index)
        spread = current_price - ma
        
        # Calculate the mean and standard deviation of the spread over the window
        spreads = []
        for i in range(curr_index - self.window + 1, curr_index + 1):
            price = float(self.dataScraper.getNumData(i, "Close"))
            ma_i = self.calculate_ma(i)
            spreads.append(price - ma_i)
            
        mean_spread = sum(spreads) / len(spreads)
        std_spread = (sum((s - mean_spread) ** 2 for s in spreads) / len(spreads)) ** 0.5
        
        # Calculate z-score
        if std_spread > 0:
            z_score = (spread - mean_spread) / std_spread
        else:
            z_score = 0
            
        # Sell signal: z-score is significantly positive (asset is overvalued relative to its pair)
        return z_score > self.z_threshold
    
    def calculate_ma(self, end_index):
        """Calculate the moving average for the specified window"""
        sum_prices = 0.0
        
        for i in range(end_index - self.window + 1, end_index + 1):
            sum_prices += float(self.dataScraper.getNumData(i, "Close"))
            
        return sum_prices / self.window
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"