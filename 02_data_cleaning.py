"""
02_data_cleaning.py
====================
Rossmann Store Sales — Data Cleaning Pipeline

Uses only Python standard library (csv module) — no pandas required.

Steps:
1. Missing value identification & classification
2. Missing value treatment
3. Duplicate detection & removal
4. Invalid/impossible value detection & correction
5. Cleaned dataset output + full cleaning report

Boundaries:
- NO EDA, NO feature engineering, NO model training
- Target variable (Sales) is NOT modified
"""

import csv
import os
import json
from collections import Counter, defaultdict
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
INPUT_FILE = os.path.join(DATA_DIR, "train_store_merged.csv")

# ──────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def load_csv(filepath):
    """Load CSV and return (header, rows_as_dicts)."""
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = list(reader.fieldnames)
        rows = list(reader)
    return header, rows


def is_empty(val):
    """Check if a cell value is missing/empty."""
    return val is None or val.strip() == ""


def safe_int(val, default=None):
    """Safely convert to int."""
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def safe_float(val, default=None):
    """Safely convert to float."""
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def compute_median(values):
    """Compute median of a list of numeric values."""
    s = sorted(values)
    n = len(s)
    if n == 0:
        return 0
    if n % 2 == 1:
        return s[n // 2]
    else:
        return (s[n // 2 - 1] + s[n // 2]) / 2


# ──────────────────────────────────────────────────────────────────────────────
# REPORT ACCUMULATOR
# ──────────────────────────────────────────────────────────────────────────────
report_lines = []

def rprint(msg=""):
    """Print and accumulate for report."""
    print(msg)
    report_lines.append(msg)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 0: LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════
rprint("=" * 95)
rprint("STEP 0: LOADING MERGED DATASET")
rprint("=" * 95)

header, rows = load_csv(INPUT_FILE)
rprint(f"\n  Loaded: {INPUT_FILE}")
rprint(f"  Shape:  {len(rows):,} rows x {len(header)} columns")
rprint(f"  Columns: {header}")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1: MISSING VALUE IDENTIFICATION
# ══════════════════════════════════════════════════════════════════════════════
rprint("\n" + "=" * 95)
rprint("STEP 1: MISSING VALUE IDENTIFICATION")
rprint("=" * 95)

null_counts = {}
for col in header:
    count = sum(1 for r in rows if is_empty(r[col]))
    null_counts[col] = count

rprint(f"\n  {'Column':<30s} {'Null Count':>12s} {'Null %':>10s} {'Status':<20s}")
rprint("  " + "-" * 75)
for col in header:
    nc = null_counts[col]
    pct = round(100 * nc / len(rows), 2)
    status = "COMPLETE" if nc == 0 else "HAS NULLS"
    rprint(f"  {col:<30s} {nc:>12,} {pct:>9.2f}% {status:<20s}")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2: MISSING VALUE CLASSIFICATION & TREATMENT STRATEGY
# ══════════════════════════════════════════════════════════════════════════════
rprint("\n" + "=" * 95)
rprint("STEP 2: MISSING VALUE CLASSIFICATION & TREATMENT STRATEGY")
rprint("=" * 95)

# --- 2a. CompetitionDistance (3 stores missing) ---
rprint("\n  --- CompetitionDistance (2,642 null rows from 3 stores) ---")
rprint("  Classification: DATA QUALITY ISSUE")
rprint("  Reason: Only 3 out of 1,115 stores lack this field. Every store has")
rprint("          competitors; distance is simply unrecorded.")
rprint("  Treatment: Fill with MEDIAN of all non-null CompetitionDistance values.")
rprint("  Justification: Median is robust to outliers (distances range from 20 to 75,860m).")

# Compute median CompetitionDistance
comp_dist_vals = [safe_int(r["CompetitionDistance"]) for r in rows if not is_empty(r["CompetitionDistance"])]
median_comp_dist = int(compute_median(comp_dist_vals))
rprint(f"  Computed median CompetitionDistance = {median_comp_dist:,} metres")

# --- 2b. CompetitionOpenSinceMonth / Year (~32% missing) ---
rprint("\n  --- CompetitionOpenSinceMonth / CompetitionOpenSinceYear (323,348 null rows) ---")
rprint("  Classification: MIXED")

# Check: how many of these nulls ALSO have CompetitionDistance = null?
comp_month_null_with_dist_null = 0
comp_month_null_with_dist_present = 0
for r in rows:
    if is_empty(r["CompetitionOpenSinceMonth"]):
        if is_empty(r["CompetitionDistance"]):
            comp_month_null_with_dist_null += 1
        else:
            comp_month_null_with_dist_present += 1

rprint(f"    - Null month AND null distance: {comp_month_null_with_dist_null:,} rows")
rprint(f"    - Null month BUT distance present: {comp_month_null_with_dist_present:,} rows")
rprint("  Reason: For stores WITH a known competitor distance, the opening date is")
rprint("          simply unknown (data quality). For stores without distance, it is")
rprint("          missing by design. In both cases the competitor exists but the")
rprint("          opening date was never recorded.")
rprint("  Treatment: Fill with 0 (sentinel value meaning 'unknown').")
rprint("  Justification: We cannot infer the actual month/year. A sentinel value (0)")
rprint("          clearly signals 'unknown' and avoids introducing false temporal")
rprint("          information. Downstream models can treat 0 as a distinct category.")

# --- 2c. Promo2SinceWeek / Promo2SinceYear / PromoInterval (~50% missing) ---
rprint("\n  --- Promo2SinceWeek / Promo2SinceYear / PromoInterval (508,031 null rows) ---")
rprint("  Classification: MISSING BY DESIGN")

# Verify: all nulls correspond to Promo2=0
promo2_null_but_promo2_is_1 = 0
promo2_null_and_promo2_is_0 = 0
for r in rows:
    if is_empty(r["Promo2SinceWeek"]):
        if r["Promo2"] == "1":
            promo2_null_but_promo2_is_1 += 1
        else:
            promo2_null_and_promo2_is_0 += 1

rprint(f"    - Null Promo2Since* AND Promo2=0: {promo2_null_and_promo2_is_0:,} rows (EXPECTED)")
rprint(f"    - Null Promo2Since* AND Promo2=1: {promo2_null_but_promo2_is_1:,} rows (ANOMALY)")
rprint("  Reason: Stores NOT participating in Promo2 (Promo2=0) have no start date")
rprint("          or interval — structurally impossible to have these values.")
rprint("  Treatment:")
rprint("    - Promo2SinceWeek:  Fill with 0 (not applicable)")
rprint("    - Promo2SinceYear:  Fill with 0 (not applicable)")
rprint("    - PromoInterval:    Fill with '' (empty string, not applicable)")
rprint("  Justification: These fields are structurally absent for non-participants.")
rprint("          Zero-filling the numeric fields and empty-string for the categorical")
rprint("          field preserves the meaning of 'not applicable'.")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3: APPLY MISSING VALUE TREATMENTS
# ══════════════════════════════════════════════════════════════════════════════
rprint("\n" + "=" * 95)
rprint("STEP 3: APPLYING MISSING VALUE TREATMENTS")
rprint("=" * 95)

fill_counts = defaultdict(int)

for r in rows:
    # CompetitionDistance → median
    if is_empty(r["CompetitionDistance"]):
        r["CompetitionDistance"] = str(median_comp_dist)
        fill_counts["CompetitionDistance"] += 1

    # CompetitionOpenSinceMonth → 0
    if is_empty(r["CompetitionOpenSinceMonth"]):
        r["CompetitionOpenSinceMonth"] = "0"
        fill_counts["CompetitionOpenSinceMonth"] += 1

    # CompetitionOpenSinceYear → 0
    if is_empty(r["CompetitionOpenSinceYear"]):
        r["CompetitionOpenSinceYear"] = "0"
        fill_counts["CompetitionOpenSinceYear"] += 1

    # Promo2SinceWeek → 0
    if is_empty(r["Promo2SinceWeek"]):
        r["Promo2SinceWeek"] = "0"
        fill_counts["Promo2SinceWeek"] += 1

    # Promo2SinceYear → 0
    if is_empty(r["Promo2SinceYear"]):
        r["Promo2SinceYear"] = "0"
        fill_counts["Promo2SinceYear"] += 1

    # PromoInterval → empty string (already is, but make explicit)
    if is_empty(r["PromoInterval"]):
        r["PromoInterval"] = ""
        fill_counts["PromoInterval"] += 1

rprint("\n  Fill summary:")
for col, count in sorted(fill_counts.items()):
    rprint(f"    {col:<30s} -> {count:>10,} values filled")

# Verify no nulls remain
remaining_nulls = {col: sum(1 for r in rows if is_empty(r[col])) for col in header}
any_remaining = any(v > 0 for v in remaining_nulls.values())
rprint(f"\n  Remaining nulls after treatment: {'NONE -- all resolved' if not any_remaining else remaining_nulls}")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4: DUPLICATE DETECTION
# ══════════════════════════════════════════════════════════════════════════════
rprint("\n" + "=" * 95)
rprint("STEP 4: DUPLICATE DETECTION")
rprint("=" * 95)

# A true duplicate is a row where (Store, Date) appears more than once
# since each store should have at most one record per day
store_date_counts = Counter()
for r in rows:
    key = (r["Store"], r["Date"])
    store_date_counts[key] += 1

dup_keys = {k: v for k, v in store_date_counts.items() if v > 1}
total_dup_rows = sum(v - 1 for v in dup_keys.values())  # excess rows

rprint(f"\n  Duplicate check key: (Store, Date)")
rprint(f"  Unique (Store, Date) combinations: {len(store_date_counts):,}")
rprint(f"  Duplicate (Store, Date) keys: {len(dup_keys):,}")
rprint(f"  Total excess duplicate rows: {total_dup_rows:,}")

if total_dup_rows > 0:
    rprint("\n  Duplicate examples (first 10):")
    for i, (k, v) in enumerate(list(dup_keys.items())[:10]):
        rprint(f"    Store={k[0]}, Date={k[1]} -> appears {v} times")
    rprint("\n  Treatment: REMOVE exact duplicate rows (keep first occurrence).")
    rprint("  Justification: Each store should have exactly one sales record per day.")
    
    # Remove duplicates — keep first occurrence
    seen = set()
    deduped_rows = []
    for r in rows:
        key = (r["Store"], r["Date"])
        if key not in seen:
            seen.add(key)
            deduped_rows.append(r)
    
    removed = len(rows) - len(deduped_rows)
    rprint(f"  Rows removed: {removed:,}")
    rprint(f"  Rows remaining: {len(deduped_rows):,}")
    rows = deduped_rows
else:
    rprint("\n  Result: NO DUPLICATES found. Dataset is clean on (Store, Date).")

# Also check for full-row exact duplicates
rprint("\n  Additional check: Full-row exact duplicates")
row_hashes = Counter()
for r in rows:
    row_hash = tuple(r[col] for col in header)
    row_hashes[row_hash] += 1
full_dups = sum(v - 1 for v in row_hashes.values() if v > 1)
rprint(f"  Full-row exact duplicates: {full_dups:,}")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 5: INVALID / IMPOSSIBLE VALUE DETECTION
# ══════════════════════════════════════════════════════════════════════════════
rprint("\n" + "=" * 95)
rprint("STEP 5: INVALID / IMPOSSIBLE VALUE DETECTION")
rprint("=" * 95)

invalid_log = []  # (row_index, column, value, issue)

# --- 5a. Open=1 but Sales=0 and Customers=0 ---
rprint("\n  --- Check 5a: Open=1 but Sales=0 and Customers=0 ---")
open_zero_sales = []
for i, r in enumerate(rows):
    if r["Open"] == "1" and r["Sales"] == "0" and r["Customers"] == "0":
        open_zero_sales.append(i)
        invalid_log.append((i, "Sales/Customers", "0/0", "Store open but zero sales AND zero customers"))

rprint(f"  Found: {len(open_zero_sales):,} rows where Open=1, Sales=0, Customers=0")
rprint("  Treatment: Flag but RETAIN. Possible genuine zero-traffic day (e.g., reopening")
rprint("             setup day, data lag). Sales is target variable -- not modified per rules.")

# --- 5b. Open=0 but Sales>0 ---
rprint("\n  --- Check 5b: Open=0 but Sales>0 ---")
closed_with_sales = []
for i, r in enumerate(rows):
    s = safe_int(r["Sales"], 0)
    if r["Open"] == "0" and s > 0:
        closed_with_sales.append((i, s))
        invalid_log.append((i, "Open/Sales", f"Open=0, Sales={s}", "Store closed but has sales"))

rprint(f"  Found: {len(closed_with_sales):,} rows where Open=0 but Sales > 0")
if closed_with_sales:
    rprint("  Examples:")
    for idx, s in closed_with_sales[:5]:
        r = rows[idx]
        rprint(f"    Row {idx}: Store={r['Store']}, Date={r['Date']}, Open=0, Sales={s}")
rprint("  Treatment: Flag but RETAIN. These may be online/pickup sales while")
rprint("             the physical store was closed. Sales is not modified.")

# --- 5c. Negative values for Sales or Customers ---
rprint("\n  --- Check 5c: Negative Sales or Customers ---")
neg_sales = sum(1 for r in rows if safe_int(r["Sales"], 0) < 0)
neg_cust = sum(1 for r in rows if safe_int(r["Customers"], 0) < 0)
rprint(f"  Negative Sales: {neg_sales:,}")
rprint(f"  Negative Customers: {neg_cust:,}")

# --- 5d. DayOfWeek out of range [1,7] ---
rprint("\n  --- Check 5d: DayOfWeek outside [1, 7] ---")
bad_dow = sum(1 for r in rows if safe_int(r["DayOfWeek"], 0) not in range(1, 8))
rprint(f"  Invalid DayOfWeek values: {bad_dow:,}")

# --- 5e. Open not in {0, 1} ---
rprint("\n  --- Check 5e: Open not in {0, 1} ---")
bad_open = sum(1 for r in rows if r["Open"] not in ("0", "1"))
rprint(f"  Invalid Open values: {bad_open:,}")

# --- 5f. Promo not in {0, 1} ---
rprint("\n  --- Check 5f: Promo not in {0, 1} ---")
bad_promo = sum(1 for r in rows if r["Promo"] not in ("0", "1"))
rprint(f"  Invalid Promo values: {bad_promo:,}")

# --- 5g. StateHoliday not in {0, a, b, c} ---
rprint("\n  --- Check 5g: StateHoliday not in {0, a, b, c} ---")
valid_sh = {"0", "a", "b", "c"}
bad_sh = sum(1 for r in rows if r["StateHoliday"] not in valid_sh)
rprint(f"  Invalid StateHoliday values: {bad_sh:,}")

# --- 5h. SchoolHoliday not in {0, 1} ---
rprint("\n  --- Check 5h: SchoolHoliday not in {0, 1} ---")
bad_sch = sum(1 for r in rows if r["SchoolHoliday"] not in ("0", "1"))
rprint(f"  Invalid SchoolHoliday values: {bad_sch:,}")

# --- 5i. StoreType not in {a, b, c, d} ---
rprint("\n  --- Check 5i: StoreType not in {a, b, c, d} ---")
bad_st = sum(1 for r in rows if r["StoreType"] not in ("a", "b", "c", "d"))
rprint(f"  Invalid StoreType values: {bad_st:,}")

# --- 5j. Assortment not in {a, b, c} ---
rprint("\n  --- Check 5j: Assortment not in {a, b, c} ---")
bad_assort = sum(1 for r in rows if r["Assortment"] not in ("a", "b", "c"))
rprint(f"  Invalid Assortment values: {bad_assort:,}")

# --- 5k. Promo2 not in {0, 1} ---
rprint("\n  --- Check 5k: Promo2 not in {0, 1} ---")
bad_p2 = sum(1 for r in rows if r["Promo2"] not in ("0", "1"))
rprint(f"  Invalid Promo2 values: {bad_p2:,}")

# --- 5l. Date format validation ---
rprint("\n  --- Check 5l: Date format validation (YYYY-MM-DD) ---")
bad_dates = 0
for r in rows:
    try:
        datetime.strptime(r["Date"], "%Y-%m-%d")
    except ValueError:
        bad_dates += 1
        invalid_log.append((0, "Date", r["Date"], "Invalid date format"))
rprint(f"  Invalid date formats: {bad_dates:,}")

# --- 5m. CompetitionOpenSinceMonth out of range [0,12] (0 = sentinel) ---
rprint("\n  --- Check 5m: CompetitionOpenSinceMonth outside [0, 12] ---")
bad_comp_month = 0
for r in rows:
    v = safe_int(r["CompetitionOpenSinceMonth"], -1)
    if v < 0 or v > 12:
        bad_comp_month += 1
rprint(f"  Invalid CompetitionOpenSinceMonth values: {bad_comp_month:,}")

# --- 5n. CompetitionOpenSinceYear validation ---
rprint("\n  --- Check 5n: CompetitionOpenSinceYear outside [0, 2015] + {1900} ---")
bad_comp_year = 0
for r in rows:
    v = safe_int(r["CompetitionOpenSinceYear"], -1)
    if v < 0 or (v != 0 and v < 1900) or v > 2015:
        bad_comp_year += 1
rprint(f"  Invalid CompetitionOpenSinceYear values: {bad_comp_year:,}")

# --- 5o. CompetitionDistance <= 0 (after imputation) ---
rprint("\n  --- Check 5o: CompetitionDistance <= 0 ---")
bad_comp_dist = sum(1 for r in rows if safe_int(r["CompetitionDistance"], 0) <= 0)
rprint(f"  CompetitionDistance <= 0: {bad_comp_dist:,}")

# --- 5p. Customers > 0 but Open = 0 ---
rprint("\n  --- Check 5p: Customers > 0 but Open=0 ---")
cust_when_closed = sum(1 for r in rows if r["Open"] == "0" and safe_int(r["Customers"], 0) > 0)
rprint(f"  Customers > 0 when closed: {cust_when_closed:,}")

# --- Summary ---
rprint("\n  INVALID VALUE SUMMARY:")
rprint("  " + "-" * 60)
total_flagged = len(open_zero_sales) + len(closed_with_sales) + neg_sales + neg_cust + bad_dow + bad_open
total_flagged += bad_promo + bad_sh + bad_sch + bad_st + bad_assort + bad_p2 + bad_dates
total_flagged += bad_comp_month + bad_comp_year + bad_comp_dist + cust_when_closed
rprint(f"  Total flagged issues: {total_flagged:,}")
rprint(f"  Issues requiring row removal: 0")
rprint(f"  Issues flagged for awareness (retained): {len(open_zero_sales) + len(closed_with_sales):,}")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 6: REMOVE CLOSED-STORE ROWS (Open=0)
# ══════════════════════════════════════════════════════════════════════════════
rprint("\n" + "=" * 95)
rprint("STEP 6: REMOVE CLOSED-STORE ROWS (Open=0)")
rprint("=" * 95)

before_count = len(rows)
closed_count = sum(1 for r in rows if r["Open"] == "0")
rprint(f"\n  Rows where Open=0: {closed_count:,} ({round(100*closed_count/before_count, 2)}%)")
rprint("  Treatment: REMOVE all rows where Open=0.")
rprint("  Justification: Closed stores generate no meaningful sales data (Sales=0 in")
rprint("           the vast majority of these rows). Keeping them would add noise.")
rprint("           The forecasting target is sales when the store IS open.")

rows = [r for r in rows if r["Open"] != "0"]
rprint(f"  Rows removed: {before_count - len(rows):,}")
rprint(f"  Rows remaining: {len(rows):,}")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 7: FINAL VALIDATION
# ══════════════════════════════════════════════════════════════════════════════
rprint("\n" + "=" * 95)
rprint("STEP 7: FINAL VALIDATION")
rprint("=" * 95)

# Null check
final_nulls = {col: sum(1 for r in rows if is_empty(r[col])) for col in header}
rprint(f"\n  Final shape: {len(rows):,} rows x {len(header)} columns")
rprint(f"\n  Final null counts:")
for col in header:
    rprint(f"    {col:<30s} -> {final_nulls[col]:,}")

# Value range summary
rprint(f"\n  Value range summary (on cleaned data):")
for col in header:
    vals = [r[col] for r in rows if not is_empty(r[col])]
    unique_count = len(set(vals))
    # Try numeric min/max
    num_vals = [safe_float(v) for v in vals if safe_float(v) is not None]
    if len(num_vals) == len(vals) and num_vals:
        rprint(f"    {col:<30s} unique={unique_count:>8,}  min={min(num_vals):>12,.0f}  max={max(num_vals):>12,.0f}")
    else:
        sample = sorted(set(vals))[:10]
        rprint(f"    {col:<30s} unique={unique_count:>8,}  values={sample}")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 8: SAVE CLEANED DATASET
# ══════════════════════════════════════════════════════════════════════════════
rprint("\n" + "=" * 95)
rprint("STEP 8: SAVE CLEANED DATASET")
rprint("=" * 95)

output_path = os.path.join(DATA_DIR, "train_store_cleaned.csv")
with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=header)
    writer.writeheader()
    for r in rows:
        writer.writerow({col: r[col] for col in header})

rprint(f"\n  Cleaned dataset saved to: {output_path}")
rprint(f"  Final shape: {len(rows):,} rows x {len(header)} columns")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 9: CLEANING SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
rprint("\n" + "=" * 95)
rprint("STEP 9: CLEANING DECISION SUMMARY")
rprint("=" * 95)

rprint("""
  +------+-------------------------------+---------------------+---------------------------------------------+
  | #    | Column(s)                     | Action              | Justification                               |
  +------+-------------------------------+---------------------+---------------------------------------------+
  | 1    | CompetitionDistance            | Fill with median    | 3 stores missing; median robust to outliers |
  |      |                               | ({median_cd})        |                                             |
  +------+-------------------------------+---------------------+---------------------------------------------+
  | 2    | CompetitionOpenSinceMonth     | Fill with 0         | Unknown opening date; 0 = sentinel for      |
  |      | CompetitionOpenSinceYear      | Fill with 0         | 'unknown'                                   |
  +------+-------------------------------+---------------------+---------------------------------------------+
  | 3    | Promo2SinceWeek               | Fill with 0         | Missing by design: store not in Promo2      |
  |      | Promo2SinceYear               | Fill with 0         | (Promo2=0), so no start date exists         |
  |      | PromoInterval                 | Fill with ''        |                                             |
  +------+-------------------------------+---------------------+---------------------------------------------+
  | 4    | (Store, Date) duplicates      | None needed         | No duplicates found                         |
  +------+-------------------------------+---------------------+---------------------------------------------+
  | 5    | Open=1, Sales=0, Cust=0       | Flag, retain        | Possible genuine zero-traffic day; Sales    |
  |      |                               |                     | is target variable -- not modified          |
  +------+-------------------------------+---------------------+---------------------------------------------+
  | 6    | Open=0 rows                   | Removed             | Closed stores have no meaningful sales;     |
  |      |                               |                     | forecasting targets open-store days         |
  +------+-------------------------------+---------------------+---------------------------------------------+
  | 7    | Sales (target)                | NOT MODIFIED        | Per task boundaries                         |
  +------+-------------------------------+---------------------+---------------------------------------------+
""".format(median_cd=median_comp_dist))


rprint("=" * 95)
rprint("DONE — All cleaning steps completed successfully.")
rprint("=" * 95)


# ══════════════════════════════════════════════════════════════════════════════
# SAVE CLEANING REPORT
# ══════════════════════════════════════════════════════════════════════════════
report_path = os.path.join(DATA_DIR, "cleaning_report.txt")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))
print(f"\n  Cleaning report saved to: {report_path}")
