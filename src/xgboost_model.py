"""
09_xgboost_model.py
===================
Trains a Gradient Boosting Regressor (XGBoost equivalent) to predict Sales.
Evaluates using MAE, RMSE, R² and compares against the baseline and Random Forest.
Generates feature importance ranking.

Implemented using ONLY Python standard library due to offline constraints.
"""

import csv
import os
import math
import random
from collections import defaultdict

# ──────────────────────────────────────────────────────────────────────────────
# PURE PYTHON GRADIENT BOOSTING (XGBOOST EQUIVALENT FOR MSE)
# ──────────────────────────────────────────────────────────────────────────────

class RegressionTree:
    def __init__(self, max_depth=3, min_samples_split=2):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.tree = None
        self.feature_importances_ = defaultdict(float)

    def fit(self, X, y):
        self.tree = self._build_tree(X, y, depth=0)

    def _build_tree(self, X, y, depth):
        num_samples = len(X)
        if num_samples == 0:
            return {"val": 0.0}
            
        mean_val = sum(y) / num_samples
        
        if depth >= self.max_depth or num_samples < self.min_samples_split:
            return {"val": mean_val}

        best_feat, best_val, best_mse_reduction, best_splits = self._best_split(X, y)
        
        if best_feat is None:
            return {"val": mean_val}
            
        self.feature_importances_[best_feat] += best_mse_reduction * num_samples
        
        left_X, left_y, right_X, right_y = best_splits
        
        left_node = self._build_tree(left_X, left_y, depth + 1)
        right_node = self._build_tree(right_X, right_y, depth + 1)
        
        return {
            "feat": best_feat,
            "val": best_val,
            "left": left_node,
            "right": right_node
        }

    def _best_split(self, X, y):
        best_mse_reduction = 0
        best_feat = None
        best_val = None
        best_splits = None
        
        current_mse = self._calc_mse(y)
        if current_mse == 0:
            return None, None, 0, None
            
        num_features = len(X[0])
        
        # Subsample features to speed up
        features_to_try = random.sample(range(num_features), min(int(math.sqrt(num_features)) + 5, num_features))
            
        for feat in features_to_try:
            # Subsample split values to speed up pure python execution
            unique_vals = list(set(row[feat] for row in X))
            if len(unique_vals) > 5:
                unique_vals = random.sample(unique_vals, 5)
                
            for val in unique_vals:
                left_X, left_y, right_X, right_y = [], [], [], []
                for r_x, r_y in zip(X, y):
                    if r_x[feat] <= val:
                        left_X.append(r_x)
                        left_y.append(r_y)
                    else:
                        right_X.append(r_x)
                        right_y.append(r_y)
                        
                if not left_y or not right_y:
                    continue
                    
                p_left = len(left_y) / len(y)
                p_right = len(right_y) / len(y)
                
                mse_left = self._calc_mse(left_y)
                mse_right = self._calc_mse(right_y)
                
                mse_reduction = current_mse - (p_left * mse_left + p_right * mse_right)
                
                if mse_reduction > best_mse_reduction:
                    best_mse_reduction = mse_reduction
                    best_feat = feat
                    best_val = val
                    best_splits = (left_X, left_y, right_X, right_y)
                    
        return best_feat, best_val, best_mse_reduction, best_splits

    def _calc_mse(self, y):
        n = len(y)
        if n == 0: return 0
        mean_y = sum(y) / n
        return sum((val - mean_y)**2 for val in y) / n

    def predict_row(self, x, node):
        if "feat" not in node:
            return node["val"]
        if x[node["feat"]] <= node["val"]:
            return self.predict_row(x, node["left"])
        else:
            return self.predict_row(x, node["right"])

class VanillaXGBoostRegressor:
    def __init__(self, n_estimators=15, max_depth=4, learning_rate=0.1):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.trees = []
        self.base_prediction = 0
        self.feature_importances_ = defaultdict(float)

    def fit(self, X, y):
        n_samples = len(X)
        self.base_prediction = sum(y) / n_samples
        
        current_preds = [self.base_prediction] * n_samples
        
        for i in range(self.n_estimators):
            # Calculate residuals (pseudo-residuals for MSE)
            residuals = [y[j] - current_preds[j] for j in range(n_samples)]
            
            tree = RegressionTree(max_depth=self.max_depth)
            
            # Use a slightly sampled subset for speed
            indices = random.sample(range(n_samples), min(n_samples, 5000))
            X_sample = [X[j] for j in indices]
            res_sample = [residuals[j] for j in indices]
            
            tree.fit(X_sample, res_sample)
            self.trees.append(tree)
            
            # Update predictions
            for j in range(n_samples):
                current_preds[j] += self.learning_rate * tree.predict_row(X[j], tree.tree)
                
            # Aggregate feature importances
            for feat, imp in tree.feature_importances_.items():
                self.feature_importances_[feat] += imp
                
        # Normalize importances
        total_imp = sum(self.feature_importances_.values())
        if total_imp > 0:
            for f in self.feature_importances_:
                self.feature_importances_[f] /= total_imp

    def predict(self, X):
        predictions = []
        for x in X:
            pred = self.base_prediction
            for tree in self.trees:
                pred += self.learning_rate * tree.predict_row(x, tree.tree)
            predictions.append(pred)
        return predictions

# ──────────────────────────────────────────────────────────────────────────────
# SCRIPT EXECUTION
# ──────────────────────────────────────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
TRAIN_FILE = os.path.join(DATA_DIR, "train_dataset.csv")
TEST_FILE = os.path.join(DATA_DIR, "test_dataset.csv")
REPORT_FILE = os.path.join(DATA_DIR, "xgboost_report.txt")
BASELINE_REPORT_FILE = os.path.join(DATA_DIR, "baseline_model_report.txt")
RF_REPORT_FILE = os.path.join(DATA_DIR, "random_forest_report.txt")

