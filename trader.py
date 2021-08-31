import config
import trade_strat
import win32api
# from playsound import playsound

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
        ask_price = float(prices['ask_price'])

        sma = ts.get_sma('ETH', data, window=12)
        p_sma = ts.get_price_sma(ask_price, sma)
        trade = ts.trade_option(p_sma)
        owned_qty = float(rh.robinhood.crypto.get_crypto_positions(info='quantity_available')[1])
        balance = get_cash()[0]
        print('Price:', ask_price)
        print('sma: ', sma)
        print('p_sma: ', p_sma)
        print('CHOICE: ', trade)
        print('Balance: ', balance)
        print('Have Bought? ', have_bought)
        print('Owned: ', owned_qty)
        
        if trade == 'BUY' and have_bought == False:
            print("BOUGHT AT: ", ask_price)
            rh.robinhood.orders.order_buy_crypto_limit_by_price('ETH', balance - 200, ask_price, timeInForce='gtc', jsonify=True)
            bought_price = ask_price
            have_bought = True
            # playsound('./ring01.wav')
            win32api.MessageBox(0, 'JUST BOUGHT', 'BUY BUY BUY', 0x00001000)
        elif trade == 'SELL' and have_bought == True:
            print(have_bought)
            print('SOLD AT: ', ask_price)
            sold_price = ask_price
            profit = sold_price - bought_price
            rh.robinhood.orders.order_sell_crypto_limit_by_price('ETH', owned_qty, ask_price, timeInForce='gtc', jsonify=True)
            # playsound('./ring01.wav')
            win32api.MessageBox(0, 'SELL SELL SELL', 'SELL SELL', 0x00001000)
            print('PROFIT: ', profit * 3)
            have_bought = False

        time.sleep(60)

    logout()
