"""
10_generate_dashboard_data.py
=============================
Pre-computes all aggregated data needed by the Streamlit/HTML dashboard.
Reads from train_dataset.csv and test_dataset.csv.
Outputs a single JSON file with all pre-aggregated metrics.

Uses only Python standard library.
"""

import csv
import os
import json
import math
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TRAIN_FILE = os.path.join(DATA_DIR, "train_dataset.csv")
TEST_FILE = os.path.join(DATA_DIR, "test_dataset.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "dashboard_data.json")

def safe_int(v, d=0):
    try: return int(v)
    except: return d

def safe_float(v, d=0.0):
    try: return float(v)
    except: return d

def mean(vals):
    return sum(vals)/len(vals) if vals else 0

def median_val(vals):
    s = sorted(vals)
    n = len(s)
    if n == 0: return 0
    if n % 2 == 1: return s[n//2]
    return (s[n//2-1] + s[n//2]) / 2

print("Loading datasets...")
# Load both train and test for comprehensive analytics
all_rows = []
with open(TRAIN_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        all_rows.append(r)
print(f"  Train: {len(all_rows):,} rows")

test_rows = []
with open(TEST_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        test_rows.append(r)
        all_rows.append(r)
print(f"  Test: {len(test_rows):,} rows")
print(f"  Total: {len(all_rows):,} rows")

dashboard = {}

# ── 1. Overview KPIs ─────────────────────────────────────────────────────────
print("Computing overview KPIs...")
all_sales = [safe_int(r["Sales"]) for r in all_rows]
all_cust = [safe_int(r["Customers"]) for r in all_rows]
num_stores = len(set(r["Store"] for r in all_rows))
dates = sorted(set(r["Date"] for r in all_rows))

dashboard["overview"] = {
    "total_records": len(all_rows),
    "num_stores": num_stores,
    "avg_daily_sales": round(mean(all_sales), 0),
    "median_daily_sales": round(median_val(all_sales), 0),
    "total_revenue": sum(all_sales),
    "avg_customers": round(mean(all_cust), 0),
    "date_range": [dates[0], dates[-1]],
    "total_days": len(dates),
}

# ── 2. Monthly Trends ────────────────────────────────────────────────────────
print("Computing monthly trends...")
monthly = defaultdict(lambda: {"sales": [], "customers": [], "count": 0})
for r in all_rows:
    ym = r["Date"][:7]
    monthly[ym]["sales"].append(safe_int(r["Sales"]))
    monthly[ym]["customers"].append(safe_int(r["Customers"]))
    monthly[ym]["count"] += 1

dashboard["monthly_trends"] = []
for ym in sorted(monthly.keys()):
    d = monthly[ym]
    dashboard["monthly_trends"].append({
        "month": ym,
        "avg_sales": round(mean(d["sales"]), 0),
        "total_sales": sum(d["sales"]),
        "avg_customers": round(mean(d["customers"]), 0),
        "records": d["count"],
    })

# ── 3. Day of Week ───────────────────────────────────────────────────────────
print("Computing day of week patterns...")
dow_names = {"1":"Mon","2":"Tue","3":"Wed","4":"Thu","5":"Fri","6":"Sat","7":"Sun"}
dow_sales = defaultdict(list)
dow_cust = defaultdict(list)
for r in all_rows:
    dow = r["DayOfWeek"]
    dow_sales[dow].append(safe_int(r["Sales"]))
    dow_cust[dow].append(safe_int(r["Customers"]))

dashboard["day_of_week"] = []
for d in sorted(dow_sales.keys()):
    dashboard["day_of_week"].append({
        "day": dow_names.get(d, d),
        "day_num": int(d),
        "avg_sales": round(mean(dow_sales[d]), 0),
        "avg_customers": round(mean(dow_cust[d]), 0),
    })

# ── 4. Store Performance ─────────────────────────────────────────────────────
print("Computing store performance...")
store_sales = defaultdict(list)
store_cust = defaultdict(list)
store_meta = {}
for r in all_rows:
    s = r["Store"]
    store_sales[s].append(safe_int(r["Sales"]))
    store_cust[s].append(safe_int(r["Customers"]))
    if s not in store_meta:
        st = "a" if r.get("StoreType_a","0")=="1" else "b" if r.get("StoreType_b","0")=="1" else "c" if r.get("StoreType_c","0")=="1" else "d"
        aso = "a" if r.get("Assortment_a","0")=="1" else "b" if r.get("Assortment_b","0")=="1" else "c"
        store_meta[s] = {"type": st, "assortment": aso}

store_perf = []
for s in store_sales:
    store_perf.append({
        "store": int(s),
        "avg_sales": round(mean(store_sales[s]), 0),
        "avg_customers": round(mean(store_cust[s]), 0),
        "type": store_meta[s]["type"],
        "assortment": store_meta[s]["assortment"],
    })
store_perf.sort(key=lambda x: x["avg_sales"], reverse=True)
dashboard["top_stores"] = store_perf[:10]
dashboard["bottom_stores"] = store_perf[-10:][::-1]

# ── 5. Store Type Analysis ───────────────────────────────────────────────────
print("Computing store type analysis...")
st_sales = defaultdict(list)
st_cust = defaultdict(list)
st_stores = defaultdict(set)
for r in all_rows:
    st = "a" if r.get("StoreType_a","0")=="1" else "b" if r.get("StoreType_b","0")=="1" else "c" if r.get("StoreType_c","0")=="1" else "d"
    st_sales[st].append(safe_int(r["Sales"]))
    st_cust[st].append(safe_int(r["Customers"]))
    st_stores[st].add(r["Store"])

dashboard["store_types"] = []
for t in sorted(st_sales.keys()):
    avg_s = mean(st_sales[t])
    avg_c = mean(st_cust[t])
    dashboard["store_types"].append({
        "type": t.upper(),
        "stores": len(st_stores[t]),
        "avg_sales": round(avg_s, 0),
        "avg_customers": round(avg_c, 0),
        "sales_per_customer": round(avg_s / avg_c, 1) if avg_c > 0 else 0,
    })

# ── 6. Assortment Analysis ──────────────────────────────────────────────────
print("Computing assortment analysis...")
as_names = {"a": "Basic", "b": "Extra", "c": "Extended"}
as_sales = defaultdict(list)
as_cust = defaultdict(list)
for r in all_rows:
    a = "a" if r.get("Assortment_a","0")=="1" else "b" if r.get("Assortment_b","0")=="1" else "c"
    as_sales[a].append(safe_int(r["Sales"]))
    as_cust[a].append(safe_int(r["Customers"]))

dashboard["assortment"] = []
for a in sorted(as_sales.keys()):
    dashboard["assortment"].append({
        "type": a.upper(),
        "name": as_names.get(a, a),
        "avg_sales": round(mean(as_sales[a]), 0),
        "avg_customers": round(mean(as_cust[a]), 0),
    })

# ── 7. Promotion Analysis ───────────────────────────────────────────────────
print("Computing promotion impact...")
promo_s = defaultdict(list)
promo_c = defaultdict(list)
for r in all_rows:
    p = "Promo" if r["Promo"] == "1" else "No Promo"
    promo_s[p].append(safe_int(r["Sales"]))
    promo_c[p].append(safe_int(r["Customers"]))

promo_lift = round((mean(promo_s["Promo"]) - mean(promo_s["No Promo"])) / mean(promo_s["No Promo"]) * 100, 1)

# Promo by store type
promo_st = defaultdict(lambda: defaultdict(list))
for r in all_rows:
    st = "a" if r.get("StoreType_a","0")=="1" else "b" if r.get("StoreType_b","0")=="1" else "c" if r.get("StoreType_c","0")=="1" else "d"
    p = "Promo" if r["Promo"] == "1" else "No Promo"
    promo_st[st][p].append(safe_int(r["Sales"]))

dashboard["promotion"] = {
    "no_promo_avg": round(mean(promo_s["No Promo"]), 0),
    "promo_avg": round(mean(promo_s["Promo"]), 0),
    "lift_pct": promo_lift,
    "no_promo_cust": round(mean(promo_c["No Promo"]), 0),
    "promo_cust": round(mean(promo_c["Promo"]), 0),
    "by_store_type": [],
}
for st in sorted(promo_st.keys()):
    np_avg = mean(promo_st[st].get("No Promo", [0]))
    p_avg = mean(promo_st[st].get("Promo", [0]))
    lift = round((p_avg - np_avg) / np_avg * 100, 1) if np_avg > 0 else 0
    dashboard["promotion"]["by_store_type"].append({
        "type": st.upper(),
        "no_promo": round(np_avg, 0),
        "promo": round(p_avg, 0),
        "lift_pct": lift,
    })

# ── 8. Seasonality (Month of Year) ──────────────────────────────────────────
print("Computing seasonality...")
month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
moy_sales = defaultdict(list)
for r in all_rows:
    m = int(r["Date"][5:7])
    moy_sales[m].append(safe_int(r["Sales"]))

dashboard["seasonality"] = []
for m in sorted(moy_sales.keys()):
    dashboard["seasonality"].append({
        "month": month_names[m],
        "month_num": m,
        "avg_sales": round(mean(moy_sales[m]), 0),
    })

# ── 9. Forecast Data (last 60 days of test) ─────────────────────────────────
print("Computing forecast sample data...")
# Get per-day averages from test set for forecast chart
test_daily = defaultdict(list)
for r in test_rows:
    test_daily[r["Date"]].append(safe_int(r["Sales"]))
test_daily_avg = {d: round(mean(v), 0) for d, v in test_daily.items()}
test_sorted = sorted(test_daily_avg.items())

dashboard["forecast_sample"] = [{"date": d, "avg_sales": v} for d, v in test_sorted]

# ── 10. Model Comparison ────────────────────────────────────────────────────
print("Setting model comparison data...")
dashboard["models"] = {
    "baseline": {"name": "Historical Average", "mae": 1225.53, "rmse": 1653.96, "r2": 0.7070},
    "random_forest": {"name": "Random Forest", "mae": 932.49, "rmse": 1338.22, "r2": 0.8082},
    "xgboost": {"name": "Gradient Boosting", "mae": 745.88, "rmse": 1091.35, "r2": 0.8724},
}

# ── 11. Feature Importances ─────────────────────────────────────────────────
dashboard["feature_importance"] = {
    "xgboost": [
        {"feature": "Sales_Lag_14", "importance": 0.2884},
        {"feature": "RollingMean_7", "importance": 0.1413},
        {"feature": "RollingMean_30", "importance": 0.1140},
        {"feature": "Promo", "importance": 0.0942},
        {"feature": "RollingStd_7", "importance": 0.0918},
        {"feature": "Sales_Lag_1", "importance": 0.0899},
        {"feature": "RollingMean_14", "importance": 0.0624},
        {"feature": "DayOfWeek", "importance": 0.0380},
        {"feature": "Sales_Lag_7", "importance": 0.0229},
        {"feature": "Day", "importance": 0.0151},
        {"feature": "WeekOfYear", "importance": 0.0061},
        {"feature": "Month", "importance": 0.0059},
        {"feature": "Sales_Lag_30", "importance": 0.0056},
        {"feature": "IsWeekend", "importance": 0.0054},
        {"feature": "PromoDurationMonths", "importance": 0.0038},
    ],
    "random_forest": [
        {"feature": "RollingMean_30", "importance": 0.1779},
        {"feature": "Sales_Lag_14", "importance": 0.1651},
        {"feature": "RollingMean_7", "importance": 0.1441},
        {"feature": "RollingStd_7", "importance": 0.1436},
        {"feature": "RollingMean_14", "importance": 0.0974},
        {"feature": "Sales_Lag_1", "importance": 0.0946},
        {"feature": "Promo", "importance": 0.0602},
        {"feature": "Sales_Lag_30", "importance": 0.0351},
        {"feature": "DayOfWeek", "importance": 0.0293},
        {"feature": "Sales_Lag_7", "importance": 0.0242},
    ],
}

# ── 12. Holiday Impact & Competition ─────────────────────────────────────────
print("Computing holiday impact and competition...")
state_hol_s = defaultdict(list)
school_hol_s = defaultdict(list)
comp_dist_s = defaultdict(list)

# Load store competition
store_comp = {}
store_path = os.path.join(DATA_DIR, "store.csv")
if os.path.exists(store_path):
    with open(store_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            dist_str = r.get("CompetitionDistance", "0")
            if not dist_str: dist_str = "0"
            store_comp[r["Store"]] = safe_float(dist_str)

for r in all_rows:
    s = safe_int(r["Sales"])
    if r.get("Open", "1") == "0": continue
    
    sh = "None"
    if r.get("StateHoliday_a") == "1": sh = "Public Holiday"
    elif r.get("StateHoliday_b") == "1": sh = "Easter"
    elif r.get("StateHoliday_c") == "1": sh = "Christmas"
    state_hol_s[sh].append(s)
    
    sch = "School Holiday" if r.get("SchoolHoliday") == "1" else "No School Holiday"
    school_hol_s[sch].append(s)
    
    dist = store_comp.get(r["Store"], 0)
    if dist <= 1000: b = "< 1km"
    elif dist <= 5000: b = "1-5km"
    elif dist <= 10000: b = "5-10km"
    else: b = "> 10km"
    comp_dist_s[b].append(s)

dashboard["holidays"] = {
    "state": [{"StateHoliday": k, "Sales": round(mean(v), 0)} for k,v in state_hol_s.items()],
    "school": [{"SchoolHoliday_Str": k, "Sales": round(mean(v), 0)} for k,v in school_hol_s.items()]
}

buckets = ["< 1km", "1-5km", "5-10km", "> 10km"]
comp_list = []
for b in buckets:
    if b in comp_dist_s:
        comp_list.append({"Comp_Bucket": b, "Sales": round(mean(comp_dist_s[b]), 0)})
        
dashboard["competition"] = comp_list

# Save JSON
print(f"Saving dashboard data to {OUTPUT_FILE}...")
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(dashboard, f, indent=2)

print("DONE -- Dashboard data generated.")
