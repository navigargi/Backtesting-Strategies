class VWAPDrift:
    def __init__(self, dataScraper, date, uptrend_threshold=0.05, downtrend_threshold=0.02):
        self.date = date
        self.dataScraper = dataScraper
        self.window_minutes = 10  # Always use the past 10 minutes
        self.uptrend_threshold = uptrend_threshold
        self.downtrend_threshold = downtrend_threshold

    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)

        if curr_index < self.window_minutes:
            return False

        vwap = self.calculate_vwap(curr_index)
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        deviation = (vwap - current_price) / vwap
        prev_price = float(self.dataScraper.getNumData(curr_index - 1, "Close"))
        price_change = (current_price - prev_price) / prev_price

        return deviation > self.downtrend_threshold and price_change > 0

    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)

        if curr_index < self.window_minutes:
            return False

        vwap = self.calculate_vwap(curr_index)
        current_price = float(self.dataScraper.getDateData(self.date, "Close"))
        deviation = (current_price - vwap) / vwap
        prev_price = float(self.dataScraper.getNumData(curr_index - 1, "Close"))
        price_change = (current_price - prev_price) / prev_price

        return deviation > self.uptrend_threshold and price_change < 0

    def calculate_vwap(self, end_index):
        sum_price_volume = 0.0
        sum_volume = 0.0

        for i in range(end_index - self.window_minutes + 1, end_index + 1):
            high = float(self.dataScraper.getNumData(i, "High"))
            low = float(self.dataScraper.getNumData(i, "Low"))
            close = float(self.dataScraper.getNumData(i, "Close"))
            typical_price = (high + low + close) / 3
            volume = float(self.dataScraper.getNumData(i, "Volume"))

            sum_price_volume += typical_price * volume
            sum_volume += volume

        return sum_price_volume / sum_volume if sum_volume > 0 else 0.0

    def setDate(self, date):
        self.date = date

    def getType(self):
        return "Close"