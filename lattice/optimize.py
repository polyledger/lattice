# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from lattice.data import HistoricRatesPipeline


supported_coins = ['BTC', 'ETH', 'LTC']

def retrieve_data():
    #==== Retrieve data ====#
    coins = dict.fromkeys(supported_coins)

    for coin in supported_coins:
        pipeline = HistoricRatesPipeline(
            '{}-USD'.format(coin), '2015-01-01', '2017-09-01', 86400
        )
        coins[coin] = pd.DataFrame(pipeline.to_list())
        coins[coin].columns = ['time', 'low', 'high', 'open', 'close', 'volume']

    #==== Prune the dataframe ====#
    columns = [coins['BTC']['time']]

    for key in coins:
        columns.append(coins[key]['close'])

    df = pd.concat(columns, axis=1)
    df.replace(0, np.nan, inplace=True)
    columns = ['{}_close'.format(key) for key in coins]
    columns.insert(0, 'time')
    df.columns = columns

    return df

def minimize_variance(weights, cov_matrix):
    def func(weights):
        return (np.matmul(np.matmul(weights.transpose(), cov_matrix), weights))

    def func_deriv(weights):
        return (
            np.matmul(weights.transpose(), cov_matrix.transpose()) +
            np.matmul(weights.transpose(), cov_matrix)
        )

    constraints = ({'type': 'eq', 'fun': lambda weights: (weights.sum() - 1)})
    b = (0.0, 1.0)
    bounds = (b, b, b)
    solution = minimize(
        fun=func, x0=weights, bounds=bounds, jac=func_deriv,
        constraints=constraints, method='SLSQP', options={'disp': False}
    )
    min_risk = solution.fun
    allocation = solution.x

    return min_risk, allocation

def maximize_returns(weights, returns):
    def func(weights):
        return (np.dot(weights, returns.values)*-1)

    constraints = ({'type': 'eq', 'fun': lambda weights: (weights.sum() - 1)})
    b = (0.0, 1.0)
    bounds = (b, b, b)
    solution = minimize(
        fun=func, x0=weights, bounds=bounds, jac=False,
        constraints=constraints, method='SLSQP', options={'disp': False}
    )
    max_return = solution.fun * -1
    allocation = solution.x

    return max_return, allocation

def efficient_frontier(returns, cov_matrix, min_return, max_return, num):
    points = np.linspace(min_return, max_return, num)
    columns = [coin for coin in supported_coins]
    columns.append('return')
    columns.append('risk')
    values = pd.DataFrame(columns=columns)
    weights = [0.25, 0.25, 0.5]

    for point in points:
        def func(weights):
            return (
                np.matmul(np.matmul(weights.transpose(), cov_matrix), weights)
            )

        constraints = (
            {'type': 'eq', 'fun': lambda weights: (weights.sum() - 1)},
            {'type': 'ineq', 'fun': lambda weights: (
                np.dot(weights, returns.values) - point
            )}
        )

        def func_deriv(weights):
            return (
                np.matmul(weights.transpose(), cov_matrix.transpose()) +
                np.matmul(weights.transpose(), cov_matrix)
            )

        b = (0.0, 1.0)
        bounds = (b, b, b)
        solution = minimize(
            fun=func, x0=weights, jac=func_deriv, bounds=bounds,
            constraints=constraints, method='SLSQP', options={'disp': False}
        )

        columns = {}
        for index, coin in enumerate(supported_coins):
            columns[coin] = round(solution.x[index], 3)
        # columns['return'] = round(np.dot(solution.x, returns.values), 6)
        # columns['risk'] = round(solution.fun, 6)

        values = values.append(columns, ignore_index=True)

    return values

def allocate(risk_index, df=None):
    if df.empty: df = retrieve_data()

    #==== Calculate the daily changes ====#
    change_columns = []
    for index, column in enumerate(df):
        if column is 'time': continue
        change_column = '{}_change'.format(supported_coins[index-1])
        df[change_column] = (
            df[column].shift(-1) - df[column]) / (-df[column].shift(-1)
        )
        change_columns.append(change_column)
    df.time = pd.to_datetime(df['time'], unit='s')
    df.set_index(['time'], inplace=True)

    #==== Variances and returns ====#
    columns = change_columns
    risks = df[columns].apply(np.nanvar, axis=0)
    returns = df[columns].apply(np.nanmean, axis=0)

    #==== Calculate risk and expected return ====#
    cov_matrix = df[columns].cov()
    weights = np.array([.2, .3, .5]).reshape(3, 1)

    #==== Calculate portfolio with the minimum risk ====#
    min_risk, min_risk_allocation = minimize_variance(weights, cov_matrix)
    min_return = round(np.dot(min_risk_allocation, returns.values), 9)

    #==== Calculate portfolio with the maximum return ====#
    max_return, max_return_allocation = maximize_returns(weights, returns)
    max_risk = np.matmul(
        np.matmul(max_return_allocation.transpose(), cov_matrix),
        max_return_allocation
    )

    #==== Calculate efficient frontier ====#
    frontier = efficient_frontier(
        returns, cov_matrix, min_return, max_return, 10
    )
    return frontier.loc[risk_index]
