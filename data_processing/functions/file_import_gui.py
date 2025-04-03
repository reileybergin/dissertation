"""
Function for brining in files w/ Tkinter GUI
Will store each file as a dataframe within a dictionary

NOTE: Has several conditions for handeling file names specific for this project
"""
# Packages ---
import tkinter as tk
from tkinter import filedialog
import pandas as pd

# File import function ----------------------------------------------------------


def read_csv_files_gui(initialdir):
    # Create an empty dictionary to store each file as a dataframe
    dfs = {}

    # Create a Tkinter root window
    root = tk.Tk()
    root.withdraw()  # NOTE: only way I found to get Tkinter to stop running

    # Open file dialog to select multiple CSV files
    filepaths = filedialog.askopenfilenames(
        title="Select Files",
        initialdir=initialdir,
        filetypes=(("csv files", "*.csv"),))

    # Loop through the selected filepaths and read each CSV file into a dataframe
    # Then store each dataframe in a dictionary with a modified filename as its key
    for filepath in filepaths:
        df = pd.read_csv(filepath)

        # Get the filename from the filepath
        filename = filepath.split("/")[-1]

        # Check if the filename contains the characters "PRS"
        if "PRS" not in filename:
            df_name = filename.replace(".csv", "")
        else:
            # Remove everything before the first underscore and after the second underscore
            df_name = filename.split(
                "_")[0] + "_" + filename.split("_")[1] + "_" + filename.split("_")[3]
            # Replace all dashes with underscores, remove "TS" and remove ".csv"
            df_name = df_name.replace(
                "-", "_").replace("TS_", "").replace(".csv", "")

        # Make the modified filename all lowercase
        df_name = df_name.lower()

        # Read the CSV file into a dataframe
        df = pd.read_csv(filepath)

        # Append the dataframe to the dictionary using its modified filename as its key
        dfs[df_name] = df

    # For reference, create a list of the key names of each dataframe appended
    keys_list = list(dfs.keys())

    return dfs, keys_list

# Old IMU data file imports ----------------------------------------------------------


def read_csv_files_gui_2(initialdir):
    # Create an empty dictionary to store each file as a dataframe
    dfs = {}

    # Create a Tkinter root window
    root = tk.Tk()
    root.withdraw()  # NOTE: only way I found to get Tkinter to stop running

    # Open file dialog to select multiple CSV files
    filepaths = filedialog.askopenfilenames(
        title="Select Files",
        initialdir=initialdir,
        filetypes=(("csv files", "*.csv"),))

    # Loop through the selected filepaths and read each CSV file into a dataframe
    # Then store each dataframe in a dictionary with a modified filename as its key
    for filepath in filepaths:
        df = pd.read_csv(filepath)

        # Get the filename from the filepath
        filename = filepath.split("/")[-1]

        # Split into "parts" by underscores
        parts = filename.split("_")

        # Extract 'subject'
        subject = parts[0].split()[-1]

        # Extract 'run_type'
        run_type = parts[1].lower() + "_" + parts[2].lower() + \
            "_" + parts[3].lower()

        # Extract 'location'
        # Joining the parts related to location which might be split into multiple parts due to spaces
        location_parts = parts[4:]
        location = "_".join(location_parts).split(
            "_0000")[0].replace(" ", "_").lower()

        # Extract 'imu_number'
        # Assuming the IMU number always starts with '0000' and is 8 digits long
        imu_number = parts[5][:8].lstrip("0")

        # Concatenating all parts
        df_name = "_".join([subject, run_type, location, imu_number])

        # Make the modified filename all lowercase
        df_name = df_name.lower()

        # Read the CSV file into a dataframe
        df = pd.read_csv(filepath)

        # Append the dataframe to the dictionary using its modified filename as its key
        dfs[df_name] = df

    # For reference, create a list of the key names of each dataframe appended
    keys_list = list(dfs.keys())

    return dfs, keys_list

# Import without pulling anything specific from filename ----------------------------------------------------------


def read_csv_files_gui_3(initialdir):
    # Create an empty dictionary to store each file as a dataframe
    dfs = {}

    # Create a Tkinter root window
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Open file dialog to select multiple CSV files
    filepaths = filedialog.askopenfilenames(
        title="Select Files",
        initialdir=initialdir,
        filetypes=(("csv files", "*.csv"),))

    # Loop through the selected filepaths and read each CSV file into a dataframe
    for filepath in filepaths:
        # Get the filename from the filepath
        filename = os.path.basename(filepath)

        # Optional: Remove the .csv extension from the filename
        filename_without_extension = os.path.splitext(filename)[0]

        # Read the CSV file into a dataframe
        df = pd.read_csv(filepath)

        # Append the dataframe to the dictionary using its filename as its key
        dfs[filename_without_extension] = df

    # For reference, create a list of the key names of each dataframe appended
    keys_list = list(dfs.keys())

    return dfs, keys_list
