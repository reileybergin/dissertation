"""
Functions for calculating stride variables during running
"""
# Packages ---
import nolds
import numpy as np
import pandas as pd
import warnings

# Stride Times (ST) Column ----------------------------------------------------------


def calc_stride_times(dfs, time_column):
    """
    Calculates the stride times for each dataframe in the input dictionary.

    The stride time is the difference between consecutive time points (i.e., foot strikes of either the left or right leg)

    The function adds a new column 'stride_times' to each dataframe in the input dictionary 'dfs'.

    """
    dfs_with_st = {}
    for key in dfs.keys():
        df = dfs[key].copy()  # creates a new copy of the dataframe
        df['stride_times'] = df[time_column].diff()
        # drop rows with NA in 'stride_times'
        # NOTE: The first row will always be an NA
        df.dropna(subset=['stride_times'], inplace=True)
        dfs_with_st[key] = df

    return dfs_with_st

# Table of Stride Time Variables ----------------------------------------------------------


def calc_stride_times_vars(dfs, stride_times_column, total_run_time_mins):
    """
    This function calculates the mean, standard deviation (SD), coefficient of variation (CV), fractal scaling index (FSI) via Detrended Fluctuation Analysis (DFA),
    and strides per minute (SPM) of the stride times column in each dataframe in the input dictionary.

    Arguments:
    - dfs: a dictionary of pandas dataframes. The keys are the names of the dataframes and the values are the dataframes themselves.
    - stride_times_column: the column name in the dataframes that contains stride times.
    - total_run_time_mins: the total duration of the run in minutes.

    The function returns a dataframe with the calculated measures.
    """
    results = []

    for key in dfs.keys():
        df = dfs[key]

        if stride_times_column in df.columns:
            # Calculate mean
            mean = df[stride_times_column].mean()

            # Calculate standard deviation (SD)
            sd = df[stride_times_column].std()

            # Calculate coefficient of variation (CV)
            cv = (sd / mean) * 100

            # Calculate FSI via DFA
            try:
                fsi = nolds.dfa(df[stride_times_column].values)
            except Exception as e:
                fsi = np.nan  # Insert a NaN if the DFA calculation fails
                print(f"Failed to calculate DFA for key {key}. Error: {e}")

            # Calculate Strides per Minute (SPM)
            total_strides = len(df[stride_times_column])
            spm = total_strides / total_run_time_mins

            # Add calculated values to the results list
            results.append({
                'key': key,
                'variable': f'{stride_times_column}_mean',
                'value': mean
            })

            results.append({
                'key': key,
                'variable': f'{stride_times_column}_sd',
                'value': sd
            })

            results.append({
                'key': key,
                'variable': f'{stride_times_column}_cv',
                'value': cv
            })

            results.append({
                'key': key,
                'variable': f'{stride_times_column}_fsi',
                'value': fsi
            })

            results.append({
                'key': key,
                'variable': f'{stride_times_column}_spm',
                'value': spm
            })

    result_df = pd.DataFrame(results)
    return result_df
