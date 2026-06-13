import streamlit as st
import pandas as pd

st.set_page_config(page_title="Model Explainability", page_icon="🧠")

st.title("🧠 Model Explainability")
st.markdown("Understand what drives the Gradient Boosting predictions.")

# Pre-computed feature importances from the XGBoost script
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

df_imp = pd.DataFrame(list(importances.items()), columns=["Feature", "Importance Score"])
df_imp = df_imp.sort_values(by="Importance Score", ascending=True) # Ascending for horizontal bar chart
df_imp.set_index("Feature", inplace=True)

st.subheader("Top 15 Predictive Features")
st.bar_chart(df_imp, horizontal=True)

st.markdown("""
### Insights:
- **`Sales_Lag_14` dominates:** The model leans heavily on the exact same day two weeks prior.
- **Rolling Momentum:** Features like `RollingMean_7` and `RollingMean_30` provide a smoothed baseline that mitigates day-to-day noise.
- **Promo:** Promotions rank as the 4th most important signal, directly validating our EDA finding that promotions cause massive sales uplifts.
""")
