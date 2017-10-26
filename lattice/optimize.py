# -*- coding: utf-8 -*-

"""
This module creates optimal portfolio allocations, given a risk index.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from lattice.data import HistoricRatesPipeline


SUPPORTED_COINS = ['BTC', 'ETH', 'LTC']

def retrieve_data(start='2017-01-01', end='2017-09-30'):
    """
    Retrives data for SUPPORTED_COINS as a DataFrame for the given dates.
    """

    #==== Retrieve data ====#
    coins = dict.fromkeys(SUPPORTED_COINS)

    for coin in SUPPORTED_COINS:
        pipeline = HistoricRatesPipeline(
            '{}-USD'.format(coin), start, end, 86400
        )
        coins[coin] = pd.DataFrame(pipeline.to_list())
        coins[coin].columns = ['time', 'low', 'high', 'open', 'close', 'volume']

    # print(coins['BTC'].head())
    # print(coins['ETH'].head())
    # print(coins['LTC'].head())

    #==== Prune the dataframe ====#
    columns = [coins['BTC']['time']]

    for key in coins:
        columns.append(coins[key]['close'])

    dataframe = pd.concat(columns, axis=1)
    dataframe.replace(0, np.nan, inplace=True)
    columns = ['{}_close'.format(key) for key in coins]
    columns.insert(0, 'time')
    dataframe.columns = columns

    return dataframe

def get_min_variance_allocation(weights, cov_matrix):
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
    solution = solve_minimize(func, weights, constraints, func_deriv)
    # NOTE: `min_risk` is unused, but may be helpful later.
    # min_risk = solution.fun
    allocation = solution.x

    return allocation

def get_max_return(weights, returns):
    """
    Maximizes the returns of a portfolio.
    """

    def func(weights):
        """The objective function that maximizes returns."""
        return np.dot(weights, returns.values) * -1

    constraints = ({'type': 'eq', 'fun': lambda weights: (weights.sum() - 1)})
    solution = solve_minimize(func, weights, constraints)
    max_return = solution.fun * -1

    # NOTE: `max_risk` is not used anywhere, but may be helpful in the future.
    # allocation = solution.x
    # max_risk = np.matmul(
    #     np.matmul(allocation.transpose(), cov_matrix), allocation
    # )

    return max_return

def efficient_frontier(returns, cov_matrix, min_return, max_return, count):
    """
    Returns a DataFrame of efficient portfolio allocations for `count` risk
    indices.
    """

    columns = [coin for coin in SUPPORTED_COINS]
    # columns.append('Return')
    # columns.append('Risk')
    values = pd.DataFrame(columns=columns)
    weights = [0.25, 0.25, 0.5]

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

        solution = solve_minimize(func, weights, constraints, func_deriv)

        columns = {}
        for index, coin in enumerate(SUPPORTED_COINS):
            columns[coin] = round(solution.x[index], 3)

        # NOTE: These lines could be helpful, but are commented out right now.
        # columns['Return'] = round(np.dot(solution.x, returns.values), 6)
        # columns['Risk'] = round(solution.fun, 6)

        values = values.append(columns, ignore_index=True)

    return values

def solve_minimize(func, weights, constraints, func_deriv=False):
    """
    Returns the solution to a minimization problem.
    """

    bounds = ((0.0, 1.0), (0.0, 1.0), (0.0, 1.0))
    return minimize(
        fun=func, x0=weights, jac=func_deriv, bounds=bounds,
        constraints=constraints, method='SLSQP', options={'disp': False}
    )

def allocate(risk_index, dataframe=None):
    """
    Returns an efficient portfolio allocation for the given risk index.
    """

    if not dataframe:
        dataframe = retrieve_data()

    #==== Calculate the daily changes ====#
    change_columns = []
    for index, column in enumerate(dataframe):
        if column == 'time':
            continue
        change_column = '{}_change'.format(SUPPORTED_COINS[index - 1])
        dataframe[change_column] = (
            (dataframe[column].shift(-1) - dataframe[column]) /
            -dataframe[column].shift(-1)
        )
        change_columns.append(change_column)
    dataframe.time = pd.to_datetime(dataframe['time'], unit='s')
    dataframe.set_index(['time'], inplace=True)

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
    weights = np.array([.2, .3, .5]).reshape(3, 1)

    #==== Calculate portfolio with the minimum risk ====#
    min_variance_allocation = get_min_variance_allocation(weights, cov_matrix)
    min_return = round(np.dot(min_variance_allocation, returns.values), 9)

    #==== Calculate portfolio with the maximum return ====#
    max_return = get_max_return(weights, returns)

    #==== Calculate efficient frontier ====#
    frontier = efficient_frontier(
        returns, cov_matrix, min_return, max_return, 10
    )
    return frontier.loc[risk_index - 1]
