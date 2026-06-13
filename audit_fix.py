import os
import re

BASE_DIR = r"d:\Sales Forecasting Analysis\streamlit_app\pages"

def replace_in_file(filename, old_str, new_str):
    filepath = os.path.join(BASE_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace(old_str, new_str)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

# 1. Update 03_explain.py content
old_explain = """# Pre-computed feature importances from the XGBoost script
importances = {
    "Sales_Lag_14": 0.2884,
    "RollingMean_7": 0.1413,
    "RollingMean_30": 0.1140,
    "Promo": 0.0942,
    "RollingStd_7": 0.0918,
    "Sales_Lag_1": 0.0899,
    "RollingMean_14": 0.0624,
    "DayOfWeek": 0.0380,
    "Sales_Lag_7": 0.0229,
    "Day": 0.0151,
    "WeekOfYear": 0.0061,
    "Month": 0.0059,
    "Sales_Lag_30": 0.0056,
    "IsWeekend": 0.0054,
    "PromoDurationMonths": 0.0038
}

df_imp = pd.DataFrame(list(importances.items()), columns=["Feature", "Importance Score"])"""

new_explain = """import json
import os

@st.cache_data
def load_dashboard_data():
    json_path = os.path.join("data", "dashboard_data.json")
    if not os.path.exists(json_path):
        json_path = os.path.join("..", "data", "dashboard_data.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

data = load_dashboard_data()

if data:
    feat_data = data["feature_importance"]["xgboost"]
    df_imp = pd.DataFrame(feat_data)
    df_imp.rename(columns={"feature": "Feature", "importance": "Importance Score"}, inplace=True)
else:
    # Fallback Pre-computed feature importances
    importances = {
        "Sales_Lag_14": 0.2884,
        "RollingMean_7": 0.1413,
        "RollingMean_30": 0.1140,
        "Promo": 0.0942,
        "RollingStd_7": 0.0918,
        "Sales_Lag_1": 0.0899,
        "RollingMean_14": 0.0624,
        "DayOfWeek": 0.0380,
        "Sales_Lag_7": 0.0229,
        "Day": 0.0151,
        "WeekOfYear": 0.0061,
        "Month": 0.0059,
        "Sales_Lag_30": 0.0056,
        "IsWeekend": 0.0054,
        "PromoDurationMonths": 0.0038
    }
    df_imp = pd.DataFrame(list(importances.items()), columns=["Feature", "Importance Score"])"""

replace_in_file("03_explain.py", old_explain, new_explain)

# 2. Update 02_forecasting.py content
old_fcst = """# --- Dataset Summary Card ---
st.subheader("Dataset Summary")
with st.container():
    ds_col1, ds_col2, ds_col3, ds_col4 = st.columns(4)
    ds_col1.metric("Raw Records", "1,017,209")
    ds_col2.metric("Cleaned Records", "844,392")
    ds_col3.metric("Stores", "1,115")
    ds_col4.metric("Date Range", "Jan 2013 – Jul 2015")
st.divider()

# --- Model Information Card ---
st.subheader("Model Information")
with st.container():
    info_col1, info_col2, info_col3, info_col4, info_col5, info_col6 = st.columns(6)
    info_col1.metric("Model", "Custom GBM")
    info_col2.metric("Train Rows", "669,308")
    info_col3.metric("Test Rows", "175,084")
    info_col4.metric("MAE", "745.88")
    info_col5.metric("RMSE", "1,091.35")
    info_col6.metric("R²", "0.8724")
st.divider()"""

new_fcst = """import json
import os

@st.cache_data
def load_dashboard_data():
    json_path = os.path.join("data", "dashboard_data.json")
    if not os.path.exists(json_path):
        json_path = os.path.join("..", "data", "dashboard_data.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

data = load_dashboard_data()

# --- Dataset Summary Card ---
st.subheader("Dataset Summary")
with st.container():
    ds_col1, ds_col2, ds_col3, ds_col4 = st.columns(4)
    if data:
        ds_col1.metric("Raw Records", "1,017,209")
        ds_col2.metric("Cleaned Records", f"{data['overview']['total_records']:,}")
        ds_col3.metric("Stores", f"{data['overview']['num_stores']:,}")
        ds_col4.metric("Date Range", "Jan 2013 – Jul 2015")
    else:
        ds_col1.metric("Raw Records", "1,017,209")
        ds_col2.metric("Cleaned Records", "844,392")
        ds_col3.metric("Stores", "1,115")
        ds_col4.metric("Date Range", "Jan 2013 – Jul 2015")
st.divider()

# --- Model Information Card ---
st.subheader("Model Information")
with st.container():
    info_col1, info_col2, info_col3, info_col4, info_col5, info_col6 = st.columns(6)
    info_col1.metric("Model", "Custom GBM")
    info_col2.metric("Train Rows", "669,308")
    info_col3.metric("Test Rows", "175,084")
    if data:
        info_col4.metric("MAE", f"{data['models']['xgboost']['mae']}")
        info_col5.metric("RMSE", f"{data['models']['xgboost']['rmse']}")
        info_col6.metric("R²", f"{data['models']['xgboost']['r2']}")
    else:
        info_col4.metric("MAE", "745.88")
        info_col5.metric("RMSE", "1,091.35")
        info_col6.metric("R²", "0.8724")
st.divider()"""

replace_in_file("02_forecasting.py", old_fcst, new_fcst)

# 3. Rename files
def safe_rename(old, new):
    old_p = os.path.join(BASE_DIR, old)
    new_p = os.path.join(BASE_DIR, new)
    if os.path.exists(old_p) and not os.path.exists(new_p):
        os.rename(old_p, new_p)

safe_rename("01_overview.py", "01_Executive_Overview.py")
safe_rename("02_forecasting.py", "04_Forecast_Center.py")
safe_rename("03_explain.py", "05_Model_Insights.py")
safe_rename("04_analytics.py", "03_Promotion_Insights.py")

print("Audit fixes complete.")
