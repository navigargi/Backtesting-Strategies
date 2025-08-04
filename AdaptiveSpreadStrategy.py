class AdaptiveSpreadStrategy:
    def __init__(self, dataScraper, date, base_spread=0.001, volatility_window=10, vol_multiplier=2.0):
        self.date = date
        self.dataScraper = dataScraper
        self.base_spread = base_spread  # Base spread when volatility is normal
        self.volatility_window = volatility_window  # Window for volatility calculation
        self.vol_multiplier = vol_multiplier  # How much to adjust spread based on volatility

    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)

        # Need enough data for volatility calculation
        if curr_index < self.volatility_window:
            return False

        # Calculate current volatility
        volatility = self.calculate_volatility(curr_index)

        # Adjust spread based on volatility
        adaptive_spread = self.base_spread * (1 + self.vol_multiplier * volatility)

        # Get current high and low prices to estimate the market spread
        high_price = float(self.dataScraper.getDateData(self.date, "High"))
        low_price = float(self.dataScraper.getDateData(self.date, "Low"))

        # Calculate estimated market spread
        market_spread = (high_price - low_price) / low_price

        # Current close
        current_close = float(self.dataScraper.getDateData(self.date, "Close"))

        # Buy signal: market spread is wider than our adaptive spread and price is near the low
        # This simulates placing a buy order at a price that's competitive but adjusted for volatility
        return (market_spread > adaptive_spread and
                current_close < (low_price + (high_price - low_price) * 0.35))

    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)

        # Need enough data for volatility calculation
        if curr_index < self.volatility_window:
            return False

        # Calculate current volatility
        volatility = self.calculate_volatility(curr_index)

        # Adjust spread based on volatility
        adaptive_spread = self.base_spread * (1 + self.vol_multiplier * volatility)

        # Get current high and low prices to estimate the market spread
        high_price = float(self.dataScraper.getDateData(self.date, "High"))
        low_price = float(self.dataScraper.getDateData(self.date, "Low"))

        # Calculate estimated market spread
        market_spread = (high_price - low_price) / low_price

        # Current close
        current_close = float(self.dataScraper.getDateData(self.date, "Close"))

        # Sell signal: market spread is wider than our adaptive spread and price is near the high
        # This simulates placing a sell order at a price that's competitive but adjusted for volatility
        return (market_spread > adaptive_spread and
                current_close > (low_price + (high_price - low_price) * 0.55))

    def calculate_volatility(self, end_index):
        """Calculate the volatility (standard deviation of returns) for the specified window"""
        returns = []

        for i in range(end_index - self.volatility_window, end_index):
            price_t = float(self.dataScraper.getNumData(i, "Close"))
            price_t_1 = float(self.dataScraper.getNumData(i + 1, "Close"))
            returns.append((price_t_1 - price_t) / price_t)

        # Calculate standard deviation of returns
        mean_return = sum(returns) / len(returns)
        sum_squared_diff = sum((r - mean_return) ** 2 for r in returns)
        return (sum_squared_diff / len(returns)) ** 0.5

    def setDate(self, date):
        self.date = date

    def getType(self):
        return "Close"