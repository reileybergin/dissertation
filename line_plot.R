# packages ----

library(tidyverse)
library(readr)
library(viridis)
library(RColorBrewer)
library(datawizard)

# data prep ----

imu_data <- read_csv("data/ch.4_imu_data.csv") %>%
  
  # Remove the two subjects who did not complete heavy week 
  filter(sub_id != "run007", sub_id != "run008") %>%
  
  # Clean up variable names; lb = low back, tb = tibia
  mutate(
    variable = str_replace_all(variable, c(
      "ax_m/s/s_meanshift_filtered_rms_1125hz_ratio" = "lb_x_rms_ratio",
      "ay_m/s/s_meanshift_filtered_rms_1125hz_ratio" = "lb_y_rms_ratio",
      "az_m/s/s_meanshift_filtered_rms_1125hz_ratio" = "lb_z_rms_ratio", 
      "control entropy" = "lb_control_entropy",
      "res_g_avg_peak_lt_1600hz" = "lt_res_pk_accel_g",
      "res_g_avg_peak_rt_1600hz" = "rt_res_pk_accel_g",
      "res_g_avg_peak_back_1125hz" = "lb_res_pk_accel_g"))) 

# Calculate avg for left and right tibia
rt_lt_avg <- imu_data %>%
  filter(variable %in% c("lt_res_pk_accel_g", "rt_res_pk_accel_g")) %>%
  group_by(sub_id, run_type) %>%
  
  # NOTE: if subject is missing rt or lt then mean is just available value
  summarize(rt_lt_avg_res_pk_accel_g = mean(value, na.rm = TRUE), .groups = 'drop') %>%
  
  mutate(
    variable = "tb_res_pk_accel_g", 
    value = rt_lt_avg_res_pk_accel_g) %>%
  select(sub_id, run_type, variable, value)

# Append the original dataset
imu_data <- bind_rows(imu_data, rt_lt_avg) %>%
  filter(!variable %in% c("lt_res_pk_accel_g", "rt_res_pk_accel_g")) %>%
  arrange(sub_id, run_type, variable)

rm(rt_lt_avg)

# Calculate average values for LD5 and HD1, and label them as BAS
bas_avg <- imu_data %>%
  filter(run_type %in% c("LD5", "HD1")) %>%
  group_by(sub_id, variable) %>%
  summarize(mean_value = mean(value, na.rm = TRUE), .groups = 'drop') %>%
  mutate(run_type = "BAS", 
         value = mean_value) %>%
  select(sub_id, run_type, variable, value)

# Append the BAS averages back to the original dataset
model_data <- bind_rows(imu_data, bas_avg) %>%
  arrange(sub_id, run_type, variable)
rm(bas_avg)

# Remove light days and heavy D1 (part of baseline calc)
model_data <- model_data %>%
  filter(!str_starts(run_type, "LD")& run_type != "HD1")

# Convert sub_id and run_type column values to factors
model_data <- model_data %>%
  mutate(
    run_type = factor(run_type, levels = c("BAS", "HD2", "HD3", "HD4", "HD5")),
    sub_id = factor(sub_id)
  )

# Plot data 

plot_data <- model_data %>%
  mutate(
    # Update sub_id
    sub_id = str_replace_all(sub_id, c(
      "run001" = "Sub01",
      "run002" = "Sub02",
      "run004" = "Sub03",
      "run005" = "Sub04",
      "run006" = "Sub05",
      "run009" = "Sub06",
      "run010" = "Sub07",
      "run012" = "Sub08",
      "run013" = "Sub09",
      "run014" = "Sub10"
    )),
    
    # Update variable names
    variable = str_replace_all(variable, c(
      "tb_res_pk_accel_g" = "Tibia Pk Accel",
      "lb_res_pk_accel_g" = "LB Pk Accel",
      "lb_x_rms_ratio" = "RMS Ratio X",
      "lb_y_rms_ratio" = "RMS Ratio Y",
      "lb_z_rms_ratio" = "RMS Ratio Z", 
      "lb_control_entropy" = "Control Entropy"
    )),
    
    # Update variable order
    variable = factor(variable, levels = c(
      "Tibia Pk Accel",
      "LB Pk Accel",
      "RMS Ratio X",
      "RMS Ratio Y",
      "RMS Ratio Z",
      "Control Entropy"
    ))
  )


# Standardize values for each variable

plot_data <- plot_data %>%
  group_by(variable) %>%
  mutate(value = as.numeric(standardize(value))) %>%
  ungroup()


# ploting ----

plot_1 <- ggplot(plot_data, aes(x = run_type, y = value, group = sub_id, color = sub_id)) +
  geom_line(linewidth=0.65, alpha=0.75) +  # Adjust line width and add transparency
  geom_point(alpha=0.75) +
  facet_wrap(~variable, ncol = 2) +  # Use 2 columns for the facets
  theme_bw() +  
  theme(legend.position = "right",  # Place legend at the bottom
        legend.title = element_blank(),  # Remove legend title
        text = element_text(size=10),  # Adjust global text size
        axis.title = element_text(face="bold"),  # Bold axis titles
        strip.text.x = element_text(face="bold"),  # Bold facet labels
        panel.spacing.y = unit(1, "lines"),  # Adjust space between rows
        panel.spacing.x = unit(1, "lines")) +  # Adjust space between columns
  labs(
    title = "",
    x = "",
    y = "",
  ) +
  scale_color_brewer(palette = "Paired")

plot_1

# save as PNG 
ggsave("ch.4_results/plots/plot_1.png", plot = plot_1, width = 8, height = 6, dpi = 300)










