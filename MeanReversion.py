class MeanReversion:
    def __init__(self, dataScraper, date, window=20, std_dev=2):
        self.date = date
        self.dataScraper = dataScraper
        self.window = window
        self.std_dev = std_dev  # Number of standard deviations for bands

    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the moving average window
        if curr_index < self.window:
            return False
            
        # Get current price
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Calculate moving average and standard deviation
        ma = self.calculate_ma(curr_index)
        std = self.calculate_std(curr_index, ma)
        
        # Calculate lower band
        lower_band = ma - (self.std_dev * std)
        
        # Buy signal: price is below the lower band (oversold condition)
        return current_price < lower_band

    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the moving average window
        if curr_index < self.window:
            return False
            
        # Get current price
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Calculate moving average and standard deviation
        ma = self.calculate_ma(curr_index)
        
        # Sell signal: price has reverted back to or above the mean
        return current_price >= ma

    def calculate_ma(self, end_index):
        """Calculate the moving average for the specified window"""
        sum_prices = 0.0
        
        for i in range(end_index - self.window + 1, end_index + 1):
            sum_prices += float(self.dataScraper.getNumData(i, "Close"))
            
        return sum_prices / self.window

    def calculate_std(self, end_index, ma):
        """Calculate the standard deviation for the specified window"""
        sum_squared_diff = 0.0
        
        for i in range(end_index - self.window + 1, end_index + 1):
            price = float(self.dataScraper.getNumData(i, "Close"))
            sum_squared_diff += (price - ma) ** 2
            
        return (sum_squared_diff / self.window) ** 0.5

    def setDate(self, date):
        self.date = date

    def getType(self):
        return "Close"