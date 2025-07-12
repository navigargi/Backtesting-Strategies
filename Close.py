class Close:
    def __init__(self, dataScraper, date):
        self.date = date
        self.dataScraper = dataScraper

    def buy(self):
        prev_index = self.dataScraper.getRow(self.date) - 1
        prev_close = float(self.dataScraper.getNumData(prev_index, "Close"))
        curr_close = float(self.dataScraper.getDateData(self.date, "Close"))
        return curr_close > prev_close
    def sell(self):
        prev_index = self.dataScraper.getRow(self.date) - 1
        prev_close = float(self.dataScraper.getNumData(prev_index, "Close"))
        curr_close = float(self.dataScraper.getDateData(self.date, "Close"))
        return curr_close < prev_close
    def setDate(self, date):
        self.date = date
    def getType(self):
        return "Close"