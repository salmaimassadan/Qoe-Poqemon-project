# Report

LaTeX source of the project report. `main.pdf` is the compiled version.

| File | Content |
|---|---|
| `main.tex` | Report text |
| `references.bib` | Bibliography |
| `make_tables.py` | Generates `tables/*.tex` from `../results/*.csv` |
| `tables/` | Generated result tables (do not edit by hand) |

Figures are read directly from `../figures/`, which the notebook generates.

## Build

1. Execute the notebook (see the repository README) so that `figures/` and `results/` are up to date.
2. From the repository root, regenerate the tables:
   ```bash
   python report/make_tables.py
   ```
3. Compile, e.g. with [Tectonic](https://tectonic-typesetting.github.io) (`brew install tectonic`):
   ```bash
   cd report && tectonic main.tex
   ```
   Any LaTeX distribution also works (`latexmk -pdf main.tex`). On Overleaf, upload `report/` together
   with `figures/` and change `\graphicspath` in `main.tex` to `{figures/}`.
