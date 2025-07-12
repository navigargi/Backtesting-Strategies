class EMA_Cross:
    def __init__(self, dataScraper, date):
        self.date = date
        self.dataScraper = dataScraper

    def buy(self):
        curr_index = self.dataScraper.getRow(self.date)

        ema_5 = self.get_ema(curr_index, 5)
        ema_20 = self.get_ema(curr_index, 20)


        ema_5_prev = self.get_ema(curr_index - 1, 5)
        ema_20_prev = self.get_ema(curr_index - 1, 20)


        return ema_5_prev <= ema_20_prev and ema_5 > ema_20

    def sell(self):
        curr_index = self.dataScraper.getRow(self.date)



        ema_5 = self.get_ema(curr_index, 5)
        ema_20 = self.get_ema(curr_index, 20)


        ema_5_prev = self.get_ema(curr_index - 1, 5)
        ema_20_prev = self.get_ema(curr_index - 1, 20)


        return ema_5_prev >= ema_20_prev and ema_5 < ema_20

    def get_ema(self, end_index, window):
        alpha = 2 / (window + 1)
        ema = float(self.dataScraper.getNumData(end_index - window + 1, "Close"))
        for i in range(end_index - window + 2, end_index + 1):
            price = float(self.dataScraper.getNumData(i, "Close"))
            ema = price * alpha + ema * (1 - alpha)
        return ema

    def setDate(self, date):
        self.date = date

    def getType(self):
        return "Close"