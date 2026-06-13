import os
import sys
import pickle

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def get_model_path():
    return os.path.join(ROOT_DIR, "models", "gbm_model.pkl")

def load_model():
    """
    Loads the pure Python VanillaXGBoostRegressor model from disk.
    Note: Requires the RegressionTree and VanillaXGBoostRegressor classes
    to be available in the unpickling namespace.
    """
    model_path = get_model_path()
    if not os.path.exists(model_path):
        return None
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    return model
