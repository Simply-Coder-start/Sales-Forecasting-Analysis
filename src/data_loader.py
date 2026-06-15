"""
01_data_loading_and_inspection.py
=================================
Rossmann Store Sales — Data Loading, Schema Inspection, Merge & Data Dictionary

Uses only Python standard library (csv module) — no pandas required.

Purpose
-------
- Load train.csv and store.csv
- Analyze schema, data types, row/column counts, and column meanings
- Merge datasets on the correct key (Store)
- Produce a comprehensive data dictionary
- NO cleaning, NO EDA, NO feature engineering
"""

import csv
import os
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


# ──────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def load_csv(filepath):
    """Load a CSV file and return (header, rows) where rows is a list of dicts."""
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames
        rows = list(reader)
    return header, rows


def infer_dtype(values):
    """Infer the dominant data type from a list of non-empty string values."""
    if not values:
        return "empty"
    int_count = 0
    float_count = 0
    for v in values:
        try:
            int(v)
            int_count += 1
            continue
        except ValueError:
            pass
        try:
            float(v)
            float_count += 1
            continue
        except ValueError:
            pass
    total = len(values)
    if int_count == total:
        return "int"
    elif (int_count + float_count) == total:
        return "float"
    else:
        return "str"


def column_stats(rows, col):
    """Compute statistics for a single column."""
    total = len(rows)
    non_empty = [r[col] for r in rows if r[col] is not None and r[col].strip() != ""]
    null_count = total - len(non_empty)
    unique_vals = sorted(set(non_empty))
    n_unique = len(unique_vals)
    dtype = infer_dtype(non_empty[:5000])  # sample for speed
    if n_unique <= 15:
        sample = unique_vals
    else:
        sample = unique_vals[:10]
    return {
        "total": total,
        "non_null": len(non_empty),
        "null_count": null_count,
        "null_pct": round(100 * null_count / total, 2) if total > 0 else 0,
        "n_unique": n_unique,
        "dtype": dtype,
        "sample": sample,
    }


def print_table(headers, rows_data, col_widths=None):
    """Print a formatted text table."""
    if col_widths is None:
        col_widths = []
        for i, h in enumerate(headers):
            max_w = len(str(h))
            for r in rows_data:
                max_w = max(max_w, len(str(r[i])))
            col_widths.append(min(max_w + 2, 60))
    
    # header
    header_line = "".join(str(headers[i]).ljust(col_widths[i]) for i in range(len(headers)))
    print(header_line)
    print("-" * sum(col_widths))
    for r in rows_data:
        line = "".join(str(r[i])[:col_widths[i]-1].ljust(col_widths[i]) for i in range(len(headers)))
        print(line)


# ──────────────────────────────────────────────────────────────────────────────
# 1. LOAD DATASETS
# ──────────────────────────────────────────────────────────────────────────────
print("=" * 90)
print("STEP 1: LOADING DATASETS")
print("=" * 90)

train_path = os.path.join(DATA_DIR, "train.csv")
store_path = os.path.join(DATA_DIR, "store.csv")

train_header, train_rows = load_csv(train_path)
store_header, store_rows = load_csv(store_path)

print(f"\n  train.csv loaded  ->  {len(train_rows):,} rows  x  {len(train_header)} columns")
print(f"  store.csv loaded  ->  {len(store_rows):,} rows  x  {len(store_header)} columns")


# ──────────────────────────────────────────────────────────────────────────────
# 2a. SCHEMA INSPECTION — train.csv
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 90)
print("STEP 2a: SCHEMA INSPECTION — train.csv")
print("=" * 90)

print(f"\n  Shape: ({len(train_rows):,}, {len(train_header)})")
print(f"  Columns: {train_header}")

print(f"\n  Column details:")
table_headers = ["Column", "Inferred Dtype", "Non-Null", "Null", "Null%", "Unique", "Sample Values"]
table_rows = []
train_col_stats = {}
for col in train_header:
    stats = column_stats(train_rows, col)
    train_col_stats[col] = stats
    table_rows.append([
        col,
        stats["dtype"],
        f"{stats['non_null']:,}",
        f"{stats['null_count']:,}",
        f"{stats['null_pct']}%",
        f"{stats['n_unique']:,}",
        str(stats["sample"][:7]),
    ])
