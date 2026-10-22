# Amazon Product Data Pipeline

A learning-first data engineering project built around a scraped Amazon product dataset. The goal is to understand each pipeline decision and implement it step by step, from profiling and cleaning through validation and storage.

## Project status

The project is currently at the field-level transformation stage. `etl_script.py` contains cleaning functions for individual fields, including titles, ratings, review counts, purchase lower bounds, prices, badges, coupons, delivery details, URLs, and collection timestamps.

The next learning milestone is to combine those functions into a row-level transformation. CSV reading and writing, a complete validation report, and a database load have not yet been integrated into the learner-authored pipeline.

## Dataset

The source dataset is named `amazon_sales_data_uncleaned.csv`. It contains 42,675 product observations and 16 source fields. Keep a local copy in the project root when working with the data. The raw dataset and generated files are excluded from Git by `.gitignore`.

The source-to-target decisions and data-quality rules are documented in [`data_contract.md`](data_contract.md). The profiling workbook is [`profiling_summary.xlsx`](profiling_summary.xlsx).

## Requirements

- Python 3.10 or newer
- Python standard library only for the current field-cleaning exercises

## Working with the cleaning functions

Open `etl_script.py` in a Python IDE or run focused experiments from its Python console. The script is a practice module at this stage, not yet a complete command-line pipeline. As you implement each transformation, add assertions for normal values, missing values, malformed values, and relevant boundaries.

For example, after importing a function in a Python console:

```python
from etl_script import clean_rating

assert clean_rating("4.6 out of 5 stars") == 4.6
assert clean_rating("6.2 out of 5 stars") is None
```

## Planned milestones

1. Complete and review the individual field transformations.
2. Build `transform_row()` and test it with representative source rows.
3. Read the source CSV and write cleaned output while preserving traceability.
4. Add row counts, null summaries, and validation issue reporting.
5. Load the cleaned data into a database and practice SQL analysis.
6. Document how to run the finished pipeline and reproduce its outputs.

## Repository contents

```text
.
├── data_contract.md
├── etl_script.py
├── profiling_summary.xlsx
├── src/                  # Earlier pipeline draft; currently excluded from Git
├── tests/                # Earlier tests; currently excluded from Git
├── outputs/              # Generated files; excluded from Git
└── amazon_sales_data_uncleaned.csv  # Local source data; excluded from Git
```

The `src/etl.py` and `tests/test_etl.py` files are earlier reference drafts and are excluded from Git while the learning implementation is being developed in `etl_script.py`.
