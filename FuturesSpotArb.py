class FuturesSpotArb:
    def __init__(self, dataScraper, date, lookback=20, arb_threshold=0.01, futures_lag=5):
        self.date = date
        self.dataScraper = dataScraper
        self.lookback = lookback  # Window for calculating fair value
        self.arb_threshold = arb_threshold  # Minimum arbitrage opportunity to trigger
        self.futures_lag = futures_lag  # Simulated lag to represent futures expiry
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for calculations
        if curr_index < self.lookback + self.futures_lag:
            return False
            
        # In a real futures vs spot arbitrage, we would:
        # 1. Calculate the fair futures price based on spot price, interest rates, and time to expiry
        # 2. Compare actual futures price to fair value
        # 3. Buy spot and sell futures when futures are overpriced
        # 4. Buy futures and sell spot when futures are underpriced
        
        # Since we don't have actual futures data, we'll simulate by:
        # - Using current price as "spot"
        # - Using a lagged price adjusted by a carrying cost as simulated "futures"
        # - Calculating theoretical fair value based on interest rates and time
        
        # Get current spot price
        spot_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Simulate futures price (using lagged data + adjustment)
        # In reality, futures would be priced with carrying costs
        lagged_index = curr_index - self.futures_lag
        lagged_price = float(self.dataScraper.getNumData(lagged_index, "Close"))
        
        # Simulate carrying cost (interest rate effect)
        simulated_interest_rate = 0.03  # 3% annual rate
        daily_rate = simulated_interest_rate / 365
        carrying_cost = lagged_price * daily_rate * self.futures_lag
        
        # Simulated futures price
        futures_price = lagged_price + carrying_cost
        
        # Calculate fair futures price
        fair_futures_price = self.calculate_fair_futures_price(spot_price, self.futures_lag)
        
        # Calculate basis (difference between futures and fair value)
        basis = futures_price - fair_futures_price
        relative_basis = basis / spot_price  # Normalize by spot price
        
        # Buy signal: futures are underpriced relative to spot
        # In this case, we would buy futures and short spot, but since we can only go long,
        # we'll use this as a buy signal for the underlying
        return relative_basis < -self.arb_threshold
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for calculations
        if curr_index < self.lookback + self.futures_lag:
            return False
            
        # Get current spot price
        spot_price = float(self.dataScraper.getDateData(self.date, "Close"))
        
        # Simulate futures price
        lagged_index = curr_index - self.futures_lag
        lagged_price = float(self.dataScraper.getNumData(lagged_index, "Close"))
        
        # Simulate carrying cost
        simulated_interest_rate = 0.03  # 3% annual rate
        daily_rate = simulated_interest_rate / 365
        carrying_cost = lagged_price * daily_rate * self.futures_lag
        
        # Simulated futures price
        futures_price = lagged_price + carrying_cost
        
        # Calculate fair futures price
        fair_futures_price = self.calculate_fair_futures_price(spot_price, self.futures_lag)
        
        # Calculate basis
        basis = futures_price - fair_futures_price
        relative_basis = basis / spot_price
        
        # Sell signal: futures are overpriced relative to spot
        # In this case, we would sell futures and buy spot, but since we're simulating,
        # we'll use this as a sell signal for the underlying
        return relative_basis > self.arb_threshold
    
    def calculate_fair_futures_price(self, spot_price, days_to_expiry):
        """Calculate theoretical fair futures price"""
        # F = S * (1 + r*t)
        # where F is futures price, S is spot price, r is interest rate, t is time to expiry
        
        # Simulate risk-free rate and dividend yield
        risk_free_rate = 0.02  # 2% annual risk-free rate
        dividend_yield = 0.01  # 1% annual dividend yield
        
        # Convert to daily rates
        daily_rate = risk_free_rate / 365
        daily_dividend = dividend_yield / 365
        
        # Calculate cost of carry
        net_carry_rate = daily_rate - daily_dividend
        
        # Fair futures price
        return spot_price * (1 + net_carry_rate * days_to_expiry)
    
    def calculate_historical_basis(self, end_index):
        """Calculate average historical basis to identify unusual deviations"""
        basis_values = []
        
        for i in range(end_index - self.lookback, end_index):
            # Get spot price
            spot_price = float(self.dataScraper.getNumData(i, "Close"))
            
            # Simulate futures price
            if i - self.futures_lag >= 0:
                lagged_price = float(self.dataScraper.getNumData(i - self.futures_lag, "Close"))
                
                # Simulate carrying cost
                simulated_interest_rate = 0.03
                daily_rate = simulated_interest_rate / 365
                carrying_cost = lagged_price * daily_rate * self.futures_lag
                
                # Simulated futures price
                futures_price = lagged_price + carrying_cost
                
                # Calculate fair futures price
                fair_futures_price = self.calculate_fair_futures_price(spot_price, self.futures_lag)
                
                # Calculate basis
                basis = futures_price - fair_futures_price
                relative_basis = basis / spot_price
                
                basis_values.append(relative_basis)
        
        # Calculate average basis
        if basis_values:
            return sum(basis_values) / len(basis_values)
        else:
            return 0
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"