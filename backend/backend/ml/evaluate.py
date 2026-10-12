"""
Deep evaluation of the trained TounesRent model.

Run:  python -m ml.evaluate

Loads:  ml/model.joblib      (produced by train_model.py)
        ml/data/rentals_clean.csv

Prints:
  - Global metrics (MAE, MedAE, RMSE, R², MAPE, MedAPE)
  - Distribution of relative errors
  - % predictions within ±10/15/20/25/30/50%
  - Error by governorate
  - Error by price bucket
  - Worst 10 predictions
  - Best 10 predictions
  - Feature importances (top 20)
  - Residual histogram + scatter plot (PNG saved to ml/eval_plots/)
"""
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")            # headless backend
import matplotlib.pyplot as plt
from sklearn.metrics import (mean_absolute_error, mean_squared_error,
                             median_absolute_error, r2_score)

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from model_utils import FEATURES, add_features   # noqa: E402

PLOTS_DIR = HERE / "eval_plots"
PLOTS_DIR.mkdir(exist_ok=True)


# ----------------------------------------------------------------------
def load_model_and_data():
    model_path = HERE / "model.joblib"
    csv_path = HERE / "data" / "rentals_clean.csv"

    if not model_path.exists():
        raise FileNotFoundError(
            f"{model_path} not found — run `python -m ml.train_model` first."
        )
    if not csv_path.exists():
        raise FileNotFoundError(
            f"{csv_path} not found — run `python -m ml.prepare_dataset` first."
        )

    bundle = joblib.load(model_path)
    pipe = bundle["pipeline"]

    df = add_features(pd.read_csv(csv_path))
    numeric = [c for c in FEATURES if c not in ("governorate", "city", "quartier")]
    df[numeric] = df[numeric].replace([np.inf, -np.inf], np.nan).fillna(0)

    return pipe, df


# ----------------------------------------------------------------------
def compute_metrics(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    medae = median_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)

    # Relative errors (guard against zero)
    safe = np.where(y_true > 0, y_true, np.nan)
    rel = np.abs(y_pred - y_true) / safe
    rel = rel[~np.isnan(rel)]

    mape = float(np.mean(rel))
    medape = float(np.median(rel))

    return {
        "n": int(len(y_true)),
        "mae": float(mae),
        "medae": float(medae),
        "rmse": float(rmse),
        "r2": float(r2),
        "mape": mape,
        "medape": medape,
        "within_10": float(np.mean(rel <= 0.10)),
        "within_15": float(np.mean(rel <= 0.15)),
        "within_20": float(np.mean(rel <= 0.20)),
        "within_25": float(np.mean(rel <= 0.25)),
        "within_30": float(np.mean(rel <= 0.30)),
        "within_50": float(np.mean(rel <= 0.50)),
    }


def print_metrics(m):
    print("=" * 70)
    print("GLOBAL METRICS")
    print("=" * 70)
    print(f"  Samples        : {m['n']:,}")
    print(f"  MAE            : {m['mae']:>10.2f} TND")
    print(f"  MedAE          : {m['medae']:>10.2f} TND")
    print(f"  RMSE           : {m['rmse']:>10.2f} TND")
    print(f"  R²             : {m['r2']:>10.4f}")
    print(f"  MAPE (mean)    : {m['mape']:>10.1%}")
    print(f"  MedAPE (median): {m['medape']:>10.1%}")
    print()
    print("  Accuracy bands (relative error):")
    for pct in (10, 15, 20, 25, 30, 50):
        print(f"    within ±{pct:>2}% : {m[f'within_{pct}']:>6.1%}")


# ----------------------------------------------------------------------
def per_group_error(df, group_col, name):
    if group_col not in df.columns:
        return
    print()
    print("=" * 70)
    print(f"ERROR BY {name.upper()}")
    print("=" * 70)
    g = df.groupby(group_col).agg(
        n=("abs_err", "size"),
        mae=("abs_err", "mean"),
        medae=("abs_err", "median"),
        medape=("rel_err", "median"),
    )
    g["medape"] = (g["medape"] * 100).round(1)
    g["mae"] = g["mae"].round(1)
    g["medae"] = g["medae"].round(1)
    g = g.sort_values("mae", ascending=False)
    print(g.to_string())


# ----------------------------------------------------------------------
def per_price_bucket(df):
    df = df.copy()
    df["bucket"] = pd.cut(
        df["y_true"],
        bins=[0, 800, 1500, 2500, 4000, 1e9],
        labels=["<800", "800-1500", "1500-2500", "2500-4000", ">=4000"],
    )
    print()
    print("=" * 70)
    print("ERROR BY PRICE BUCKET")
    print("=" * 70)
    g = df.groupby("bucket", observed=True).agg(
        n=("abs_err", "size"),
        mae=("abs_err", "mean"),
        medae=("abs_err", "median"),
        medape=("rel_err", "median"),
    )
    g["medape"] = (g["medape"] * 100).round(1)
    g["mae"] = g["mae"].round(1)
    g["medae"] = g["medae"].round(1)
    print(g.to_string())


