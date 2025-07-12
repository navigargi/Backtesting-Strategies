class CalendarSpread:
    def __init__(self, dataScraper, date, lookback=20, spread_threshold=0.015, 
                 near_term_lag=5, far_term_lag=20):
        self.date = date
        self.dataScraper = dataScraper
        self.lookback = lookback  # Window for calculating historical spreads
        self.spread_threshold = spread_threshold  # Threshold for trading signals
        self.near_term_lag = near_term_lag  # Simulated near-term futures (e.g., front month)
        self.far_term_lag = far_term_lag  # Simulated far-term futures (e.g., back month)
        
    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for calculations
        if curr_index < self.lookback + self.far_term_lag:
            return False
            
        # In a real calendar spread strategy, we would:
        # 1. Calculate the spread between near-term and far-term futures
        # 2. Compare current spread to historical spreads
        # 3. Buy the spread (long far-term, short near-term) when it's abnormally narrow
        # 4. Sell the spread (short far-term, long near-term) when it's abnormally wide
        
        # Since we don't have actual futures data, we'll simulate by:
        # - Using lagged prices with different lags to represent different maturities
        # - Adjusting for carrying costs to simulate futures pricing
        
        # Calculate current calendar spread
        current_spread = self.calculate_calendar_spread(curr_index)
        
        # Calculate historical average spread and standard deviation
        historical_spreads = []
        for i in range(curr_index - self.lookback, curr_index):
            historical_spreads.append(self.calculate_calendar_spread(i))
        
        avg_spread = sum(historical_spreads) / len(historical_spreads)
        std_dev = (sum((s - avg_spread) ** 2 for s in historical_spreads) / len(historical_spreads)) ** 0.5
        
        # Calculate z-score of current spread
        z_score = (current_spread - avg_spread) / std_dev if std_dev > 0 else 0
        
        # Buy signal: spread is abnormally narrow (z-score < -2)
        # In a real calendar spread, we would buy the spread (long far-term, short near-term)
        # Since we can only go long the underlying, we'll use this as a buy signal when
        # the far-term futures are undervalued relative to near-term
        return z_score < -2 and current_spread < avg_spread - self.spread_threshold
    
    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        
        # Need enough data for calculations
        if curr_index < self.lookback + self.far_term_lag:
            return False
            
        # Calculate current calendar spread
        current_spread = self.calculate_calendar_spread(curr_index)
        
        # Calculate historical average spread and standard deviation
        historical_spreads = []
        for i in range(curr_index - self.lookback, curr_index):
            historical_spreads.append(self.calculate_calendar_spread(i))
        
        avg_spread = sum(historical_spreads) / len(historical_spreads)
        std_dev = (sum((s - avg_spread) ** 2 for s in historical_spreads) / len(historical_spreads)) ** 0.5
        
        # Calculate z-score of current spread
        z_score = (current_spread - avg_spread) / std_dev if std_dev > 0 else 0
        
        # Sell signal: spread is abnormally wide (z-score > 2)
        # In a real calendar spread, we would sell the spread (short far-term, long near-term)
        # Since we can only go long the underlying, we'll use this as a sell signal when
        # the far-term futures are overvalued relative to near-term
        return z_score > 2 and current_spread > avg_spread + self.spread_threshold
    
    def calculate_calendar_spread(self, index):
        """Calculate the simulated calendar spread between near-term and far-term futures"""
        # Get spot price (current price)
        spot_price = float(self.dataScraper.getNumData(index, "Close"))
        
        # Simulate near-term futures price
        near_term_index = index - self.near_term_lag
        if near_term_index < 0:
            return 0  # Not enough data
            
        near_term_price = float(self.dataScraper.getNumData(near_term_index, "Close"))
        
        # Simulate far-term futures price
        far_term_index = index - self.far_term_lag
        if far_term_index < 0:
            return 0  # Not enough data
            
        far_term_price = float(self.dataScraper.getNumData(far_term_index, "Close"))
        
        # Adjust prices with carrying costs to simulate futures pricing
        near_term_futures = self.adjust_with_carrying_cost(near_term_price, self.near_term_lag)
        far_term_futures = self.adjust_with_carrying_cost(far_term_price, self.far_term_lag)
        
        # Calculate spread as percentage difference
        # In futures markets, calendar spread is often quoted as far_term - near_term
        spread = (far_term_futures - near_term_futures) / near_term_futures
        
        return spread
    
    def adjust_with_carrying_cost(self, price, days_to_expiry):
        """Adjust price with carrying cost to simulate futures pricing"""
        # Simulate risk-free rate and dividend yield
        risk_free_rate = 0.02  # 2% annual risk-free rate
        dividend_yield = 0.01  # 1% annual dividend yield
        
        # Convert to daily rates
        daily_rate = risk_free_rate / 365
        daily_dividend = dividend_yield / 365
        
        # Calculate net cost of carry
        net_carry_rate = daily_rate - daily_dividend
        
        # Adjust price with carrying cost
        return price * (1 + net_carry_rate * days_to_expiry)
    
    def calculate_theoretical_spread(self, spot_price):
        """Calculate theoretical calendar spread based on cost of carry model"""
        # In a perfect market, the spread between futures with different maturities
        # should reflect the cost of carry between the two expiration dates
        
        # Calculate carrying costs for near-term and far-term
        near_term_carry = self.calculate_carrying_cost(self.near_term_lag)
        far_term_carry = self.calculate_carrying_cost(self.far_term_lag)
        
        # Calculate theoretical prices
        near_term_theoretical = spot_price * (1 + near_term_carry)
        far_term_theoretical = spot_price * (1 + far_term_carry)
        
        # Calculate theoretical spread
        theoretical_spread = (far_term_theoretical - near_term_theoretical) / near_term_theoretical
        
        return theoretical_spread
    
    def calculate_carrying_cost(self, days_to_expiry):
        """Calculate carrying cost for a given time period"""
        # Simulate risk-free rate and dividend yield
        risk_free_rate = 0.02  # 2% annual risk-free rate
        dividend_yield = 0.01  # 1% annual dividend yield
        
        # Convert to daily rates
        daily_rate = risk_free_rate / 365
        daily_dividend = dividend_yield / 365
        
        # Calculate net cost of carry
        net_carry_rate = daily_rate - daily_dividend
        
        # Total carrying cost for the period
        return net_carry_rate * days_to_expiry
    
    def setDate(self, date):
        self.date = date
    
    def getType(self):
        return "Close"