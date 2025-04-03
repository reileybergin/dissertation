library(shiny)
library(readxl)
library(tidyverse)
library(shinyWidgets)
library(raincloudplots)
library(cowplot)
library(reactable)

# Load Data ----

df <- read_excel(
  "data/imu_training_load_variables.xlsx", sheet = "variables") %>%
  # keep only verified rows
  #filter(verified != "n") %>%
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

# Functions ----

# table used in compare tab below plot
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

# plot for comparing two runs
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
    #ggtitle(df$variable[1]) +
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
    #ggtitle(df$variable[1]) +
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

# UI ----

ui <- 
  
  navbarPage("IMU TL",
             
             # Tab 1
             tabPanel("Comparison",
                      sidebarLayout(
                        sidebarPanel(
                          pickerInput(
                            "variable", "Variable:", 
                            choices = unique(df$variable), 
                            selected = unique(df$variable)[1], 
                            options = list(`live-search`=TRUE)),
                          pickerInput(
                            "run_type1", "Run Type 1:", 
                            choices = unique(df$run_type), 
                            selected = "light_prs_pre",
                            options = list(`live-search`=TRUE)),
                          pickerInput(
                            "run_type2", "Run Type 2:",
                            choices = unique(df$run_type), 
                            selected = "heavy_prs_pre",
                            options = list(`live-search`=TRUE)),
                          pickerInput(
                            "sub_id",
                            "Subjects:",
                            choices = unique(df$sub_id),
                            options = list(`actions-box` = TRUE),
                            multiple = TRUE,
                            selected = unique(df$sub_id)),
                          downloadButton("downloadDataComparison", "Export Data")
                        ),
                        mainPanel(
                          plotOutput("plot_compare"),
                          reactableOutput("table_compare")
                        )
                      )
             ),
             # Tab 2
             tabPanel("Weekly",
                      sidebarLayout(
                        sidebarPanel(
                          pickerInput(
                            "variable_wkly", "Running Variable:", 
                            choices = unique(df$variable), 
                            selected = unique(df$variable)[1], 
                            options = list(`live-search`=TRUE)),
                          pickerInput(
                            "sub_id_wkly",
                            "Subjects:",
                            choices = unique(df$sub_id),
                            options = list(`actions-box` = TRUE),
                            multiple = TRUE,
                            selected = unique(df$sub_id))
                        ),
                        mainPanel(
                          plotOutput("plot_weekly"),
                        )
                      )
             )
  )

# Server ----

server <- function(input, output, session) {

# Reactive expression for creating comparison table ---
  comparison_tbl <- reactive({
    df_compare_run_types(df, 
                         input$variable, 
                         input$run_type1, 
                         input$run_type2, 
                         input$sub_id)
  })

# Plot for comparing run types ---
  output$plot_compare <- renderPlot({
    plot_compare_run_types(comparison_tbl())
  }, res = 96, width = 550)
  
# Reactive expression for filtered table on weekly tab ---
  filtered_tbl <- reactive(
    df %>% filter(
    variable == input$variable_wkly, 
    sub_id %in% input$sub_id_wkly))  
  
# Plot for weekly values ---
  output$plot_weekly <- renderPlot({
    plot_weekly_values(filtered_tbl())
  }, res = 96, height = 600)
  
# Reactable Table ---

  output$table_compare <- renderReactable({
    
    df <- comparison_tbl() %>%
      select(-variable) %>%
      mutate(across(.cols = c(2,3), .fns = ~round(., 3))) %>%
      select(-direction, everything(), direction) %>%
      arrange(desc(abs_diff))
    
    averages <- df %>%
      summarise(across(where(is.numeric), ~mean(., na.rm = TRUE))) %>%
      mutate(across(everything(), ~round(., 3))) %>%
      mutate(sub_id = "AVG")
    
    df <- 
      bind_rows(df, averages) %>%
      # need to re-calculate this to have this show up for average
      mutate(direction = ifelse(diff > 0, "+", "-")) %>%
      select(-abs_diff)
 
    # Color scale functions
    BuYlRd <- function(x) rgb(colorRamp(c("#E6E6FA", "#b77fd7"))(x), maxColorValue = 255)
    
    colorRampNeg <- colorRamp(c("white", "#F78888"))  # Red gradient for negative
    colorRampPos <- colorRamp(c("white", "#88D498"))  # Green gradient for positive
    
    BuYlRdNeg <- function(x) rgb(colorRampNeg(abs(x)), maxColorValue = 255) # Function for negative values
    BuYlRdPos <- function(x) rgb(colorRampPos(abs(x)), maxColorValue = 255) # Function for positive values
    
    df %>%
      reactable(
        defaultColDef = colDef(
          header = function(value) gsub(".", " ", value, fixed = TRUE),
          cell = function(value, rowIndex) {
            style <- if (rowIndex == nrow(df)) {
              list(fontWeight = "bold")
            } else {
              list()
            }
            htmltools::tags$div(style = style, value)
          },
          align = "center",
          minWidth = 110,
          headerStyle = list(background = "#f7f7f8")
        ),
        
        columns = list(
          
          sub_id = colDef(minWidth = 50),
          
          diff = colDef(
            style = function(value) {
              if (!is.numeric(value) || is.na(value)) return()
              if (value < 0) {
                normalized <- abs(value) / max(abs(df$diff[df$diff < 0]), na.rm = TRUE)
                color <- BuYlRdNeg(normalized)
              } else {
                normalized <- value / max(df$diff[df$diff > 0], na.rm = TRUE)
                color <- BuYlRdPos(normalized)
              }
              list(background = color)
            }
          ),
          
          abs_diff = colDef(
             style = function(value) {
              if (!is.numeric(value) || is.na(value)) return()
               normalized <- (value - min(df$abs_diff, na.rm = TRUE)) / 
                 (max(df$abs_diff, na.rm = TRUE) - min(df$abs_diff, na.rm = TRUE))
               color <- BuYlRd(normalized)
               list(background = color)
             }
           ),
          
          direction = colDef(
            minWidth = 70,
            style = function(value) {
              color <- "#777" # Default to gray color
              if (is.na(value)) return()
              if (value == "+") {
                color <- "#88D498"
              } else if (value == "-") {
                color <- "#F78888"
              } 
              list(color = color, fontWeight = "bold")
            }
          )
          
        ),
        bordered = TRUE,
        highlight = TRUE
      )
  })
  
  
  

}

# Run the application 
shinyApp(ui = ui, server = server)
