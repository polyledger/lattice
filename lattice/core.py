# -*- coding: utf-8 -*-

from __future__ import print_function
from lattice import util
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

    def get_request_count(self):
        """Check how many API calls need to be made."""
        # Convert start and end to timestamp integer
        start = util.datetime_string_to_timestamp(self._start)
        end = util.datetime_string_to_timestamp(self._end)

        # Calculate the total number of candles to be fetched
        candles = (end - start) / self._granularity

        # MAX_CANDLES is the maximum candles allowed per request
        request_count = int(math.ceil(float(candles) / float(self.MAX_CANDLES)))

        print(_Color.BLUE + 'INFO - ' + _Color.END + 'API requests required: {0}'.format(request_count))

        return request_count

    def partition_request(self):
        """Returns a list of (start, end) datetime tuples.

        Requests have to be partitioned into smaller chunks that result in less
        than MAX_CANDLES response length. Longer date ranges and smaller
        granularities will increase the number of partitions.
        """
        request_count = self.get_request_count()

        # Convert start and end to timestamp integer
        start_timestamp = util.datetime_string_to_timestamp(self._start)
        end_timestamp = util.datetime_string_to_timestamp(self._end)

        # Find the time interval s.t. t <= 200 * granularity
        interval = self.MAX_CANDLES * self._granularity

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

    def to_file(self, filename = 'output', path = os.getcwd()):
        """Output historical rates to file."""
        print(_Color.BLUE + 'Requesting data from ' + _Color.CYAN + _Color.UNDERLINE + 'https://api.gdax.com' + _Color.END + _Color.BLUE + '...' + _Color.END)

        filepath = os.path.join(path, '{0}.csv'.format(filename))
        partitions = self.partition_request()
        params = {
            'product': self._product,
            'start': self._start,
            'end': self._end,
            'granularity': self._granularity
        }

        f = open(filepath, 'w')
        f.close()

        for index, partition in enumerate(partitions):
            print(_Color.BLUE + 'INFO - ' + _Color.END + 'Receiving data partition {0}/{1}'.format(index, len(partitions)) + '\r', end='\r')
            sys.stdout.flush()

            params['start'], params['end'] = partition

            batch = _GdaxPublicClient().get_product_historic_rates(params)

            with open(filepath, 'a') as csvfile:
                writer = csv.writer(csvfile, delimiter = ',')
                writer.writerows(batch)

        print(_Color.BLUE + 'INFO - ' + _Color.END + 'Receiving data partition {0}/{0}'.format(len(partitions)))
        print(_Color.GREEN + 'SUCCESS - ' + _Color.END + 'Write to {0}.csv complete.'.format(filename))

    def to_list(self):
        """Returns historical rates as a list."""
        print(_Color.YELLOW + 'WARNING - ' + _Color.END + 'This holds all data in memory. I sure hope you know what you are doing.')
        print(_Color.BLUE + 'Requesting data from ' + _Color.CYAN + _Color.UNDERLINE + 'https://api.gdax.com' + _Color.END + _Color.BLUE + '...' + _Color.END)

        result = []
        partitions = self.partition_request()
        params = {
            'product': self._product,
            'start': self._start,
            'end': self._end,
            'granularity': self._granularity
        }

        for index, partition in enumerate(partitions):
            print(_Color.BLUE + 'INFO - ' + _Color.END + 'Receiving data partition {0}/{1}'.format(index, len(partitions)) + '\r', end='\r')
            sys.stdout.flush()

            params['start'], params['end'] = partition

            batch = _GdaxPublicClient().get_product_historic_rates(params)

            result.extend(batch)

        print(_Color.BLUE + 'INFO - ' + _Color.END + 'Receiving data partition {0}/{0}'.format(len(partitions)))
        print(_Color.GREEN + 'SUCCESS - ' + _Color.END + 'In-memory list created.')

        return result
