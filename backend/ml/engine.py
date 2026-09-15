"""
ML Prediction Engine — Orchestration layer.

Handles parallel dispatch to all three models, response aggregation
with timeout handling, and integration with the explainability layer.
"""

import asyncio
import time
import uuid
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from backend.config import (
    MODELS_DIR,
    FRAUD_MODEL_TIMEOUT,
    CREDIT_RISK_MODEL_TIMEOUT,
    SEGMENTATION_MODEL_TIMEOUT,
)
from backend.ml.feature_store import FeatureStore
from backend.ml.explainability import ExplainabilityEngine


class PredictionEngine:
    """Orchestrates parallel predictions across all three models.

    Handles feature computation, parallel model dispatch, timeout fallback,
    SHAP explanation generation, and response aggregation.
    """

    def __init__(self):
        self.feature_store = FeatureStore()
        self.explainability = ExplainabilityEngine()
        self.credit_risk_model = None
        self.fraud_model = None
        self.segmentation_model = None
        self._loaded = False

    def load_models(self, models_dir: Optional[str] = None):
        """Load all three model artifacts from disk.

        Args:
            models_dir: Path to the models directory. Defaults to config MODELS_DIR.
        """
        if models_dir is None:
            models_dir = str(MODELS_DIR)

        models_path = Path(models_dir)

        # Load credit risk model
        try:
            from backend.ml.credit_risk.model import CreditRiskModel
            cr_path = models_path / "credit_risk"
            if cr_path.exists() and any(cr_path.iterdir()):
                self.credit_risk_model = CreditRiskModel.load(str(cr_path))
                self.explainability.init_credit_risk_explainer(self.credit_risk_model)
                print("✓ Credit risk model loaded")
            else:
                print("⚠ Credit risk model not found — skipping")
        except Exception as e:
            print(f"⚠ Failed to load credit risk model: {e}")

        # Load fraud model
        try:
            from backend.ml.fraud.model import FraudModel
            fraud_path = models_path / "fraud"
            if fraud_path.exists() and any(fraud_path.iterdir()):
                self.fraud_model = FraudModel.load(str(fraud_path))
                self.explainability.init_fraud_explainer(self.fraud_model)
                print("✓ Fraud model loaded")
            else:
                print("⚠ Fraud model not found — skipping")
        except Exception as e:
            print(f"⚠ Failed to load fraud model: {e}")

        # Load segmentation model
        try:
            from backend.ml.segmentation.model import SegmentationModel
            seg_path = models_path / "segmentation"
            if seg_path.exists() and any(seg_path.iterdir()):
                self.segmentation_model = SegmentationModel.load(str(seg_path))
                self.explainability.init_segmentation_explainer(self.segmentation_model)
                print("✓ Segmentation model loaded")
            else:
                print("⚠ Segmentation model not found — skipping")
        except Exception as e:
            print(f"⚠ Failed to load segmentation model: {e}")

        self._loaded = True

    async def predict(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """Run all three models in parallel on the given input.

        Args:
            raw_input: Raw input data from the API request.

        Returns:
            Dictionary with prediction_id, timestamp, model_versions,
            and results for each model (score + SHAP explanation).
        """
        prediction_id = str(uuid.uuid4())
        start_time = time.time()

        # Step 1: Compute features for all models
        features = self.feature_store.get_features(raw_input)

        # Step 2: Dispatch all models in parallel with timeouts
        tasks = []

        if "credit_risk" in features and self.credit_risk_model is not None:
            tasks.append(
                self._run_with_timeout(
                    "credit_risk",
                    self._predict_credit_risk,
                    features["credit_risk"],
                    CREDIT_RISK_MODEL_TIMEOUT,
                )
            )
        else:
            tasks.append(self._unavailable_result("credit_risk", "Insufficient input data or model not loaded"))

        if "fraud" in features and self.fraud_model is not None:
            tasks.append(
                self._run_with_timeout(
                    "fraud",
                    self._predict_fraud,
                    features["fraud"],
                    FRAUD_MODEL_TIMEOUT,
                )
            )
        else:
            tasks.append(self._unavailable_result("fraud", "Insufficient input data or model not loaded"))

        if "segmentation" in features and self.segmentation_model is not None:
            tasks.append(
                self._run_with_timeout(
                    "segmentation",
                    self._predict_segmentation,
                    features["segmentation"],
                    SEGMENTATION_MODEL_TIMEOUT,
                )
            )
        else:
            tasks.append(self._unavailable_result("segmentation", "Insufficient input data or model not loaded"))

        # Step 3: Gather results
        results = await asyncio.gather(*tasks)

        duration_ms = (time.time() - start_time) * 1000

        # Step 4: Build response
        credit_risk_result = results[0]
        fraud_result = results[1]
        segmentation_result = results[2]

        # Collect model versions
        model_versions = {}
        if credit_risk_result.get("status") == "success":
            model_versions["credit_risk"] = credit_risk_result.get("model_version", "unknown")
        if fraud_result.get("status") == "success":
            model_versions["fraud"] = fraud_result.get("model_version", "unknown")
        if segmentation_result.get("status") == "success":
            model_versions["segmentation"] = segmentation_result.get("model_version", "unknown")

        return {
            "prediction_id": prediction_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": round(duration_ms, 2),
            "model_versions": model_versions,
            "credit_risk": credit_risk_result,
            "fraud": fraud_result,
            "segmentation": segmentation_result,
        }

    async def _run_with_timeout(
        self,
        model_name: str,
        predict_fn,
        features: Dict[str, float],
        timeout: float,
    ) -> Dict[str, Any]:
        """Run a prediction function with a timeout.

        Args:
            model_name: Name of the model (for error reporting).
            predict_fn: Synchronous prediction function to call.
            features: Feature dictionary to pass to the function.
            timeout: Maximum time in seconds.

        Returns:
            Prediction result dict, or an error/timeout result.
        """
        try:
            # Run the synchronous prediction in a thread executor
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(None, predict_fn, features),
                timeout=timeout,
            )
            return result
        except asyncio.TimeoutError:
            return {
                "status": "timeout",
                "model_name": model_name,
                "error": f"Model prediction timed out after {timeout}s",
                "score": None,
            }
        except Exception as e:
            return {
                "status": "error",
                "model_name": model_name,
                "error": str(e),
                "score": None,
            }

    def _predict_credit_risk(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Run credit risk prediction + SHAP explanation."""
        start = time.time()
        prediction = self.credit_risk_model.predict(features)

        # Get SHAP explanation
        feature_names = self.credit_risk_model.get_feature_names()
        shap_explanation = self.explainability.explain_credit_risk(features, feature_names)

        latency_ms = (time.time() - start) * 1000

        return {
            "status": "success",
            "model_name": "credit_risk",
            "score": prediction.get("probability", 0.0),
            "risk_tier": prediction.get("risk_tier", "unknown"),
            "probability_of_default": prediction.get("probability", 0.0),
            "model_version": prediction.get("model_version", "unknown"),
            "latency_ms": round(latency_ms, 2),
            "shap_explanation": shap_explanation,
        }

    def _predict_fraud(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Run fraud prediction + SHAP explanation."""
        start = time.time()
        prediction = self.fraud_model.predict(features)

        # Get SHAP explanation
        feature_names = self.fraud_model.get_feature_names()
        shap_explanation = self.explainability.explain_fraud(features, feature_names)

        latency_ms = (time.time() - start) * 1000

        return {
            "status": "success",
            "model_name": "fraud",
            "score": prediction.get("fraud_score", 0.0),
            "decision": prediction.get("decision", "unknown"),
            "decision_tier": prediction.get("decision_tier", "unknown"),
            "model_version": prediction.get("model_version", "unknown"),
            "latency_ms": round(latency_ms, 2),
            "shap_explanation": shap_explanation,
        }

    def _predict_segmentation(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Run segmentation prediction + SHAP explanation."""
        start = time.time()
        prediction = self.segmentation_model.predict(features)

        # Get SHAP explanation for the predicted segment
        feature_names = self.segmentation_model.get_feature_names()
        predicted_class = prediction.get("segment_id", 0)
        shap_explanation = self.explainability.explain_segmentation(
            features, feature_names, predicted_class
        )

        latency_ms = (time.time() - start) * 1000

        return {
            "status": "success",
            "model_name": "segmentation",
            "segment_id": prediction.get("segment_id", 0),
            "segment_name": prediction.get("segment_name", "Unknown"),
            "confidence": prediction.get("confidence", 0.0),
            "model_version": prediction.get("model_version", "unknown"),
            "latency_ms": round(latency_ms, 2),
            "shap_explanation": shap_explanation,
        }

    async def _unavailable_result(self, model_name: str, reason: str) -> Dict[str, Any]:
        """Return a result for an unavailable model."""
        return {
            "status": "unavailable",
            "model_name": model_name,
            "error": reason,
            "score": None,
        }

    @property
    def is_loaded(self) -> bool:
        """Check if any models are loaded."""
        return self._loaded
