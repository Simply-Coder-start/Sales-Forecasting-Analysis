# Rossmann Store Sales Forecasting

## Project Overview
This project presents a comprehensive machine learning pipeline designed to predict daily sales across 1,115 Rossmann drug stores. A unique constraint of this research was the utilization of a strict offline development environment, precluding the use of standard machine learning libraries such as `scikit-learn`, `pandas`, or `xgboost`. The entire predictive analytics framework—including data preprocessing, feature engineering, and modeling—was engineered from scratch utilizing the Python Standard Library.

## Dataset
The raw dataset contained 1,017,209 records. After removing non-operational (closed-store) records, the cleaned dataset contained 844,392 records.
- **Train Size:** 669,308
- **Test Size:** 175,084

## Key Findings & Business Insights
- **Promotional Power:** Active promotions drive a massive **38.77% uplift** in daily sales universally.
- **Top Predictor:** The most important feature for predicting future sales is **`Sales_Lag_14`** (Sales from exactly two weeks prior), capturing bi-weekly cyclic behavior.

## Custom Machine Learning Models
Three models were evaluated. The Random Forest and Gradient Boosting regressors were built from algorithmic first principles in pure Python.

| Model | MAE | RMSE | R² |
| :--- | :--- | :--- | :--- |
| **Historical Baseline** | 1,225.53 | 1,653.96 | 0.7070 |
| **Random Forest** | 932.49 | 1,338.22 | 0.8082 |
| **Gradient Boosting** | **745.88** | **1,091.35** | **0.8724** |

## Deliverables
- **Jupyter Notebooks:** Complete step-by-step pipeline from data cleaning to forecasting.
- **Dashboard:** Interactive HTML/JS business intelligence dashboard rendering pre-computed metrics.
- **Academic Report:** Full final-year university project documentation.

## Dashboard Screenshots
*(Note: Please drop your final application screenshots into the `screenshots/` directory)*

![Executive Overview](screenshots/executive_overview.png)
*Figure 1: Executive Overview Dashboard*

![Sales Analytics](screenshots/sales_analytics.png)
*Figure 2: Sales Analytics View*

![Forecast Center](screenshots/forecast_center.png)
*Figure 3: Interactive Forecasting Engine*
