# Chapter 7 data: fresh illustrative data sets; every number drawn in ch07.py is read from
# results/ch07_data.json (written here).
#   same_box : four whole-distribution shapes forced to one five-number summary (type 7, n = 201)
#   n_hidden : n = 9 and n = 9001 with the same five numbers (type 7 positions are exact data points)
#   ch3_echo : Chapter 3's eight values; Tukey hinges (base R boxplot) vs type 7 (ggplot2 / matplotlib)
#   compare  : twelve groups for the "compact comparison" small multiple
suppressMessages(library(jsonlite))
set.seed(7077)
out <- list(R = R.version.string)
tgt <- c(15, 40, 50, 60, 85)
force5 <- function(x) {                      # piecewise-linear, monotone: shape kept, five numbers fixed
  x <- sort(x); n <- length(x); h <- (n - 1) * c(0, .25, .5, .75, 1) + 1
  approx(x[h], tgt, xout = x)$y
}
q7 <- function(y) unname(quantile(y, c(0, .25, .5, .75, 1), type = 7))
shapes <- list(
  one_peak  = rnorm(201),
  two_peaks = c(rnorm(100, -2, 0.5), rnorm(101, 2, 0.5)),
  flat      = runif(201),
  lumpy     = c(rnorm(40, -2.2, 0.06), rnorm(40, -0.9, 0.06), rnorm(41, 0, 0.06), rnorm(40, 1.1, 0.06), rnorm(40, 2.4, 0.06))
)
out$same_box <- lapply(shapes, function(x) { y <- force5(x); list(x = y, q7 = q7(y), n_out = length(boxplot.stats(y)$out)) })

small <- force5(rnorm(9)); big <- force5(rnorm(9001))
out$n_hidden <- list(small = list(x = small, q7 = q7(small)), big = list(x = big, q7 = q7(big)))

x <- c(1, 2, 4, 7, 8, 10, 13, 23)
h <- boxplot.stats(x); q <- unname(quantile(x, c(.25, .75), type = 7)); iqr <- diff(q)
out$ch3_echo <- list(x = x,
  hinges = list(q1 = h$stats[2], q3 = h$stats[4], upper_fence = h$stats[4] + 1.5 * (h$stats[4] - h$stats[2]), out = h$out),
  type7  = list(q1 = q[1], q3 = q[2], upper_fence = q[2] + 1.5 * iqr, out = x[x > q[2] + 1.5 * iqr]))

cmp <- lapply(1:12, function(i) boxplot.stats(rnorm(40, 50 + 6 * sin(i / 2), 6 + (i %% 4)))$stats)
out$compare <- cmp
write_json(out, "results/ch07_data.json", digits = 8, auto_unbox = TRUE, pretty = TRUE)

for (k in names(out$same_box)) cat(k, round(out$same_box[[k]]$q7, 4), "out:", out$same_box[[k]]$n_out, "\n")
cat("n=9   ", round(out$n_hidden$small$q7, 4), "\nn=9001", round(out$n_hidden$big$q7, 4), "\n")
str(out$ch3_echo)
