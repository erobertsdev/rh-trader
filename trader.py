import config
import trade_strat
import win32api

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


def get_cash():
    rh_cash = rh.robinhood.account.build_user_profile()
    crypto_buying_power = rh.robinhood.profiles.load_account_profile(
        info='crypto_buying_power')
    cash = float(rh_cash['cash'])
    equity = float(rh_cash['equity'])
    return(cash, equity)


have_bought = False

if __name__ == "__main__":
    login(days=1)

    stocks = rh.robinhood.crypto.get_crypto_info('ETH')

    ts = trade_strat.trader(stocks)

    while open_market():

        prices = rh.robinhood.crypto.get_crypto_quote('ETH')
        data = ts.get_historical_prices()
        ask_price = prices['ask_price']

        sma = ts.get_sma('ETH', data, window=12)
        p_sma = ts.get_price_sma(float(ask_price), sma)
        trade = ts.trade_option(p_sma)
        print('Price:', float(ask_price))
        print('sma: ', sma)
        print('p_sma: ', p_sma)
        print('CHOICE: ', trade)
        print('Balance: ', get_cash()[0])
        
        if trade == 'BUY' and have_bought == False:
            print("BOUGHT AT: ", float(ask_price))
            robin_stocks.robinhood.orders.order_buy_crypto_limit_by_price('ETH', 10000, ask_price, timeInForce='gtc', jsonify=True)
            bought_price = float(ask_price)
            have_bought = True
            win32api.MessageBox(0, 'BUY MOTHER FUCKER', 'BUY BUY BUY', 0x00001000)
        elif trade == 'SELL' and have_bought == True:
            print('SOLD AT: ', float(ask_price))
            sold_price = float(ask_price)
            profit = sold_price - bought_price
            win32api.MessageBox(0, 'SELL SELL SELL', 'SELL SELL', 0x00001000)
            print('PROFIT: ', profit * 3)
            have_bought = False

        time.sleep(15)

    logout()