report_lines = []
def rprint(msg=""):
    print(msg)
    report_lines.append(msg)

rprint("=" * 80)
rprint("XGBOOST REGRESSOR TRAINING & EVALUATION (VANILLA PYTHON)")
rprint("=" * 80)

def safe_float(v):
    try:
        return float(v)
    except:
        return 0.0

rprint("\n[1/5] Loading datasets...")

train_X = []
train_y = []
test_X = []
test_y = []
feature_names = []
drop_cols = {"Sales", "Date", "Customers", "PromoInterval"}

# Load Train
with open(TRAIN_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    all_fields = list(reader.fieldnames)
    feature_names = [f for f in all_fields if f not in drop_cols]
    
    # We'll sample more data this time, e.g. 20,000 rows
    for i, row in enumerate(reader):
        if i % 25 == 0:
            train_X.append([safe_float(row[feat]) for feat in feature_names])
            train_y.append(safe_float(row["Sales"]))

rprint(f"      Train Set Sampled: {len(train_X):,} rows, {len(feature_names)} features")

# Load Test
with open(TEST_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        test_X.append([safe_float(row[feat]) for feat in feature_names])
        test_y.append(safe_float(row["Sales"]))
        
rprint(f"      Test Set: {len(test_X):,} rows")

rprint("\n[2/5] Prepared features and target.")

# 3. Train Model
rprint("\n[3/5] Training XGBoost (Gradient Boosting) Regressor (Pure Python)...")
random.seed(42)
# Using 20 trees, depth 5, learning rate 0.2
xgb_model = VanillaXGBoostRegressor(n_estimators=20, max_depth=5, learning_rate=0.2)
xgb_model.fit(train_X, train_y)
rprint("      Training complete.")

# 4. Evaluate Model
rprint("\n[4/5] Evaluating on test set...")
y_pred = xgb_model.predict(test_X)

n_test = len(test_y)
mae = sum(abs(a - p) for a, p in zip(test_y, y_pred)) / n_test
mse = sum((a - p)**2 for a, p in zip(test_y, y_pred)) / n_test
rmse = math.sqrt(mse)

mean_y = sum(test_y) / n_test
ss_tot = sum((a - mean_y)**2 for a in test_y)
ss_res = mse * n_test
r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

rprint("      XGBoost Metrics:")
rprint(f"      MAE:  {mae:,.2f}")
rprint(f"      RMSE: {rmse:,.2f}")
rprint(f"      R²:   {r2:.4f}")

# 5. Feature Importance
rprint("\n[5/5] Calculating Feature Importances...")
importances = xgb_model.feature_importances_
feature_imp = [(feature_names[i], imp) for i, imp in importances.items()]
feature_imp.sort(key=lambda x: x[1], reverse=True)

rprint("      Top 15 Important Features:")
rprint("      " + "-" * 40)
for i, (feat, imp) in enumerate(feature_imp[:15]):
    rprint(f"      {i+1:<2}. {feat:<25} {imp:.4f}")

# 6. Model Comparison
rprint("\n" + "=" * 80)
rprint("MODEL COMPARISON: BASELINE vs RANDOM FOREST vs XGBOOST")
rprint("=" * 80)

baseline_metrics = {}
if os.path.exists(BASELINE_REPORT_FILE):
    with open(BASELINE_REPORT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if "MAE:" in line:
                try: baseline_metrics['MAE'] = float(line.split(":")[1].replace(",", "").strip())
                except: pass
            elif "RMSE:" in line:
                try: baseline_metrics['RMSE'] = float(line.split(":")[1].replace(",", "").strip())
                except: pass
            elif "R²:" in line:
                try: baseline_metrics['R²'] = float(line.split(":")[1].replace(":", "").strip())
                except: pass
            elif "R:" in line:
                try: baseline_metrics['R²'] = float(line.split(":")[1].replace(":", "").strip())
                except: pass

rf_metrics = {}
if os.path.exists(RF_REPORT_FILE):
    with open(RF_REPORT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if "MAE:" in line:
                try: rf_metrics['MAE'] = float(line.split(":")[1].replace(",", "").strip())
                except: pass
            elif "RMSE:" in line:
                try: rf_metrics['RMSE'] = float(line.split(":")[1].replace(",", "").strip())
                except: pass
            elif "R²:" in line:
                try: rf_metrics['R²'] = float(line.split(":")[1].replace(":", "").strip())
                except: pass
            elif "R:" in line:
                try: rf_metrics['R²'] = float(line.split(":")[1].replace(":", "").strip())
                except: pass

rprint(f"      {'Metric':<10} | {'Baseline':>12} | {'Random Forest':>15} | {'XGBoost':>15}")
rprint("      " + "-" * 62)
rprint(f"      {'MAE':<10} | {baseline_metrics.get('MAE',0):>12.2f} | {rf_metrics.get('MAE',0):>15.2f} | {mae:>15.2f}")
rprint(f"      {'RMSE':<10} | {baseline_metrics.get('RMSE',0):>12.2f} | {rf_metrics.get('RMSE',0):>15.2f} | {rmse:>15.2f}")
rprint(f"      {'R²':<10} | {baseline_metrics.get('R²',0):>12.4f} | {rf_metrics.get('R²',0):>15.4f} | {r2:>15.4f}")

with open(REPORT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

rprint(f"\nReport saved to: {REPORT_FILE}")
rprint("\nDONE -- XGBoost model evaluation complete.")
