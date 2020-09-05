#!/usr/local/bin/python3
'''
This script processes a dataset in survival format and for each day of the observation, it
produces a csv file with the estimated afr-age curve as it would have looked with all the
data available on that day.
'''

import os
import argparse
import datetime as dt
import numpy as np
import pandas as pd

from tqdm import tqdm

# First date in dataset (corresponds to day 0).
ORIGIN = dt.date.fromisoformat('2013-04-11')
# Disk models to be processed.
GROUPS = ['S4', 'H4A', 'H4B', 'S8C', 'S8E', 'S12E', 'H12E']
# Long names of disk models.
MODEL_NAMES = {
    'S4': 'ST4000DM000',
    'H4A': 'HGST HMS5C4040ALE640',
    'H4B': 'HGST HMS5C4040BLE640',
    'S8C': 'ST8000DM002',
    'S8E': 'ST8000NM0055',
    'S12E': 'ST12000NM0007',
    'H12E': 'HGST HUH721212ALN604'
}


def simulate_date(data, date):
    '''Censors things that happen after date.'''
    # if birthday > date then remove.
    data_on_date = data[data.birthday <= date].copy()

    # if birthday + age > date then set age = date - birthday and censored = 1.
    truncated = (data_on_date.birthday + data_on_date.age > date)
    data_on_date.loc[truncated, 'age'] = date - data_on_date.birthday
    data_on_date.loc[truncated, 'censored'] = 1

    return data_on_date


def to_afr(val):
    '''Failure rate to AFR.'''
    return val * 365 * 100


def hazard(data, date, window_size):
    '''Calculate hazard vs age at date.'''
    data_on_date = simulate_date(data, date)

    if data_on_date.empty:
        empty = pd.Series([0])
        return empty, empty, empty, empty, empty

    population = data_on_date.count().min()
    max_age = data_on_date.age.max()

    # Compute deaths and number of disks alive at each time.
    dead = data_on_date[data_on_date.censored == 0] \
        .groupby(['age']) \
        .count() \
        .max(axis=1) \
        .reindex(range(max_age + 1), fill_value=0)
    censored = data_on_date[data_on_date.censored == 1] \
        .groupby(['age']) \
        .count() \
        .max(axis=1) \
        .reindex(range(max_age + 1), fill_value=0)
    alive = population - (dead + censored).shift(1, fill_value=0).cumsum()

    def window_fun_mean(arr):
        '''Custom window which decays quadratically.'''
        half_width = arr.shape[0] / 2
        weights = np.fromfunction(
            lambda i: 1 - (i - half_width)**2 / (half_width + 1)**2,
            arr.shape
        )
        return np.average(arr, weights=weights)

    def window_fun_sum(arr):
        '''Custom window which decays quadratically.'''
        half_width = arr.shape[0] / 2
        weights = np.fromfunction(
            lambda i: 1 - (i - half_width)**2 / (half_width + 1)**2,
            arr.shape
        )
        weights *= arr.shape[0] / weights.sum()
        return np.dot(arr, weights)

    alive_window = alive \
        .rolling(window_size, min_periods=1) \
        .apply(window_fun_sum, raw=True)
    dead_window = dead \
        .rolling(window_size, min_periods=1) \
        .apply(window_fun_sum, raw=True)
    alive_box = alive \
        .rolling(window_size, min_periods=1) \
        .sum()
    dead_box = dead \
        .rolling(window_size, min_periods=1) \
        .sum()

    risk = (dead / alive).fillna(0)
    hazards = risk \
        .rolling(window_size, min_periods=1) \
        .apply(window_fun_mean, raw=True)
    afr = to_afr(hazards)

    if alive_window.empty:
        alive_window = 0.0
    if dead_window.empty:
        dead_window = 0.0
    if afr.empty:
        afr = 0.0

    return alive, dead, alive_window, dead_window, alive_box, dead_box, afr


def canary_disks(data, canary_size):
    '''Get the canary disks for this dataset.'''
    births = data \
        .groupby(['birthday']) \
        .count() \
        .max(axis=1) \
        .cumsum()

    cutoff_date = (births >= canary_size).idxmax()
    canary = data[data.birthday <= cutoff_date]
    return canary


def process_data(args):
    '''Process dataset.'''
    # Load data.
    data = pd.read_csv(args.file)
    data = data[data.age >= 0]

    for group in tqdm(GROUPS, desc='Group'):
        group_data = data[data.model == group]
        if args.canary:
            group_data = canary_disks(group_data, args.canary_size)

        first_day = group_data.birthday.min() + 1
        last_day = (group_data.birthday + group_data.age).max()

        if pd.isna(first_day):
            first_day = 1

        if pd.isna(last_day):
            last_day = first_day

        for day in tqdm(range(first_day, last_day + 1), desc='Day', leave=False):
            curr_date = ORIGIN + dt.timedelta(days=day)
            alive, dead, alive_window, dead_window, alive_box, dead_box, afr = hazard(group_data, day, args.window_size)
            dataframe = pd.DataFrame(
                data={
                    'model': MODEL_NAMES[group],
                    'date': curr_date,
                    'age': range(len(alive)),
                    'disk_days': alive.astype(int),
                    'failures': dead.astype(int),
                    'disk_days_window': alive_window.astype(float),
                    'failures_window': dead_window.astype(float),
                    'disk_days_box': alive_box.astype(int),
                    'failures_box': dead_box.astype(int),
                    'afr': afr.astype(float),
                })
            output_dir = os.path.join(args.output_dir, group)
            output_file = os.path.join(output_dir, f'{curr_date}.csv')
            os.makedirs(output_dir, exist_ok=True)
            dataframe.to_csv(output_file)


def main():
    '''Parse arguments and process data.'''
    parser = argparse.ArgumentParser(description='Generate daily AFRs from dataset.')
    parser.add_argument('file', help='CSV file with data in survival format.')
    parser.add_argument('--output-dir', help='Output directory.', default='simulated_date_data')
    parser.add_argument('--window-size', help='Size in days of smoothing window for AFRs.',
                        type=int, default=60)
    parser.add_argument('--canary', help='Calculate AFR for canaries only.',
                        action='store_true')
    parser.add_argument('--canary-size', help='Size of the canary group.',
                        type=int, default=2000)

    args = parser.parse_args()
    process_data(args)


if __name__ == '__main__':
    main()
