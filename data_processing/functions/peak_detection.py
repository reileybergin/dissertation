"""
Functions for calculating peaks
 - Peak detection for positive, negative, and absolute values
 - Peak detection for negative and absolute values using specified window based on *each* resultant peak
"""
# Packages
import numpy as np
import pandas as pd
import warnings
from scipy.signal import find_peaks

# Average Peak Acceleration for Positive Peaks ----------------------------------------------------------


import numpy as np
import pandas as pd
import warnings
from scipy.signal import find_peaks


def calc_avg_positive_peaks(dfs, columns, time_column=None,  min_peak_height=None, max_peak_height=None, min_samples_between_peaks=None):
    """
    Calculates the average positive peak for the specified columns in each dataframe in the input dictionary.

    For Running ... 
    When the IMU is located on the low back the *min_samples_between_peaks* should be ~ 0.25 secs (time between left *and* right steps during running)
    - 1125hz = 281
    - 1600hz = 400
    When the IMU is located on the left or right leg the numbers above are just doubled in order to represent the time between just one side (vs both)

    Notes:
    - For each column in 'columns', the function finds the peaks using the scipy.signal.find_peaks function, calculates the average of these peaks,
    and stores the result in a dictionary along with the key of the dataframe in 'dfs' and the column name (appended with '_avg_peak').
    - A new column indicating the peak locations is also added to the original dataframe. 
    - The function also creates a dictionary containing dfs with the time and peak values for each peak.

    """
    results = []
    dfs_peak_values = {}

    for key in dfs.keys():
        df = dfs[key]
        df.reset_index(drop=True, inplace=True)

        for col in columns:
            if col in df.columns:
                peaks, properties = find_peaks(
                    df[col], height=(min_peak_height, max_peak_height), distance=min_samples_between_peaks)
                peak_values = properties["peak_heights"]
                avg_peak_value = np.mean(peak_values)

                # Add new column to *original* dataframe indicating the peak locations
                df[f'{col}_peaks'] = 0
                df.loc[peaks, f'{col}_peaks'] = 1

                # Create a dictionary of dfs w/ a column for the values (heights) for each peak and time at which they occured.
                # 'time_column': this column contains the time values at the points where peaks have been identified in the data.
                # NOTE: these time values are fetched from the 'time_column' of the *original* df at the indices where the peaks were found (the peaks array).
                peak_df = pd.DataFrame({
                    time_column: df[time_column][peaks],
                    'peak_values': peak_values
                })
                # Storing this peak_df in a larger dictionary (dfs_peak_values):
                # The key under which this df is stored is the original key of the df
                dfs_peak_values[f'{key}'] = peak_df

                results.append({
                    'key': key,
                    'variable': f'{col}_avg_peak',
                    'value': avg_peak_value,
                })
            else:
                warnings.warn(f"The column '{col}' does not exist in '{key}'")

        # Replace the original dataframe with the modified one in the dictionary
        dfs[key] = df

    result_df = pd.DataFrame(results)
    return result_df, dfs_peak_values

# Dynamic Version of Average Peak Acceleration for Positive Peaks ----------------------------------------------------------


def calc_avg_positive_peaks_from_tbl(dfs, columns, time_column=None, summary_table=None, id_column=None, min_peak_height_column=None, max_peak_height_column=None, min_samples_between_peaks=None):
    """
    Update:
    This modification fetches min_peak_height and max_peak_height for each dataframe in the input dictionary 'dfs' dynamically from the input 'summary_table'. 
    The 'id_column' parameter specifies the column in 'summary_table' that matches with the keys in 'dfs'. 
    The 'min_peak_height_column' and 'max_peak_height_column' parameters specify the columns in 'summary_table' from where to 
    fetch the min and max peak heights for each dataframe.
    """
    results = []
    dfs_peak_values = {}

    for key in dfs.keys():
        df = dfs[key]
        df.reset_index(drop=True, inplace=True)

        # Obtain min and max peak heights for the current dataframe from the summary table
        min_peak_height = summary_table.loc[summary_table[id_column]
                                            == key, min_peak_height_column].values[0]
        max_peak_height = summary_table.loc[summary_table[id_column]
                                            == key, max_peak_height_column].values[0]

        for col in columns:
            if col in df.columns:
                peaks, properties = find_peaks(
                    df[col], height=(min_peak_height, max_peak_height), distance=min_samples_between_peaks)
                peak_values = properties["peak_heights"]
                avg_peak_value = np.mean(peak_values)

                # Add new column to *original* dataframe indicating the peak locations
                df[f'{col}_peaks'] = 0
                df.loc[peaks, f'{col}_peaks'] = 1

                # Create a dictionary of dfs w/ a column for the values (heights) for each peak and time at which they occured.
                peak_df = pd.DataFrame({
                    time_column: df[time_column][peaks],
                    'peak_values': peak_values
                })
                dfs_peak_values[f'{key}'] = peak_df

                results.append({
                    'key': key,
                    'variable': f'{col}_avg_peak',
                    'value': avg_peak_value,
                })
            else:
                warnings.warn(f"The column '{col}' does not exist in '{key}'")

        # Replace the original dataframe with the modified one in the dictionary
        dfs[key] = df

    result_df = pd.DataFrame(results)
    return result_df, dfs_peak_values

