# -*- coding: utf-8 -*-

from __future__ import print_function
import math
import time
import csv
import sys
import os

import matplotlib.pyplot as plt
import pandas as pd
import requests

from lattice import util

class _Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class _GdaxPublicClient(object):

    def __init__(self, url='https://api.gdax.com'):
        self._url = url

    def get_product_historic_rates(self, params):
        """
        Get historic rates for product_id from GDAX.
        :param params: url parameters for api call
        :return:
        """
        product = params['product']
        params = dict(params)  # Make a local copy of params
        del params['product']

        res = requests.get("{0._url}/products/{1}/candles".format(self, product),
                           params=params, timeout=30)

        if not res.json():
            # Research why GDAX is inconsistent here. In the meantime, try the request again.
            # One possibility is that the user entered a bad date range, in which case can raise:
            # raise Exception('GDAX did not return any data.')
            res = requests.get("{0._url}/products/{1}/candles".format(self, product),
                               params=params, timeout=30)

        while res.status_code == 429:
            # Rate limit exceeded. Wait a second and try again.
            time.sleep(1)
            res = requests.get("{0._url}/products/{1}/candles".format(self, product),
                               params=params, timeout=30)

        return res.json()

class Pipeline(object):

    def __init__(self):
        pass

class HistoricRatesPipeline(Pipeline):

    MAX_CANDLES = 200

    def __init__(self, product, start, end=util.current_datetime_string(), granularity=86400):
        Pipeline.__init__(self)
        self._product = product
        self._start = start
        self._end = end
        self._granularity = granularity

    def get_request_count(self, silent=False):
        """
        Check how many API calls need to be made.
        :param silent: boolean indicating to silence info messages
        :returns: the number of requests to be made
        """
        # Convert start and end to timestamp integer
        start = util.datetime_string_to_timestamp(self._start)
        end = util.datetime_string_to_timestamp(self._end)

        # Calculate the total number of candles to be fetched
        candles = (end - start) / self._granularity

        # MAX_CANDLES is the maximum candles allowed per request
        request_count = int(math.ceil(float(candles) / float(self.MAX_CANDLES)))

        if not silent:
            print(_Color.BLUE + 'INFO - ' + _Color.END + 'API requests required: {0}'.format(request_count))

        return request_count

    def partition_request(self, silent=False):
        """
        Returns a list of (start, end) datetime tuples. Requests have to be
        partitioned into smaller chunks that result in less than MAX_CANDLES
        response length. Longer date ranges and smaller granularities will
        increase the number of partitions.

        :param silent: boolean indicating to silence info messages
        :returns: a list of start/end datetime tuples
        """
        request_count = self.get_request_count(silent=silent)

        # Convert start and end to timestamp integer
        start_timestamp = util.datetime_string_to_timestamp(self._start)
        end_timestamp = util.datetime_string_to_timestamp(self._end)

        # Find the time interval s.t. t <= 200 * granularity
        interval = self.MAX_CANDLES * self._granularity

        if not silent:
            print(_Color.BLUE + 'INFO - ' + _Color.END + 'Time interval per request: {0} seconds'.format(interval))

        partitions = []

        for i in range(request_count):
            if (start_timestamp + interval) < end_timestamp:
                end_datetime = util.timestamp_to_datetime(start_timestamp + interval)
            else:
                end_datetime = util.date_string_to_datetime(self._end)
            start_datetime = util.timestamp_to_datetime(start_timestamp)
            partitions.insert(0, (start_datetime, end_datetime))
            start_timestamp += interval

        return partitions

    def to_file(self, filename='output', path=os.getcwd(), silent=False):
        """
        Output historical rates to file.

        :param filename: the name for the created file
        :param path: an absolute path to where the file will be created
        :param silent: boolean indicating to silence info messages
        """
        if not silent:
            print(_Color.BLUE + 'Requesting data from ' + _Color.CYAN + _Color.UNDERLINE + 'https://api.gdax.com' + _Color.END + _Color.BLUE + '...' + _Color.END)

        filepath = os.path.join(path, '{0}.csv'.format(filename))
        partitions = self.partition_request(silent=silent)
        params = {
            'product': self._product,
            'start': self._start,
            'end': self._end,
            'granularity': self._granularity
        }

        newfile = open(filepath, 'w')
        newfile.close()

        for index, partition in enumerate(partitions):
            if not silent:
                print(_Color.BLUE + 'INFO - ' + _Color.END + 'Receiving data partition {0}/{1}'.format(index, len(partitions)) + '\r', end='\r')
                sys.stdout.flush()

            params['start'], params['end'] = partition

            batch = _GdaxPublicClient().get_product_historic_rates(params)

            with open(filepath, 'a') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerows(batch)

        if not silent:
            print(_Color.BLUE + 'INFO - ' + _Color.END + 'Receiving data partition {0}/{0}'.format(len(partitions)))
            print(_Color.GREEN + 'SUCCESS - ' + _Color.END + 'Write to {0}.csv complete.'.format(filename))

    def to_list(self, silent=False):
        """
        Returns historical rates as a list.

        :param silent: boolean indicating to silence info messages
        :returns: a multi-dimentsional list of historical pricing data
        """
        if not silent:
            print(_Color.YELLOW + 'WARNING - ' + _Color.END + 'This holds all data in memory. I sure hope you know what you are doing.')
            print(_Color.BLUE + 'Requesting data from ' + _Color.CYAN + _Color.UNDERLINE + 'https://api.gdax.com' + _Color.END + _Color.BLUE + '...' + _Color.END)

        result = []
        partitions = self.partition_request(silent=silent)
        params = {
            'product': self._product,
            'start': self._start,
            'end': self._end,
            'granularity': self._granularity
        }

        for index, partition in enumerate(partitions):
            if not silent:
                print(_Color.BLUE + 'INFO - ' + _Color.END + 'Receiving data partition {0}/{1}'.format(index, len(partitions)) + '\r', end='\r')
                sys.stdout.flush()

            params['start'], params['end'] = partition

            batch = _GdaxPublicClient().get_product_historic_rates(params)

            result.extend(batch)

        if not silent:
            print(_Color.BLUE + 'INFO - ' + _Color.END + 'Receiving data partition {0}/{0}'.format(len(partitions)))
            print(_Color.GREEN + 'SUCCESS - ' + _Color.END + 'In-memory list created.')

        return result


