"""
Functions for prepping IMU data for calculations
"""
# Packages
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
import warnings
import re

# Five min crop data ----------------------------------------------------------


# Function for getting rid of extra rows so that there are 5mins of data
# Applies to:
# - IMeasureU Blue Trident Senors
# - Sampling freq for lowg = 1125hz
# - Sampling freq for highg = 1600hz
# - 5 minutes = 337500 rows for 1125hz or 478000 for 1600hz

"""
Using 1125hz as an example:

This function processes a dictionary of pandas DataFrames, each identified by a key. 
For each DataFrame, it ensures that it contains exactly 337,500 rows, which represents five minutes of data according to the context. 

If a DataFrame contains fewer than 337,500 rows, a warning is issued and the DataFrame remains unchanged. 
If a DataFrame contains more than 337,500 rows, the excess rows are removed from the *beginning*. 

After the function is executed, the dictionary of DataFrames is updated such that each DataFrame has exactly 337,500 rows (unless it initially had fewer), 
representing a consistent five-minute span of data.
"""


def crop_df_five_mins(dfs, sample_freq):

    # Number of rows needed for exactly 5 mins of data
    rows_needed = sample_freq * 60 * 5

    for key in dfs:
        # Get the dataframe
        df = dfs[key]

        total_rows = len(df)

        # Issue a warning message if the # of rows is less than 5 mins worth of data
        if total_rows < rows_needed:
            warnings.warn(
                f"{key} has only {total_rows} rows, needs {rows_needed}.")

        # Remove excess rows from the dataframe if necessary
        # NOTE: removes rows at the beginning of run
        excess_rows = len(df) - rows_needed
        if excess_rows > 0:
            df = df.iloc[excess_rows:]

        # Update the dictionary with the modified dataframe of 5 mins
        dfs[key] = df


# Add resultant column ----------------------------------------------------------


"""
This function calculates the resultant of three specified columns in each DataFrame within a given dictionary of DataFrames.
The resultant is then added as a new column in each DataFrame.

 Parameters:
    dfs (dict): The dictionary of DataFrames on which the function will operate.
    column_x, column_y, column_z (str): The names of the three columns used for the calculation.
    res_column (str): The name of the resultant column to be added in each DataFrame.
"""


def add_resultant_column(dfs, column_x, column_y, column_z, name_of_res_column):
    for key in dfs.keys():
        df = dfs[key]

        # Calculate resultant acceleration based on the specified columns
        df[name_of_res_column] = np.sqrt(
            df[column_x] ** 2 + df[column_y] ** 2 + df[column_z] ** 2
        )
        # Update the dictionary with the new DataFrame
        dfs[key] = df

# Convert acceleration columns to gs ----------------------------------------------------------


def accel_to_gs_columns(dfs, column_x='ax_m/s/s', column_y='ay_m/s/s', column_z='az_m/s/s', name_of_res_column='res_m/s/s'):
    g = 9.81  # standard acceleration due to gravity

    for key in dfs.keys():
        df = dfs[key]

        # Convert acceleration columns to units of g
        df['ax_g'] = df[column_x] / g
        df['ay_g'] = df[column_y] / g
        df['az_g'] = df[column_z] / g

        # Check if resultant acceleration column exists in the dataframe
        if name_of_res_column in df.columns:
            df['res_g'] = df[name_of_res_column] / g

        # Update the dictionary with the modified dataframe
        dfs[key] = df


# Shift time to start at 0 ----------------------------------------------------------

# Time values are adjusted such that they start at 0
# Adds a column for time that is scaled to start at 0 secs and end at 300 secs (5 mins)
# NOTE: This is just for making the plots easier to read
"""
This function processes a dictionary of pandas DataFrames, each identified by a key. 
It operates on a 'time_s' column assumed to be present in each DataFrame. 

For each DataFrame, the function creates a new column 'time_s_scaled'. 
This new column is a transformed version of the 'time_s' column where the time of the first row is subtracted from each time value. 
This effectively shifts the time scale to start at 0. 

After the function is executed, each DataFrame in the dictionary contains a new column 'time_s_scaled' with the adjusted time scale.
"""


def shift_time_s_to_zero(dfs, time_col='time_s'):
    for key in dfs.keys():
        df = dfs[key]

        # Subtract the time of the first row from each value in the specified time column
        # This will shift the time scale to start at 0 by adjusting all time values
        df['time_s_scaled'] = (df[time_col] - df[time_col].iloc[0])

        # Update the dictionary with the modified dataframe
        dfs[key] = df


# Butterworth filter from SciPy -----------------------------------------------------------


"""
This function applies a Butterworth low-pass filter to a given dataset. 

The function takes four parameters:
1. data: The input data to be filtered.
2. cutoff: The cutoff frequency for the low-pass filter.
3. fs: The sampling rate of the data.
4. order: The order of the Butterworth filter.

The function first calculates the Nyquist frequency (half the sampling rate) and uses it to normalize the cutoff frequency. 
It then designs a Butterworth low-pass filter using the specified order and the normalized cutoff frequency. 
Finally, the function applies the filter to the data and returns the filtered data.
"""


