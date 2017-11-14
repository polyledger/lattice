# -*- coding: utf-8 -*-

"""
This module creates optimal portfolio allocations, given a risk index.
"""

import math
import numpy as np
import pandas as pd
from scipy.optimize import minimize

from lattice import util
from lattice.data import get_historic_data, get_price


DEFAULT_COINS = [
    'BTC', 'ETH', 'BCH', 'XRP', 'LTC', 'XMR', 'ZEC', 'DASH', 'ETC', 'NEO'
]

class Allocator(object):
    
    def __init__(self, coins=DEFAULT_COINS, start='2017-10-01', end=util.current_date_string()):
        self.SUPPORTED_COINS = coins
        self.start = start
        self.end = end

    def retrieve_data(self):
        """
        Retrives data as a DataFrame.
        """

        #==== Retrieve data ====#

        dataframe = get_historic_data(self.start, self.end)
        dataframe.replace(0, np.nan, inplace=True)
        return dataframe

    def get_min_risk(self, weights, cov_matrix):
        """
        Minimizes the variance of a portfolio.
        """

        def func(weights):
            """The objective function that minimizes variance."""
            return np.matmul(np.matmul(weights.transpose(), cov_matrix), weights)

        def func_deriv(weights):
            """The derivative of the objective function."""
            return (
                np.matmul(weights.transpose(), cov_matrix.transpose()) +
                np.matmul(weights.transpose(), cov_matrix)
            )

        constraints = ({'type': 'eq', 'fun': lambda weights: (weights.sum() - 1)})
        solution = self.solve_minimize(func, weights, constraints, func_deriv=func_deriv)
        # NOTE: `min_risk` is unused, but may be helpful later.
        # min_risk = solution.fun
        allocation = solution.x

        return allocation

    def get_max_return(self, weights, returns):
        """
        Maximizes the returns of a portfolio.
        """

        def func(weights):
            """The objective function that maximizes returns."""
            return np.dot(weights, returns.values) * -1

        constraints = ({'type': 'eq', 'fun': lambda weights: (weights.sum() - 1)})
        solution = self.solve_minimize(func, weights, constraints)
        max_return = solution.fun * -1

        # NOTE: `max_risk` is not used anywhere, but may be helpful in the future.
        # allocation = solution.x
        # max_risk = np.matmul(
        #     np.matmul(allocation.transpose(), cov_matrix), allocation
        # )

        return max_return

    def efficient_frontier(self, returns, cov_matrix, min_return, max_return, count):
        """
        Returns a DataFrame of efficient portfolio allocations for `count` risk
        indices.
        """

        columns = [coin for coin in self.SUPPORTED_COINS]
        # columns.append('Return')
        # columns.append('Risk')
        values = pd.DataFrame(columns=columns)
        weights = [1/len(self.SUPPORTED_COINS)] * len(self.SUPPORTED_COINS)

        def func(weights):
            """The objective function that minimizes variance."""
            return np.matmul(np.matmul(weights.transpose(), cov_matrix), weights)

        def func_deriv(weights):
            """The derivative of the objective function."""
            return (
                np.matmul(weights.transpose(), cov_matrix.transpose()) +
                np.matmul(weights.transpose(), cov_matrix)
            )

        for point in np.linspace(min_return, max_return, count):
            constraints = (
                {'type': 'eq', 'fun': lambda weights: (weights.sum() - 1)},
                {'type': 'ineq', 'fun': lambda weights, i=point: (
                    np.dot(weights, returns.values) - i
                )}
            )

            solution = self.solve_minimize(func, weights, constraints, func_deriv=func_deriv)

            columns = {}
            for index, coin in enumerate(self.SUPPORTED_COINS):
                columns[coin] = math.floor(solution.x[index] * 100 * 100) / 100

            # NOTE: These lines could be helpful, but are commented out right now.
            # columns['Return'] = round(np.dot(solution.x, returns.values), 6)
            # columns['Risk'] = round(solution.fun, 6)

            values = values.append(columns, ignore_index=True)

        return values

    def solve_minimize(self, func, weights, constraints, lower_bound=0.0, upper_bound=1.0, func_deriv=False):
        """
        Returns the solution to a minimization problem.
        """

        bounds = ((lower_bound, upper_bound), ) * len(self.SUPPORTED_COINS)
        return minimize(
            fun=func, x0=weights, jac=func_deriv, bounds=bounds,
            constraints=constraints, method='SLSQP', options={'disp': False}
        )

    def allocate(self, start='2017-10-01', end=util.current_date_string()):
        """
        Returns an efficient portfolio allocation for the given risk index.
        """

        dataframe = self.retrieve_data()

        #==== Calculate the daily changes ====#
        change_columns = []
        for column in dataframe:
            if column in self.SUPPORTED_COINS:
                if column == 'time':
                    continue
                change_column = '{}_change'.format(column)
                dataframe[change_column] = (
                    (dataframe[column].shift(-1) - dataframe[column]) /
                    -dataframe[column].shift(-1)
                )
                change_columns.append(change_column)

        # print(dataframe.head())
        # print(dataframe.tail())

        #==== Variances and returns ====#
        columns = change_columns
        # NOTE: `risks` is not used, but may be used in the future
        risks = dataframe[columns].apply(np.nanvar, axis=0)
        # print('\nVariance:\n{}\n'.format(risks))
        returns = dataframe[columns].apply(np.nanmean, axis=0)
        # print('\nExpected returns:\n{}\n'.format(returns))

        #==== Calculate risk and expected return ====#
        cov_matrix = dataframe[columns].cov()
        weights = np.array([1/len(self.SUPPORTED_COINS)] * len(self.SUPPORTED_COINS)).reshape(len(self.SUPPORTED_COINS), 1)

        #==== Calculate portfolio with the minimum risk ====#
        min_risk = self.get_min_risk(weights, cov_matrix)
        min_return = np.dot(min_risk, returns.values)

        #==== Calculate portfolio with the maximum return ====#
        max_return = self.get_max_return(weights, returns)

        #==== Calculate efficient frontier ====#
        frontier = self.efficient_frontier(
            returns, cov_matrix, min_return, max_return, 6
        )
        return frontier
