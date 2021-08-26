import pandas as pd

import robin_stocks as rh
import robin_stocks.helper as helper
import robin_stocks.urls as urls


class trader():
    def __init__(self, stocks):
        self.stocks = stocks

        self.sma_hour = {'ETHUSD': 0 for i in range(0, len(stocks))}
        self.run_time = 0
        # self.buffeer = 0.005 #0.5%

        self.price_sma_hour = {'ETHUSD': 0 for i in range(0, len(stocks))}

        # print('price_sma_hour:', self.price_sma_hour)

    def get_historical_prices(self):
        # span_interval = {'day': '5minute', 'week': '10minute',
        #                  'month': 'hour', '3month': 'hour', 'year': 'day', '5year': 'week'}
        # interval = span_interval[span]

        # url = urls.historicals()
        # payload = {'symbols': 'ETHUSD',
        #            'interval': interval,
        #            'span': span,
        #            'bounds': 'regular'}

        # symbol, interval, span, bounds, info
        historical_data = rh.robinhood.crypto.get_crypto_historicals(
            'ETH', span='day', interval='5minute')

        df = pd.DataFrame(historical_data)

        dates_times = pd.to_datetime(df.loc[:, 'begins_at'])
        close_prices = df.loc[:, 'close_price'].astype('float')

        df_price = pd.concat([close_prices, dates_times], axis=1)
        df_price = df_price.rename(columns={'close_price': 'ETH'})
        df_price = df_price.set_index('begins_at')

        return(df_price)