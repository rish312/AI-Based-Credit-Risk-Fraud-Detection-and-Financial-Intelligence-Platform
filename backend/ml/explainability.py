"""
SHAP Explainability layer for the ML prediction platform.

Provides TreeSHAP explanations for credit risk and fraud models,
and surrogate-based SHAP explanations for the segmentation model.
"""

import numpy as np
import shap
from typing import Dict, Any, List, Optional


class ExplainabilityEngine:
    """Generates SHAP-based explanations for all three models."""

    def __init__(self):
        self._credit_risk_explainer = None
        self._fraud_explainer = None
        self._segmentation_explainer = None

    def _extract_tree_model(self, model):
        """Extract a tree-based model that TreeExplainer can handle.

        Unwraps CalibratedClassifierCV, our XGBClassifier fallback wrapper,
        and similar wrappers to find the underlying estimator.
        """
        from sklearn.calibration import CalibratedClassifierCV
        from sklearn.ensemble import (
            HistGradientBoostingClassifier,
            RandomForestClassifier,
            GradientBoostingClassifier,
        )

        # CalibratedClassifierCV wraps a base estimator
        if isinstance(model, CalibratedClassifierCV):
            if hasattr(model, "calibrated_classifiers_"):
                # Use the first calibrated estimator's base
                inner = model.calibrated_classifiers_[0].estimator
                return self._extract_tree_model(inner)
            elif hasattr(model, "estimator"):
                return self._extract_tree_model(model.estimator)

        # Our XGBClassifier fallback wraps HistGradientBoostingClassifier
        if hasattr(model, "model") and isinstance(
            model.model,
            (HistGradientBoostingClassifier, RandomForestClassifier, GradientBoostingClassifier),
        ):
            return model.model

        # Already a supported type
        supported = (
            HistGradientBoostingClassifier,
            RandomForestClassifier,
            GradientBoostingClassifier,
        )
        if isinstance(model, supported):
            return model

        # Try xgboost
        try:
            import xgboost

            if isinstance(model, (xgboost.XGBClassifier, xgboost.XGBRegressor)):
                return model
        except ImportError:
            pass

        return model

    def init_credit_risk_explainer(self, model):
        """Initialize SHAP explainer for the credit risk model."""
        try:
            tree_model = self._extract_tree_model(model.model if hasattr(model, "model") else model)
            self._credit_risk_explainer = shap.TreeExplainer(tree_model)
            print("  ✓ Credit risk SHAP explainer initialized")
        except Exception as e:
            print(f"  ⚠ Credit risk SHAP: TreeExplainer failed ({e}), using KernelExplainer fallback")
            try:
                tree_model = self._extract_tree_model(model.model if hasattr(model, "model") else model)
                # Use a small background dataset for KernelExplainer
                bg = np.zeros((1, len(model.feature_names))) if hasattr(model, "feature_names") else np.zeros((1, 14))
                self._credit_risk_explainer = shap.Explainer(
                    lambda x: tree_model.predict_proba(x)[:, 1] if hasattr(tree_model, "predict_proba") else tree_model.predict(x),
                    bg,
                )
                print("  ✓ Credit risk SHAP explainer initialized (Explainer fallback)")
            except Exception as e2:
                print(f"  ✗ Credit risk SHAP failed completely: {e2}")
                self._credit_risk_explainer = None

    def init_fraud_explainer(self, model):
        """Initialize SHAP explainer for the fraud model."""
        try:
            xgb = model.xgb_model if hasattr(model, "xgb_model") else model
            tree_model = self._extract_tree_model(xgb)
            self._fraud_explainer = shap.TreeExplainer(tree_model)
            print("  ✓ Fraud SHAP explainer initialized")
        except Exception as e:
            print(f"  ⚠ Fraud SHAP: TreeExplainer failed ({e}), using Explainer fallback")
            try:
                xgb = model.xgb_model if hasattr(model, "xgb_model") else model
                tree_model = self._extract_tree_model(xgb)
                bg = np.zeros((1, len(model.feature_names))) if hasattr(model, "feature_names") else np.zeros((1, 20))
                self._fraud_explainer = shap.Explainer(
                    lambda x: tree_model.predict_proba(x)[:, 1] if hasattr(tree_model, "predict_proba") else tree_model.predict(x),
                    bg,
                )
                print("  ✓ Fraud SHAP explainer initialized (Explainer fallback)")
            except Exception as e2:
                print(f"  ✗ Fraud SHAP failed completely: {e2}")
                self._fraud_explainer = None

    def init_segmentation_explainer(self, model):
        """Initialize SHAP explainer for the segmentation surrogate model."""
        try:
            surrogate = model.surrogate if hasattr(model, "surrogate") else model
            self._segmentation_explainer = shap.TreeExplainer(surrogate)
            print("  ✓ Segmentation SHAP explainer initialized")
        except Exception as e:
            print(f"  ✗ Segmentation SHAP failed: {e}")
            self._segmentation_explainer = None

    def explain_credit_risk(
        self, features: Dict[str, float], feature_names: List[str]
    ) -> Dict[str, Any]:
        """Generate SHAP explanation for credit risk prediction."""
        if self._credit_risk_explainer is None:
            return self._empty_explanation(features, feature_names)
        return self._explain(self._credit_risk_explainer, features, feature_names, class_index=1)

    def explain_fraud(
        self, features: Dict[str, float], feature_names: List[str]
    ) -> Dict[str, Any]:
        """Generate SHAP explanation for fraud prediction."""
        if self._fraud_explainer is None:
            return self._empty_explanation(features, feature_names)
        return self._explain(self._fraud_explainer, features, feature_names, class_index=1)

    def explain_segmentation(
        self, features: Dict[str, float], feature_names: List[str], predicted_class: int = 0
    ) -> Dict[str, Any]:
        """Generate SHAP explanation for segmentation (via surrogate)."""
        if self._segmentation_explainer is None:
            return self._empty_explanation(features, feature_names)
        return self._explain(self._segmentation_explainer, features, feature_names, class_index=predicted_class)

    def _explain(
        self, explainer, features: Dict[str, float], feature_names: List[str], class_index: int = 1
    ) -> Dict[str, Any]:
        """Generate a SHAP explanation."""
        feature_values = np.array([[features.get(name, 0.0) for name in feature_names]])

        try:
            shap_result = explainer(feature_values)

            # Extract SHAP values
            if hasattr(shap_result, "values"):
                vals = shap_result.values
                if vals.ndim == 3:
                    sv = vals[0, :, min(class_index, vals.shape[2] - 1)]
                elif vals.ndim == 2:
                    sv = vals[0]
                else:
                    sv = vals
                base = shap_result.base_values
                if isinstance(base, np.ndarray):
                    if base.ndim == 2:
                        base_value = float(base[0, min(class_index, base.shape[1] - 1)])
                    elif base.ndim == 1:
                        base_value = float(base[0])
                    else:
                        base_value = float(base)
                else:
                    base_value = float(base)
            else:
                # Old-style shap_values return
                if isinstance(shap_result, list):
                    sv = shap_result[min(class_index, len(shap_result) - 1)][0]
                elif isinstance(shap_result, np.ndarray):
                    if shap_result.ndim == 3:
                        sv = shap_result[0, :, min(class_index, shap_result.shape[2] - 1)]
                    else:
                        sv = shap_result[0]
                else:
                    sv = np.zeros(len(feature_names))

                base_value = explainer.expected_value
                if isinstance(base_value, (list, np.ndarray)):
                    base_value = float(base_value[min(class_index, len(base_value) - 1)])
                else:
                    base_value = float(base_value)

            # Build contributions list
            contributions = []
            for i, name in enumerate(feature_names):
                contributions.append({
                    "name": name,
                    "value": round(float(features.get(name, 0.0)), 4),
                    "contribution": round(float(sv[i]) if i < len(sv) else 0.0, 6),
                })

            contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
            output_value = base_value + sum(c["contribution"] for c in contributions)

            return {
                "base_value": round(base_value, 6),
                "features": contributions,
                "output_value": round(output_value, 6),
            }

        except Exception as e:
            print(f"  ⚠ SHAP explanation failed: {e}")
            return self._empty_explanation(features, feature_names)

    def _empty_explanation(
        self, features: Dict[str, float], feature_names: List[str]
    ) -> Dict[str, Any]:
        """Return an empty explanation when SHAP is unavailable."""
        return {
            "base_value": 0.0,
            "features": [
                {"name": name, "value": round(float(features.get(name, 0.0)), 4), "contribution": 0.0}
                for name in feature_names
            ],
            "output_value": 0.0,
        }
