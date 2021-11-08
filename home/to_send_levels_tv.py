from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpl_dates
from collections import Counter
# import matplotlib.pyplot as plt
# from datetime import datetime
# from initer import initer
# import dateutil.parser
# import mplfinance
# import yfinance
import pandas as pd
import numpy as np
import json
import time
from home.Binance import Binance

exchange = Binance('home/credentials.txt')
# exchange = Binance('credentials.txt')
# exchange2 = Binance('creds.txt')


def isSupport(df, i):
    # print("DF['low'][i]: " + str(df['low'][i]) + " DF['low'][i-1]: " + str(df['low'][i-1]) + " DF['low'][i]: " + str(df['low'][i]) + " DF['low'][i+2]: " + str(df['low'][i+2]) + " DF['low'][i-1]: " + str(df['low'][i+1]) + " DF['low'][i-2]: " + str(df['low'][i-2]))
    # print("df['low'][i]: " + str(df['low'][i]) + " < df['low'][i-1]: " + str(df['low'][i-1]) + " and df['low'][i]: " + str(df['low'][i]) + " < df['low'][i+1]" + str(df['low'][i+1]) + " and df['low'][i+1]:" + str(df['low'][i+1]) + " < df['low'][i+2]: " + str(df['low'][i+2]) + " and df['low'][i-1]:" + str(df['low'][i-1]) + " < df['low'][i-2]:" + str(df['low'][i-2]))

    support = df['low'][i] < df['low'][i - 1] < df['low'][i - 2] and df['low'][i] < df['low'][i + 1] < df['low'][
        i + 2]
    return support


def isResistance(df, i):
    # print("df['high'][i]: " + str(df['high'][i]) + " < df['high'][i-1]: " + str(df['high'][i-1]) + " and df['high'][i]: " + str(df['high'][i]) + " < df['high'][i+1]" + str(df['high'][i+1]) + " and df['high'][i+1]:" + str(df['high'][i+1]) + " < df['high'][i+2]: " + str(df['high'][i+2]) + " and df['high'][i-1]:" + str(df['high'][i-1]) + " < df['high'][i-2]:" + str(df['high'][i-2]))

    resistance = df['high'][i] > df['high'][i - 1] > df['high'][i - 2] and df['high'][i] > df['high'][i + 1] > df['high'][i + 2]
    return resistance


def isUptrend(df, i):
    # print("DF['low'][i]: " + str(df['low'][i]) + " DF['low'][i-1]: " + str(df['low'][i-1]) + " DF['low'][i]: " +
    # str(df['low'][i]) + " DF['low'][i+2]: " + str(df['low'][i+2]) + " DF['low'][i-1]: " + str(df['low'][i+1]) + "
    # DF['low'][i-2]: " + str(df['low'][i-2])) print("df['low'][i]: " + str(df['low'][i]) + " < df['low'][i-1]: " +
    # str(df['low'][i-1]) + " and df['low'][i]: " + str(df['low'][i]) + " < df['low'][i+1]" + str(df['low'][i+1]) + "
    # and df['low'][i+1]:" + str(df['low'][i+1]) + " < df['low'][i+2]: " + str(df['low'][i+2]) + " and df['low'][
    # i-1]:" + str(df['low'][i-1]) + " < df['low'][i-2]:" + str(df['low'][i-2]))
    uptrend = df['low'][i - 1] < df['low'][i] < df['low'][i + 1] < df['low'][i + 2] and df['low'][
        i - 1] > df['low'][i - 2]
    return uptrend


def isFarFromLevel(l):
    return np.sum([abs(l - x) < s for x in levels]) == 0


def write_levels(coin_levels):
    secondElem = []
    virtProfit_list = []
    coin_levels.sort(reverse=True, key=takeSecond)
    # print(coin_levels)
    return coin_levels


def takeSecond(elem):
    return elem[0]


def get_request_df(symbol, interval, limit):
    obj = exchange.GetSymbolKlines(symbol=symbol, interval=interval, limit=limit)

    return obj


def get_levels_coin(obj):
    obj['date'] = obj['date'].astype(str)
    obj = obj.to_dict(orient='records')
    with open("home/DOPE.json", "w") as jsonFile:
        c = jsonFile.write(json.dumps(obj, indent=4))
    with open('home/DOPE.json') as json_file:
        data_btc = json.load(json_file)

    dope_levels = {}
    ADW = {}
    nnn = []
    CLA = {"data": ""}

    CLA_HOLDER = {}
    df = pd.DataFrame.from_dict(data_btc)
    df = df.loc[:, ['open', 'high', 'low', 'close', 'volume', 'date']]
    # print(df)
    levels = []
    for j in range(2, df.shape[0] - 2):
        if isSupport(df, j):
            levels.append((j, df['low'][j]))
        elif isResistance(df, j):
            levels.append((j, df['high'][j]))

    s = np.mean(df['high'] - df['low'])
    levels = []
    for j in range(2, df.shape[0] - 2):
        if isSupport(df, j):
            l = df['low'][j]
            if ([abs(l - x) < s for x in levels]) == 0:
                levels.append(l)
        elif isResistance(df, j):
            l = df['high'][j]
            if np.sum([abs(l - x) < s for x in levels]) == 0:
                levels.append(l)
    levels.sort(reverse=True)
    return levels


# Get DF of TimeSeries Data of a Particular Coin
symbol = "ETCTUSD"
interval = "1d"
limit = 1000

# request_df = get_request_df(symbol, interval, limit)
# print(request_df)

# info = exchange.GetOrderInfo('XRPUSDT')
# print(info)

# levels = get_levels_coin(request_df)
# current_trend = get_current_trendline(request_df)
# levels = get_levels_coin(request_df)

#
# def GetCurrentOpenSpotOrders(self):
#     params = {
#         'timestamp': int(round(time.time() * 1000)) + request_delay
#     }
#     self.signRequest(params)
#     url = self.base + self.endpoints['openOrders']
#     try:
#         response = requests.get(url, params=params, headers=self.headers)
#         data = response.text
#     except Exception as e:
#         print(e)
#         data = {'code': '-1', 'msg': e}
#         return json.loads(data)
#
#
# # GetTradingSymbols
# print(str(GetCurrentOpenSpotOrders(exchange)))

t = int(time.time()) * 1000
# print(t)
# s = exchange.GetAllOrderInfo('BTCUSDT')
# print(s)

# a = exchange.GetOrderInfo('BTCUSDT', 6793950387)
# print(a)



#
# s = exchange2.GetAllOrderInfo('BTCUSDT')
# print(s)
#