print()
print_table(table_headers, table_rows)

print(f"\n  First 5 rows:")
for i, row in enumerate(train_rows[:5]):
    vals = [f"{col}={row[col]}" for col in train_header]
    print(f"    [{i}] {', '.join(vals)}")

print(f"\n  Last 5 rows:")
for i, row in enumerate(train_rows[-5:], start=len(train_rows)-5):
    vals = [f"{col}={row[col]}" for col in train_header]
    print(f"    [{i}] {', '.join(vals)}")


# ──────────────────────────────────────────────────────────────────────────────
# 2b. SCHEMA INSPECTION — store.csv
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 90)
print("STEP 2b: SCHEMA INSPECTION — store.csv")
print("=" * 90)

print(f"\n  Shape: ({len(store_rows):,}, {len(store_header)})")
print(f"  Columns: {store_header}")

print(f"\n  Column details:")
table_rows_s = []
store_col_stats = {}
for col in store_header:
    stats = column_stats(store_rows, col)
    store_col_stats[col] = stats
    table_rows_s.append([
        col,
        stats["dtype"],
        f"{stats['non_null']:,}",
        f"{stats['null_count']:,}",
        f"{stats['null_pct']}%",
        f"{stats['n_unique']:,}",
        str(stats["sample"][:10]),
    ])
print()
print_table(table_headers, table_rows_s)

print(f"\n  First 5 rows:")
for i, row in enumerate(store_rows[:5]):
    vals = [f"{col}={row[col]}" for col in store_header]
    print(f"    [{i}] {', '.join(vals)}")

print(f"\n  Last 5 rows:")
for i, row in enumerate(store_rows[-5:], start=len(store_rows)-5):
    vals = [f"{col}={row[col]}" for col in store_header]
    print(f"    [{i}] {', '.join(vals)}")


# ──────────────────────────────────────────────────────────────────────────────
# 3. MERGE KEY ANALYSIS & MERGE
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 90)
print("STEP 3: MERGE KEY ANALYSIS & MERGE")
print("=" * 90)

# Identify the merge key
train_stores = set(r["Store"] for r in train_rows)
store_stores = set(r["Store"] for r in store_rows)

print(f"\n  Merge key: 'Store'")
print(f"    Unique stores in train.csv : {len(train_stores)}")
print(f"    Unique stores in store.csv : {len(store_stores)}")
print(f"    Stores in train NOT in store: {train_stores - store_stores if train_stores - store_stores else '{none}'}")
print(f"    Stores in store NOT in train: {store_stores - train_stores if store_stores - train_stores else '{none}'}")
print(f"    Overlap (inner join coverage): {len(train_stores & store_stores)} stores")

# Build store lookup
store_lookup = {}
# Columns from store that are NOT the merge key
store_extra_cols = [c for c in store_header if c != "Store"]

for row in store_rows:
    store_lookup[row["Store"]] = row

# Merged header
merged_header = list(train_header) + store_extra_cols

# Perform LEFT JOIN
merged_rows = []
for row in train_rows:
    merged = dict(row)
    store_data = store_lookup.get(row["Store"])
    if store_data:
        for col in store_extra_cols:
            merged[col] = store_data[col]
    else:
        for col in store_extra_cols:
            merged[col] = ""
    merged_rows.append(merged)

print(f"\n  Merged dataset shape: {len(merged_rows):,} rows  x  {len(merged_header)} columns")
print(f"  Row count preserved (no rows lost): {len(merged_rows) == len(train_rows)}")
print(f"\n  Merged columns ({len(merged_header)}):")
print(f"    {merged_header}")

print(f"\n  First 3 rows of merged dataset:")
for i, row in enumerate(merged_rows[:3]):
    vals = [f"{col}={row[col]}" for col in merged_header]
    print(f"    [{i}] {', '.join(vals)}")


# ──────────────────────────────────────────────────────────────────────────────
# 4. SAVE MERGED DATASET
# ──────────────────────────────────────────────────────────────────────────────
merged_path = os.path.join(DATA_DIR, "train_store_merged.csv")
with open(merged_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=merged_header)
    writer.writeheader()
    for row in merged_rows:
        writer.writerow({col: row[col] for col in merged_header})

print(f"\n  Merged dataset saved to: {merged_path}")


