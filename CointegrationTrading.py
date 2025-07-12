class CointegrationTrading:
    def __init__(self, dataScraper, date, window=60, z_threshold=2.0, lookback=20):
        self.date = date
        self.dataScraper = dataScraper
        self.window = window  # Window for estimating cointegration parameters
        self.z_threshold = z_threshold  # Z-score threshold for trading signals
        self.lookback = lookback  # Lookback period for simulating multiple assets
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the window and lookback
        if curr_index < self.window + self.lookback:
            return False
            
        # In a real cointegration-based trading strategy, we would have data for multiple assets
        # Since we only have one asset, we'll simulate by comparing the asset to a weighted combination
        # of its past values, which we'll treat as a "cointegrated basket"
        
        # Get current price
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Calculate the cointegration parameters (beta weights) using OLS regression
        # In a real scenario, we would regress one asset against others to find the cointegrating vector
        # Here we'll simulate by regressing current price against lagged prices
        
        # Collect data for regression
        y_values = []  # Current prices
        x_values = []  # Lagged prices (multiple lags to simulate multiple assets)
        
        for i in range(curr_index - self.window + 1, curr_index + 1):
            if i - self.lookback >= 0:  # Ensure we don't go out of bounds
                y_values.append(float(self.dataScraper.getNumData(i, "Close")))
                
                # Create a "row" of lagged prices for each data point
                x_row = []
                for lag in range(1, self.lookback + 1, 5):  # Use every 5th lag to reduce collinearity
                    if i - lag >= 0:
                        x_row.append(float(self.dataScraper.getNumData(i - lag, "Close")))
                    else:
                        x_row.append(0.0)
                x_values.append(x_row)
        
        # Simple OLS regression to estimate beta weights
        # In a real implementation, we would use proper statistical libraries
        beta_weights = self.simple_ols(x_values, y_values)
        
        # Calculate the predicted price based on the cointegration relationship
        predicted_price = 0.0
        for j, lag in enumerate(range(1, self.lookback + 1, 5)):
            if j < len(beta_weights) and curr_index - lag >= 0:
                predicted_price += beta_weights[j] * float(self.dataScraper.getNumData(curr_index - lag, "Close"))
        
        # Calculate the spread (residual) between actual and predicted price
        spread = current_price - predicted_price
        
        # Calculate the mean and standard deviation of the spread over the window
        spreads = []
        for i in range(curr_index - self.window + 1, curr_index + 1):
            if i - self.lookback >= 0:  # Ensure we don't go out of bounds
                actual = float(self.dataScraper.getNumData(i, "Close"))
                
                # Calculate predicted price for this point
                pred = 0.0
                for j, lag in enumerate(range(1, self.lookback + 1, 5)):
                    if j < len(beta_weights) and i - lag >= 0:
                        pred += beta_weights[j] * float(self.dataScraper.getNumData(i - lag, "Close"))
                
                spreads.append(actual - pred)
        
        mean_spread = sum(spreads) / len(spreads)
        std_spread = (sum((s - mean_spread) ** 2 for s in spreads) / len(spreads)) ** 0.5
        
        # Calculate the z-score of the current spread
        if std_spread > 0:
            z_score = (spread - mean_spread) / std_spread
        else:
            z_score = 0
            
        # Buy signal: z-score is significantly negative (actual price is below predicted price)
        # This suggests the asset is undervalued relative to its cointegrated relationship
        return z_score < -self.z_threshold
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for the window and lookback
        if curr_index < self.window + self.lookback:
            return False
            
        # Get current price
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Calculate the cointegration parameters (beta weights) using OLS regression
        y_values = []  # Current prices
        x_values = []  # Lagged prices (multiple lags to simulate multiple assets)
        
        for i in range(curr_index - self.window + 1, curr_index + 1):
            if i - self.lookback >= 0:  # Ensure we don't go out of bounds
                y_values.append(float(self.dataScraper.getNumData(i, "Close")))
                
                # Create a "row" of lagged prices for each data point
                x_row = []
                for lag in range(1, self.lookback + 1, 5):  # Use every 5th lag to reduce collinearity
                    if i - lag >= 0:
                        x_row.append(float(self.dataScraper.getNumData(i - lag, "Close")))
                    else:
                        x_row.append(0.0)
                x_values.append(x_row)
        
        # Simple OLS regression to estimate beta weights
        beta_weights = self.simple_ols(x_values, y_values)
        
        # Calculate the predicted price based on the cointegration relationship
        predicted_price = 0.0
        for j, lag in enumerate(range(1, self.lookback + 1, 5)):
            if j < len(beta_weights) and curr_index - lag >= 0:
                predicted_price += beta_weights[j] * float(self.dataScraper.getNumData(curr_index - lag, "Close"))
        
        # Calculate the spread (residual) between actual and predicted price
        spread = current_price - predicted_price
        
        # Calculate the mean and standard deviation of the spread over the window
        spreads = []
        for i in range(curr_index - self.window + 1, curr_index + 1):
            if i - self.lookback >= 0:  # Ensure we don't go out of bounds
                actual = float(self.dataScraper.getNumData(i, "Close"))
                
                # Calculate predicted price for this point
                pred = 0.0
                for j, lag in enumerate(range(1, self.lookback + 1, 5)):
                    if j < len(beta_weights) and i - lag >= 0:
                        pred += beta_weights[j] * float(self.dataScraper.getNumData(i - lag, "Close"))
                
                spreads.append(actual - pred)
        
        mean_spread = sum(spreads) / len(spreads)
        std_spread = (sum((s - mean_spread) ** 2 for s in spreads) / len(spreads)) ** 0.5
        
        # Calculate the z-score of the current spread
        if std_spread > 0:
            z_score = (spread - mean_spread) / std_spread
        else:
            z_score = 0
            
        # Sell signal: z-score is significantly positive (actual price is above predicted price)
        # This suggests the asset is overvalued relative to its cointegrated relationship
        return z_score > self.z_threshold
    
    def simple_ols(self, X, y):
        """
        Simple implementation of Ordinary Least Squares regression
        Returns beta weights for the regression y = X * beta
        """
        # Number of observations and features
        n = len(y)
        if n == 0 or len(X) == 0:
            return [0.0]
            
        p = len(X[0])
        
        # Calculate X'X (covariance matrix)
        XX = [[0.0 for _ in range(p)] for _ in range(p)]
        for i in range(p):
            for j in range(p):
                for k in range(n):
                    XX[i][j] += X[k][i] * X[k][j]
        
        # Calculate X'y
        Xy = [0.0 for _ in range(p)]
        for i in range(p):
            for k in range(n):
                Xy[i] += X[k][i] * y[k]
        
        # Solve for beta using a simple approximation
        # In a real implementation, we would use proper matrix inversion
        beta = [0.0 for _ in range(p)]
        for i in range(p):
            if XX[i][i] > 0:  # Avoid division by zero
                beta[i] = Xy[i] / XX[i][i]
        
        return beta
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"