class RSI_Strategy:
    def __init__(self, dataScraper, date, window=14, buy_threshold=30, sell_threshold=70):
        self.date = date
        self.dataScraper = dataScraper
        self.window = window
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)
        rsi = self.get_rsi(curr_index)
        rsi_prev = self.get_rsi(curr_index - 1)
        # Buy signal: RSI crosses above buy_threshold (e.g. 30)
        return rsi_prev <= self.buy_threshold and rsi > self.buy_threshold

    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)
        rsi = self.get_rsi(curr_index)
        rsi_prev = self.get_rsi(curr_index - 1)
        # Sell signal: RSI crosses below sell_threshold (e.g. 70)
        return rsi_prev >= self.sell_threshold and rsi < self.sell_threshold

    def get_rsi(self, end_index):
        # Calculate RSI using the classic method
        if end_index < self.window:
            # Not enough data yet
            return 50.0  # neutral RSI

        gains = 0.0
        losses = 0.0

        for i in range(end_index - self.window + 1, end_index + 1):
            change = float(self.dataScraper.getNumData(i, "Close")) - float(self.dataScraper.getNumData(i - 1, "Close"))
            if change > 0:
                gains += change
            else:
                losses -= change  # losses are positive values

        avg_gain = gains / self.window
        avg_loss = losses / self.window

        if avg_loss == 0:
            return 100.0  # no losses → RSI = 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def setDate(self, date):
        self.date = date

    def getType(self):
        return "Close"