def butter_lowpass_filter(data, cutoff, fs, order):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    filtered_data = filtfilt(b, a, data)
    return filtered_data

# Function for applying Butterworth filter ----------------------------------------------------------


# NOTE: parameters are preset using sampleing freq = 1125hz, fourth order with cutoff at 10hz"


def apply_butter_lowpass_filter_to_dfs(dfs, columns, fs, cutoff, order):
    """
    This function applies a Butterworth lowpass filter to the specified columns in each dataframe in the input dictionary.

    Arguments:
    - dfs: a dictionary of pandas dataframes. The keys are the names of the dataframes and the values are the dataframes themselves.
    - columns: a list of strings, where each string is a column name in the dataframes that the filter should be applied to.
    - fs: the sampling rate of the signal.
    - cutoff: the cutoff frequency of the filter.
    - order: the order of the filter.

    For each column in 'columns', the function adds a new column to the dataframe with the suffix '_filtered'. 
    This new column contains the result of applying the Butterworth filter to the original column. 
    If a column in 'columns' does not exist in a dataframe, a warning message is issued and the column is skipped.
    """
    for key in dfs.keys():
        df = dfs[key]

        for col in columns:
            if col in df.columns:
                new_col = f'{col}_filtered'
                df[new_col] = butter_lowpass_filter(df[col], cutoff, fs, order)
            else:
                warnings.warn(f"The column '{col}' does not exist in '{key}'")

        # Update the dictionary with the modified dataframe
        dfs[key] = df

# Zero-Centering / Mean-Centering ----------------------------------------------------------


def calc_mean_shift(dfs, column_names):
    """
    This function takes a dictionary of DataFrames (dfs) and a list of column names (column_names) 
    and creates new columns in each DataFrame which are zero-centered versions of the specified columns.

    Zero-centering, or mean-centering, is a preprocessing step where the mean of the data is subtracted 
    from each data point. This shifts the data such that it's centered around 0.
    """
    for key in dfs.keys():
        df = dfs[key]
        for column_name in column_names:
            # Ensure the column exists in the dataframe
            if column_name in df.columns:
                mean_value = df[column_name].mean()
                df[column_name + '_meanshift'] = df[column_name] - mean_value
        # Update the dictionary with the modified dataframe
        dfs[key] = df


# Function for creating the export table I need ----------------------------------------------------------


def export_tbl(df):
    # Prepare a list to store the rows
    rows_list = []

    # Iterate through df
    for index, row in df.iterrows():
        # extract the sub_id
        sub_id = row['key'].split('_')[0]

        # extract the run_type
        run_type_parts = row['key'].split('_')[1:-2]
        run_type = '_'.join(
            [part for part in run_type_parts if not part.isdigit()])

        # extract the sensor
        sensor = None
        for word in row['key'].split('_'):
            if len(word) == 5 and word.isdigit():
                sensor = word
                break

        # Create a dict to represent the row and append it to the list
        row_dict = {
            'sub_id': sub_id,
            'run_type': run_type,
            'sensor': sensor,
            'variable': row['variable'],
            'value': row['value']
        }
        rows_list.append(row_dict)

    # Create a DataFrame from the list of rows
    df_export = pd.DataFrame(rows_list)

    return df_export


def export_tbl_imu_val(df):
    # Prepare a list to store the rows
    rows_list = []

    # Iterate through df
    for index, row in df.iterrows():
        # Split the key
        parts = row['key'].split('_')

        # Extract the sub_id (first two parts)
        sub_id = '_'.join(parts[:3])

        # Extract the run_type (fourth and fifth parts)
        run_type = '_'.join(parts[3:6])

        # Extract the sensor (last part)
        sensor = parts[-1]

        # Create a dict to represent the row and append it to the list
        row_dict = {
            'sub_id': sub_id,
            'run_type': run_type,
            'sensor': sensor,
            'variable': row['variable'],
            'value': row['value']
        }
        rows_list.append(row_dict)

    # Create a DataFrame from the list of rows
    df_export = pd.DataFrame(rows_list)

    return df_export


# Append to data to my Excel table ----------------------------------------------------------


def append_df_to_excel(df_to_append, file_path, sheet_name):
    # Load existing excel file (if it exists) or create a new one (if it does not exist)
    try:
        with pd.ExcelFile(file_path) as xlsx:
            df = pd.read_excel(xlsx, sheet_name=sheet_name)
    except FileNotFoundError:
        df = pd.DataFrame()

    # Append df to the existing data in the Excel file using concat
    df = pd.concat([df, df_to_append], ignore_index=True)

    # Write the updated dataframe to the Excel file
    with pd.ExcelWriter(file_path) as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    # Print a message to indicate that the file has been saved
    print(f'Data has been saved successfully to {file_path}.')

# Remove dfs from a dictionary based on trial number ----------------------------------------------------------


