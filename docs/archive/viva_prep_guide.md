# University Examiner Viva Preparation Guide: Rossmann Sales Forecasting

This guide contains 50 rigorous viva questions spanning from basic concepts to advanced cross-examinations, complete with detailed model answers tailored specifically to your custom Python implementation and offline constraints.

---

## 1. Machine Learning & Modeling

### Easy
**Q1. What is the difference between a Random Forest and Gradient Boosting?**
**Answer:** Random Forest is a *bagging* ensemble method that builds multiple decision trees independently in parallel and averages their predictions. Gradient Boosting is a *boosting* ensemble method that builds trees sequentially, where each new tree tries to correct the errors (residuals) made by the previous trees.

**Q2. Why did you use Regression Trees instead of Classification Trees?**
**Answer:** Sales forecasting predicts a continuous numerical value (daily sales in Euros) rather than a discrete category (e.g., Yes/No). Therefore, Regression Trees, which use Mean Squared Error (MSE) to make splits, are the mathematically correct choice.

**Q3. What do MAE, RMSE, and $R^2$ represent?**
**Answer:** MAE (Mean Absolute Error) is the average absolute difference between predicted and actual sales. RMSE (Root Mean Squared Error) is the square root of the average squared differences, which heavily penalizes large errors. $R^2$ (Coefficient of Determination) measures the proportion of variance in the target variable explained by the model; our 0.87 means the model explains 87% of the variance in sales.

**Q4. Why is your baseline model important?**
**Answer:** The Historical Average Baseline acts as a benchmark. If a complex machine learning model cannot beat a simple historical average, the complexity is unjustified. Our Gradient Boosting model reduced the baseline MAE by 39%, proving its value.

### Medium
**Q5. Explain how your custom Gradient Boosting algorithm minimizes loss.**
**Answer:** Our custom algorithm uses Mean Squared Error as the loss function. At each iteration, we calculate the negative gradient of the loss function, which mathematically equals the *pseudo-residuals* (Actual - Predicted). We then train a new decision tree to predict these residuals, multiply the tree's output by a learning rate, and add it to our running prediction.

**Q6. What is the purpose of the learning rate in Gradient Boosting?**
**Answer:** The learning rate scales the contribution of each individual tree. A smaller learning rate means the model learns more slowly, making the ensemble more robust to overfitting but requiring more trees (`n_estimators`) to achieve the same accuracy.

**Q7. Since you didn't use scikit-learn, how did you evaluate splits in your custom tree?**
**Answer:** For every feature and every unique value of that feature, the algorithm calculates the Mean Squared Error of the left split and the right split. The split that yields the largest reduction in MSE (variance reduction) is chosen as the node.

### Hard
**Q8. Why did you sample 26,000 rows instead of using all 844,000 records?**
**Answer:** Because we implemented the algorithms in pure Python without vectorized C/C++ backends like `numpy` or `xgboost`, iterating over 844,000 rows for every possible split at every node of every tree became computationally intractable in our offline environment. The sampling was deterministic and stratified to capture enough temporal variance while keeping training times reasonable.

**Q9. If you had access to hyperparameter tuning, which parameters would you tune and how?**
**Answer:** I would use Grid Search with time-series cross-validation. For Gradient Boosting, I would tune `n_estimators` (number of trees), `max_depth` (tree complexity), and `learning_rate`. Generally, lowering the learning rate while increasing `n_estimators` yields better generalization.

**Q10. How does your model handle heteroscedasticity in the sales data?**
**Answer:** Tree-based models are non-parametric and naturally handle heteroscedasticity better than linear regression models, as they partition the feature space into regions and predict the mean of each region, making no assumptions about constant variance in the residuals.

---

## 2. Technical Implementation & Python

### Easy
**Q11. Why did you build the algorithms from scratch instead of using libraries?**
**Answer:** The project was developed in a strict offline environment where installing external packages like `pandas` and `scikit-learn` was impossible. This constraint forced a deeper understanding of the underlying mathematics and algorithms, requiring them to be built using only the Python Standard Library.

