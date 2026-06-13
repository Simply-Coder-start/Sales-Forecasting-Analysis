# Viva Presentation: Rossmann Sales Forecasting

*This document contains the exact slide titles, bullet points, and speaker notes required to build a 15-slide PowerPoint/Google Slides deck for your 10-15 minute viva presentation.*

---

## Slide 1: Title Slide
**Predictive Analytics for Retail Operations**
*A Machine Learning Approach to Rossmann Store Sales Forecasting*

- **Submitted By:** [Your Name]
- **Course:** BCA (Final Year AI/ML Project)
- **Institution:** [University Name]
- **Date:** [Date]

**🗣 Speaker Notes:**
> "Good morning respected examiners and faculty members. My final-year project is focused on Predictive Analytics for Retail Operations, specifically utilizing advanced Machine Learning techniques to forecast daily sales for the Rossmann drug store chain."

---

## Slide 2: Problem Statement
**The Challenge in Retail Forecasting**

- **The Problem:** Rossmann operates 1,115 stores, each with unique sales patterns influenced by promotions, holidays, and competition.
- **The Gap:** Traditional historical average forecasting leads to massive inaccuracies (overstocking or stockouts).
- **The Need:** A robust, data-driven machine learning model capable of handling non-linear temporal dynamics.
- **The Constraint:** Developing this solution entirely from scratch in an offline Python environment.

**🗣 Speaker Notes:**
> "Accurate sales forecasting is the backbone of retail profitability. The problem Rossmann faces is that simple historical averages fail to account for complex factors like promotions or school holidays. Our goal is to replace naive guessing with a robust machine learning framework, built entirely from scratch in pure Python."

---

## Slide 3: Objectives
**Project Goals & Deliverables**

- **Objective 1:** Build an end-to-end ML pipeline without relying on external libraries (`scikit-learn`, `pandas`).
- **Objective 2:** Engineer complex temporal features (lags, rolling statistics).
- **Objective 3:** Implement Custom Random Forest and Gradient Boosting algorithms.
- **Objective 4:** Develop a functional, dependency-free interactive business dashboard.

**🗣 Speaker Notes:**
> "The primary objectives were two-fold: First, to achieve high predictive accuracy. Second, to demonstrate deep algorithmic mastery by building these complex tree-based algorithms from mathematical first principles, culminating in a functional business dashboard."

---

## Slide 4: Dataset
**Rossmann Store Sales Data**

- **Scope:** 1,115 European drug stores.
- **Timeframe:** Jan 2013 to Jul 2015.
- **Total Records:** 844,392 daily transactional logs.
- **Key Features:**
  - `Sales`, `Customers`, `Open` status.
  - `Promo` (Active promotions).
  - `StateHoliday` & `SchoolHoliday`.
  - Store Metadata: `StoreType` (A, B, C, D) and `Assortment`.

**🗣 Speaker Notes:**
> "We utilized a highly complex dataset comprising over 844,000 records. It integrates daily transaction logs—like footfall and active promotions—with static store metadata, such as the distance to the nearest competitor."

---

## Slide 5: Data Cleaning
**Ensuring Algorithmic Robustness**

- **Outlier Removal:** Dropped records where stores were marked "Open" but recorded 0 sales.
- **Handling Missing Values:**
  - Continuous data (`CompetitionDistance`) imputed with the dataset **median**.
  - Categorical data (`Promo2Since`) defaulted to 0.
- **Data Integration:** Merged transaction data with static store metadata using primary keys.

**🗣 Speaker Notes:**
> "Garbage in equals garbage out. We cleaned the data by dropping anomalous records—such as stores reporting zero sales despite being open—and aggressively imputed missing competition metadata using median values to prevent skewing."

---

## Slide 6: Exploratory Data Analysis (EDA)
**Key Business Insights**

- **Promotional Power:** Active promotions drive a massive **~23% uplift** in daily sales universally.
- **Seasonal Dominance:** December generates peak revenue due to holiday shopping behaviors.
- **Store Typology:**
  - **Type B:** Highest absolute daily sales.
  - **Type D:** Highest average spend per customer.
- **Weekly Trends:** Mondays hold the peak sales volume, while Saturdays drop significantly.

**🗣 Speaker Notes:**
> "Our EDA uncovered immediate business value. We proved mathematically that active promotions drive a 23% sales uplift. We also mapped strong annual seasonality peaking in December and identified that Store Type B dominates overall revenue."

---

## Slide 7: Feature Engineering
**Translating Time-Series to Supervised Learning**

- **Temporal Parsing:** Decomposed string dates into `Year`, `Month`, `DayOfWeek`, `IsWeekend`.
- **Lag Features:** 
  - Created historical anchors: `Sales_Lag_7`, `Sales_Lag_14`, `Sales_Lag_30`.
- **Rolling Statistics:** 
  - Computed short-term momentum: `RollingMean_7` and `RollingStd_7`.
- **Constraint Handling:** Achieved $O(1)$ fast lookups using native Python dictionary hashing.

**🗣 Speaker Notes:**
> "Machine learning models cannot naturally read dates. We engineered time-series features by calculating 'lags'—such as sales from exactly 14 days prior—and rolling averages to capture short-term momentum. We used Python dictionaries to ensure fast lookups."

---

## Slide 8: Train/Test Split & Sampling
**Chronological Validation Strategy**

- **Chronological Split:** Random splitting causes temporal data leakage. We reserved the final 6 weeks (175,084 rows) as a strict chronological test set.
- **Deterministic Sampling:** 
  - Due to pure-Python limitations, the algorithm trained on a stratified sample of 26,773 records.
  - Test set was evaluated on the **full** 175,000+ records.
