"""
AI Model Service - Integrates Member 3's trained priority model

This service loads and uses the civicpulse_priority_model.pkl artifact
developed by the AI team. It provides safe model inference with proper
error handling and feature validation.
"""

import pickle
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AIModelError(Exception):
    """Base exception for AI model operations."""
    pass


class ModelLoadError(AIModelError):
    """Raised when model artifact cannot be loaded."""
    pass


class FeatureValidationError(AIModelError):
    """Raised when complaint features don't match model requirements."""
    pass


class InferenceError(AIModelError):
    """Raised when model inference fails."""
    pass


class AIModel(ABC):
    """Abstract interface for AI models."""
    
    @abstractmethod
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run inference on complaint features.
        
        Args:
            features: Dictionary with complaint features
        
        Returns:
            Dictionary with predictions (at least 'priority_category' and 'priority_score')
        
        Raises:
            FeatureValidationError: If features are invalid
            InferenceError: If inference fails
        """
        pass
    
    @abstractmethod
    def get_feature_names(self) -> list:
        """Get required input feature names."""
        pass
    
    @abstractmethod
    def get_model_version(self) -> str:
        """Get model version/identifier."""
        pass


class SklearnModel(AIModel):
    """
    Wrapper for scikit-learn models (Classification or Regression).
    
    Assumes the pickle contains a fitted sklearn model with:
    - predict() or predict_proba() method
    - Classes are one of: Low, Medium, High, Critical
    """
    
    def __init__(self, model_artifact: Any, feature_names: list, model_version: str = "sklearn-v1"):
        """
        Initialize sklearn model wrapper.
        
        Args:
            model_artifact: The loaded pickle object (sklearn model)
            feature_names: List of feature names in order
            model_version: Version identifier for this model
        """
        self.model = model_artifact
        self.feature_names = feature_names
        self.model_version = model_version
        self.is_classifier = hasattr(model_artifact, 'classes_')
        
        # Get the expected feature count
        if hasattr(model_artifact, 'n_features_in_'):
            self.n_features = model_artifact.n_features_in_
        else:
            self.n_features = len(feature_names)
        
        logger.info(
            f"Sklearn model initialized: {self.n_features} features, "
            f"classifier={self.is_classifier}, version={self.model_version}"
        )
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run inference using sklearn model.
        
        For classifiers: Returns predicted class and confidence
        For regressors: Returns predicted score
        """
        try:
            # Extract and validate features
            feature_vector = self._extract_feature_vector(features)
            
            # Run inference
            if self.is_classifier:
                prediction = self.model.predict([feature_vector])[0]
                
                # Get probabilities if available
                if hasattr(self.model, 'predict_proba'):
                    probabilities = self.model.predict_proba([feature_vector])[0]
                    confidence = float(max(probabilities))
                else:
                    confidence = None
                
                return {
                    'priority_category': prediction,
                    'priority_score': self._category_to_score(prediction),
                    'confidence': confidence,
                    'method': 'classification'
                }
            else:
                # Regression model
                score = float(self.model.predict([feature_vector])[0])
                score = max(0, min(100, score))  # Clamp to 0-100
                
                return {
                    'priority_category': self._score_to_category(score),
                    'priority_score': int(score),
                    'confidence': None,
                    'method': 'regression'
                }
        
        except Exception as e:
            logger.error(f"Inference error: {e}")
            raise InferenceError(f"Model inference failed: {e}")
    
    def get_feature_names(self) -> list:
        """Return required feature names."""
        return self.feature_names
    
    def get_model_version(self) -> str:
        """Return model version identifier."""
        return self.model_version
    
    def _extract_feature_vector(self, features: Dict[str, Any]) -> list:
        """
        Extract features in the order expected by the model.
        
        Raises:
            FeatureValidationError: If required features are missing
        """
        vector = []
        missing = []
        
        for fname in self.feature_names:
            if fname not in features or features[fname] is None:
                missing.append(fname)
            else:
                vector.append(features[fname])
        
        if missing:
            raise FeatureValidationError(
                f"Missing required features: {missing}"
            )
        
        if len(vector) != self.n_features:
            raise FeatureValidationError(
                f"Expected {self.n_features} features, got {len(vector)}"
            )
        
        return vector
    
    @staticmethod
    def _category_to_score(category: str) -> int:
        """Convert priority category to numeric score."""
        mapping = {
            'Low': 25,
            'Medium': 50,
            'High': 75,
            'Critical': 95
        }
        return mapping.get(category, 50)
    
    @staticmethod
    def _score_to_category(score: float) -> str:
        """Convert numeric score to priority category."""
        if score >= 75:
            return 'Critical'
        elif score >= 50:
            return 'High'
        elif score >= 25:
            return 'Medium'
        else:
            return 'Low'