**Q12. How did you load and process the CSV data without pandas?**
**Answer:** We used the built-in `csv` module with `DictReader` to parse the files line-by-line, storing the data as lists of dictionaries and lists of lists, managing memory explicitly.

**Q13. How did you handle missing values in pure Python?**
**Answer:** We iterated through the dataset to compute medians and modes, and then ran a second pass to impute missing continuous variables (like `CompetitionDistance`) with the median, and categorical variables with 0 or the mode.

### Medium
**Q14. What data structures did you use for your Decision Tree?**
**Answer:** A recursive, nested dictionary/object structure. Each Node object contains the `feature_index` to split on, the `threshold` value, and references to `left` and `right` child Nodes. Leaf nodes simply store the predicted `value`.

**Q15. How do you prevent your recursive tree-building function from infinite recursion?**
**Answer:** By implementing stopping criteria: maximum depth (`max_depth`), minimum samples required to split (`min_samples_split`), and checking if all target values in the current node are identical.

**Q16. Why are `for` loops in pure Python slow, and how did it affect your project?**
**Answer:** Pure Python is dynamically typed and interpreted, meaning a standard `for` loop carries massive overhead compared to compiled C loops (which libraries like numpy use). This computational bottleneck restricted us to training on a ~3% sample of the total dataset.

### Hard
**Q17. Explain the Big-O time complexity of training your Random Forest.**
**Answer:** For each tree, at each node, we evaluate $F$ features over $N$ samples. Evaluating a split takes $O(N \log N)$ if sorting is required, or $O(N)$ if pre-sorted. For a tree of depth $D$, the complexity is roughly $O(D \cdot F \cdot N \log N)$. With $T$ trees in the forest, it scales linearly by $T$.

**Q18. How did you ensure fast lookups when calculating lag features without pandas `shift()`?**
**Answer:** We utilized Python dictionaries (Hash Maps) using `(Store_ID, Date)` tuples as keys. This provided $O(1)$ average time complexity for lookups when retrieving sales from $T-14$ days ago, compared to $O(N)$ if we had searched through lists.

---

## 3. Feature Engineering & Time Series

### Easy
**Q19. What is a Lag Feature?**
**Answer:** A lag feature uses the value of the target variable from a prior time step. For example, `Sales_Lag_14` is the sales volume from exactly exactly two weeks prior to the target prediction date.

**Q20. Why is `Sales_Lag_14` the most important feature?**
**Answer:** Retail sales follow strong weekly cycles. A 14-day lag captures both the specific day of the week (e.g., a Monday vs. a Sunday) and the immediate recent performance trend of that specific store.

**Q21. How did you extract temporal features from the raw date string?**
**Answer:** We used Python's `datetime` module to parse the "YYYY-MM-DD" string and extract the year, month, day, day of the week, and week of the year as integer features.

### Medium
**Q22. What is a Rolling Statistic?**
**Answer:** A rolling statistic is an aggregate measure over a sliding window. We calculated `RollingMean_7` (average sales over the past 7 days) and `RollingStd_7` (volatility) to capture short-term momentum and sales stability.

**Q23. Why didn't you use `Sales_Lag_1` for forecasting?**
**Answer:** Because we often need to forecast several days or weeks in advance. If we are predicting day $T+7$, we do not know the actual sales for day $T+6$, meaning we cannot use `Lag_1` without a highly complex autoregressive simulation. Using `Lag_14` ensures the data is strictly historical when predicting up to two weeks out.

**Q24. How do you prevent "Data Leakage" in feature engineering?**
**Answer:** By ensuring that when predicting for Day $T$, all lag and rolling features are calculated using strictly data from $T-1$ or earlier. If future data leaks into the training features, the model will report artificially high accuracy but fail in production.

