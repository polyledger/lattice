# -*- coding: utf-8 -*-

"""
This module creates optimal portfolio allocations, given a risk index.
"""

import math
import numpy as np
import pandas as pd
from datetime import datetime
from scipy.optimize import minimize

from lattice import util
from lattice.data import Manager


DEFAULT_COINS = [
    'BTC', 'ETH', 'BCH', 'XRP', 'LTC', 'XMR', 'ZEC', 'DASH', 'ETC', 'NEO'
]

class Allocator(object):

    def __init__(
        self,
        coins=DEFAULT_COINS,
        start=datetime(2017, 10, 1),
        end=datetime.today(),
        manager=Manager()
    ):
        self.SUPPORTED_COINS = coins
        self.start = start
        self.end = end
        self.manager = manager

    def retrieve_data(self):
        """
        Retrives data as a DataFrame.
        """

        #==== Retrieve data ====#

        df = self.manager.get_historic_data(self.start.date(), self.end.date())
        df.replace(0, np.nan, inplace=True)
        return df

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

    def efficient_frontier(
        self,
        returns,
        cov_matrix,
        min_return,
        max_return,
        count
    ):
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
            # columns['Return'] = round(np.dot(solution.x, returns), 6)
            # columns['Risk'] = round(solution.fun, 6)

            values = values.append(columns, ignore_index=True)

        return values

    def solve_minimize(
        self,
        func,
        weights,
        constraints,
        lower_bound=0.0,
        upper_bound=1.0,
        func_deriv=False
    ):
        """
        Returns the solution to a minimization problem.
        """

        bounds = ((lower_bound, upper_bound), ) * len(self.SUPPORTED_COINS)
        return minimize(
            fun=func, x0=weights, jac=func_deriv, bounds=bounds,
            constraints=constraints, method='SLSQP', options={'disp': False}
        )

    def allocate(self):
        """
        Returns an efficient portfolio allocation for the given risk index.
        """
        df = self.manager.get_historic_data()[self.SUPPORTED_COINS]

        #==== Calculate the daily changes ====#
        change_columns = []
        for column in df:
            if column in self.SUPPORTED_COINS:
                change_column = '{}_change'.format(column)
                values = pd.Series(
                    (df[column].shift(-1) - df[column]) /
                    -df[column].shift(-1)
                ).values
                df[change_column] = values
                change_columns.append(change_column)

        # print(df.head())
        # print(df.tail())

        #==== Variances and returns ====#
        columns = change_columns
        # NOTE: `risks` is not used, but may be used in the future
        risks = df[columns].apply(np.nanvar, axis=0)
        # print('\nVariance:\n{}\n'.format(risks))
        returns = df[columns].apply(np.nanmean, axis=0)
        # print('\nExpected returns:\n{}\n'.format(returns))

        #==== Calculate risk and expected return ====#
        cov_matrix = df[columns].cov()
        # NOTE: The diagonal variances weren't calculated correctly, so here is a fix.
        cov_matrix.values[[np.arange(len(self.SUPPORTED_COINS))] * 2] = df[columns].apply(np.nanvar, axis=0)
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
