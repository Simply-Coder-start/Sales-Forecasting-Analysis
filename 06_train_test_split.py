"""
06_train_test_split.py
======================
Rossmann Store Sales — Train/Test Split Pipeline

Creates a production-grade time-series split using a strict chronological cutoff.
Output:
- train_dataset.csv
- test_dataset.csv
- train_test_split_report.txt
- Leakage validation checks
"""

import csv
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
INPUT_FILE = os.path.join(DATA_DIR, "train_store_features.csv")
TRAIN_FILE = os.path.join(DATA_DIR, "train_dataset.csv")
TEST_FILE = os.path.join(DATA_DIR, "test_dataset.csv")
REPORT_FILE = os.path.join(DATA_DIR, "train_test_split_report.txt")

report_lines = []
def rprint(msg=""):
    print(msg)
    report_lines.append(msg)

rprint("=" * 80)
rprint("TRAIN/TEST SPLIT PIPELINE")
rprint("=" * 80)

# ──────────────────────────────────────────────────────────────────────────────
# 1. LOAD DATA
# ──────────────────────────────────────────────────────────────────────────────
rprint("\n[1/5] Loading engineered feature dataset...")
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    header = list(reader.fieldnames)
    rows = list(reader)

rprint(f"      Loaded {len(rows):,} rows.")

# ──────────────────────────────────────────────────────────────────────────────
# 2. DETERMINE CUTOFF DATE
# ──────────────────────────────────────────────────────────────────────────────
rprint("\n[2/5] Determining chronological cutoff...")
unique_dates = sorted(list(set(r["Date"] for r in rows)))
total_days = len(unique_dates)

# Standard 80/20 chronological split
split_idx = int(total_days * 0.8)
cutoff_date = unique_dates[split_idx]

rprint(f"      Total unique dates: {total_days:,}")
rprint(f"      Dataset date range: {unique_dates[0]} to {unique_dates[-1]}")
rprint(f"      Calculated cutoff date for 80/20 split: {cutoff_date}")

# ──────────────────────────────────────────────────────────────────────────────
# 3. PERFORM SPLIT
# ──────────────────────────────────────────────────────────────────────────────
rprint("\n[3/5] Splitting data strictly by time (No random sampling)...")

train_rows = []
test_rows = []

for r in rows:
    if r["Date"] < cutoff_date:
        train_rows.append(r)
    else:
        test_rows.append(r)

rprint(f"      Train Set: {len(train_rows):,} rows ({len(train_rows)/len(rows)*100:.1f}%)")
rprint(f"      Test Set:  {len(test_rows):,} rows ({len(test_rows)/len(rows)*100:.1f}%)")

# ──────────────────────────────────────────────────────────────────────────────
# 4. LEAKAGE VALIDATION
# ──────────────────────────────────────────────────────────────────────────────
rprint("\n[4/5] Running Leakage Validation Checks...")

train_dates = set(r["Date"] for r in train_rows)
test_dates = set(r["Date"] for r in test_rows)

max_train_date = max(train_dates)
min_test_date = min(test_dates)

rprint(f"      Train Date Range: {min(train_dates)} to {max_train_date}")
rprint(f"      Test Date Range:  {min_test_date} to {max(test_dates)}")

errors = 0

# Check 1: Strict temporal boundary
if max_train_date >= min_test_date:
    rprint("      [ERROR] Train data overlaps or exceeds Test data time period!")
    errors += 1
else:
    rprint("      [PASS] Strict chronological boundary maintained. No time travel leakage.")

# Check 2: Store distribution check (ensure no missing stores)
train_stores = set(r["Store"] for r in train_rows)
test_stores = set(r["Store"] for r in test_rows)
missing_in_train = test_stores - train_stores
missing_in_test = train_stores - test_stores

if missing_in_train:
    rprint(f"      [WARNING] {len(missing_in_train)} stores in Test set have NO training data.")
else:
    rprint("      [PASS] All stores in Test set have historical training data.")

if errors == 0:
    rprint("      STATUS: VALIDATION PASSED. Splitting is fully leak-proof.")
else:
    rprint("      STATUS: VALIDATION FAILED. Fix errors before proceeding.")

# ──────────────────────────────────────────────────────────────────────────────
# 5. SAVE DATASETS
# ──────────────────────────────────────────────────────────────────────────────
rprint("\n[5/5] Saving outputs to disk...")

with open(TRAIN_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=header)
    writer.writeheader()
    writer.writerows(train_rows)
rprint(f"      Saved {TRAIN_FILE}")

with open(TEST_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=header)
    writer.writeheader()
    writer.writerows(test_rows)
rprint(f"      Saved {TEST_FILE}")

# Save Report
with open(REPORT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))
rprint(f"      Saved {REPORT_FILE}")

rprint("=" * 80)
rprint("DONE -- Train/Test Split Complete.")
rprint("=" * 80)