### Hard
**Q25. How do you forecast the entire 6-week test set when lag features depend on prior days?**
**Answer:** We used an **autoregressive loop**. We predict Day 1 of the test set, append that prediction to our historical dataset, recalculate the rolling means and lags using that prediction, and then use those newly engineered features to predict Day 2. We repeat this recursively.

**Q26. What happens if the model makes a large error on Day 1 in an autoregressive loop?**
**Answer:** It causes *error propagation*. Because Day 2's prediction relies on Day 1's output, an error on Day 1 will skew the features for Day 2, causing the errors to compound over the 6-week horizon. This is the biggest risk in recursive forecasting.

---

## 4. Business Analytics & Data EDA

### Easy
**Q27. According to your EDA, what is the impact of promotions?**
**Answer:** Active promotions increase average daily sales by approximately 23%. This is a universal trend, though the specific uplift varies by store type.

**Q28. Which month had the highest sales and why?**
**Answer:** December showed the strongest seasonality with significantly higher sales, driven entirely by the holiday shopping season.

**Q29. What did you discover about Store Types?**
**Answer:** Store Type B generates the highest absolute daily revenue, but Store Type D has the highest average spend per customer. 

### Medium
**Q30. Why do some stores record zero sales?**
**Answer:** Most zero-sales records correlate with the `Open = 0` flag (e.g., closed for Sundays or state holidays). However, we found anomalies where stores were marked as open but recorded zero sales. We removed these as outliers to prevent skewing the model.

**Q31. How does the distance to competitors (`CompetitionDistance`) affect sales?**
**Answer:** Interestingly, the impact was non-linear. In some cases, stores clustered tightly with competitors saw high sales due to being in high-foot-traffic retail hubs, defying the assumption that competitors simply steal sales.

**Q32. If a store has missing competitor information, why impute with the median?**
**Answer:** The median is robust to outliers. If we used the mean, one store with a competitor 500km away could drastically skew the imputed value.

### Hard
**Q33. If Promotions are so effective, why shouldn't Rossmann run promotions 365 days a year?**
**Answer:** Running continuous promotions leads to customer fatigue and expectation—customers will refuse to buy at full price, eroding profit margins. Promotions work because they are temporary injections of urgency.

**Q34. Based on your model, what is the best strategy for a struggling Store Type C?**
**Answer:** Since our EDA showed Extra assortment (Assortment B) and Promotions yield high ROI, a struggling Type C store should shift inventory towards a wider assortment and heavily utilize targeted promotions to drive foot traffic.

---

## 5. Dashboard & Deployment

### Easy
**Q35. What is the purpose of the dashboard?**
**Answer:** Machine learning models output raw arrays. A dashboard translates these complex mathematical predictions into visual, actionable insights (KPIs, charts) that business stakeholders (like regional managers) can easily understand and act upon.

**Q36. Why did you use HTML/JS instead of a framework like Streamlit?**
**Answer:** We designed a Streamlit architecture, but due to strict offline environment constraints preventing dependency installation, we pivoted to a dependency-free HTML/JS implementation using inline SVGs to ensure the dashboard was instantly deployable and viewable in any browser.

**Q37. What KPIs did you prioritize on the Executive Overview page?**
**Answer:** Total Revenue, Average Daily Sales, Promotion Lift Percentage, and Model Accuracy ($R^2$). 

### Medium
**Q38. How does your HTML dashboard get its data if there is no backend server?**
**Answer:** We wrote a Python script (`generate_dashboard_data.py`) that pre-aggregates all the metrics, trends, and model results into a static `dashboard_data.json` file. This JSON is embedded directly into the HTML file, allowing it to render instantly without a backend.

**Q39. Explain the "Forecast Center" section of the dashboard.**
**Answer:** The Forecast Center visualizes the test-period actuals versus the model's predictions as a time-series line chart, proving visually that the model successfully captures the weekly sales rhythm and seasonal peaks.