- **Autoregressive Loop:** Predictions for $T+1$ were fed back into the loop to generate lag features for predicting $T+2$.

**🗣 Speaker Notes:**
> "In time-series, random splitting is a fatal flaw. We strictly trained on past data to predict the final 6 weeks. To accommodate the heavy computational load of pure Python, we trained on a 26,000-row sample, but validated against the full 175,000-row test set."

---

## Slide 9: Baseline Model
**Historical Average Benchmark**

- **Methodology:** Predicted sales simply by taking the historical mean for a specific store on a specific day of the week.
- **Results:**
  - $R^2$: 0.7070
  - MAE: 1,225.53
  - RMSE: 1,653.96
- **Conclusion:** Serves as the mathematical floor. Any complex ML model must significantly beat an MAE of €1,225 to justify its usage.

**🗣 Speaker Notes:**
> "To prove our ML models were actually working, we established a naive baseline: just guessing the historical average for that day of the week. The baseline had an MAE of roughly 1,225 Euros."

---

## Slide 10: Random Forest (Custom Implementation)
**Bootstrap Aggregation**

- **Algorithm:** Custom-built ensemble of decision trees.
- **Mechanism:** Trains multiple deep trees in parallel on random subsets of data to reduce variance and prevent overfitting.
- **Splitting Criterion:** Evaluated nodes mathematically to maximize Mean Squared Error (MSE) reduction.
- **Results:**
  - $R^2$: 0.8082
  - MAE: 932.49

**🗣 Speaker Notes:**
> "Our first advanced model was a Random Forest, built entirely from scratch. By training multiple decision trees on random subsets of the data and averaging their outputs, we successfully reduced the MAE to 932 Euros."

---

## Slide 11: Gradient Boosting (Custom Implementation)
**Sequential Error Correction**

- **Algorithm:** Custom-built boosting architecture.
- **Mechanism:** Trees are built sequentially. Tree 2 predicts the *errors* (pseudo-residuals) made by Tree 1. 
- **Hyperparameters:** `n_estimators = 20`, `max_depth = 5`, `learning_rate = 0.2`.
- **Results:**
  - $R^2$: **0.8724**
  - MAE: **745.88**

**🗣 Speaker Notes:**
> "Our flagship model was the Gradient Boosting algorithm. Unlike Random Forest, this model learns sequentially, aggressively targeting the residual errors of the previous trees. It was our highest-performing architecture."

---

## Slide 12: Results Comparison & Feature Importance
**Gradient Boosting Wins**

| Model | MAE (€) | RMSE (€) | $R^2$ |
| :--- | :--- | :--- | :--- |
| Historical Baseline | 1,225 | 1,653 | 0.70 |
| Random Forest | 932 | 1,338 | 0.80 |
| **Gradient Boosting** | **745** | **1,091** | **0.87** |

**Top 3 Features:**
1. `Sales_Lag_14` (Captures bi-weekly rhythm)
2. `RollingMean_7` (Captures immediate momentum)
3. `Promo` (Highest non-temporal business driver)

**🗣 Speaker Notes:**
> "Comparing the models, Gradient Boosting reduced the baseline error by a massive 39%, achieving an R-squared of 0.87. We also found that the 14-day sales lag and active promotions were the most dominant predictors of future sales."

---

## Slide 13: Dashboard Architecture
**Deploying Actionable Insights**

- **Requirement:** A highly interactive, zero-dependency business intelligence UI.
- **Implementation:** Self-contained HTML/JS dashboard rendering pre-computed metrics.
- **Key Modules:**
  - **Executive Overview:** High-level KPIs and revenue trackers.
  - **Forecast Center:** Autoregressive simulator comparing test actuals to predicted trends.
  - **Promo Insights:** Quantifying ROI across Store Types.

**🗣 Speaker Notes:**
> "Machine learning is useless if business stakeholders can't access it. We built a fully functional, self-contained HTML dashboard that visualizes these KPIs, allowing managers to see precise promo ROI and forecast trajectories without any software installations."

---

## Slide 14: Conclusion
**Project Summary**

- **Success:** Proved that state-of-the-art predictive accuracy ($R^2$ = 0.87) can be achieved using foundational mathematics without reliance on heavy external libraries like `scikit-learn` or `XGBoost`.
- **Business Value:** Accurate forecasting allows Rossmann to reduce stockouts, optimize staff scheduling, and strategically deploy promotional campaigns in Store Type A for maximum ROI.
- **Technical Growth:** Mastered data structures, recursive tree building, and autoregressive time-series loops.

**🗣 Speaker Notes:**
> "To conclude, we successfully engineered a highly accurate forecasting system from algorithmic first principles. By reducing the prediction error to just 745 Euros, Rossmann can confidently optimize inventory and staffing."

---

## Slide 15: Future Scope
**Next Steps for Expansion**

- **Cloud Deployment:** Migrate the algorithms to leverage vectorized C-backends (`pandas`, `numpy`) for full 844k dataset training.
- **Hyperparameter Optimization:** Implement Grid Search CV for optimal tree depth and learning rates.
- **External Data Integration:** Incorporate macro-economic variables, local weather APIs, and Google Trends search volume.
- **Deep Learning:** Explore LSTM (Long Short-Term Memory) networks for advanced sequential memory.

**🗣 Speaker Notes:**
> "In the future, migrating this logic to a cloud environment would allow us to train on the full 844,000 row dataset using optimized libraries. Furthermore, integrating local weather data or Deep Learning algorithms like LSTMs could push the accuracy even higher. Thank you, I am now open to questions."
