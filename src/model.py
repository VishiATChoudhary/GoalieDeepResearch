"""Modelling: what drives a goalkeeper's World Cup 'showcase success', and a
scoring function reused by the live 2026 dashboard.

Two complementary models are trained:
  * Logistic Regression (interpretable coefficients / direction of effect)
  * Random Forest (non-linear feature importance + permutation importance)

Given the modest sample size (a few dozen keeper-tournaments), the goal is
*explanation and ranking*, not high-precision prediction. We report
cross-validated performance honestly and lean on permutation importance and
coefficient signs to identify the 'driving factors'.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from features import build_feature_matrix


def _numeric_pipeline(estimator) -> Pipeline:
    """Impute medians + scale, then fit estimator. Scaling is a no-op for the
    forest but harmless and keeps a single code path."""
    return Pipeline(
        steps=[
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("model", estimator),
        ]
    )


@dataclass
class TrainedModels:
    feature_names: list[str]
    logit: Pipeline
    forest: Pipeline
    cv_metrics: dict = field(default_factory=dict)
    logit_coefs: pd.DataFrame | None = None
    perm_importance: pd.DataFrame | None = None


def train(df: pd.DataFrame, target: str = "showcase_success",
          random_state: int = 42) -> TrainedModels:
    X, feats = build_feature_matrix(df)
    y = df[target].astype(int).values

    logit = _numeric_pipeline(
        LogisticRegression(max_iter=2000, class_weight="balanced",
                           random_state=random_state)
    )
    forest = _numeric_pipeline(
        RandomForestClassifier(n_estimators=400, max_depth=4,
                              min_samples_leaf=2, class_weight="balanced",
                              random_state=random_state)
    )

    # Honest small-sample cross-validation.
    n_splits = min(5, int(np.bincount(y).min()))
    cv_metrics = {}
    if n_splits >= 2:
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True,
                            random_state=random_state)
        for name, pipe in [("logit", logit), ("forest", forest)]:
            proba = cross_val_predict(pipe, X, y, cv=cv, method="predict_proba")[:, 1]
            pred = (proba >= 0.5).astype(int)
            cv_metrics[name] = {
                "accuracy": float((pred == y).mean()),
                "base_rate": float(y.mean()),
                "n": int(len(y)),
            }
            try:
                from sklearn.metrics import roc_auc_score
                cv_metrics[name]["roc_auc"] = float(roc_auc_score(y, proba))
            except ValueError:
                cv_metrics[name]["roc_auc"] = float("nan")

    logit.fit(X, y)
    forest.fit(X, y)

    # Logistic coefficients (on standardized features → comparable magnitudes).
    coefs = pd.DataFrame({
        "feature": feats,
        "coef": logit.named_steps["model"].coef_[0],
    }).sort_values("coef", key=np.abs, ascending=False).reset_index(drop=True)

    # Permutation importance on the forest (more reliable than impurity).
    perm = permutation_importance(forest, X, y, n_repeats=50,
                                 random_state=random_state, scoring="roc_auc")
    perm_df = pd.DataFrame({
        "feature": feats,
        "perm_importance": perm.importances_mean,
        "perm_std": perm.importances_std,
    }).sort_values("perm_importance", ascending=False).reset_index(drop=True)

    return TrainedModels(feats, logit, forest, cv_metrics, coefs, perm_df)


def score_keepers(models: TrainedModels, df: pd.DataFrame) -> pd.Series:
    """Return showcase-success probability for each keeper row, averaging the
    two models (an ensemble that is more stable on small data)."""
    X = df[models.feature_names].copy()
    p_logit = models.logit.predict_proba(X)[:, 1]
    p_forest = models.forest.predict_proba(X)[:, 1]
    return pd.Series((p_logit + p_forest) / 2.0, index=df.index)
