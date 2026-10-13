# Chapter 6 data: fresh illustrative data sets + the statistics each boxplot variant draws.
# Every number drawn in ch06.py is read from results/ch06_data.json (written here).
#   variable width : boxes ∝ sqrt(n)            (R ?boxplot, varwidth; McGill, Tukey & Larsen 1978)
#   notches        : median ± 1.58 IQR / sqrt(n) (R ?boxplot.stats; McGill et al. 1978, p. 16)
#   adjusted       : robustbase::adjboxStats, medcouple fences (Hubert & Vandervieren 2008)
#   letter values  : depth-based letter values M, F, E, D, C (Hofmann, Kafadar & Wickham)
#   same box       : four shapes forced to one five-number summary (type 7; n = 201 so quartiles are data points)
suppressMessages({library(jsonlite); library(robustbase)})
set.seed(2026)
out <- list(R = R.version.string, robustbase = as.character(packageVersion("robustbase")))

st <- function(x) { b <- boxplot.stats(x); list(stats = b$stats, n = b$n, conf = b$conf, out = b$out) }

# variable width: same population, very different n
vw <- lapply(c(12, 120, 1200), function(n) c(st(rnorm(n, 50, 10)), list(width = sqrt(n))))
out$varwidth <- vw

# notches: two groups whose boxes overlap; notches (≈95% median comparison) do not
g1 <- rnorm(60, 48, 10); g2 <- rnorm(60, 56, 10)
out$notch <- list(a = st(g1), b = st(g2))

# adjusted boxplot on right-skewed data (e.g. expression / concentration-like values)
sk <- rlnorm(200, log(20), 0.6)
std <- boxplot.stats(sk)
adj <- adjboxStats(sk)
out$adjusted <- list(x = sort(sk), mc = mc(sk),
                     standard = list(stats = std$stats, n_out = length(std$out), out = std$out),
                     adjusted = list(stats = adj$stats, fence = adj$fence, n_out = length(adj$out), out = adj$out))

# letter values for n = 10,000 (depths: M = (n+1)/2, then d_{k+1} = (floor(d_k) + 1)/2)
lv <- rnorm(10000, 50, 10); s <- sort(lv); n <- length(s)
d <- (n + 1) / 2; L <- list(); nm <- c("M", "F", "E", "D", "C", "B")
for (k in seq_along(nm)) {
  lo <- (s[floor(d)] + s[ceiling(d)]) / 2; hi <- (s[n + 1 - floor(d)] + s[n + 1 - ceiling(d)]) / 2
  L[[nm[k]]] <- list(depth = d, lower = lo, upper = hi)
  d <- (floor(d) + 1) / 2
}
out$letter <- list(n = n, values = L, standard_n_out = length(boxplot.stats(lv)$out))

# same box, different insides. Shapes are generated, then mapped piecewise-linearly so that
# min, Q1, median, Q3, max (type 7; n = 201 → positions 1, 51, 101, 151, 201) hit the same targets.
tgt <- c(20, 40, 50, 60, 80)
force5 <- function(x) {
  x <- sort(x); a <- c(x[1], x[51], x[101], x[151], x[201])
  approx(a, tgt, xout = x)$y
}
n <- 201
shapes <- list(
  uniform   = runif(n),
  bimodal   = c(rnorm(100, -1, 0.45), rnorm(101, 1, 0.45)),
  clustered = c(rnorm(67, -2, 0.08), rnorm(67, 0, 0.08), rnorm(67, 2, 0.08)),
  empty_mid = c(runif(50, -3, -1), runif(50, -1, -0.9), 0, runif(50, 0.9, 1), runif(50, 1, 3))  # gap around the median
)
out$samebox <- lapply(shapes, function(x) {
  y <- force5(x)
  list(x = y, q7 = unname(quantile(y, c(0, .25, .5, .75, 1), type = 7)), bstats = boxplot.stats(y)$stats,
       n_out = length(boxplot.stats(y)$out))
})
write_json(out, "results/ch06_data.json", digits = 8, auto_unbox = TRUE, pretty = TRUE)

cat("varwidth n:", sapply(vw, `[[`, "n"), "\n")
cat("notch a conf:", out$notch$a$conf, " b conf:", out$notch$b$conf, "\n")
cat("notch a box:", out$notch$a$stats[c(2, 4)], " b box:", out$notch$b$stats[c(2, 4)], "\n")
cat("adjusted: mc =", mc(sk), " standard outliers:", length(std$out), " adjusted outliers:", length(adj$out), "\n")
cat("  standard whiskers", std$stats[c(1, 5)], " adjusted whiskers", adj$stats[c(1, 5)], " fences", adj$fence, "\n")
cat("letter values:", sapply(L, function(z) sprintf("%.1f–%.1f", z$lower, z$upper)), " std outliers:", out$letter$standard_n_out, "\n")
for (k in names(out$samebox)) cat(k, ":", round(out$samebox[[k]]$q7, 4), "| boxplot.stats", round(out$samebox[[k]]$bstats, 3), "| out", out$samebox[[k]]$n_out, "\n")
