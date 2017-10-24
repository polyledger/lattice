# -*- coding: utf-8 -*-

from __future__ import print_function
import math
import time
import csv
import sys
import os

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

class HistoricRatesPipeline(object):

    MAX_CANDLES = 200

    def __init__(self, product, start, end=util.current_datetime_string(), granularity=86400):
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
