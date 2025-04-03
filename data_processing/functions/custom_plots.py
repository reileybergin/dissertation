"""
Functions for Plots
"""
# Packages ---
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Line Plot w/ Plotly ---

# Creates line plots for each dataframe in a dictionary and stores them in another dictionary


def create_line_plots(dfs, x_col, y_cols, color_discrete_sequence=px.colors.qualitative.Set2):
    # Create a dictionary to store the plots
    plots = {}

    grid_color = '#EBEBEB'

    for key in dfs.keys():
        df = dfs[key]

        # Create line plot of res_acc_g, az_g, and ay_g vs. time_s
        fig = px.line(df, x=x_col, y=y_cols, title=key,
                      color_discrete_sequence=color_discrete_sequence)

        # Update the plot's axis labels
        fig.update_xaxes(title_text='Time (s)')
        fig.update_yaxes(title_text='Acceleration')

        # Set the plot's background color to white
        fig.update_layout(plot_bgcolor='white')

        # Set the axis/grid lines color
        fig.update_xaxes(linecolor=grid_color)
        fig.update_yaxes(linecolor=grid_color)
        fig.update_xaxes(gridcolor=grid_color)
        fig.update_yaxes(gridcolor=grid_color)

        # Save the plot as a variable in the dictionary
        plots[key] = fig

    return plots


# Line Plot w/ Seaborn ---

def create_line_plots_seaborn(dfs, x_col, y_cols, color_palette='Set2', fig_width=12, fig_height=6):
    # Create a dictionary to store the plots
    plots = {}

    for key in dfs.keys():
        df = dfs[key]

        # Create a figure and axes with specified width
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))

        # Define the color palette
        palette = sns.color_palette(color_palette, len(y_cols))

        # Create line plot for each y column
        for i, y_col in enumerate(y_cols):
            sns.lineplot(data=df, x=x_col, y=y_col, ax=ax,
                         color=palette[i], label=y_col)

        # Set the plot's labels
        ax.set_title(key)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Acceleration')

        # Add legend at the bottom
        ax.legend(loc='upper center', bbox_to_anchor=(
            0.5, -0.15), shadow=True, ncol=len(y_cols))

        # Save the plot as a variable in the dictionary
        plots[key] = fig

    return plots

# For IMU Validation


def plot_trial_data(dfs_trials_separate, trial_number, column_name, timestamp_column='timestamp', offset_windows_df=None):
    # Retrieve the dataframes for the specified trial
    trial_dfs = dfs_trials_separate[trial_number]

    # Create a subplot
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Colors for each IMU location
    color_map = {
        'right_tibia': 'red',
        'low_back': 'blue',
        'left_tibia': 'green'
    }

    for key, df in trial_dfs.items():
        # Check if the specified column exists in the dataframe
        if column_name in df.columns and timestamp_column in df.columns:
            # Extract the body_part from the key
            parts = key.split('_')
            body_part = '_'.join(parts[6:8])  # Correctly extract the body_part

            # Determine the color based on the body_part
            # Default color is gray if body_part is not found
            color = color_map.get(body_part, 'gray')

            # Add a trace for each dataframe
            # Using the timestamp column of the dataframe for the x-axis
            fig.add_trace(
                go.Scatter(x=df[timestamp_column], y=df[column_name],
                           mode='lines', name=key, line=dict(color=color)),
                secondary_y=False,
            )

            # If offset_windows_df is provided and contains the current df_id
            if offset_windows_df is not None and key in offset_windows_df['df_id'].values:
                window_data = offset_windows_df[offset_windows_df['df_id'] == key]
                window_start_time = window_data['window_start_timestamp'].values[0]
                window_end_time = window_data['window_end_timestamp'].values[0]

                # Determine the color for the vertical lines based on the body part
                line_color = color_map.get(body_part, 'gray')

                # Add vertical lines for the start and end window
                fig.add_shape(type='line',
                              x0=window_start_time, y0=0,
                              x1=window_start_time, y1=1,
                              xref='x', yref='paper',
                              line=dict(color=line_color, width=2, dash='dot'))

                fig.add_shape(type='line',
                              x0=window_end_time, y0=0,
                              x1=window_end_time, y1=1,
                              xref='x', yref='paper',
                              line=dict(color=line_color, width=2, dash='dot'))

    # Update plot layout
    fig.update_layout(
        title=f'Trial {trial_number} - {column_name}',
        xaxis_title='Timestamp',
        yaxis_title=column_name
    )

    # Show the plot
    fig.show()
