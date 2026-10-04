# The Banana Apocalypse? Let's Investigate with Genomics and Code

This repository contains computational material accompanying the BioCodeTalks video **"The Banana Apocalypse? Let's Investigate with Genomics and Code."**

The project started with a simple question: are bananas really heading towards an "apocalypse"? The investigation led through banana evolution, triploidy, comparative genomics, orthology, Panama disease, disease resistance, and banana production in India.

## What is included

### OMA comparative genomics

`code/oma/`

Queries the OMA orthology database to examine orthologous relationships between human and banana genes and several additional species.

The human-banana analysis used in the video returned:

- 13,522 human-banana ortholog pairs
- 3,683 human genes with at least one banana ortholog
- 20,430 human main-isoform genes in the OMA snapshot
- 18.0% of human genes with a banana ortholog

The repository includes the cached OMA snapshot used for the analysis under `data/oma/cache/` and derived tables under `results/oma/`.

OMA is a continuously maintained database. Results from a future live query may therefore differ from the frozen snapshot included here.

### FAOSTAT banana production

`code/production/`

Reproduces the production statistics and figures used in the India section of the video.

For 2024, the dataset used here gives:

- India: 37.61 million tonnes
- World: 139.41 million tonnes
- India share: 26.98%

The input snapshot is stored under `data/faostat/`, derived tables under `results/faostat/`, and generated figures under `figures/`.

### Triploidy toy simulation

`code/triploidy/triploid_meiosis_sim.py`

A deliberately simplified simulation used to illustrate why chromosome segregation is difficult in a triploid organism.

For 11 chromosome types with three copies of each, the toy model treats a gamete as "balanced" only when all chromosome types segregate consistently to the same copy-number state.

`P(balanced) = 2 / 2^11 ≈ 0.0977%`

or approximately 1 in 1,024.

This is an educational toy model, **not a quantitative model of real banana meiosis or fertility**. Real meiotic behaviour is substantially more complicated.

### Manim source

`manim/`

Source code for selected scientific animations used in the project.

## Reproducing the analyses

Install the dependencies from the repository root:

```bash
pip install -r requirements.txt
```

Then enter the project directory:

```bash
cd banana_apocalypse
```

Triploidy simulation:

```bash
python code/triploidy/triploid_meiosis_sim.py
```

FAOSTAT analyses:

```bash
python code/production/fao_production.py
python code/production/fao_v2.py
```

Short live OMA query:

```bash
python code/oma/how_much_banana.py
```

Full comparative analysis:

```bash
python code/oma/oma_orthologs.py
```

The full OMA analysis can make many requests to the public OMA REST API. Cached data are included to preserve the snapshot used for the video and reduce unnecessary repeated downloads.

## Repository structure

```text
banana_apocalypse/
├── code/       analysis scripts
├── data/       input data and frozen API snapshots
├── figures/    generated figures
├── manim/      animation source
├── results/    derived analysis outputs
└── sources/    source and reference documentation
```

## Notes

The analyses here were created for scientific communication and reproducibility around the accompanying video. Simplified demonstrations are identified as such and should not be interpreted as substitutes for the primary literature.

Third-party datasets and resources remain subject to their original licenses and terms.
