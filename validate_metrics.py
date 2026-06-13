import os
import csv
import json

DATA_DIR = "data"

# Helper to count rows
def count_rows(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return 0
    with open(path, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f) - 1  # -1 for header

# 1. Dataset Sizes
metrics = {}
metrics["Total Records (Raw train.csv)"] = count_rows("train.csv")
metrics["Total Records (Merged)"] = count_rows("train_store_merged.csv")
metrics["Cleaned Records"] = count_rows("train_store_cleaned.csv")
metrics["Train Size"] = count_rows("train_dataset.csv")
metrics["Test Size"] = count_rows("test_dataset.csv")

# 2. Recompute Promo Lift from merged dataset (before cleaning/split)
promo_sales = []
no_promo_sales = []

merged_path = os.path.join(DATA_DIR, "train_store_merged.csv")
if os.path.exists(merged_path):
    with open(merged_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                sales = float(row.get('Sales', 0))
                promo = int(row.get('Promo', 0))
                if sales > 0:
                    if promo == 1:
                        promo_sales.append(sales)
                    else:
                        no_promo_sales.append(sales)
            except:
                pass

if promo_sales and no_promo_sales:
    avg_promo = sum(promo_sales) / len(promo_sales)
    avg_no_promo = sum(no_promo_sales) / len(no_promo_sales)
    lift = ((avg_promo - avg_no_promo) / avg_no_promo) * 100
    metrics["Promo Lift %"] = f"{lift:.2f}% (Promo Avg: {avg_promo:.1f}, No Promo: {avg_no_promo:.1f})"
else:
    metrics["Promo Lift %"] = "Could not compute"

# 3. Read Model Reports
def extract_model_metrics(report_name):
    path = os.path.join(DATA_DIR, report_name)
    results = {}
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if "MAE:" in line:
                    results["MAE"] = line.split("MAE:")[1].strip()
                elif "RMSE:" in line:
                    results["RMSE"] = line.split("RMSE:")[1].strip()
                elif "R²:" in line:
                    results["R²"] = line.split("R²:")[1].strip()
    return results

metrics["Baseline Metrics"] = extract_model_metrics("baseline_model_report.txt")
metrics["Random Forest Metrics"] = extract_model_metrics("random_forest_report.txt")
metrics["Gradient Boosting Metrics"] = extract_model_metrics("xgboost_report.txt")

# Print the report
print(json.dumps(metrics, indent=4))
