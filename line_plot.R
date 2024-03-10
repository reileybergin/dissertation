# packages ----

library(tidyverse)
library(readr)
library(viridis)
library(RColorBrewer)

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

# ploting ----


ggplot(model_data, aes(x = run_type, y = value, group = sub_id, color = sub_id)) +
  geom_line() +  # The aes color mapping is applied to lines
  geom_point() +  # The aes color mapping is applied to points as well
  
  # Create a facet grid by variable with free y scales
  facet_grid(rows = vars(variable), scales = "free_y") + 
  
  theme_bw() +  # Apply the black and white theme
  
  theme(legend.position = "bottom",  # Place legend at the bottom
        legend.title = element_blank(),  # Remove legend title
        text = element_text(size=12),  # Adjust global text size
        axis.title = element_text(face="bold"),  # Bold axis titles
        strip.text.x = element_text(face="bold")) +  # Bold facet labels
  
  labs(
    title = "",
    x = "",
    y = "",
  ) +
  
  scale_color_brewer(palette = "Paired")  












