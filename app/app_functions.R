library(tidyverse)
library(readxl)
library(raincloudplots)
library(cowplot)

df <- read_excel(
  "app/data/imu_training_load_variables.xlsx", sheet = "variables") %>%
  # keep only verified rows
  filter(verified != "n") %>%
  # drop verified column
  select(-c(verified, sensor))%>%
  # day number 
  mutate(day_num = case_when(
    run_type %in% c('light_prs_pre', 'light_prs_post', 'heavy_prs_pre', 'heavy_prs_post') ~ 'D5',
    TRUE ~ toupper(str_extract(run_type, "d\\d+"))
  )) %>%
  # week type
  mutate(run_week = case_when(
    str_detect(run_type, "^light") ~ "Light Week",
    str_detect(run_type, "^heavy") ~ "Heavy Week",
    TRUE ~ NA_character_
  )) %>%
  # arrange run_type based on custom order
  arrange(factor(run_type, levels = c("lightd1", "lightd2", "lightd3", "lightd4", "light_prs_pre", "light_prs_post", 
                                      "heavyd1_prs_pre", "heavyd1_prs_post", "heavyd2_prs_pre", "heavyd2_prs_post", 
                                      "heavyd3_prs_pre", "heavyd3_prs_post", "heavyd4_prs_pre", "heavyd4_prs_post", 
                                      "heavy_prs_pre", "heavy_prs_post")))


df_swc_indiv <- df %>%
  # Filter the data
  filter(run_type %in% c("light_prs_pre", "heavyd1_prs_pre")) %>%
  # Group by 'sub_id' and 'variable'
  group_by(sub_id, variable) %>%
  # Calculate standard deviation, SWC positive and negative
  summarise(
    avg = mean(value, na.rm = TRUE),
    sd = sd(value, na.rm = TRUE),
    swc = sd(value, na.rm = TRUE) * 0.2, 
    .groups = "keep"
  ) %>%
  # Create the new columns for lower and upper bound
  mutate(
    swc_upper_bound = avg + swc,
    swc_lower_bound = avg - swc
  )


# Functions ----

df_compare_run_types <- function(df, var, run_type_1, run_type_2, subjects) {
  
  df_filtered <- df %>%
    # Remove columns I don't need
    select(-c(day_num, run_week)) %>%
    # Filter data according to the inputs
    filter(sub_id %in% subjects, 
           variable == var, 
           run_type %in% c(run_type_1, run_type_2)) 
  
  # Pivot data so run_types are columns that contain values
  df_wide <- df_filtered %>%
    pivot_wider(names_from = run_type, values_from = value)
  
  # Add the new columns
  df_newcolumns <- df_wide %>%
    mutate(
      # The `sym()` function converts the values of run_type_1 and run_type_2
      # into symbols that represent the actual column names in the dataframe.
      # The `!!` operator unquotes these symbols so they're recognized as column names.
      # This allows for the use of the values of run_type_1 and run_type_2 as column names
      diff = round(!!sym(run_type_2) - !!sym(run_type_1), 3),
      # looking at the direction of change from run type 1 to run type 2
      direction = ifelse(diff > 0, "+", "-"),
      abs_diff = abs(diff)
    )
  
  return(df_newcolumns)
}

# plot for comparison tab
plot_compare_run_types <- function(df) {
  
  # Create table
  df_1x1 <- data_1x1(
    array_1 = df[[3]],
    array_2 = df[[4]],
    jit_distance = .09,
    jit_seed = 321)
  
  # Calculate the averages
  avg_col3 <- mean(df[[3]], na.rm = TRUE)
  avg_col4 <- mean(df[[4]], na.rm = TRUE)
  
  # Column names for table
  col3_name <- names(df)[3]
  col4_name <- names(df)[4]
  
  # Table for storing averages 
  average_tbl <- tibble(
    !!col3_name := avg_col3, 
    !!col4_name := avg_col4
  )
  
  # Create a raincloud plot
  p <- raincloud_1x1_repmes(
    data = df_1x1,
    colors = (c('dodgerblue', 'darkorange')),
    fills = (c('dodgerblue', 'darkorange')),
    line_color = 'gray',
    line_alpha = .3,
    size = 2,
    alpha = .6,
    align_clouds = TRUE) +
    
    # Add average points
    geom_point(aes(x = 1, y = avg_col3), color = "grey", size = 3, shape = 15, alpha = 0.25) +
    geom_point(aes(x = 2, y = avg_col4), color = "grey", size = 3, shape = 15, alpha = 0.25) +
    # Add dotted line
    geom_segment(aes(x = 1, y = avg_col3, xend = 2, yend = avg_col4), 
                 linetype = "dashed", color = "grey", alpha = 0.25) + 
    
    scale_x_continuous(breaks=c(1,2), labels=c(names(df)[3], names(df)[4]), limits=c(0.5, 3)) +
    xlab("") + 
    ylab("") +
    theme_cowplot() +
    ggtitle(df$variable[1]) +
    theme(
      axis.text.x = element_text(color = "black"),
      axis.text.y = element_text(color = "#525252")
    )
  
  return(p)
}

# plot for weekly facet plot

plot_weekly_values <- function(df) {
  
  # Create the summary dataframe with the bounds
  df_swc_indiv <- df %>%
    group_by(sub_id, variable) %>%
    summarise(
      avg = mean(value, na.rm = TRUE),
      sd = sd(value, na.rm = TRUE),
      swc = sd(value, na.rm = TRUE) * 1.0,
      .groups = "keep"
    ) %>%
    mutate(
      swc_upper_bound = avg + swc,
      swc_lower_bound = avg - swc
    )
  
  # Join the original dataframe with the summary dataframe
  df <- df %>%
    left_join(df_swc_indiv, by = c("sub_id", "variable"))
  
  # Filter out the post running assessments
  df <- df %>% 
    filter(!grepl("post$", run_type))
  
  ggplot(df, aes(x = day_num, y = value, group = interaction(sub_id, run_week), color = run_week)) +
    geom_point(alpha = 0.5) +
    geom_line(alpha = 0.5) +
    geom_line(aes(y = swc_upper_bound), linetype = "dotted", color = "darkgrey") +
    geom_line(aes(y = swc_lower_bound), linetype = "dotted", color = "darkgrey") +
    labs(x = "", y = "", color = "") +
    ggtitle(df$variable[1]) +
    scale_color_manual(
      values = c("Light Week" = "#006666", "Heavy Week" = "#990033"),
      breaks = c("Light Week", "Heavy Week"),
      labels = c("Light Week", "Heavy Week")
    ) +
    theme_cowplot() +
    facet_wrap(~sub_id) +
    theme(
      axis.text.x = element_text(color = "#525252"),
      axis.text.y = element_text(color = "#525252"),
      legend.position = "top",
      legend.justification = c(0.5, 1),
      legend.box.spacing = unit(0.5, "cm")
    ) 
}

# just need this test things out
df <- df %>%
  filter(variable == "control entropy")
