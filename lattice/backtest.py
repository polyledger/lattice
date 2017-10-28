# -*- coding: utf-8 -*-

"""
This module allows backtesting of mock portfolios. Refer to the README for
usage.
"""

from __future__ import print_function

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

from lattice import util
from lattice.data import HistoricRatesPipeline

class Portfolio(object):
    """
    An object that contains the state of a mock portfolio at any given time.
    """

    def __init__(self, assets=None, created_at=util.current_datetime_string()):
        self.created_at = created_at
        self.history = []
        if assets:
            self.assets = {}
            for asset, amount in assets.items():
                self.add_asset(asset, amount, created_at)
        else:
            self.assets = {'USD': 0}

    def add_asset(self, asset='USD', amount=0,
                  datetime=util.current_datetime_string()):
        """
        Adds the given amount of an asset to this portfolio.

        :param asset: the asset to add to the portfolio
        :param amount: the amount of the asset to add
        :param datetime: datetime string indicating the time the asset was added
        """
        if amount < 0:
            raise ValueError('Asset amount must be greater than zero. '
                             'Given amount: {}'.format(amount))
        if asset not in self.assets:
            self.assets[asset] = amount
        else:
            self.assets[asset] += amount
        self.history.append({
            'datetime': datetime,
            'asset': asset,
            'amount': +amount
        })

    @staticmethod
    def __get_price(asset, unit='USD', datetime=util.current_datetime_string()):
        """
        Gets the price of a given asset at a given time.

        :param asset: the asset to check the price of
        :param unit: the unit of the price data
        :param datetime: the datetime to check the price at
        :returns: the price of the asset
        """
        supported_units = ['USD', 'BTC', 'ETH', 'LTC']

        if unit not in supported_units:
            expected = ', '.join(supported_units)
            raise ValueError('Received an unsupported unit \'{0}\'. '
                             'Must be one of {1}'.format(unit, expected))

        if unit == 'USD':
            product = '{0}-{1}'.format(asset, unit)
        else:
            product = '{1}-{0}'.format(asset, unit)
        # To ensure a single price is returned, we set set a one hour timeframe
        # and a granularity of 3600
        start = datetime
        end = str(util.timestamp_to_datetime(
            util.datetime_string_to_timestamp(datetime) + 3600
        ))
        granularity = 3600
        pipeline = HistoricRatesPipeline(product, start, end, granularity)
        data = pipeline.to_list(silent=True)

        if not data:
            # Retry with a wider window. This may result in slightly inaccurate
            # data, but it's the best we can do right now.
            end = str(util.timestamp_to_datetime(
                util.datetime_string_to_timestamp(end) + 3600
            ))
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
                price = self.__get_price(asset, unit='USD', datetime=datetime)
                value = price * amount
            else:
                if asset not in backdated_assets:
                    raise ValueError('This portfolio does not contain {0}'
                                     .format(asset))
                return backdated_assets['USD']
        else:
            for backdated_asset in backdated_assets:
                amount = backdated_assets[backdated_asset]
                if backdated_asset != 'USD':
                    price = self.__get_price(
                        backdated_asset, unit='USD', datetime=datetime
                    )
                    value += price * amount
                else:
                    value += amount
        return value

    def get_historical_value(
            self,
            start_datetime,
            end_datetime=util.current_datetime_string(),
            freq='D',
            date_format='%m-%d-%Y',
            chart=False,
            filename='chart.png',
            silent=False
        ):
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
            print(util.Color.BLUE + 'INFO - ' + util.Color.END +
                  'Getting pricing data...')

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
            axes = time_series.plot(rot=90)
            axes.set_xlabel('Date')
            axes.set_ylabel('Value ($)')
            plt.savefig(filename)
        else:
            dates = time_series.index.strftime(date_format).tolist()
            return {'dates': dates, 'values': values}

    def remove_asset(
            self,
            asset='USD',
            amount=0,
            datetime=util.current_datetime_string()
        ):
        """
        Removes the given amount of an asset to this portfolio.

        :param asset: the asset to add to the portfolio
        :param amount: the amount of the asset to add
        :param datetime: datetime string indicating the time the asset was added
        """
        if amount < 0:
            raise ValueError('Asset amount must be greater than zero. '
                             'Given amount: {}'.format(amount))
        if self.get_value(datetime, asset) < amount:
            raise ValueError('Removal of {0} requested but only {1} exists in '
                             'portfolio.'.format(amount, self.assets[asset]))
        self.assets[asset] -= amount
        self.history.append({
            'datetime': datetime,
            'asset': asset,
            'amount': -amount
        })

    def trade_asset(
            self,
            amount,
            from_asset,
            to_asset,
            datetime=util.current_datetime_string()
        ):
        """
        Exchanges one asset for another. If it's a backdated trade, the
        historical exchange rate is used.

        :param amount: the amount of the asset to trade
        :param from_asset: the asset you are selling
        :param to_asset: the asset you are buying
        :param datetime: datetime string indicating the time the asset was
                         traded
        """
        price = self.__get_price(from_asset, unit=to_asset, datetime=datetime)
        self.remove_asset(from_asset, amount, datetime)
        self.add_asset(to_asset, amount * price, datetime)
