# -*- coding: utf-8 -*-

from __future__ import print_function
from lattice import util
import matplotlib
import requests
import math
import time
import csv
import sys
import os

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

    def __init__(self, url = 'https://api.gdax.com'):
        self._url = url

    def get_product_historic_rates(self, params):
        """Get historic rates for product_id from GDAX."""
        product = params['product']
        params = dict(params)  # Make a local copy of params
        del params['product']

        r = requests.get("{0._url}/products/{1}/candles".format(self, product), params=params, timeout=30)

        if not r.json():
            # TODO: Research why GDAX is inconsistent here. In the meantime, try the request again.
            r = requests.get("{0._url}/products/{1}/candles".format(self, product), params=params, timeout=30)
            # raise Exception('GDAX did not return any data.')

        while (r.status_code == 429):
            # Rate limit exceeded. Wait a second and try again.
            time.sleep(1)
            r = requests.get("{0._url}/products/{1}/candles".format(self, product), params=params, timeout=30)

        return r.json()

class Pipeline(object):

    def __init__(self):
        pass

class HistoricRatesPipeline(Pipeline):

    MAX_CANDLES = 200

    def __init__(self, product, start, end, granularity):
        Pipeline.__init__(self)
        self._product = product
        self._start = start
        self._end = end
        self._granularity = granularity

    def get_request_count(self, silent = False):
        """Check how many API calls need to be made."""
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

    def partition_request(self, silent = False):
        """Returns a list of (start, end) datetime tuples.

        Requests have to be partitioned into smaller chunks that result in less
        than MAX_CANDLES response length. Longer date ranges and smaller
        granularities will increase the number of partitions.
        """
        request_count = self.get_request_count(silent = silent)

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

    def to_file(self, filename = 'output', path = os.getcwd(), silent = False):
        """Output historical rates to file."""
        if not silent:
            print(_Color.BLUE + 'Requesting data from ' + _Color.CYAN + _Color.UNDERLINE + 'https://api.gdax.com' + _Color.END + _Color.BLUE + '...' + _Color.END)

        filepath = os.path.join(path, '{0}.csv'.format(filename))
        partitions = self.partition_request(silent = silent)
        params = {
            'product': self._product,
            'start': self._start,
            'end': self._end,
            'granularity': self._granularity
        }

        f = open(filepath, 'w')
        f.close()

        for index, partition in enumerate(partitions):
            if not silent:
                print(_Color.BLUE + 'INFO - ' + _Color.END + 'Receiving data partition {0}/{1}'.format(index, len(partitions)) + '\r', end='\r')
                sys.stdout.flush()

            params['start'], params['end'] = partition

            batch = _GdaxPublicClient().get_product_historic_rates(params)

            with open(filepath, 'a') as csvfile:
                writer = csv.writer(csvfile, delimiter = ',')
                writer.writerows(batch)

        if not silent:
            print(_Color.BLUE + 'INFO - ' + _Color.END + 'Receiving data partition {0}/{0}'.format(len(partitions)))
            print(_Color.GREEN + 'SUCCESS - ' + _Color.END + 'Write to {0}.csv complete.'.format(filename))

    def to_list(self, silent = False):
        """Returns historical rates as a list."""
        if not silent:
            print(_Color.YELLOW + 'WARNING - ' + _Color.END + 'This holds all data in memory. I sure hope you know what you are doing.')
            print(_Color.BLUE + 'Requesting data from ' + _Color.CYAN + _Color.UNDERLINE + 'https://api.gdax.com' + _Color.END + _Color.BLUE + '...' + _Color.END)

        result = []
        partitions = self.partition_request(silent = silent)
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

    def __init__(self, assets = {}):
        self.assets = assets
        self.created_at = util.current_datetime_string()
        self.history = []

    def add_asset(self, asset = 'USD', amount = 0, datetime = util.current_datetime_string()):
        """Adds the given amount of an asset to this portfolio."""
        if amount < 0:
            raise ValueError('Asset amount must be greater than zero. Given amount: {}'.format(amount))
        if asset not in self.assets:
            self.assets[asset] = amount
        else:
            self.assets[asset] += amount
        self.history.append({ 'datetime': datetime, 'asset': asset, 'amount': +amount})

    def __get_price(self, asset, datetime):
        """Gets the price of a given asset at a given time."""
        product = '{0}-USD'.format(asset)
        # To ensure a single price is returned, we set set a one minute timeframe
        # and a granularity of 60
        start = datetime
        end = str(util.timestamp_to_datetime(util.datetime_string_to_timestamp(datetime) + 3600))
        granularity = 60
        pipeline = HistoricRatesPipeline(product, start, end, granularity)
        return pipeline.to_list(silent = True)[0][4]

    def get_value(self, datetime = util.current_datetime_string()):
        """Get the value of the portfolio at a given time."""
        value = 0

        # Backdate the portfolio by changing its values temporarily
        backdated_assets = self.assets.copy()
        for trade in self.history:
            if trade['datetime'] > datetime:
                backdated_assets[trade['asset']] -= trade['amount']

                if backdated_assets[trade['asset']] == 0:
                    del backdated_assets[trade['asset']]

        for asset in backdated_assets:
            amount = backdated_assets[asset]
            if asset is not 'USD':
                value += self.__get_price(asset, datetime) * amount
            else:
                value += amount
        return value

    def historical_value_chart(self, start_datetime, end_datetime):
        """Display a chart of this portfolios value during the specified timeframe."""
        # TODO: Use matplotlib for this.
        pass

    def remove_asset(self, asset = 'USD', amount=0, datetime = util.current_datetime_string()):
        """Removes the given amount of an asset to this portfolio."""
        if amount < 0:
            raise ValueError('Asset amount must be greater than zero. Given amount: {}'.format(amount))
        if self.assets[asset] < amount:
            raise ValueError('Removal of {0} requested but only {1} exists in portfolio.'.format(amount, self.assets[asset]))
        self.assets[asset] -= amount
        self.history.append({ 'datetime': datetime, 'asset': asset, 'amount': -amount})

    def trade_asset(self):
        """Exchanges one asset for another. If it's a backdated trade, the historical exchange rate is used."""
        pass