# Average Peak Acceleration for Negative Peaks ----------------------------------------------------------


def calc_avg_neg_peaks(dfs, columns, min_peak_height=1.0, min_samples_between_peaks=281):
    """
    This function calculates the average negative peak acceleration for the specified columns in each dataframe in the input dictionary.

    NOTE: 
    - min peak height is defaulted to 1.0 to get peaks in negative direction
    - The min samples between peaks is meant to reflect ~ 0.25 secs (time between left *and* right steps during running)

    Arguments:
    - dfs: a dictionary of pandas dataframes. The keys are the names of the dataframes and the values are the dataframes themselves.
    - columns: a list of strings, where each string is a column name in the dataframes that the average peak acceleration should be calculated for.
    - min_peak_height: the minimum height for a peak to be recognized, default is 1.0.
    - min_samples_between_peaks: the minimum number of samples between peaks, default is 281 (comes from 1125hz = 0.25 secs).

    For each column in 'columns', the function finds the peaks using the scipy.signal.find_peaks function, calculates the average 
    of these peaks, and stores the result in a dictionary along with the key of the dataframe in dfs and the column name (appended with '_avg_peak'). 

    If a column in 'columns' does not exist in a dataframe, a warning message is issued and the column is skipped.

    The function returns a dataframe with the average peak accelerations for each key and 
    adds a column to the original dataframe to indicate the location of the peaks. 

    """
    results = []

    for key in dfs.keys():
        df = dfs[key]
        df.reset_index(drop=True, inplace=True)

        for col in columns:
            if col in df.columns:
                # Multiply by -1 to find negative peaks
                peaks, properties = find_peaks(
                    -df[col], height=min_peak_height, distance=min_samples_between_peaks)
                peak_values = properties["peak_heights"]
                avg_peak_value = np.mean(peak_values)

                # Add new column to original dataframe indicating the peak locations
                df[f'{col}_neg_peaks'] = 0
                df.loc[peaks, f'{col}_neg_peaks'] = 1

                results.append({
                    'key': key,
                    'variable': f'{col}_avg_neg_peak',
                    'value': avg_peak_value,
                })
            else:
                warnings.warn(f"The column '{col}' does not exist in '{key}'")

    result_df = pd.DataFrame(results)
    return result_df

# Average Peak Acceleration for Absolute Values ----------------------------------------------------------


def calc_avg_abs_peaks(dfs, columns, min_peak_height=1.0, min_samples_between_peaks=281):
    """
    This function calculates the average absolute peak acceleration for the specified columns in each dataframe in the input dictionary.

    NOTE: 
    - min peak height is defaulted to 1.0
    - The min samples between peaks is meant to reflect ~ 0.25 secs (time between steps during running)
    - the average represents the average of the values converted into absolute values

    Arguments:
    - dfs: a dictionary of pandas dataframes. The keys are the names of the dataframes and the values are the dataframes themselves.
    - columns: a list of strings, where each string is a column name in the dataframes that the average peak acceleration should be calculated for.
    - min_peak_height: the minimum height for a peak to be recognized, default is 1.0.
    - min_samples_between_peaks: the minimum number of samples between peaks, default is 281 (comes from 1125hz = 0.25 secs).

    For each column in 'columns', the function finds the peaks using the scipy.signal.find_peaks function, calculates the average 
    of these peaks, and stores the result in a dictionary along with the key of the dataframe in dfs and the column name (appended with '_avg_abs_peak'). 

    If a column in 'columns' does not exist in a dataframe, a warning message is issued and the column is skipped.

    The function returns a dataframe with the average peak accelerations for each key and 
    adds a column to the original dataframe to indicate the location of the peaks. 

    """
    results = []

    for key in dfs.keys():
        df = dfs[key]
        df.reset_index(drop=True, inplace=True)

        for col in columns:
            if col in df.columns:
                # Find peaks on the absolute values of the data
                peaks, properties = find_peaks(
                    df[col].abs(), height=min_peak_height, distance=min_samples_between_peaks)
                # Calculate absolute peak values
                peak_values = df[col].iloc[peaks].abs()
                avg_peak_value = np.mean(peak_values)

                # Add new column to original dataframe indicating the peak locations
                df[f'{col}_abs_peaks'] = 0
                df.loc[peaks, f'{col}_abs_peaks'] = 1

                results.append({
                    'key': key,
                    'variable': f'{col}_avg_abs_peak',
                    'value': avg_peak_value,
                })
            else:
                warnings.warn(f"The column '{col}' does not exist in '{key}'")

    result_df = pd.DataFrame(results)
    return result_df

