"""
Shared helpers for the TounesRent model (used by training AND inference).

The API / dashboard should import from here so the feature pipeline
stays identical between training and prediction:

    from ml.model_utils import ClipRegressor, add_features, FEATURES
"""
import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin

# ---------------------------------------------------------------- schema
CAT_COLS = ["governorate", "city", "quartier"]
NUM_COLS = ["surface", "bedrooms", "bathrooms"]
BOOL_COLS = ["is_house", "furnished", "garage", "elevator", "aircon",
             "heating", "security", "pool", "sea_view", "terrace",
             "equipped_kitchen"]
ENGINEERED = ["surface_per_bedroom", "log_surface"]

# column order the model was trained on
FEATURES = CAT_COLS + NUM_COLS + BOOL_COLS + ENGINEERED

# plausible rent range for clipping predictions (2026 market)
RENT_MIN, RENT_MAX = 100.0, 20000.0


def add_features(df):
    """
    Add the engineered columns the model expects (returns a copy).

    Safe against:
      - bedrooms = -1 (unknown)  → denominator floored to 1
      - missing bedrooms         → filled with 1
      - surface = 0 / NaN / inf  → clipped to >= 1
    """
    df = df.copy()

    # ---- clean surface (avoid log(0) and inf) ----
    df["surface"] = (
        df["surface"]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(1.0)
        .clip(lower=1.0)
        .astype(float)
    )

    # ---- safe surface_per_bedroom ----
    bedrooms_safe = (
        df["bedrooms"]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(1.0)
        .clip(lower=1.0)          # -1 → 1, 0 → 1
        .astype(float)
    )
    df["surface_per_bedroom"] = (df["surface"] / bedrooms_safe).clip(1, 500)

    # ---- safe log_surface ----
    df["log_surface"] = np.log(df["surface"])

    return df


class ClipRegressor(BaseEstimator, RegressorMixin):
    """Wraps a regressor and clips predictions to a plausible rent range."""

    def __init__(self, model, lo=RENT_MIN, hi=RENT_MAX):
        self.model = model
        self.lo = lo
        self.hi = hi

    def fit(self, X, y):
        self.model.fit(X, y)
        return self

    def predict(self, X):
        preds = self.model.predict(X)
        return np.clip(preds, self.lo, self.hi)