# ----------------------------------------------------------------------
def worst_and_best(df, k=10):
    print()
    print("=" * 70)
    print(f"WORST {k} PREDICTIONS")
    print("=" * 70)
    cols = ["governorate", "city", "quartier", "surface", "bedrooms",
            "y_true", "y_pred", "abs_err", "rel_err"]
    worst = df.sort_values("abs_err", ascending=False).head(k)[cols]
    worst["rel_err"] = (worst["rel_err"] * 100).round(1)
    print(worst.to_string(index=False))

    print()
    print("=" * 70)
    print(f"BEST {k} PREDICTIONS")
    print("=" * 70)
    best = df.sort_values("abs_err").head(k)[cols]
    best["rel_err"] = (best["rel_err"] * 100).round(1)
    print(best.to_string(index=False))


# ----------------------------------------------------------------------
def feature_importances(pipe, top=20):
    try:
        model = pipe.named_steps["model"]
        # Unwrap ClipRegressor if needed
        inner = getattr(model, "model", model)
        if not hasattr(inner, "feature_importances_"):
            print("\n(model has no feature_importances_)")
            return

        # Recover feature names from the ColumnTransformer
        pre = pipe.named_steps["pre"]
        ohe = pre.named_transformers_["cat"]
        cat_names = ohe.get_feature_names_out(["governorate", "city", "quartier"])
        num_names = np.array([c for c in pre.transformers[1][2]])
        names = np.concatenate([cat_names, num_names])
        importances = inner.feature_importances_

        imp = pd.DataFrame({"feature": names, "importance": importances})
        imp = imp.sort_values("importance", ascending=False).head(top)

        print()
        print("=" * 70)
        print(f"TOP {top} FEATURE IMPORTANCES")
        print("=" * 70)
        print(imp.to_string(index=False))

        # Plot
        fig, ax = plt.subplots(figsize=(9, 7))
        ax.barh(imp["feature"][::-1], imp["importance"][::-1], color="#c8102e")
        ax.set_xlabel("Importance")
        ax.set_title(f"Top {top} feature importances — {bundle_name()}")
        plt.tight_layout()
        out = PLOTS_DIR / "feature_importances.png"
        plt.savefig(out, dpi=120)
        plt.close()
        print(f"\n  → saved plot {out}")
    except Exception as e:
        print(f"\n(could not compute feature importances: {e})")


def bundle_name():
    try:
        with open(HERE / "model_metrics.json") as f:
            return json.load(f).get("model", "model")
    except Exception:
        return "model"


# ----------------------------------------------------------------------
def plots(df):
    # 1. Residual histogram
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(df["resid"], bins=60, color="#0a7a2f", edgecolor="white")
    ax.axvline(0, color="black", lw=1)
    ax.set_xlabel("Residual (predicted − actual) TND")
    ax.set_title("Residual distribution")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "residual_hist.png", dpi=120)
    plt.close()

    # 2. Actual vs predicted scatter
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(df["y_true"], df["y_pred"], alpha=0.3, s=8, color="#c8102e")
    lim = [0, max(df["y_true"].max(), df["y_pred"].max()) * 1.05]
    ax.plot(lim, lim, "k--", lw=1, label="perfect")
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel("Actual rent (TND)")
    ax.set_ylabel("Predicted rent (TND)")
    ax.set_title("Actual vs Predicted")
    ax.legend()
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "actual_vs_pred.png", dpi=120)
    plt.close()

    # 3. Relative error distribution
    fig, ax = plt.subplots(figsize=(8, 4))
    rel = (df["rel_err"] * 100).clip(upper=100)
    ax.hist(rel, bins=60, color="#c8102e", edgecolor="white")
    ax.axvline(25, color="black", lw=1, linestyle="--", label="±25%")
    ax.set_xlabel("Relative error (%)")
    ax.set_title("Relative error distribution (clipped at 100%)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "relative_error.png", dpi=120)
    plt.close()

    print(f"\n  → saved 3 plots to {PLOTS_DIR}/")


# ----------------------------------------------------------------------
def main():
    pipe, df = load_model_and_data()

    X = df[FEATURES]
    y_true = df["rent"].values
    y_pred = pipe.predict(X)

    # Attach for per-group analysis
    df = df.copy()
    df["y_true"] = y_true
    df["y_pred"] = y_pred
    df["abs_err"] = np.abs(y_pred - y_true)
    df["resid"] = y_pred - y_true
    df["rel_err"] = np.abs(y_pred - y_true) / np.where(y_true > 0, y_true, np.nan)

    # ---- 1. Global metrics ----
    m = compute_metrics(y_true, y_pred)
    print_metrics(m)

    # ---- 2. Per-group errors ----
    per_group_error(df, "governorate", "governorate")
    per_group_error(df, "quartier", "quartier (top 15)")
    per_price_bucket(df)

    # ---- 3. Worst/best ----
    worst_and_best(df, k=10)

    # ---- 4. Feature importances ----
    feature_importances(pipe, top=20)

    # ---- 5. Plots ----
    plots(df)

    # ---- 6. Save summary JSON ----
    summary = {
        "global": m,
        "by_governorate": df.groupby("governorate")["abs_err"]
                            .agg(["count", "mean", "median"])
                            .round(1).to_dict(orient="index"),
        "n_features": len(FEATURES),
        "features": FEATURES,
    }
    out = HERE / "evaluation.json"
    with open(out, "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print()
    print("=" * 70)
    print(f"Full evaluation saved → {out}")
    print("=" * 70)


if __name__ == "__main__":
    main()