# Find absolute peaks using a window determined by the RES peaks -----------------------------------------------------------


def calc_avg_windowed_abs_peaks(dfs, resultant_column, columns, min_peak_height=1.0, min_samples_between_peaks=281, window_size=150):
    """
    This function calculates the average absolute peak acceleration for the specified columns in each dataframe in the input dictionary,
    within a window of 'window_size' samples centered around each peak in 'resultant_column'.
    """
    results = []
    peak_counts = []
    half_window_size = window_size // 2

    for key in dfs.keys():
        df = dfs[key]
        df.reset_index(drop=True, inplace=True)

        if resultant_column not in df.columns:
            warnings.warn(
                f"The column '{resultant_column}' does not exist in '{key}'")
            continue

        # Find locations of resultant peaks
        # NOTE: resultant_peaks is an array with the index ie location of each peak
        resultant_peaks, _ = find_peaks(
            df[resultant_column], height=min_peak_height, distance=min_samples_between_peaks)

        # Mark resultant peak locations in the *original* dataframe
        # NOTE: the purpose of this is just to have these to use for plotting the data later
        df['resultant_peaks'] = 0
        df.loc[resultant_peaks, 'resultant_peaks'] = 1

        # Keep track of the total count of peaks found which will be used as a comparison to the count of absolute peaks (which should be the same)
        num_resultant_peaks = len(resultant_peaks)

        for col in columns:
            if col in df.columns:

                # Create a column for storing the locations of the absolute peaks
                # NOTE: Just like above, the purpose of this is to be able plot the data later
                df[f'{col}_windowed_abs_peak'] = 0

                # Create a list to store the actual values of the highest peaks within the windows for the current column
                windowed_abs_peak = []

                # Loop through the peak locations in resultant_peaks
                # Use the half_window_size to index the places where I want to start and end the window
                # NOTE: the max and min ensures that the window does not go beyond the DataFrame's boundaries
                for peak in resultant_peaks:
                    start = max(0, peak - half_window_size)
                    end = min(len(df) - 1, peak + half_window_size)
                    # Extracts the window of data from the current column using the indexes created above
                    # the plus 1 makes the end point inclusive
                    window = df[col][start:end+1]

                    # Find peaks on the absolute values of the data within the window
                    # NOTE: peaks here corresponds to location of the peaks not their actual values
                    peaks, properties = find_peaks(
                        window.abs(), height=min_peak_height)

                    # Because multiple peaks may have been found I need to find the single *highest* one
                    if len(peaks) > 0:  # check if there are any peaks in the first place
                        # Finds the index of the *highest* peak within the window.
                        # The argmax() function returns the index of the maximum value in *this array*
                        highest_peak_index = np.argmax(
                            properties['peak_heights'])

                        # Now I need to get the actual index of the highest peak *within the current window*
                        highest_peak_index_in_window = peaks[highest_peak_index]

                        # Mark the absolute peak location in the original dataframe
                        peak_indices = start + highest_peak_index_in_window
                        df.loc[peak_indices, f'{col}_windowed_abs_peak'] = 1

                        # And finally, using this locaiton, grab the absolute peak height *value* in the window and append it the list
                        # NOTE: Need to first calculate abs() because the window represents the orginal values
                        windowed_abs_peak.append(
                            abs(window.iloc[highest_peak_index_in_window]))

                # Calculate average absolute peak values
                avg_peak_value = np.mean(windowed_abs_peak)

                # Adding a row to the results table
                results.append({
                    'key': key,
                    'variable': f'{col}_avg_windowed_abs_peak',
                    'value': avg_peak_value,
                })

                # Adding a row to the peak count table
                num_abs_peaks = df[f'{col}_windowed_abs_peak'].sum()
                peak_counts.append({
                    'key': key,
                    'variable': col,
                    'num_resultant_peaks': num_resultant_peaks,
                    'num_abs_peaks': num_abs_peaks,
                    'difference': num_resultant_peaks - num_abs_peaks
                })

            else:
                warnings.warn(f"The column '{col}' does not exist in '{key}'")

        # Replace the original dataframe with the modified one in the dictionary
        dfs[key] = df

    result_df = pd.DataFrame(results)
    peak_count_df = pd.DataFrame(peak_counts)

    return result_df, peak_count_df

