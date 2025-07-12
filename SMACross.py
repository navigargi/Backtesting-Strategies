class SMA_Cross:
    def __init__(self, dataScraper, date):
        self.date = date
        self.dataScraper = dataScraper

    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)

        sma_5 = self.get_sma(curr_index, 5)
        sma_20 = self.get_sma(curr_index, 20)


        sma_5_prev = self.get_sma(curr_index - 1, 5)
        sma_20_prev = self.get_sma(curr_index - 1, 20)


        return sma_5_prev <= sma_20_prev and sma_5 > sma_20

    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)



        sma_5 = self.get_sma(curr_index, 5)
        sma_20 = self.get_sma(curr_index, 20)


        sma_5_prev = self.get_sma(curr_index - 1, 5)
        sma_20_prev = self.get_sma(curr_index - 1, 20)


        return sma_5_prev >= sma_20_prev and sma_5 < sma_20

    def get_sma(self, end_index, window):
        total = 0.0
        count = 0
        for i in range(end_index - window + 1, end_index + 1):
            price = float(self.dataScraper.getNumData(i, "Close"))
            total += price
            count += 1
        return total / count if count > 0 else 0.0

    def setDate(self, date):
        self.date = date

    def getType(self):
        return "Close"