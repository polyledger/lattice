# -*- coding: utf-8 -*-

"""
This module is an interface for accessing cryptocurrency market data.
"""

import os
import math
import requests
import pandas as pd
import numpy as np
from pandas.io.common import EmptyDataError

from lattice import util


coins = ['BTC', 'ETH', 'BCH', 'XRP', 'LTC', 'XMR', 'ZEC', 'DASH', 'ETC', 'NEO']

filepath = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'datasets/day_historical.csv'
)

def request_from_cryptocompare():
    dataframe = pd.DataFrame()
    url = 'https://min-api.cryptocompare.com/data/histoday'

    for coin in coins:
        print('Getting {} prices...'.format(coin))
        params = {
            'fsym': coin,
            'tsym': 'USD',
            'allData': 'true'
        }
        result = requests.get(url=url, params=params)
        data = result.json()['Data']
        df = pd.DataFrame.from_records(data, columns=['time', 'close'])
        df.set_index('time', inplace=True, drop=True)
        df.index = pd.to_datetime(df.index, unit='s')
        df.columns = [coin]
        dataframe = pd.concat([dataframe, df], axis=1)
    dataframe = dataframe.iloc[::-1]
    try:
        df2 = pd.read_csv(filepath, index_col=0)
        dataframe = dataframe.join(df2)
        dataframe.to_csv(filepath)
    except:
        dataframe.to_csv(filepath)


def get_historic_data(start='2010-01-01', end=util.current_date_string()):
    try:
        df = pd.read_csv(filepath, index_col=0).loc[end:start,:]
        if df.index[0] < end:
            request_from_cryptocompare()
    except Exception as e:
        request_from_cryptocompare()
    return pd.read_csv(filepath, index_col=0).loc[end:start,:]

def get_price(coin, date):
    df = get_historic_data()
    price = df.loc[date, coin]
    return price
