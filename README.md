# 📈 Rossmann Store Sales Forecasting (Pure Python)

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Badge"/>
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit Badge"/>
  <img src="https://img.shields.io/badge/Machine%20Learning-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white" alt="ML Badge"/>
  <img src="https://img.shields.io/badge/Status-Complete-success?style=for-the-badge" alt="Status Badge"/>
</div>

<br/>

> **An end-to-end Machine Learning pipeline and custom Gradient Boosting predictive framework engineered entirely from scratch using only the Python Standard Library (no `scikit-learn`, `pandas`, or `xgboost`).**

---

## 🎯 Executive Summary
This repository presents a demand forecasting pipeline designed to predict daily sales across 1,115 Rossmann drug stores. A unique engineering constraint of this project was developing the solution in a strict offline, sandboxed environment. Consequently, the entire predictive analytics framework—including data cleaning, feature engineering, and model training—was implemented from first principles using the **Python Standard Library**.

* **Core Achievement:** Developed a custom sequential Gradient Boosting Regressor that reduces baseline Mean Absolute Error (MAE) by **39.1%**, achieving an $R^2$ of **0.8724** on the hold-out test set.
* **Hashed Temporal Engine:** Built a custom time-series engineering database utilizing dictionary lookups to achieve $O(1)$ fast lookups for lag and rolling calculations.
* **Autoregressive Forecasting:** Implemented a multi-step chronological recursive loop that rolls predictions forward to forecast sales up to 6 weeks in advance.

For detailed mathematical formulations and architectural details, see the **[Technical Report](reports/technical_report.md)**.

---

## 💡 Key Business Findings
* **Promotional Uplift:** Active promotions generate a massive **38.77% average sales lift** per day across the store network. Store Type A benefits most (+43.0% lift), while Store Type B experiences the lowest relative lift (+18.2%).
* **Temporal Driver:** The most important predictor of future sales is `Sales_Lag_14` (sales from exactly 14 days ago), capturing bi-weekly cyclic consumer purchasing patterns.
* **Assortment Impact:** Stores offering "Extra" assortment levels generate 30.4% higher average daily sales than those carrying only "Basic" assortments.

---

## 🤖 Model Performance

The custom-built models were trained on chronological subsets and validated against a strict hold-out test set (final 6 weeks of data, 175,084 records).

| Model | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) | R-squared ($R^2$) |
| :--- | :---: | :---: | :---: |
| **Historical Baseline** | €1,225.53 | €1,653.96 | 0.7070 |
| **Custom Random Forest** | €932.49 | €1,338.22 | 0.8082 |
| **Custom Gradient Boosting** | **€745.88** | **€1,091.35** | **0.8724** |

---

## 🖥️ Deliverables & Interactive Dashboards

This project includes two fully operational front-end analytics dashboards:

### 1. Zero-Dependency HTML Dashboard (`dashboard/rossmann_dashboard.html`)
A fully interactive, client-side business intelligence dashboard rendering pre-computed metrics and forecast simulators. By leveraging inline SVG graphics and embedded JSON data, it runs instantaneously in any web browser without requiring a backend server or external dependencies.
* **Accessing the Dashboard:** Simply clone the repository and open [dashboard/rossmann_dashboard.html](dashboard/rossmann_dashboard.html) in your browser.

### 2. Multi-Page Streamlit Application (`streamlit_app/`)
An enterprise-grade forecasting dashboard containing visual KPI cards, sales analytics pages, promotion insights, and an interactive forecasting simulator.
* **Run command:** `streamlit run streamlit_app/main.py`

<div align="center">
  <img src="screenshots/executive_overview.png" width="900" alt="Executive Overview"/>
  <br/><i>Executive Overview Dashboard</i><br/><br/>
  <img src="screenshots/forecast_center.png" width="900" alt="Forecast Center"/>
  <br/><i>Autoregressive Forecast Projection Simulator</i><br/><br/>
