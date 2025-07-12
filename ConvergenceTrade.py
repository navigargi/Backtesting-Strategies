class ConvergenceTrade:
    def __init__(self, dataScraper, date, window=60, z_threshold=2.0, ratio_window=120):
        self.date = date
        self.dataScraper = dataScraper
        self.window = window  # Window for calculating recent price ratio statistics
        self.z_threshold = z_threshold  # Z-score threshold for trading signals
        self.ratio_window = ratio_window  # Window for establishing the historical relationship
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for both windows
        if curr_index < self.ratio_window:
            return False
            
        # In a real convergence trade strategy, we would have data for two related assets
        # Since we only have one asset, we'll simulate by comparing the asset to a smoothed version of itself
        
        # Get current price
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Calculate a smoothed price (e.g., 30-day moving average) to simulate a related asset
        smoothed_price = self.calculate_ma(curr_index, 30)
        
        # Calculate the current price ratio
        if smoothed_price > 0:
            current_ratio = current_price / smoothed_price
        else:
            return False
        
        # Calculate the historical price ratios over the ratio_window
        historical_ratios = []
        for i in range(curr_index - self.ratio_window + 1, curr_index + 1):
            if i >= 30:  # Need enough data for the moving average
                price_i = float(self.dataScraper.getNumData(i, "Close"))
                smoothed_i = self.calculate_ma(i, 30)
                if smoothed_i > 0:
                    historical_ratios.append(price_i / smoothed_i)
        
        # Calculate the mean and standard deviation of the historical ratios
        if not historical_ratios:
            return False
            
        mean_ratio = sum(historical_ratios) / len(historical_ratios)
        std_ratio = (sum((r - mean_ratio) ** 2 for r in historical_ratios) / len(historical_ratios)) ** 0.5
        
        # Calculate the recent price ratios over the window
        recent_ratios = historical_ratios[-self.window:] if len(historical_ratios) >= self.window else historical_ratios
        
        # Calculate the mean and standard deviation of the recent ratios
        if not recent_ratios:
            return False
            
        recent_mean = sum(recent_ratios) / len(recent_ratios)
        recent_std = (sum((r - recent_mean) ** 2 for r in recent_ratios) / len(recent_ratios)) ** 0.5
        
        # Calculate the z-score of the current ratio relative to the historical distribution
        if std_ratio > 0:
            z_score_historical = (current_ratio - mean_ratio) / std_ratio
        else:
            z_score_historical = 0
            
        # Calculate the z-score of the current ratio relative to the recent distribution
        if recent_std > 0:
            z_score_recent = (current_ratio - recent_mean) / recent_std
        else:
            z_score_recent = 0
        
        # Buy signal: current ratio is significantly below historical mean (asset is undervalued)
        # and the ratio has started to revert (recent z-score is less extreme than historical z-score)
        return (z_score_historical < -self.z_threshold and 
                abs(z_score_recent) < abs(z_score_historical))
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for both windows
        if curr_index < self.ratio_window:
            return False
            
        # Get current price
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Calculate a smoothed price (e.g., 30-day moving average) to simulate a related asset
        smoothed_price = self.calculate_ma(curr_index, 30)
        
        # Calculate the current price ratio
        if smoothed_price > 0:
            current_ratio = current_price / smoothed_price
        else:
            return False
        
        # Calculate the historical price ratios over the ratio_window
        historical_ratios = []
        for i in range(curr_index - self.ratio_window + 1, curr_index + 1):
            if i >= 30:  # Need enough data for the moving average
                price_i = float(self.dataScraper.getNumData(i, "Close"))
                smoothed_i = self.calculate_ma(i, 30)
                if smoothed_i > 0:
                    historical_ratios.append(price_i / smoothed_i)
        
        # Calculate the mean and standard deviation of the historical ratios
        if not historical_ratios:
            return False
            
        mean_ratio = sum(historical_ratios) / len(historical_ratios)
        std_ratio = (sum((r - mean_ratio) ** 2 for r in historical_ratios) / len(historical_ratios)) ** 0.5
        
        # Calculate the recent price ratios over the window
        recent_ratios = historical_ratios[-self.window:] if len(historical_ratios) >= self.window else historical_ratios
        
        # Calculate the mean and standard deviation of the recent ratios
        if not recent_ratios:
            return False
            
        recent_mean = sum(recent_ratios) / len(recent_ratios)
        recent_std = (sum((r - recent_mean) ** 2 for r in recent_ratios) / len(recent_ratios)) ** 0.5
        
        # Calculate the z-score of the current ratio relative to the historical distribution
        if std_ratio > 0:
            z_score_historical = (current_ratio - mean_ratio) / std_ratio
        else:
            z_score_historical = 0
            
        # Calculate the z-score of the current ratio relative to the recent distribution
        if recent_std > 0:
            z_score_recent = (current_ratio - recent_mean) / recent_std
        else:
            z_score_recent = 0
        
        # Sell signal: current ratio is significantly above historical mean (asset is overvalued)
        # and the ratio has started to revert (recent z-score is less extreme than historical z-score)
        return (z_score_historical > self.z_threshold and 
                abs(z_score_recent) < abs(z_score_historical))
    
    def calculate_ma(self, end_index, window):
        """Calculate the moving average for the specified window"""
        sum_prices = 0.0
        count = 0
        
        for i in range(end_index - window + 1, end_index + 1):
            if i >= 0:  # Ensure we don't go out of bounds
                sum_prices += float(self.dataScraper.getNumData(i, "Close"))
                count += 1
                
        return sum_prices / count if count > 0 else 0.0
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"