class Portfolio(object):

    def __init__(self, assets={}, created_at=util.current_datetime_string()):
        self.assets = {}
        self.created_at = created_at
        self.history = []
        for asset, amount in assets.items():
            self.add_asset(asset, amount, created_at)

    def add_asset(self, asset='USD', amount=0, datetime=util.current_datetime_string()):
        """
        Adds the given amount of an asset to this portfolio.

        :param asset: the asset to add to the portfolio
        :param amount: the amount of the asset to add
        :param datetime: a datetime string indicating the time the asset was added
        """
        if amount < 0:
            raise ValueError('Asset amount must be greater than zero. Given amount: {}'.format(amount))
        if asset not in self.assets:
            self.assets[asset] = amount
        else:
            self.assets[asset] += amount
        self.history.append({'datetime': datetime, 'asset': asset, 'amount': +amount})

    def __get_price(self, asset, unit='USD', datetime=util.current_datetime_string()):
        """
        Gets the price of a given asset at a given time.

        :param asset: the asset to check the price of
        :param unit: the unit of the price data
        :param datetime: the datetime to check the price at
        :returns: the price of the asset
        """
        supported_units = ['USD', 'BTC', 'ETH', 'LTC']

        if unit not in supported_units:
            raise ValueError('Received an unsupported unit \'{0}\'. Must be one of {1}'.format(unit, ', '.join(supported_units)))

        product = '{0}-{1}'.format(asset, unit) if unit == 'USD' else '{1}-{0}'.format(asset, unit)
        # To ensure a single price is returned, we set set a one hour timeframe
        # and a granularity of 3600
        start = datetime
        end = str(util.timestamp_to_datetime(util.datetime_string_to_timestamp(datetime) + 3600))
        granularity = 3600
        pipeline = HistoricRatesPipeline(product, start, end, granularity)
        data = pipeline.to_list(silent=True)

        if not data:
            # Retry with a wider window. This may result in slightly inaccurate data, but it's
            # the best we can do right now.
            end = str(util.timestamp_to_datetime(util.datetime_string_to_timestamp(end) + 3600))
            pipeline = HistoricRatesPipeline(product, start, end, granularity)
            data = pipeline.to_list(silent=True)
        rate = data[0][4]
        return 1/rate if asset == 'USD' else rate

    def get_value(self, datetime=util.current_datetime_string(), asset=None):
        """
        Get the value of the portfolio at a given time.

        :param asset: gets the value of a given asset in this portfolio if
                      specified; if None, returns the portfolio's value
        :param datetime: a datetime to check the portfolio's value at
        :returns: the value of the portfolio
        """
        value = 0

        # Backdate the portfolio by changing its values temporarily
        backdated_assets = self.assets.copy()
        for trade in self.history:
            if trade['datetime'] > datetime:
                backdated_assets[trade['asset']] -= trade['amount']

                if backdated_assets[trade['asset']] == 0:
                    del backdated_assets[trade['asset']]

        if asset:
            if asset != 'USD':
                amount = backdated_assets[asset]
                value = self.__get_price(asset, unit='USD', datetime=datetime) * amount
            else:
                if asset not in backdated_assets:
                    raise ValueError('This portfolio does not contain {0}'.format(asset))
                return backdated_assets['USD']
        else:
            for asset in backdated_assets:
                amount = backdated_assets[asset]
                if asset != 'USD':
                    value += self.__get_price(asset, unit='USD', datetime=datetime) * amount
                else:
                    value += amount
        return value

    def get_historical_value(self, start_datetime, end_datetime=util.current_datetime_string(), freq='D', date_format='%m-%d-%Y', chart=False, silent=False):
        """
        Display a chart of this portfolios value during the specified timeframe.

        :param start_datetime: the left bound of the time interval
        :param end_datetime: the right bound of the time interval
        :param freq: a time frequency within the interval
        :param date_format: the format of the date/x-axis labels
        :param chart: whether to display a chart or return data
        :param silent: boolean indicating to silence info messages
        :returns: a dict of historical value data if chart is false
        """
        if not silent:
            print(_Color.BLUE + 'INFO - ' + _Color.END + 'Getting pricing data...')

        date_range = pd.date_range(start_datetime, end_datetime, freq=freq)

        # Set the maximum number of x-axis ticks to 22 since every date results
        # in an API call.
        to_remove = []

        while len(date_range) > 22:
            for index, date in enumerate(date_range):
                if index % 2 == 0 and index != 0:
                    to_remove.append(date)
            date_range = date_range.drop(to_remove)
            to_remove = []

        values = []

        for date in date_range:
            values.append(self.get_value(str(date.date())))

        time_series = pd.DataFrame(index=date_range, data={'Value': values})

        if chart:
            ax = time_series.plot(rot=90)
            ax.set_xlabel('Date')
            ax.set_ylabel('Value ($)')
            plt.show()
        else:
            return {'dates': time_series.index.strftime(date_format).tolist(), 'values': values}

    def remove_asset(self, asset='USD', amount=0, datetime=util.current_datetime_string()):
        """
        Removes the given amount of an asset to this portfolio.

        :param asset: the asset to add to the portfolio
        :param amount: the amount of the asset to add
        :param datetime: a datetime string indicating the time the asset was added
        """
        if amount < 0:
            raise ValueError('Asset amount must be greater than zero. Given amount: {}'.format(amount))
        if self.get_value(datetime, asset) < amount:
            raise ValueError('Removal of {0} requested but only {1} exists in portfolio.'.format(amount, self.assets[asset]))
        self.assets[asset] -= amount
        self.history.append({'datetime': datetime, 'asset': asset, 'amount': -amount})

    def trade_asset(self, amount, from_asset, to_asset, datetime=util.current_datetime_string()):
        """
        Exchanges one asset for another. If it's a backdated trade, the historical exchange rate is used.

        :param amount: the amount of the asset to trade
        :param from_asset: the asset you are selling
        :param to_asset: the asset you are buying
        :param datetime: a datetime string indicating the time the asset was traded
        """
        price = self.__get_price(from_asset, unit=to_asset, datetime=datetime)
        self.remove_asset(from_asset, amount, datetime)
        self.add_asset(to_asset, amount * price, datetime)

class TradingStrategy(object):

    def __init__(self):
        pass
