# File Compression Experiment

Compare gzip levels 1 and 9 on 50 text files using paired statistical tests.

## Folders

- `scripts/`: Python code
- `data/raw/`: original books
- `data/compressed/`: level 1 and level 9 outputs
- `data/processed/`: measurements for analysis

## Setup

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Start

- `power_analysis.py`: calculates the planned paired t-test sample size and simulates Wilcoxon power under stated assumptions.
- `download_files.py`: selects and downloads books from Project Gutenberg and saves their source information.
- `compress_files.py`: compresses each book at levels 1 and 9, checks that both restore the original, and records sizes and percentages.
- `analyze_results.py`: summarizes the results, creates assumption-check plots, and runs the Wilcoxon and paired t-tests.

```sh
python scripts/power_analysis.py
python scripts/download_files.py
python scripts/compress_files.py
python scripts/analyze_results.py
```

Change `NUM_BOOKS = 50` at the top of `scripts/download_files.py` to get more
books. Rerunning reuses existing downloads and adds books from the same saved
catalog. Use `data/sources.csv` as the list of selected files for analysis.
If a download fails, the script stops. Run it again to reuse saved files.

Compression results are saved in `data/processed/compression_results.csv`.
Percentages show compressed size relative to original size. A positive
`difference_pp` means level 9 saved more space.

The analysis saves `analysis_results.txt` and `difference_checks.png` in
`data/processed/`. Wilcoxon is the primary reported test, with the originally
planned paired t-test as a secondary analysis. We selected Wilcoxon after
observing skew; its symmetry assumption remains a limitation. Both tests
assume independent book pairs. The supplementary Wilcoxon power estimate
uses hypothetical symmetric differences, not the observed data.