# Find negative peaks using a window determined by the RES peaks ----------------------------------------------------------


def calc_avg_windowed_neg_peaks(dfs, resultant_column, columns, min_peak_height=1.0, min_samples_between_peaks=281, window_size=150):
    """
    This function calculates the average negative peak acceleration for the specified columns in each dataframe in the input dictionary,
    within a window of 'window_size' samples centered around each peak in 'resultant_column'.
    """
    results = []
    peak_counts = []
    half_window_size = window_size // 2

    for key in dfs.keys():
        df = dfs[key]
        df.reset_index(drop=True, inplace=True)

        if resultant_column not in df.columns:
            warnings.warn(
                f"The column '{resultant_column}' does not exist in '{key}'")
            continue

        # Find locations of resultant peaks
        # NOTE: resultant_peaks is an array with the index ie location of each peak
        resultant_peaks, _ = find_peaks(
            df[resultant_column], height=min_peak_height, distance=min_samples_between_peaks)

        # Mark resultant peak locations in the *original* dataframe
        # NOTE: the purpose of this is just to have these to use for plotting the data later
        df['resultant_peaks'] = 0
        df.loc[resultant_peaks, 'resultant_peaks'] = 1

        # Keep track of the total count of peaks found which will be used as a comparison to the count of negative peaks (which should be the same)
        num_resultant_peaks = len(resultant_peaks)

        for col in columns:
            if col in df.columns:

                # Create a column for storing the locations of the negative peaks
                # NOTE: Just like above, the purpose of this is to be able plot the data later
                df[f'{col}_windowed_neg_peak'] = 0

                # Create a list to store the actual values of the highest peaks within the windows for the current column
                windowed_neg_peak = []

                # Loop through the peak locations in resultant_peaks
                # Use the half_window_size to index the places where I want to start and end the window
                # NOTE: the max and min ensures that the window does not go beyond the DataFrame's boundaries
                for peak in resultant_peaks:
                    start = max(0, peak - half_window_size)
                    end = min(len(df) - 1, peak + half_window_size)
                    # Extracts the window of data from the current column using the indexes created above
                    # the plus 1 makes the end point inclusive
                    window = df[col][start:end+1]

                    # Find peaks on the negative values of the data within the window
                    # To do this I am just negating all the values
                    # NOTE: peaks here corresponds to location of the peaks not their actual values
                    peaks, properties = find_peaks(
                        -window, height=min_peak_height)

                    # Because multiple peaks may have been found I need to find the single *highest* one
                    if len(peaks) > 0:  # check if there are any peaks in the first place
                        # Finds the index of the *highest* peak within the window.
                        # The argmax() function returns the index of the minimum value in *this array*
                        highest_peak_index = np.argmax(
                            properties['peak_heights'])

                        # Now I need to get the actual index of the highest peak *within the current window*
                        highest_peak_index_in_window = peaks[highest_peak_index]

                        # Mark the negative peak location in the original dataframe
                        peak_indices = start + highest_peak_index_in_window
                        df.loc[peak_indices, f'{col}_windowed_neg_peak'] = 1

                        # And finally, using this locaiton, grab the negative peak height *value* in the window and append it the list
                        # NOTE: Need to first negate all the value because the window represents the orginal values
                        windowed_neg_peak.append(
                            -window.iloc[highest_peak_index_in_window])

                # Calculate average negative peak values
                avg_peak_value = np.mean(windowed_neg_peak)

                # Adding a row to the results table
                results.append({
                    'key': key,
                    'variable': f'{col}_avg_windowed_neg_peak',
                    'value': avg_peak_value,
                })

                # Adding a row to the peak count table
                num_neg_peaks = df[f'{col}_windowed_neg_peak'].sum()
                peak_counts.append({
                    'key': key,
                    'variable': col,
                    'num_resultant_peaks': num_resultant_peaks,
                    'num_neg_peaks': num_neg_peaks,
                    'difference': num_resultant_peaks - num_neg_peaks
                })

            else:
                warnings.warn(f"The column '{col}' does not exist in '{key}'")

        # Replace the original dataframe with the modified one in the dictionary
        dfs[key] = df

    result_df = pd.DataFrame(results)
    peak_count_df = pd.DataFrame(peak_counts)

    return result_df, peak_count_df