class AIModelService:
    """
    Service for loading and using the trained AI model.
    
    Responsibilities:
    1. Load the pickle model artifact safely
    2. Initialize the appropriate wrapper (sklearn, etc.)
    3. Validate input features
    4. Run inference
    5. Handle errors gracefully
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize AI model service.
        
        Args:
            model_path: Path to the pickle model artifact.
                       Defaults to C:\seva_hackthon\model\civicpulse_priority_model.pkl
        """
        self.model_path = model_path or r"C:\seva_hackthon\model\civicpulse_priority_model.pkl"
        self.ai_model: Optional[AIModel] = None
        self._load_model()
    
    def _load_model(self):
        """Load the model artifact from disk."""
        try:
            model_file = Path(self.model_path)
            if not model_file.exists():
                raise ModelLoadError(f"Model file not found: {self.model_path}")
            
            logger.info(f"Loading model from: {self.model_path}")
            
            with open(model_file, 'rb') as f:
                artifact = pickle.load(f)
            
            # Determine model type and create appropriate wrapper
            # This assumes the artifact is a sklearn model
            if hasattr(artifact, 'predict'):
                # Extract feature names if available
                feature_names = self._extract_feature_names(artifact)
                
                self.ai_model = SklearnModel(
                    artifact,
                    feature_names=feature_names,
                    model_version="civicpulse-ai-v1"
                )
                logger.info(f"✓ Model loaded successfully: {artifact.__class__.__name__}")
            else:
                raise ModelLoadError(
                    f"Unsupported model type: {type(artifact).__name__}"
                )
        
        except pickle.UnpicklingError as e:
            raise ModelLoadError(f"Failed to unpickle model: {e}")
        except Exception as e:
            raise ModelLoadError(f"Error loading model: {e}")
    
    @staticmethod
    def _extract_feature_names(model: Any) -> list:
        """
        Extract feature names from the model artifact.
        
        Tries multiple approaches:
        1. Check for get_feature_names() method
        2. Check for feature_names_ attribute
        3. Use standard complaint features as fallback
        """
        if hasattr(model, 'get_feature_names_out'):
            try:
                return list(model.get_feature_names_out())
            except:
                pass
        
        if hasattr(model, 'feature_names_'):
            return model.feature_names_
        
        # Fallback: standard complaint features
        return [
            'category_encoded',
            'repeat_complaint_count',
            'description_length',
            'has_coordinates',
            'hour_reported'
        ]
    
    def predict(self, complaint_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict priority for a complaint.
        
        Args:
            complaint_data: Dictionary with complaint information
        
        Returns:
            Dictionary with:
            - priority_category: Low/Medium/High/Critical
            - priority_score: 0-100
            - confidence: Model confidence (if available)
            - model_version: Version of the model used
        
        Raises:
            ModelLoadError: If model is not loaded
            FeatureValidationError: If features are missing/invalid
            InferenceError: If prediction fails
        """
        if self.ai_model is None:
            raise ModelLoadError("AI model not loaded")
        
        try:
            # Add metadata
            result = self.ai_model.predict(complaint_data)
            result['model_version'] = self.ai_model.get_model_version()
            return result
        
        except (FeatureValidationError, InferenceError) as e:
            raise
        except Exception as e:
            raise InferenceError(f"Unexpected error during prediction: {e}")
    
    def is_ready(self) -> bool:
        """Check if model is loaded and ready for inference."""
        return self.ai_model is not None
    
    def get_required_features(self) -> list:
        """Get list of required input features."""
        if self.ai_model:
            return self.ai_model.get_feature_names()
        return []


# Global service instance
_ai_service: Optional[AIModelService] = None


def get_ai_service() -> AIModelService:
    """Get or create the global AI model service."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIModelService()
    return _ai_service


def set_ai_service(service: AIModelService):
    """Replace the global AI service (for testing or custom configuration)."""
    global _ai_service
    _ai_service = service
