"""
Functions for measures calculated from the IMU on the low back
 - Root Mean Squared (RMS) for each axis (VT, ML, and AP) and resultant (RES)
 - Sample Entropy (SE) for each single axis
"""
# Packages
import nolds
import numpy as np
import pandas as pd
import warnings

# Root Mean Squared (RMS) ----------------------------------------------------------


# Function for calculating RMS of single column:
# Calculates the RMS for an entire series (column of a DataFrame) returning a single value for the column.

# Steps:
# 1) Square each value in the series (series.pow(2)). pow(2) means "power of 2"
# 2) Compute the mean of the squared values (np.mean(series.pow(2))).
# 3) Compute the square root of the mean of the squared values (np.sqrt(np.mean(series.pow(2)))).


def calculate_rms(series):
    return np.sqrt(np.mean(series.pow(2)))

# RMS for specified columns for each df in a dictionary ----------------------------------------------------------


def apply_rms_to_dfs(dfs, columns):
    """
    This function calculates the root mean square (RMS) of the specified columns in each dataframe in the input dictionary.

    Arguments:
    - dfs: a dictionary of pandas dataframes. The keys are the names of the dataframes and the values are the dataframes themselves.
    - columns: a list of strings, where each string is a column name in the dataframes that the RMS should be calculated for.

    For each column in 'columns', the function calculates the RMS using the calculate_rms function and 
    stores the result in a dictionary along with the key of the dataframe in dfs and the column name (appended with '_rms'). 
    If a column in 'columns' does not exist in a dataframe, a warning message is issued and the column is skipped. 

    The function returns a dataframe with the RMS calculations.
    """
    results = []

    for key in dfs.keys():
        df = dfs[key]

        for col in columns:
            if col in df.columns:
                rms_value = calculate_rms(df[col])

                results.append({
                    'key': key,
                    'variable': f'{col}_rms',
                    'value': rms_value
                })
            else:
                warnings.warn(f"The column '{col}' does not exist in '{key}'")

    result_df = pd.DataFrame(results)
    return result_df


# Sample Entropy for specified columns for each df in a dictionary ----------------------------------------------------------


# NOTE: Uses the sample entropy function from the nolds package: https://nolds.readthedocs.io/en/latest/nolds.html#sample-entropy
# - emd_dim is m
# - tolerance is r


def apply_sampen_to_dfs(dfs, columns, emb_dim=2, tolerance=0.2):
    """
    This function calculates the sample entropy of the specified columns in each dataframe in the input dictionary.

    Arguments:
    - dfs: a dictionary of pandas dataframes. The keys are the names of the dataframes and the values are the dataframes themselves.
    - columns: a list of strings, where each string is a column name in the dataframes that the sample entropy should be calculated for.
    - emb_dim: embedding dimension for sample entropy calculation, default is 2.
    - tolerance: tolerance for sample entropy calculation, default is 0.15.

    For each column in 'columns', the function calculates the sample entropy using the nolds.sampen function and 
    stores the result in a dictionary along with the key of the dataframe in dfs and the column name (appended with '_sampen'). 
    If a column in 'columns' does not exist in a dataframe, a warning message is issued and the column is skipped. 

    The function returns a dataframe with the sample entropy calculations.
    """
    results = []

    for key in dfs.keys():
        df = dfs[key]

        for col in columns:
            if col in df.columns:
                sampen_value = nolds.sampen(
                    df[col], emb_dim=emb_dim, tolerance=tolerance)

                results.append({
                    'key': key,
                    'variable': f'{col}_sampen',
                    'value': sampen_value
                })
            else:
                warnings.warn(f"The column '{col}' does not exist in '{key}'")

    result_df = pd.DataFrame(results)
    return result_df
