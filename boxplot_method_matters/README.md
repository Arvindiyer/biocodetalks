# Same Data, Different Boxplot? | Method Matters

This repository contains code and reproducible material accompanying the BioCodeTalks video **"Same Data, Different Boxplot? | Method Matters."**

The episode explores how the same dataset can produce different boxplots depending on methodological choices such as quartile definitions, hinges, whisker rules, exact quantile algorithms, and approximate quantile sketches.

## What is included

### Quantile algorithms
`code/quantile_algorithms/`

Benchmark comparing full sorting with partition-based selection.

Frozen output: `results/selection_benchmark.json`

### Quantile sketches
`code/quantile_sketches/`

Experiments illustrating approximate quantile estimation with streaming sketches.

Frozen output: `results/sketches.json`

Python dependency: `datasketches`

### Boxplot evolution
`code/boxplot_evolution/`

R code used for the boxplot-evolution examples, including adjusted boxplots based on medcouple statistics.

R dependencies: `jsonlite`, `robustbase`

Frozen output: `results/ch06_data.json`

### What boxplots hide
`code/what_boxplots_hide/`

R code used for examples showing how boxplots can hide distributional structure and how methodological choices affect the displayed summary.

R dependency: `jsonlite`

Frozen output: `results/ch07_data.json`

### Manim source
`manim/scenes/`

Source for the seven visual chapters used in the episode. Rendered videos, audio, transcripts, build caches, and production files are intentionally excluded.

## Reproducing the Python analyses

From the repository root:

```bash
pip install -r requirements.txt
cd boxplot_method_matters
python code/quantile_algorithms/benchmark.py
python code/quantile_sketches/sketch_experiments.py
```

## Reproducing the R analyses

Install the required packages:

```r
install.packages(c("jsonlite", "robustbase"))
```

Then run:

```bash
Rscript code/boxplot_evolution/make_data.R
Rscript code/what_boxplots_hide/make_data.R
```

## Repository structure

```text
boxplot_method_matters/
├── code/
├── data/
├── figures/
├── manim/
│   └── scenes/
├── results/
└── README.md
```

## Notes

This is a reproducible companion to the BioCodeTalks episode, not a standalone statistical software package.

Some examples are deliberately simplified for explanation. Third-party software and references remain subject to their original licenses and terms.
