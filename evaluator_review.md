# University Examiner Review: Rossmann Sales Forecasting Project

## 1. Critical Issues & Factual Inconsistencies

1. **Dataset Size vs. Training Size Discrepancy:** The abstract and dataset description claim the use of 844,392 records. However, the actual Python implementation used a deterministically sampled subset (13,387 rows for Random Forest, 26,773 rows for Gradient Boosting) due to the pure-Python execution constraint. Claiming the model was trained on the full dataset is a significant factual inaccuracy.
2. **Library vs. Custom Implementation Misrepresentation:** The Literature Review mentions XGBoost and LightGBM. While theoretically accurate, the actual implementation was a custom, vanilla Python `GradientBoostingRegressor` built from scratch without external dependencies (`scikit-learn`, `xgboost`). Failing to state this undermines the technical achievement of building the algorithm from scratch and misrepresents the methodology.
3. **Hyperparameter Tuning Omission:** The report does not mention that hyperparameter tuning was entirely bypassed. The models were run with fixed parameters (e.g., `n_estimators=20`, `max_depth=5`).
4. **Forecasting Methodology Unexplained:** The report states the model predicts sales "up to six weeks in advance," but fails to explain the complex autoregressive (recursive) loop required to project lag features (`Sales_Lag_14`) into the future. 

## 2. Recommended Fixes

- **Embrace the Constraint:** Turn the inability to use `scikit-learn` into a massive positive. Explicitly state that "due to strict offline environment constraints, the Gradient Boosting algorithm was engineered entirely from scratch using the Python Standard Library." This shows deep algorithmic understanding, highly valued in BCA AI/ML projects.
- **Clarify the Sampling Strategy:** Explicitly document the stratified sampling technique used to bypass the computational limits of native Python for loop execution.
- **Detail the Autoregressive Loop:** Add a subsection explaining how $T+1$ predictions are fed back into the rolling and lag feature calculations to predict $T+2$.

## 3. Missing Content Expected in BCA Final-Year Projects

- **System Architecture:** A high-level overview of how the data flows from raw CSVs $\rightarrow$ Preprocessing $\rightarrow$ Pure Python Model $\rightarrow$ Streamlit/HTML Dashboard.
- **Workflow / Flowchart Description:** Textual representation of the algorithmic steps.
- **Hardware/Software Environment Setup:** Detailing the offline sandbox nature.
- **Limitations Section:** Directly addressing the lack of hyperparameter tuning and full dataset utilization.

## 4. Potential Viva Questions You May Be Asked

1. *"You mentioned you didn't use scikit-learn or XGBoost. Can you explain the mathematical difference between your Random Forest and Gradient Boosting implementations?"*
2. *"Your model heavily relies on `Sales_Lag_14`. How do you predict day 15 if you don't have the actual sales data for day 1?"* (Answer: Autoregressive recursive forecasting—using your predictions as the actuals to roll forward).
3. *"Why did you sample only 26,000 rows out of 844,000, and how does this impact the model's ability to capture yearly seasonality?"*
4. *"What is the loss function used in your Gradient Boosting implementation, and how do you calculate the pseudo-residuals?"*

## 5. Grading

| Category | Score / 10 | Remarks |
| :--- | :---: | :--- |
| Problem Statement | 9/10 | Clear and well-defined business problem. |
| Dataset Selection | 9/10 | Excellent, high-complexity Kaggle dataset. |
| Data Cleaning | 8/10 | Solid approach to handling open/closed days and missing metadata. |
| EDA | 9/10 | Uncovered highly actionable business metrics (promo lift, store types). |
| Feature Eng. | 10/10 | Creating recursive lags without pandas is a huge technical achievement. |
| Modeling | 7/10 | (Initial Report) 7/10 because the report hid the custom Python implementation. With the custom implementation acknowledged, it's a 10/10 technical flex. |
| Evaluation | 8/10 | Solid use of MAE, RMSE, and $R^2$. |
| Dashboard | 9/10 | Impressive pivot to a dependency-free HTML dashboard using inline SVGs. |
| Documentation | 6/10 | Initial report had factual inconsistencies regarding dataset size and libraries. |

**Final Academic Score:** 8.3 / 10 (A-)  
**Final Portfolio Score:** 9.0 / 10 (Highly impressive due to pure Python implementation).
