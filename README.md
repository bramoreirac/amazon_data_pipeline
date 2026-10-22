# Amazon Product Data Pipeline

A learning-first data engineering project built around an Amazon product dataset. The goal is to understand each pipeline decision by building and validating the pipeline step by step—from profiling and cleaning to storage and analysis.

## Current status

The project currently includes:

- A [data contract](data_contract.md) and profiling workbook ([profiling_summary.xlsx](profiling_summary.xlsx)).
- Field-level cleaning functions and a row-level `transform_row()` function in [`etl_script.py`](etl_script.py).
- A CSV workflow that reads the raw file and writes cleaned rows to `outputs/clean_data.csv`.
- Unit tests for the cleaners and a representative transformed row in [`tests/test_etl_script.py`](tests/test_etl_script.py). The latest reported test run passed all 17 tests.

The full-file run is in progress. The latest reported counts are 2,576 raw rows and 2,519 cleaned rows. Since the current code does not intentionally filter rows, we are investigating this discrepancy and will verify counts using CSV records rather than physical lines or spreadsheet display counts.

## Dataset and generated files

The source file is `amazon_sales_data_uncleaned.csv`, with 16 source fields. Keep a local copy in the project root when working with the pipeline. The raw dataset and generated output are excluded from Git by `.gitignore`.

The cleaned output is written to `outputs/clean_data.csv`. Running the ETL script replaces that output file. The `outputs/` directory must exist before running the script.

## Requirements

- Python 3.10 or newer
- Python standard library only for the current CSV transformation and tests

## Run the tests

From the project root, run:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -p "test_etl_script.py"
```

The tests cover individual cleaners and a representative end-to-end row transformation. They do not process the full raw CSV.

## Run the CSV transformation

From the project root, run:

```powershell
.venv\Scripts\python.exe etl_script.py
```

This reads `amazon_sales_data_uncleaned.csv`, transforms its records one at a time, and writes the cleaned CSV to `outputs/clean_data.csv`. Processing one row at a time avoids keeping the entire dataset in memory.

## Learning roadmap

1. Reconcile the raw and cleaned CSV record counts; confirm that every source record is accounted for.
2. Add row counts, null summaries, and data-quality issue reporting.
3. Define a PostgreSQL table and load the validated cleaned data.
4. Compare database and CSV row counts, then practice SQL analysis.
5. Build a Streamlit dashboard connected to PostgreSQL to explore product, price, rating, coupon, and delivery insights.
6. Document a reproducible run from raw data through dashboard.

## Repository layout

```text
.
├── data_contract.md
├── etl_script.py
├── profiling_summary.xlsx
├── tests/
│   └── test_etl_script.py
├── outputs/                         # Generated files; excluded from Git
└── amazon_sales_data_uncleaned.csv  # Local source data; excluded from Git
```

`src/etl.py` and `tests/test_etl.py` are earlier reference drafts, excluded from Git while the learning implementation is developed in `etl_script.py`.
