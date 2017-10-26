# -*- coding: utf-8 -*-

"""
This module is an interface for accessing cryptocurrency market data.
"""

from __future__ import print_function
import math
import time
import csv
import sys
import os

import requests

from lattice import util


def get_product_historic_rates(params):
    """
    Get historic rates for product_id from GDAX.
    :param params: url parameters for api call
    :return:
    """
    product = params['product']
    params = dict(params)  # Make a local copy of params
    del params['product']

    res = requests.get(
        'https://api.gdax.com/products/{0}/candles'.format(product),
        params=params,
        timeout=30
    )

    if not res.json():
        # Research why GDAX is inconsistent here. In the meantime, try the
        # request again. One possibility is that the user entered a bad date
        # range, in which case can raise:
        # raise Exception('GDAX did not return any data.')
        res = requests.get(
            'https://api.gdax.com/products/{0}/candles'.format(product),
            params=params,
            timeout=30
        )

    while res.status_code == 429:
        # Rate limit exceeded. Wait a second and try again.
        time.sleep(1)
        res = requests.get(
            'https://api.gdax.com/products/{0}/candles'.format(product),
            params=params,
            timeout=30
        )

    return res.json()

class HistoricRatesPipeline(object):
    """
    Creates an object that can fetch market exchange data.
    """

    MAX_CANDLES = 200

    def __init__(
            self,
            product,
            start,
            end=util.current_datetime_string(),
            granularity=86400
        ):
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
            print(util.Color.BLUE + 'INFO - ' + util.Color.END +
                  'API requests required: {0}'.format(request_count))

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
            print(util.Color.BLUE + 'INFO - ' + util.Color.END + 'Time '
                  'interval per request: {0} seconds'.format(interval))

        partitions = []

        for _ in range(request_count):
            if (start_timestamp + interval) < end_timestamp:
                end_datetime = util.timestamp_to_datetime(
                    start_timestamp + interval
                )
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
            print(util.Color.BLUE + 'Requesting data from ' + util.Color.CYAN +
                  util.Color.UNDERLINE + 'https://api.gdax.com' +
                  util.Color.END + util.Color.BLUE + '...' + util.Color.END)

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
                print(util.Color.BLUE + 'INFO - ' + util.Color.END +
                      'Receiving data partition {0}/{1}'
                      .format(index, len(partitions)) + '\r', end='\r')
                sys.stdout.flush()

            params['start'], params['end'] = partition

            batch = get_product_historic_rates(params)

            with open(filepath, 'a') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerows(batch)

        if not silent:
            print(util.Color.BLUE + 'INFO - ' + util.Color.END + 'Receiving '
                  'data partition {0}/{0}'.format(len(partitions)))
            print(util.Color.GREEN + 'SUCCESS - ' + util.Color.END + 'Write to '
                  '{0}.csv complete.'.format(filename))

    def to_list(self, silent=False):
        """
        Returns historical rates as a list.

        :param silent: boolean indicating to silence info messages
        :returns: a multi-dimentsional list of historical pricing data
        """
        if not silent:
            print(util.Color.YELLOW + 'WARNING - ' + util.Color.END + 'This '
                  'holds all data in memory. I sure hope you know what you are '
                  'doing.')
            print(util.Color.BLUE + 'Requesting data from ' + util.Color.CYAN +
                  util.Color.UNDERLINE + 'https://api.gdax.com' +
                  util.Color.END + util.Color.BLUE + '...' + util.Color.END)

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
                print(util.Color.BLUE + 'INFO - ' + util.Color.END +
                      'Receiving data partition {0}/{1}'
                      .format(index, len(partitions)) + '\r', end='\r')
                sys.stdout.flush()

            params['start'], params['end'] = partition

            batch = get_product_historic_rates(params)

            result.extend(batch)

        if not silent:
            print(util.Color.BLUE + 'INFO - ' + util.Color.END + 'Receiving '
                  'data partition {0}/{0}'.format(len(partitions)))
            print(util.Color.GREEN + 'SUCCESS - ' + util.Color.END +
                  'In-memory list created.')

        return result