def remove_trials_from_dfs(dfs, bad_trials):
    """
    Exclude specific trials from the dictionary of DataFrames based on trial numbers.

    Inputs:
    dfs (dict): Dictionary of DataFrames.
    bad_trials (list): List of trial numbers to be excluded.

    Returns:
    dict: Updated dictionary with specific trials excluded.
    """
    # Convert trial numbers to string and format them as they appear in the ids
    formatted_bad_trials = [f"_trial{trial}" for trial in bad_trials]

    # Use dictionary comprehension to exclude the unwanted trials
    dfs_without_bad_trials = {key: df for key, df in dfs.items() if not any(
        bad_trial in key for bad_trial in formatted_bad_trials)}

    return dfs_without_bad_trials

# Remove dfs based on trial number and location --------------------------------------------------------------


def filter_out_dfs(dfs, offset_times_df):
    # Compile a regex pattern for extracting the body part and trial number from the keys
    pattern = re.compile(
        r"imu_val_\d+_time\d+_og_run_(left_tibia|right_tibia)_(\d+)_trial(\d+)")

    # Create a set of tuples (body part, trial number) for quick lookup
    valid_trials = set(
        zip(offset_times_df['imu'], offset_times_df['trial_num']))

    # Collect keys to remove (can't remove while iterating over the dictionary)
    keys_to_remove = []

    for key in dfs.keys():
        match = pattern.search(key)
        if match:
            body_part, _, trial_num = match.groups()
            trial_num = int(trial_num)  # convert trial number to integer

            # Check if the (body part, trial number) tuple is not in the valid_trials set
            if (body_part, trial_num) not in valid_trials:
                keys_to_remove.append(key)

    # Remove the keys that are not in the valid trials
    for key in keys_to_remove:
        del dfs[key]

    return dfs

# For IMU Validtion. Finding windows to match up w/ force plate footstikes -------------------------------------------


'''
Identifying the initial peak values in a specific column (res_g) and computing search windows 
based on offset times related to specific events (e.g., footstrikes). 
For each DataFrame, it extracts and associates relevant information 
such as the peak value, peak index, and the start and end indices of the search window, 
summarizing this information into a consolidated DataFrame. 

'''


def peak_and_window_data(dfs, offset_times_df, sampling_rate=500, search_window_margin=50):
    summary_data = []
    # Store peak timestamps and indices for each trial of right_tibia
    right_tibia_peaks = {}

    # First loop: Process only right_tibia
    for key, df in dfs.items():
        df = df.reset_index(drop=True)
        parts = key.split('_')
        body_part = '_'.join(parts[6:8])
        trial_num = int(parts[-1].replace('trial', ''))

        if body_part == 'right_tibia':
            initial_peak_row = df['res_g'].idxmax()
            peak_timestamp = df.loc[initial_peak_row, 'timestamp']
            right_tibia_peaks[trial_num] = (initial_peak_row, peak_timestamp)

    # Second loop: Process left_tibia and right_tibia (for creating search windows)
    for key, df in dfs.items():
        df = df.reset_index(drop=True)
        parts = key.split('_')
        body_part = '_'.join(parts[6:8])
        trial_num = int(parts[-1].replace('trial', ''))

        # Retrieve corresponding offset time
        matching_rows = offset_times_df.loc[
            (offset_times_df['imu'] == body_part) & (
                offset_times_df['trial_num'] == trial_num), 'offset'
        ]
        offset_time = matching_rows.values[0] if not matching_rows.empty else None

        if body_part in ['right_tibia', 'left_tibia'] and trial_num in right_tibia_peaks and offset_time is not None:
            right_tibia_peak_row, right_tibia_peak_timestamp = right_tibia_peaks[trial_num]

            if body_part == 'right_tibia':
                peak_row = right_tibia_peak_row
                peak_timestamp = right_tibia_peak_timestamp
                peak_value = df['res_g'].max()
            else:  # For left_tibia, use right_tibia's peak timestamp but no peak value
                peak_row = right_tibia_peak_row  # Aligning with the right_tibia
                peak_timestamp = None  # No peak timestamp for left_tibia
                peak_value = None  # No peak value for left_tibia

            # Calculate row offset based on the peak timestamp index of right tibia
            # This now applies to both right_tibia and left_tibia
            row_offset = peak_row + int(offset_time * sampling_rate)

            # Define the search window indices, ensure they are within the DataFrame bounds
            window_start_idx = max(0, row_offset - search_window_margin)
            window_end_idx = min(
                len(df) - 1, row_offset + search_window_margin)

            # Fetch timestamp values for the window start and end indices
            window_start_timestamp = df.loc[window_start_idx,
                                            'timestamp'] if window_start_idx < len(df) else None
            window_end_timestamp = df.loc[window_end_idx,
                                          'timestamp'] if window_end_idx < len(df) else None

            # Append the data to the summary list
            summary_data.append({
                'df_id': key,
                'body_part': body_part,
                'trial_num': trial_num,
                'offset_time': offset_time,
                'peak_value': peak_value,
                'peak_timestamp': peak_timestamp,
                'window_start_timestamp': window_start_timestamp,
                'window_end_timestamp': window_end_timestamp
            })

    # Create a DataFrame from the summary data
    summary_df = pd.DataFrame(summary_data)
    return summary_df
