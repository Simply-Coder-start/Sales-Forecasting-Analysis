import streamlit as st

st.set_page_config(
    page_title="Rossmann Sales Forecaster",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("Navigation")
st.sidebar.info("Select a page above to navigate the dashboard.")

st.title("Rossmann Sales Forecasting Dashboard")
st.markdown("""
Welcome to the Rossmann Sales Forecasting dashboard! 

This tool is built on a robust **Gradient Boosting Regressor** to predict daily store sales based on historical momentum, promotions, and store characteristics.

👈 **Use the sidebar to navigate:**
- **Overview:** High-level executive metrics and model performance.
- **Future Forecasting:** Interactive simulator for recursive autoregressive predictions.
- **Model Explainability:** Dive into the key features driving the predictions.
""")