### Hard
**Q40. What would be required to deploy this model in a real-time production environment?**
**Answer:** We would need to serialize (pickle) the trained model, expose it via a REST API (using Flask or FastAPI), set up a daily CRON job to ingest the previous day's sales to update the lag features, and host the Streamlit dashboard on a cloud platform like AWS or GCP connected to the API.

---

## 6. Difficult Cross-Questions (Stress Tests)

**Q41. If your baseline model achieves an $R^2$ of 0.70, why go through the massive effort of building a Gradient Boosting algorithm just to reach 0.87? Is the ROI worth it?**
**Answer:** In retail at scale, a 17% increase in explained variance translates to predicting tens of millions of Euros more accurately across 1,115 stores. This drastically reduces safety stock holding costs and prevents stockouts, easily justifying the engineering effort.

**Q42. You claim Gradient Boosting is better than Random Forest. Could your Random Forest have performed better if you just tuned it or gave it deeper trees?**
**Answer:** It's possible that a tuned Random Forest could close the gap. However, mathematically, Gradient Boosting typically outperforms Random Forests on structured tabular data because it actively learns from the exact mistakes of prior trees rather than relying entirely on random chance and averaging.

**Q43. Your model was trained on 26,000 rows. How can you confidently say it generalizes to 844,000 rows?**
**Answer:** We used a deterministic, stratified sampling method ensuring temporal spread across the years. The fact that the model achieved an $R^2$ of 0.87 on the massive *unsampled* 175,000-row test set proves it generalized perfectly and did not overfit the small training sample.

**Q44. What happens to your `Sales_Lag_14` feature if a store closes for exactly two weeks due to renovations?**
**Answer:** The lag feature would pull a value of 0, causing the model to incorrectly predict near-zero sales upon reopening. To handle this in production, we would need to implement an imputation strategy for lag variables based on historical rolling averages rather than hard 14-day lookbacks when a store is closed.

**Q45. You used MAE and RMSE. When would you prefer RMSE over MAE in a business context?**
**Answer:** RMSE heavily penalizes large errors. In retail, if underpredicting sales by 500 units causes a stockout and furious customers, while underpredicting by 50 units ten times is manageable, RMSE is the better metric because it punishes that massive 500-unit miss exponentially.

**Q46. Explain the concept of Bootstrap Aggregation in your Random Forest.**
**Answer:** Bootstrap aggregation (bagging) means we create random subsets of the training data with replacement. Each decision tree is trained on a different random subset. This decorrelates the trees, reducing variance and preventing overfitting.

**Q47. If you could add one external dataset to improve this model, what would it be and why?**
**Answer:** Local weather data. Rain or snow heavily impacts foot traffic. Adding precipitation and temperature features would likely explain much of the variance currently missed by the model.

**Q48. In your pure Python implementation, why use dictionaries instead of lists for your dataset?**
**Answer:** Dictionaries allow lookup by string keys (column names), which makes the code readable, but more importantly, dictionaries provide $O(1)$ hashing lookups. If we used lists to find previous dates for lag features, the $O(N)$ linear scans would have made the script take weeks to run.

**Q49. Why is evaluating a time-series model with random Train/Test Split (like $80/20$ split) a fatal mistake?**
**Answer:** Because time flows sequentially. If you randomly split the data, you might use data from December 2014 to predict sales in January 2013. This is temporal data leakage. You must split chronologically (e.g., Train on 2013-2014, Test on 2015).

**Q50. Ultimately, what is the biggest flaw in your methodology, and how would you fix it?**
**Answer:** The biggest flaw is the reliance on a fixed 14-day and 30-day lag/rolling window approach fed into an autoregressive loop. Errors propagate heavily. Fixing this would require using deep learning sequence models like LSTMs or Temporal Fusion Transformers, which are explicitly designed to maintain long-term internal temporal memory rather than relying on manually engineered rolling features.
