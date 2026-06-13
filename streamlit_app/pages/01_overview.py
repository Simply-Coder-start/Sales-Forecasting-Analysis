import streamlit as st

st.set_page_config(page_title="Executive Overview", page_icon="📊")

st.title("Executive Overview")
st.markdown("""
This dashboard is powered by a custom **Gradient Boosting Regressor** built entirely using the Python standard library. 
It replaces the historical baseline and Random Forest model, providing significantly better predictive accuracy by learning from the errors of previous trees in an iterative fashion.
""")

st.header("Model Performance")
st.markdown("The XGBoost equivalent model achieved the following performance on the hold-out test dataset:")

col1, col2, col3 = st.columns(3)
col1.metric(label="Mean Absolute Error (MAE)", value="745.88", delta="-479.65 vs Baseline", delta_color="inverse")
col2.metric(label="Root Mean Sq. Error (RMSE)", value="1,091.35", delta="-562.61 vs Baseline", delta_color="inverse")
col3.metric(label="R-squared (R²)", value="0.8724", delta="+0.1654 vs Baseline")

st.header("Key Findings")
st.info("""
- **Gradient Boosting is Superior:** Iteratively learning from past errors provides a robust 0.87 R².
- **Recent Memory Dominates:** Two-week and one-week sales momentum patterns heavily adjust predictions.
- **Promotional Lift:** Promotions act as a strong signal, closing the gap in forecasting during promotional periods.
""")