</div>

---

## 🛠️ Technology Stack
* **Core ML Engine:** Pure Python 3.x (Standard Library modules: `csv`, `math`, `collections`, `datetime`, `pickle`, `json`)
* **Interactive Frontend:** Streamlit
* **Data Visualization:** Plotly & HTML5 Inline SVGs
* **Validation & Logging:** Automated feature leakage checks and chronological boundary testing.

---

## 📂 Repository Structure

```text
Sales-Forecasting-Analysis/
├── dashboard/               # Interactive frontend deliverables
│   └── rossmann_dashboard.html # Zero-dependency HTML/JS dashboard (Tracked!)
├── data/                    # Dataset folder (Ignored from Git for size limits)
├── docs/                    # Architecture charts & academic archives
│   ├── archive/             # Preserved academic papers & slides (for personal reference)
│   │   ├── final_academic_report.md
│   │   ├── viva_prep_guide.md
│   │   ├── evaluator_review.md
│   │   └── viva_presentation_slides.md
│   └── architecture.png     # Pipeline flowchart
├── notebooks/               # Step-by-step Jupyter notebooks (Cleaning to Modeling)
│   ├── 01_Data_Loading_and_Cleaning.ipynb
│   ├── 02_EDA.ipynb
│   ├── 03_Feature_Engineering.ipynb
│   ├── 04_Model_Development.ipynb
│   └── 05_Forecasting_and_Dashboard.ipynb
├── reports/                 # Technical documentation & HTML EDA reports
│   ├── technical_report.md  # Deep dive into mathematics and pipeline design
│   └── eda_report.html      # Self-contained HTML EDA report
├── screenshots/             # Visual dashboard assets
├── src/                     # Modular source code
│   ├── data_loader.py       # Data loading and metadata merge
│   ├── data_cleaning.py     # Missing value imputation & outlier handling
│   ├── eda_analysis.py      # Statistical EDA computing & HTML report compilation
│   ├── feature_engineering.py# Temporal splits, O(1) lag hashing & rolling metrics
│   ├── leakage_validation.py# Feature validation & leakage checking
│   ├── train_test_split.py  # Chronological data splitting
│   ├── baseline_model.py    # Historical baseline builder
│   ├── random_forest.py     # Custom decision tree & Random Forest regressor
│   ├── xgboost_model.py     # Custom sequential Gradient Boosting regressor
│   └── generate_dashboard_data.py # Dashboard JSON pre-aggregator
├── streamlit_app/           # Interactive Streamlit application
├── requirements.txt         # Package dependencies
└── LICENSE.txt              # Project License
```

---

## 🚀 How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/Simply-Coder-start/Sales-Forecasting-Analysis.git
cd Sales-Forecasting-Analysis
```

### 2. Download the Dataset
The raw transaction files exceed GitHub's size limit and are ignored by Git. 
1. Download the dataset files (`train.csv` and `store.csv`) directly from the [Kaggle Rossmann Store Sales Competition](https://www.kaggle.com/c/rossmann-store-sales/data).
2. Place the CSV files directly inside the `data/` directory.

### 3. Install Dependencies
*(Note: The core ML engine runs in pure Python, but the visual dashboards require Streamlit, Plotly, and pandas)*
```bash
pip install -r requirements.txt
```

### 4. Run the Pipeline
You can run the steps sequentially to clean, engineer, train, and generate dashboard data:
```bash
python src/data_loader.py
python src/data_cleaning.py
python src/eda_analysis.py
python src/feature_engineering.py
python src/leakage_validation.py
python src/train_test_split.py
python src/xgboost_model.py
python src/generate_dashboard_data.py
```

### 5. Launch the Dashboards
* **To open the HTML dashboard:** Double click `dashboard/rossmann_dashboard.html` to run in any browser.
* **To run the Streamlit app:** 
  ```bash
  streamlit run streamlit_app/main.py
  ```
