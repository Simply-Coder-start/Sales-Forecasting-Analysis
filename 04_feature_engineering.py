"""
04_feature_engineering.py
=========================
Rossmann Store Sales — Feature Engineering Pipeline

Uses only Python standard library.

Steps:
1. Date parsing and features (Year, Month, Quarter, Week, IsWeekend, etc.)
2. Lag features (1, 7, 14, 30 days) using strict calendar lookups to prevent leakage
3. Rolling statistics (Mean 7, 14, 30, Std 7)
4. Competition features (Age in months)
5. Promotion features (Promo2 Duration in months, IsPromoMonth)
6. One-Hot Encoding for categorical variables

Outputs:
- train_store_features.csv
- feature_engineering_report.txt
"""

import csv
import os
import math
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
INPUT_FILE = os.path.join(DATA_DIR, "train_store_cleaned.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "train_store_features.csv")
REPORT_FILE = os.path.join(DATA_DIR, "feature_engineering_report.txt")

report_lines = []
def rprint(msg=""):
    print(msg)
    report_lines.append(msg)

rprint("=" * 80)
rprint("FEATURE ENGINEERING PIPELINE")
rprint("=" * 80)

# ──────────────────────────────────────────────────────────────────────────────
# 1. LOAD DATA
# ──────────────────────────────────────────────────────────────────────────────
rprint("\n[1/6] Loading cleaned dataset...")
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    header = list(reader.fieldnames)
    rows = list(reader)

rprint(f"      Loaded {len(rows):,} rows.")

# ──────────────────────────────────────────────────────────────────────────────
# 2. BUILD SALES LOOKUP FOR LAGS
# ──────────────────────────────────────────────────────────────────────────────
rprint("\n[2/6] Building temporal sales lookup dictionary...")
# sales_dict[(store_id, "YYYY-MM-DD")] = sales
sales_dict = {}
for r in rows:
    sales_dict[(r["Store"], r["Date"])] = int(r["Sales"])

def get_past_sales(store, current_date_obj, days_ago):
    """Retrieves exact sales N calendar days ago. Returns 0 if missing (closed)."""
    past_date = current_date_obj - timedelta(days=days_ago)
    return sales_dict.get((store, past_date.strftime("%Y-%m-%d")), 0)

# ──────────────────────────────────────────────────────────────────────────────
# 3. FEATURE COMPUTATION
# ──────────────────────────────────────────────────────────────────────────────
rprint("\n[3/6] Computing temporal, lag, rolling, and categorical features...")

new_rows = []

# To keep track of generated columns dynamically
sample_row = None

for i, r in enumerate(rows):
    store = r["Store"]
    date_str = r["Date"]
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    
    # --- Date Features ---
    year = date_obj.year
    month = date_obj.month
    day = date_obj.day
    iso_year, iso_week, iso_dow = date_obj.isocalendar()
    
    quarter = (month - 1) // 3 + 1
    # isocalendar dow is 1-7 (Mon-Sun). Ensure DayOfWeek matches.
    dow = iso_dow
    is_weekend = 1 if dow >= 6 else 0
    
    r["Year"] = year
    r["Month"] = month
    r["Quarter"] = quarter
    r["WeekOfYear"] = iso_week
    r["Day"] = day
    r["DayOfWeek"] = dow
    r["IsWeekend"] = is_weekend
    
    # --- Lag Features ---
    lag_1 = get_past_sales(store, date_obj, 1)
    lag_7 = get_past_sales(store, date_obj, 7)
    lag_14 = get_past_sales(store, date_obj, 14)
    lag_30 = get_past_sales(store, date_obj, 30)
    
    r["Sales_Lag_1"] = lag_1
    r["Sales_Lag_7"] = lag_7
    r["Sales_Lag_14"] = lag_14
    r["Sales_Lag_30"] = lag_30
    
    # --- Rolling Statistics ---
    past_7 = [get_past_sales(store, date_obj, d) for d in range(1, 8)]
    past_14 = [get_past_sales(store, date_obj, d) for d in range(1, 15)]
    past_30 = [get_past_sales(store, date_obj, d) for d in range(1, 31)]
    
    mean_7 = sum(past_7) / 7.0
    mean_14 = sum(past_14) / 14.0
    mean_30 = sum(past_30) / 30.0
    
    # Sample standard deviation for past 7 days (N-1 = 6)
    var_7 = sum((x - mean_7) ** 2 for x in past_7) / 6.0
    std_7 = math.sqrt(var_7)
    
    r["RollingMean_7"] = round(mean_7, 2)
    r["RollingMean_14"] = round(mean_14, 2)
    r["RollingMean_30"] = round(mean_30, 2)
    r["RollingStd_7"] = round(std_7, 2)
    
    # --- Competition Features ---
    comp_year = int(r.get("CompetitionOpenSinceYear", 0))
    comp_month = int(r.get("CompetitionOpenSinceMonth", 0))
    
    if comp_year == 0 or comp_month == 0:
        comp_age = 0
    else:
        comp_age = 12 * (year - comp_year) + (month - comp_month)
        if comp_age < 0:
            comp_age = 0
            
    r["CompetitionAgeMonths"] = comp_age
    
    # --- Promotion Features ---
    promo2 = r.get("Promo2", "0")
    promo2_year = int(r.get("Promo2SinceYear", 0))
    promo2_week = int(r.get("Promo2SinceWeek", 0))
    promo_interval = r.get("PromoInterval", "")
    
    promo_dur = 0.0
    is_promo_month = 0
    
    if promo2 == "1" and promo2_year != 0 and promo2_week != 0:
        # Calculate duration in months (approx 4.345 weeks/month)
        promo_dur = 12 * (year - promo2_year) + (iso_week - promo2_week) / 4.345
        if promo_dur < 0:
            promo_dur = 0.0
            
        # Check if currently active and in the right month
        # fromisocalendar is available in Python 3.8+
        try:
            p2_start = datetime.fromisocalendar(promo2_year, promo2_week, 1).date()
            if date_obj >= p2_start:
                month_abbr = date_obj.strftime("%b")
                if month_abbr in promo_interval:
                    is_promo_month = 1
        except ValueError:
            pass # fallback to 0 if invalid iso calendar mapping
            
    r["PromoDurationMonths"] = round(promo_dur, 2)
    r["IsPromoMonth"] = is_promo_month
    
    # --- Categorical Encoding (One-Hot) ---
    store_type = r["StoreType"]
    for t in ["a", "b", "c", "d"]:
        r[f"StoreType_{t}"] = 1 if store_type == t else 0
        
    assortment = r["Assortment"]
    for a in ["a", "b", "c"]:
        r[f"Assortment_{a}"] = 1 if assortment == a else 0
        
    state_hol = r["StateHoliday"]
    for sh in ["0", "a", "b", "c"]:
        r[f"StateHoliday_{sh}"] = 1 if state_hol == sh else 0
        
    # Remove original categoricals to keep dataset clean
    if "StoreType" in r: del r["StoreType"]
    if "Assortment" in r: del r["Assortment"]
    if "StateHoliday" in r: del r["StateHoliday"]
    
    if sample_row is None:
        sample_row = list(r.keys())
        
    new_rows.append(r)
    
    if (i + 1) % 100000 == 0:
        print(f"      Processed {i + 1:,} rows...")

# ──────────────────────────────────────────────────────────────────────────────
# 4. REPORT GENERATION
# ──────────────────────────────────────────────────────────────────────────────
rprint(f"\n[4/6] Validating generated features...")

# Final Columns order
# Keep original headers (minus removed ones), then add new ones
original_kept = [h for h in header if h not in ["StoreType", "Assortment", "StateHoliday"]]
new_cols = [c for c in sample_row if c not in original_kept]
final_header = original_kept + new_cols

rprint(f"      Original features: {len(original_kept)}")
rprint(f"      New engineered features: {len(new_cols)}")
rprint(f"      Total features: {len(final_header)}")

rprint("\n  New Features List:")
rprint("  " + "-"*40)
for nc in new_cols:
    rprint(f"  - {nc}")

# ──────────────────────────────────────────────────────────────────────────────
# 5. SAVE DATASET
# ──────────────────────────────────────────────────────────────────────────────
rprint("\n[5/6] Saving engineered dataset to disk...")
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=final_header)
    writer.writeheader()
    writer.writerows(new_rows)
    
rprint(f"      Saved {len(new_rows):,} rows to {OUTPUT_FILE}")

# ──────────────────────────────────────────────────────────────────────────────
# 6. SAVE REPORT
# ──────────────────────────────────────────────────────────────────────────────
rprint("\n[6/6] Saving feature engineering report...")
with open(REPORT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

rprint(f"      Report saved to {REPORT_FILE}")

rprint("=" * 80)
rprint("DONE -- Feature Engineering Pipeline Complete.")
rprint("=" * 80)
