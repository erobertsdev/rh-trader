import config
import trade_strat_btc
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
    stocks.append(ticker)
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

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


have_bought = False
ticker = 'BTC'

if __name__ == "__main__":
    login(days=1)

    stocks = rh.robinhood.crypto.get_crypto_info(ticker)

    ts = trade_strat_btc.trader(stocks)

    while open_market():

        try:
            prices = rh.robinhood.crypto.get_crypto_quote(ticker)
            data = ts.get_historical_prices()
            ask_price = float(prices['ask_price'])

            sma = ts.get_sma(ticker, data, window=12)
            p_sma = ts.get_price_sma(ask_price, sma)
            trade = ts.trade_option(p_sma)
            owned_qty = float(rh.robinhood.crypto.get_crypto_positions(info='quantity_available')[1])
            balance = get_cash()[1]
            buy_amt = balance - 200
            # print(f'Balance: {balance}')
            # print(f'Buy Amount: {buy_amt}')
            
            print(f'Price: {ask_price} | sma: {sma} | p_sma: {p_sma} | {bcolors.WARNING}{trade}{bcolors.ENDC} | Owned: {owned_qty}')
            # print('sma: ', sma)
            # print('p_sma: ', p_sma)
            # print('CHOICE: ', trade)
            # print('Balance: ', balance)
            # print('Have Bought? ', have_bought)
            # print('Owned: ', owned_qty)
            
            if trade == 'BUY' and owned_qty <= 0:

                rh.robinhood.orders.order_buy_crypto_by_price(ticker, buy_amt, timeInForce='gtc', jsonify=True)
                bought_price = ask_price
                print(f"{bcolors.OKGREEN}BOUGHT AT: {ask_price}{bcolors.ENDC}")
                have_bought = True
                # playsound('./ring01.wav')
                # win32api.MessageBox(0, 'JUST BOUGHT', 'BUY BUY BUY', 0x00001000)
            elif trade == 'SELL' and ask_price > bought_price:

                sold_price = ask_price
                profit = sold_price - bought_price
                rh.robinhood.orders.order_sell_crypto_by_quantity(ticker, owned_qty, timeInForce='gtc', jsonify=True)
                # playsound('./ring01.wav')
                print('PROFIT: ', profit * owned_qty)
                print(f'{bcolors.OKGREEN}SOLD AT: {ask_price}{bcolors.ENDC}')
                have_bought = False
                # win32api.MessageBox(0, 'JUST SOLD', 'SELL SELL', 0x00001000)

            if have_bought == False:
                time.sleep(3)
            elif have_bought == True:
                time.sleep(3)
                
        except TypeError as e:
            print('***ENCOUNTERED AN ERROR, RETRYING IN 10 SECONDS***')
            time.sleep(10)

    logout()
