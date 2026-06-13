"""
08_random_forest_model.py
=========================
Trains a Random Forest Regressor to predict Sales.
Evaluates using MAE, RMSE, R² and compares against the baseline model.
Generates feature importance ranking.

Implemented using ONLY Python standard library.
"""

import csv
import os
import math
import random
from collections import defaultdict

# ──────────────────────────────────────────────────────────────────────────────
# PURE PYTHON RANDOM FOREST IMPLEMENTATION
# ──────────────────────────────────────────────────────────────────────────────

class RegressionTree:
    def __init__(self, max_depth=5, min_samples_split=2, max_features=None):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features
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
        features_to_try = list(range(num_features))
        if self.max_features is not None:
            features_to_try = random.sample(features_to_try, min(self.max_features, num_features))
            
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

class VanillaRandomForestRegressor:
    def __init__(self, n_estimators=10, max_depth=5, min_samples_split=2, max_features=None):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features
        self.trees = []
        self.feature_importances_ = defaultdict(float)

    def fit(self, X, y):
        n_samples = len(X)
        for i in range(self.n_estimators):
            # Bootstrap sample
            indices = [random.randint(0, n_samples - 1) for _ in range(n_samples)]
            X_sample = [X[j] for j in indices]
            y_sample = [y[j] for j in indices]
            
            tree = RegressionTree(max_depth=self.max_depth, 
                                  min_samples_split=self.min_samples_split,
                                  max_features=self.max_features)
            tree.fit(X_sample, y_sample)
            self.trees.append(tree)
            
            for feat, imp in tree.feature_importances_.items():
                self.feature_importances_[feat] += imp
                
        total_imp = sum(self.feature_importances_.values())
        if total_imp > 0:
            for f in self.feature_importances_:
                self.feature_importances_[f] /= total_imp

    def predict(self, X):
        predictions = []
        for x in X:
            tree_preds = [tree.predict_row(x, tree.tree) for tree in self.trees]
            predictions.append(sum(tree_preds) / len(tree_preds))
        return predictions

# ──────────────────────────────────────────────────────────────────────────────
# SCRIPT EXECUTION
# ──────────────────────────────────────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TRAIN_FILE = os.path.join(DATA_DIR, "train_dataset.csv")
TEST_FILE = os.path.join(DATA_DIR, "test_dataset.csv")
REPORT_FILE = os.path.join(DATA_DIR, "random_forest_report.txt")
BASELINE_REPORT_FILE = os.path.join(DATA_DIR, "baseline_model_report.txt")

report_lines = []
def rprint(msg=""):
    print(msg)
    report_lines.append(msg)

rprint("=" * 80)
rprint("RANDOM FOREST REGRESSOR TRAINING & EVALUATION (VANILLA PYTHON)")
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
    
    # Read a sample to keep python implementation fast
    # We'll sample 5000 rows deterministically (every 100th row roughly)
    for i, row in enumerate(reader):
        if i % 50 == 0:
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
rprint(f"      Using {len(feature_names)} features for modeling.")

# 3. Train Model
rprint("\n[3/5] Training Random Forest Regressor (Pure Python)...")
random.seed(42)
# Using 10 trees, depth 6, max_features sqrt for reasonable pure python speed
rf_model = VanillaRandomForestRegressor(n_estimators=10, max_depth=6, 
                                        min_samples_split=5, 
                                        max_features=int(math.sqrt(len(feature_names))))
rf_model.fit(train_X, train_y)
rprint("      Training complete.")

# 4. Evaluate Model
rprint("\n[4/5] Evaluating on test set...")
y_pred = rf_model.predict(test_X)

n_test = len(test_y)
mae = sum(abs(a - p) for a, p in zip(test_y, y_pred)) / n_test
mse = sum((a - p)**2 for a, p in zip(test_y, y_pred)) / n_test
rmse = math.sqrt(mse)

mean_y = sum(test_y) / n_test
ss_tot = sum((a - mean_y)**2 for a in test_y)
ss_res = mse * n_test
r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

rprint("      Random Forest Metrics:")
rprint(f"      MAE:  {mae:,.2f}")
rprint(f"      RMSE: {rmse:,.2f}")
rprint(f"      R²:   {r2:.4f}")

# 5. Feature Importance
rprint("\n[5/5] Calculating Feature Importances...")
importances = rf_model.feature_importances_
feature_imp = [(feature_names[i], imp) for i, imp in importances.items()]
feature_imp.sort(key=lambda x: x[1], reverse=True)

rprint("      Top 15 Important Features:")
rprint("      " + "-" * 40)
for i, (feat, imp) in enumerate(feature_imp[:15]):
    rprint(f"      {i+1:<2}. {feat:<25} {imp:.4f}")

# 6. Baseline Comparison
rprint("\n" + "=" * 80)
rprint("BASELINE COMPARISON")
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
                try: baseline_metrics['R²'] = float(line.split(":")[1].strip())
                except: pass

if baseline_metrics:
    rprint(f"      {'Metric':<10} {'Baseline':>12} {'Random Forest':>15} {'Improvement':>15}")
    rprint("      " + "-" * 55)
    
    mae_imp = baseline_metrics.get('MAE', 0) - mae
    rmse_imp = baseline_metrics.get('RMSE', 0) - rmse
    r2_imp = r2 - baseline_metrics.get('R²', 0)
    
    rprint(f"      {'MAE':<10} {baseline_metrics.get('MAE',0):>12.2f} {mae:>15.2f} {mae_imp:>15.2f} ({mae_imp/baseline_metrics.get('MAE',1)*100:.1f}%)")
    rprint(f"      {'RMSE':<10} {baseline_metrics.get('RMSE',0):>12.2f} {rmse:>15.2f} {rmse_imp:>15.2f} ({rmse_imp/baseline_metrics.get('RMSE',1)*100:.1f}%)")
    rprint(f"      {'R²':<10} {baseline_metrics.get('R²',0):>12.4f} {r2:>15.4f} {r2_imp:>15.4f}")
else:
    rprint("      Baseline report not found. Cannot perform comparison.")

with open(REPORT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

rprint(f"\nReport saved to: {REPORT_FILE}")
rprint("\nDONE -- Random Forest model evaluation complete.")
