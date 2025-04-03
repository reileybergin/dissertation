# packages ----
library(easystats)
library(effsize)
library(readxl)

# data ----
run <- read_excel("data/right_vs_left.xlsx", sheet = "run_both_time_pts")
walk <- read_excel("data/right_vs_left.xlsx", sheet = "walk_both_time_pts")

run_t1 <- read_excel("data/right_vs_left.xlsx", sheet = "run_time1")
walk_t1 <- read_excel("data/right_vs_left.xlsx", sheet = "walk_time1")


run_t2 <- read_excel("data/right_vs_left.xlsx", sheet = "run_time2")
walk_t2 <- read_excel("data/right_vs_left.xlsx", sheet = "walk_time2")

# paried t-test ----

# running
ttest_run <- t.test(run[["left"]], run[["right"]], paired = TRUE)
d_run <- cohen.d(run[["left"]], run[["right"]], paired = TRUE)

ttest_run_t1 <- t.test(run_t1[["left"]], run_t1[["right"]], paired = TRUE)
d_run_t1 <- cohen.d(run_t1[["left"]], run_t1[["right"]], paired = TRUE)

ttest_run_t2 <- t.test(run_t2[["left"]], run_t2[["right"]], paired = TRUE)
d_run_t2 <- cohen.d(run_t2[["left"]], run_t2[["right"]], paired = TRUE)


# walking
ttest_walk <- t.test(walk[["left"]], walk[["right"]], paired = TRUE)
d_walk <- cohen.d(walk[["left"]], walk[["right"]], paired = TRUE)

ttest_walk_t1 <- t.test(walk_t1[["left"]], walk_t1[["right"]], paired = TRUE)
d_walk_t1 <- cohen.d(walk_t1[["left"]], walk_t1[["right"]], paired = TRUE)

ttest_walk_t2 <- t.test(walk_t2[["left"]], walk_t2[["right"]], paired = TRUE)
d_walk_t2 <- cohen.d(walk_t2[["left"]], walk_t2[["right"]], paired = TRUE)


