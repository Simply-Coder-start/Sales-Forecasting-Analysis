"""
07_baseline_model.py
====================
Builds a simple, robust baseline forecasting model using historical averages.
Model Logic: Predicts future sales using the historical average sales for the 
same Store and same DayOfWeek from the training set.

Uses only Python standard library.
"""

import csv
import os
import math
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TRAIN_FILE = os.path.join(DATA_DIR, "train_dataset.csv")
TEST_FILE = os.path.join(DATA_DIR, "test_dataset.csv")
REPORT_FILE = os.path.join(DATA_DIR, "baseline_model_report.txt")

report_lines = []
def rprint(msg=""):
    print(msg)
    report_lines.append(msg)

rprint("=" * 80)
rprint("BASELINE MODEL: STORE + DAY-OF-WEEK HISTORICAL AVERAGE")
rprint("=" * 80)

# ──────────────────────────────────────────────────────────────────────────────
# 1. LOAD TRAINING DATA & "TRAIN" BASELINE MODEL
# ──────────────────────────────────────────────────────────────────────────────
rprint("\n[1/4] Loading training data and computing historical averages...")

store_dow_sales = defaultdict(list)
store_sales = defaultdict(list)
global_sales = []

with open(TRAIN_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        s = int(r["Sales"])
        store = r["Store"]
        dow = r["DayOfWeek"]
        
        store_dow_sales[(store, dow)].append(s)
        store_sales[store].append(s)
        global_sales.append(s)

# Compute Means (The "Model")
store_dow_mean = {k: sum(v)/len(v) for k, v in store_dow_sales.items()}
store_mean = {k: sum(v)/len(v) for k, v in store_sales.items()}
global_mean = sum(global_sales) / len(global_sales)

rprint(f"      Trained on {len(global_sales):,} records.")
rprint(f"      Global mean sales: {global_mean:,.2f}")

# ──────────────────────────────────────────────────────────────────────────────
# 2. EVALUATE ON TEST DATASET
# ──────────────────────────────────────────────────────────────────────────────
rprint("\n[2/4] Generating predictions on test dataset...")

actuals = []
predictions = []

with open(TEST_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        store = r["Store"]
        dow = r["DayOfWeek"]
        actual = int(r["Sales"])
        
        # Prediction Logic with fallbacks
        if (store, dow) in store_dow_mean:
            pred = store_dow_mean[(store, dow)]
        elif store in store_mean:
            pred = store_mean[store]
        else:
            pred = global_mean
            
        actuals.append(actual)
        predictions.append(pred)

rprint(f"      Generated predictions for {len(actuals):,} test records.")

# ──────────────────────────────────────────────────────────────────────────────
# 3. CALCULATE METRICS (MAE, RMSE, R²)
# ──────────────────────────────────────────────────────────────────────────────
rprint("\n[3/4] Calculating Evaluation Metrics...")

n = len(actuals)

# MAE
mae = sum(abs(a - p) for a, p in zip(actuals, predictions)) / n

# RMSE
mse = sum((a - p) ** 2 for a, p in zip(actuals, predictions)) / n
rmse = math.sqrt(mse)

# R-squared
test_mean = sum(actuals) / n
ss_tot = sum((a - test_mean) ** 2 for a in actuals)
ss_res = sum((a - p) ** 2 for a, p in zip(actuals, predictions))
r_squared = 1 - (ss_res / ss_tot)

rprint(f"      MAE:  {mae:,.2f}")
rprint(f"      RMSE: {rmse:,.2f}")
rprint(f"      R²:   {r_squared:.4f}")

# ──────────────────────────────────────────────────────────────────────────────
# 4. PREDICTION VS ACTUAL SUMMARY
# ──────────────────────────────────────────────────────────────────────────────
rprint("\n[4/4] Prediction vs Actual Summary (First 10 records)...")

rprint(f"      {'Record':<8} {'Actual Sales':>12} {'Predicted Sales':>16} {'Error':>12}")
rprint("      " + "-" * 50)
for i in range(10):
    a = actuals[i]
    p = predictions[i]
    err = p - a
    rprint(f"      {i+1:<8} {a:>12} {p:>16.2f} {err:>12.2f}")

rprint("\n" + "=" * 80)
rprint("STRENGTHS AND WEAKNESSES OF THIS BASELINE")
rprint("=" * 80)
rprint("STRENGTHS:")
rprint("- Highly interpretable and fast to execute (O(1) lookup).")
rprint("- Captures the two most important variations in retail: Store location and Day of Week.")
rprint("- Robust to outliers since it averages over large periods of historical data.")
rprint("\nWEAKNESSES:")
rprint("- Ignores critical temporal dynamics (trend, holidays, promo periods).")
rprint("- Cannot capture recent momentum (e.g., if a store's sales have been growing recently).")
rprint("- Will consistently underpredict during active promotions and overpredict during slumps.")

# Save Report
with open(REPORT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

rprint(f"\nReport saved to: {REPORT_FILE}")
rprint("\nDONE -- Baseline model evaluation complete.")
