import config
import trade_strat

import robin_stocks as rh
import datetime as dt
import time


def login(days):
    time_logged_in = 60*60*24*days
    rh.robinhood.authentication.login(username=config.USERNAME,
                                      password=config.PASSWORD,
                                      expiresIn=time_logged_in,
                                      scope='internal',
                                      store_session=True)


def logout():
    rh.robinhood.authentication.logout()


def get_stocks():
    stocks = list()
    stocks.append('ETH')
    return(stocks)


# MARKET IS ALWAYS OPEN ON CRYPTO, BITCH
def open_market():
    market = True
    # time_now = dt.datetime.now().time()

    # market_open = dt.time(7, 30, 0)  # 7:30AM
    # market_close = dt.time(13, 59, 0)  # 1:59PM

    # if time_now > market_open and time_now < market_close:
    #     market = True
    # else:
    #     print('### MARKET IS CLOSED, BITCH ###')

    return(market)


if __name__ == "__main__":
    login(days=1)

    stocks = rh.robinhood.crypto.get_crypto_info('ETH')

    ts = trade_strat.trader(stocks)

    while open_market():
        # prices = rh.robinhood.crypto.get_crypto_quote_from_id(stocks)
        prices = rh.robinhood.crypto.get_crypto_quote('ETH')
        data = ts.get_historical_prices()
        # print(prices)
        ask_price = prices['ask_price']
        print('Historical:', data)
        print('Current Ask Price:', float(ask_price))

        time.sleep(30)

    logout()
