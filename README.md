# Overview

This repository contains code for analyzing running data collected using inertial measurement units (IMUs) located on the left tibia, right tibia, and lower back.

## Repository Structure

- `data_processing/`: Python scripts for processing IMU data
- `statistical_analysis/`: R scripts for statistical analysis of processed data
- `shiny_app/`: Interactive R Shiny application to visualize results

## Python Environment Setup

### Requirements

This project uses Python for data processing (imu feature extraction). The code was last tested with Python 3.11.3.

### Installation

1. Clone this repository to your local machine
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

The requirements.txt file includes the following key packages:
- pandas
- numpy
- matplotlib
- plotly
- scipy
- nolds (for entropy calculations)

## R Environment Setup

### RStudio Setup

1. In the upper right of the GitHub repository page, select the green "Code" button and copy the HTTPS link
2. Open RStudio and click on "File" > "New Project"
3. In the "New Project" window, select "Version Control" > "Git"
4. In the "Repository URL" field, enter the URL you copied in Step 1
5. Choose the directory where you want to save your project
6. Click on "Create Project". RStudio will automatically clone this GitHub repository to your local machine and create a new RStudio project based on the files in this repository

### Package Management

This project uses the package manager [renv](https://rstudio.github.io/renv/index.html) for reproducible environments. For more information on collaborating with renv [click here](https://rstudio.github.io/renv/articles/collaborating.html).

After the project has been cloned, install the renv package by running the following command:
```r
install.packages("renv")
```

Once the package has been installed run the command:
```r
renv::init()
```

Following this command you should see the following prompt:
*This project already has a lockfile. What would you like to do?*
- 1: Restore the project from the lockfile.
- 2: Discard the lockfile and re-initialize the project.
- 3: Activate the project without snapshotting or installing any packages.
- 4: Abort project initialization.

Choose **Option 1**, this will install all the packages and appropriate versions needed to run the code in this project.

The main R packages used in this project include:
- tidyverse
- brms (Bayesian regression models)
- lme4 (linear mixed effects models)
- easystats
- ggplot2
- shiny

## Data Setup and Processing

### Data Structure
This repository is designed to work with data located in the folder **data/**. While the data files are not included in the repository, here's how to set up the data for processing:

1. Create a `data` folder at the root level of the repository
2. Organize your raw IMU data files within the data folder using the following structure:
   ```
   data/
   ├── five_min_runs/
   │   ├── [subject_id]/
   │   │   ├── lowg_1125hz/
   │   │   │   ├── back/
   │   │   │   ├── left_tibia/
   │   │   │   └── right_tibia/
   │   │   └── highg_1600hz/
   │   │       ├── back/
   │   │       ├── left_tibia/
   │   │       └── right_tibia/
   │   └── [another_subject_id]/
   │       └── ...
   ├── validity_og/
   │   └── ...
   └── processed_variables/
       └── imu_training_load_variables.xlsx
   ```

3. Place your raw IMU CSV files in the appropriate subject/sensor location folders

### Processing Steps

1. Python notebooks in the `data_processing/` folder:
   - Run `ch.3_tibia_imu_val.ipynb`, `ch.3_low_back_imu_val.ipynb` for validation study data
   - Run `ch.4_tibia.ipynb`, `ch.4_low_back.ipynb`, and `ch.4_control_entropy.ipynb` for imu training load study
   - Run `ch.4_heart_rate.ipynb` for heart rate data

2. The processed data will be saved to `data/processed_variables/imu_training_load_variables.xlsx`

3. Use the R scripts in `statistical_analysis/` to analyze the processed data:
   - Run `ch.3_analysis.qmd` for validation and reliability analysis
   - Run `ch4_analysis.qmd` for imu training load study analysis

4. Visualize results using the Shiny app in `shiny_app/` by running:
   ```r
   shiny::runApp("shiny_app")
   ```

## Contact

For questions about this repository, please contact reiley.bergin@uky.edu