# ──────────────────────────────────────────────────────────────────────────────
# 5. DATA DICTIONARY
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 90)
print("STEP 4: COMPREHENSIVE DATA DICTIONARY")
print("=" * 90)

# Column descriptions based on Rossmann Store Sales Kaggle competition
COLUMN_DESCRIPTIONS = {
    "Store":                     "Unique ID for each store (1-1115)",
    "DayOfWeek":                 "Day of the week (1=Mon … 7=Sun)",
    "Date":                      "Date of the sales record (YYYY-MM-DD)",
    "Sales":                     "Turnover for a given day (target variable)",
    "Customers":                 "Number of customers on a given day",
    "Open":                      "Whether the store was open (0=closed, 1=open)",
    "Promo":                     "Whether a promotion was running that day (0=no, 1=yes)",
    "StateHoliday":              "State holiday indicator (a=public, b=Easter, c=Christmas, 0=none)",
    "SchoolHoliday":             "Whether the (Store, Date) was affected by school closures (0=no, 1=yes)",
    "StoreType":                 "Store model type (a, b, c, d) — differentiates business models",
    "Assortment":                "Assortment level (a=basic, b=extra, c=extended)",
    "CompetitionDistance":        "Distance in metres to the nearest competitor store",
    "CompetitionOpenSinceMonth":  "Month when the nearest competitor opened",
    "CompetitionOpenSinceYear":   "Year when the nearest competitor opened",
    "Promo2":                    "Continuing/consecutive promotion (0=not participating, 1=participating)",
    "Promo2SinceWeek":           "Calendar week when the store started Promo2",
    "Promo2SinceYear":           "Year when the store started Promo2",
    "PromoInterval":             "Months when Promo2 restarts (e.g. 'Jan,Apr,Jul,Oct')",
}

# Compute merged column stats
merged_col_stats = {}
for col in merged_header:
    merged_col_stats[col] = column_stats(merged_rows, col)

# Determine source
def get_source(col):
    in_train = col in train_header
    in_store = col in store_header
    if in_train and in_store:
        return "train.csv & store.csv (merge key)"
    elif in_train:
        return "train.csv"
    else:
        return "store.csv"

# Print data dictionary table
print()
dict_headers = ["#", "Column", "Source", "Dtype", "Non-Null", "Null", "Null%", "Unique", "Description"]
dict_rows = []
for i, col in enumerate(merged_header, 1):
    s = merged_col_stats[col]
    desc = COLUMN_DESCRIPTIONS.get(col, "—")
    dict_rows.append([
        i,
        col,
        get_source(col),
        s["dtype"],
        f"{s['non_null']:,}",
        f"{s['null_count']:,}",
        f"{s['null_pct']}%",
        f"{s['n_unique']:,}",
        desc,
    ])

print_table(dict_headers, dict_rows)

# Also print detailed sample values
print("\n\n  DETAILED SAMPLE VALUES PER COLUMN:")
print("  " + "-" * 85)
for col in merged_header:
    s = merged_col_stats[col]
    sample_str = str(s["sample"][:12])
    if s["n_unique"] > 12:
        sample_str += f" ... ({s['n_unique']:,} total unique)"
    print(f"    {col:30s}  ->  {sample_str}")

# ──────────────────────────────────────────────────────────────────────────────
# 6. SAVE DATA DICTIONARY AS CSV
# ──────────────────────────────────────────────────────────────────────────────
dict_csv_path = os.path.join(DATA_DIR, "data_dictionary.csv")
with open(dict_csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["#", "Column", "Source", "Inferred_Dtype", "Non_Null_Count", "Null_Count",
                     "Null_Pct", "Unique_Values", "Sample_Values", "Description"])
    for i, col in enumerate(merged_header, 1):
        s = merged_col_stats[col]
        desc = COLUMN_DESCRIPTIONS.get(col, "")
        writer.writerow([
            i, col, get_source(col), s["dtype"],
            s["non_null"], s["null_count"], f"{s['null_pct']}%",
            s["n_unique"], str(s["sample"][:10]), desc
        ])

print(f"\n  Data dictionary saved to: {dict_csv_path}")

print("\n" + "=" * 90)
print("DONE — All steps completed successfully.")
print("=" * 90)
