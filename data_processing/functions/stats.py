"""
Functions for calculating statistical measures
"""
# Packages ---
import pandas as pd
import numpy as np
import scipy.stats as stats

# Creates table with summary stats ----------------------------------------------------------


def create_summary_tbl(dfs, column_names, k=3, z=3):
    """
    This function takes a dictionary of DataFrames (dfs), a list of column names (column_names),
    a cutoff value for extreme outliers based on IQR (k), and a Z-Score (z) and creates a summary table 
    for each of the specified columns in each DataFrame.
    """

    # Initialize an empty list to store the summary data
    summary_data = []

    for key in dfs.keys():
        df = dfs[key]
        for column_name in column_names:
            # Ensure the column exists in the dataframe
            if column_name in df.columns:
                # Calculate summary statistics
                mean_value = df[column_name].mean()
                max_value = df[column_name].max()
                min_value = df[column_name].min()
                sd_value = df[column_name].std()

                # Calculate Coefficient of Variation
                # multiplied by 100 to convert it to percentage
                cv_value = (sd_value / mean_value) * 100

                # Calculate IQR
                Q1 = df[column_name].quantile(0.25)
                Q3 = df[column_name].quantile(0.75)
                iqr = stats.iqr(df[column_name])
                lower_bound_k = Q1 - k * iqr
                upper_bound_k = Q3 + k * iqr

                # Calculate Z-Score bounds
                lower_bound_z = mean_value - z * sd_value
                upper_bound_z = mean_value + z * sd_value

                # Add a row to the summary data
                summary_data.append({
                    'id': key,
                    'variable': column_name,
                    'mean': mean_value,
                    'max': max_value,
                    'min': min_value,
                    'sd': sd_value,
                    'cv': cv_value,
                    'lower_bound_k': lower_bound_k,
                    'upper_bound_k': upper_bound_k,
                    'lower_bound_z': lower_bound_z,
                    'upper_bound_z': upper_bound_z
                })

    # Convert the summary data to a DataFrame
    summary_df = pd.DataFrame(summary_data)

    return summary_df

# Remove Outliers ----------------------------------------------------------


def remove_outliers(dfs, column_of_values, summary_table, id_column, lower_threshold_column, upper_threshold_column):
    """
    Remove outliers from the specified column in each dataframe in the input dictionary.
    NOTE: This function use the output of the 'create_summary_table' function.

    The function removes rows in the specified column 'column_of_values' that are outside the range specified by 
    'lower_threshold_column' and 'upper_threshold_column' in 'summary_table' for the corresponding dataframe.
    """
    dfs_with_outliers_removed = {}
    row_counts = []

    for key in dfs.keys():
        df = dfs[key].copy()  # create a copy of the dataframe
        lower_threshold = summary_table.loc[summary_table[id_column]
                                            == key, lower_threshold_column].values[0]
        upper_threshold = summary_table.loc[summary_table[id_column]
                                            == key, upper_threshold_column].values[0]

        # count the rows to be removed
        row_count = len(df[(df[column_of_values] < lower_threshold) | (
            df[column_of_values] > upper_threshold)])
        row_counts.append({'id': key, 'count': row_count})

        # remove the outliers
        df = df[(df[column_of_values] > lower_threshold) &
                (df[column_of_values] < upper_threshold)]
        dfs_with_outliers_removed[key] = df

    counts_of_rows_removed_df = pd.DataFrame(row_counts)

    return dfs_with_outliers_removed, counts_of_rows_removed_df
