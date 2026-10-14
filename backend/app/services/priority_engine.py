"""
Priority Engine Interface and Implementation

This module provides a modular interface for complaint priority evaluation.
Integrates Member 3's actual AI model for production predictions.

Phases:
- Phase 1: Mock/development adapter
- Phase 2: Real AI model integration
- Phase 3+: Advanced features (ensemble, retraining, A/B testing)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class PriorityEvaluation:
    """
    Standard response format for priority evaluations.
    
    This structure is independent of the underlying AI implementation.
    """
    complaint_id: str
    priority_category: str  # Low, Medium, High, Critical
    priority_score: Optional[int] = None  # 0-100, if provided by engine
    explanation: str = ""  # Human-readable reason for the score
    contributing_factors: Optional[Dict[str, Any]] = None  # Model inputs/weights
    model_version: str = "development"  # AI model version or ruleset
    evaluated_at: datetime = None
    
    def __post_init__(self):
        if self.evaluated_at is None:
            self.evaluated_at = datetime.utcnow()


class PriorityEngine(ABC):
    """
    Abstract base class for priority evaluation engines.
    
    Implementations should:
    1. Validate all inputs before processing
    2. Handle timeouts and service failures gracefully
    3. Return PriorityEvaluation with complete metadata
    4. Never claim mock scores are actual model predictions
    5. Log all evaluations for audit trails
    """
    
    @abstractmethod
    def evaluate(self, complaint_data: Dict[str, Any]) -> PriorityEvaluation:
        """
        Evaluate complaint priority.
        
        Args:
            complaint_data: Dictionary with complaint fields
        
        Returns:
            PriorityEvaluation with score and explanation
        """
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check if the priority engine is available."""
        pass


class AIModelPriorityEngine(PriorityEngine):
    """
    Production Priority Engine using Member 3's trained AI model.
    
    Uses the actual civicpulse_priority_model.pkl artifact for predictions.
    """
    
    def __init__(self):
        """Initialize with the AI model service."""
        try:
            from app.services.ai_model_service import get_ai_service
            self.ai_service = get_ai_service()
            self.name = "AIModelPriorityEngine"
            
            if self.ai_service.is_ready():
                logger.info("✓ AI Model Priority Engine initialized successfully")
            else:
                logger.warning("⚠ AI Model not ready, will fall back to mock")
        
        except Exception as e:
            logger.error(f"Failed to initialize AI Model service: {e}")
            self.ai_service = None
    
    def evaluate(self, complaint_data: Dict[str, Any]) -> PriorityEvaluation:
        """
        Evaluate priority using the actual AI model.
        
        Extracts complaint features and runs inference through Member 3's model.
        """
        # Validate required fields
        required_fields = ['id', 'title', 'description', 'category']
        for field in required_fields:
            if field not in complaint_data or not complaint_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        complaint_id = complaint_data['id']
        
        if not self.ai_service or not self.ai_service.is_ready():
            raise RuntimeError("AI Model service not available")
        
        try:
            # Prepare features for the model
            features = self._extract_model_features(complaint_data)
            
            # Run inference
            prediction = self.ai_service.predict(features)
            
            logger.info(
                f"AI priority evaluation: {complaint_id} → "
                f"{prediction['priority_category']} (score: {prediction.get('priority_score', 'N/A')})"
            )
            
            return PriorityEvaluation(
                complaint_id=complaint_id,
                priority_category=prediction['priority_category'],
                priority_score=prediction.get('priority_score'),
                explanation=(
                    f"Priority evaluated by AI model {prediction.get('model_version', 'unknown')}. "
                    f"Category: {complaint_data.get('category', 'Unknown')}. "
                    f"Recurrence: {complaint_data.get('repeat_complaint_count', 0)}"
                ),
                contributing_factors={
                    'confidence': prediction.get('confidence'),
                    'method': prediction.get('method', 'classification')
                },
                model_version=prediction.get('model_version', 'unknown')
            )
        
        except Exception as e:
            logger.error(f"AI Model inference failed: {e}")
            raise
    
    def health_check(self) -> bool:
        """Check if AI model is available."""
        return self.ai_service is not None and self.ai_service.is_ready()
    
    @staticmethod
    def _extract_model_features(complaint_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and preprocess complaint data into model features.
        
        This should match the preprocessing used during model training.
        """
        from datetime import datetime
        
        features = {}
        
        # Category encoding (depends on model training)
        category = complaint_data.get('category', 'Unknown')
        category_mapping = {
            'Electrical Hazard': 0,
            'Drainage': 1,
            'Road & pavement': 2,
            'Streetlight': 3,
            'Public space': 4
        }
        features['category_encoded'] = category_mapping.get(category, 4)
        
        # Recurrence count
        features['repeat_complaint_count'] = complaint_data.get('repeat_complaint_count', 0)
        
        # Description length as proxy for detail level
        features['description_length'] = len(complaint_data.get('description', ''))
        
        # Whether coordinates are provided
        features['has_coordinates'] = 1 if (complaint_data.get('latitude') and complaint_data.get('longitude')) else 0
        
        # Hour of report (if timestamp available)
        if complaint_data.get('reported_at'):
            try:
                if isinstance(complaint_data['reported_at'], str):
                    dt = datetime.fromisoformat(complaint_data['reported_at'])
                else:
                    dt = complaint_data['reported_at']
                features['hour_reported'] = dt.hour
            except:
                features['hour_reported'] = 12  # Default to noon
        else:
            features['hour_reported'] = 12
        
        return features


class MockPriorityEngine(PriorityEngine):
    """
    Mock/Development Priority Engine
    
    **IMPORTANT**: This is a mock implementation for development only.
    Scores are PROTOTYPE and do NOT represent actual AI model predictions.
    
    Use this during development and testing. Replace with actual AI model
    in production.
    
    Mock Strategy:
    - Uses simple heuristics based on complaint data
    - Assigns scores based on category, recurrence, description length
    - Always marks model as 'development-mock'
    - Never represents mock data as real predictions
    """
    
    def __init__(self):
        self.name = "MockPriorityEngine"
        self.model_version = "development-mock-v1"
        self.is_available = True
    
    def evaluate(self, complaint_data: Dict[str, Any]) -> PriorityEvaluation:
        """
        Evaluate priority using mock heuristics.
        
        **DISCLAIMER**: This is a development mock. Scores are for testing only.
        """
        # Validate required fields
        required_fields = ['id', 'title', 'description', 'category']
        for field in required_fields:
            if field not in complaint_data or not complaint_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        complaint_id = complaint_data['id']
        category = complaint_data.get('category', 'Unknown')
        description_length = len(complaint_data.get('description', ''))
        repeat_count = complaint_data.get('repeat_complaint_count', 0)
        
        # Mock scoring heuristics (for development only)
        score = 50  # Start at medium
        factors = {}
        
        # Category-based weighting
        category_weights = {
            'Electrical Hazard': 30,  # Safety critical
            'Drainage': 20,           # Infrastructure impact
            'Road & pavement': 15,    # Traffic impact
            'Streetlight': 10,        # Safety
            'Public space': 5,        # Amenity
        }
        score += category_weights.get(category, 5)
        factors['category_weight'] = category_weights.get(category, 5)
        
        # Recurrence increases priority
        repeat_boost = min(repeat_count * 5, 20)  # Cap at +20 for repeats
        score += repeat_boost
        factors['repeat_boost'] = repeat_boost
        
        # Longer descriptions get slight priority
        if description_length > 50:
            score += 5
            factors['detailed_description'] = True
        
        # Geographic boost if coordinates provided
        if complaint_data.get('latitude') and complaint_data.get('longitude'):
            score += 5
            factors['has_coordinates'] = True
        
        # Clamp score to 0-100
        score = max(0, min(100, score))
        
        # Determine priority category from score
        if score >= 80:
            priority_category = 'Critical'
        elif score >= 60:
            priority_category = 'High'
        elif score >= 40:
            priority_category = 'Medium'
        else:
            priority_category = 'Low'
        
        explanation = (
            f"Mock priority evaluation for development. "
            f"Category: {category}. "
            f"Recurrence: {repeat_count}. "
            f"Description length: {description_length} chars. "
            f"**This is a prototype score and NOT based on an actual AI model.**"
        )
        
        logger.info(
            f"Mock priority evaluation: {complaint_id} → "
            f"{priority_category} (score: {score})"
        )
        
        return PriorityEvaluation(
            complaint_id=complaint_id,
            priority_category=priority_category,
            priority_score=score,
            explanation=explanation,
            contributing_factors=factors,
            model_version=self.model_version
        )
    
    def health_check(self) -> bool:
        """Mock engine is always healthy in development."""
        return self.is_available


class AIServiceUnavailable(Exception):
    """Raised when AI service is not available."""
    pass


class PriorityEvaluator:
    """
    Wrapper around priority engine with error handling and fallback.
    
    Handles:
    - Service unavailability
    - Timeouts
    - Invalid responses
    - Graceful fallback to manual priority
    """
    
    def __init__(self, engine: Optional[PriorityEngine] = None):
        """
        Initialize with optional custom engine.
        
        If no engine provided, uses MockPriorityEngine for development.
        """
        self.engine = engine or MockPriorityEngine()
        logger.info(f"Priority evaluator initialized with: {self.engine.name}")
    
    def evaluate(self, complaint_data: Dict[str, Any]) -> Optional[PriorityEvaluation]:
        """
        Safely evaluate complaint priority with fallback.
        
        Returns:
            PriorityEvaluation if successful, None if service unavailable
        """
        try:
            if not self.engine.health_check():
                logger.warning("Priority engine not available, skipping evaluation")
                return None
            
            evaluation = self.engine.evaluate(complaint_data)
            logger.debug(f"Priority evaluation successful: {evaluation.complaint_id}")
            return evaluation
        
        except ValueError as e:
            logger.error(f"Invalid complaint data for priority evaluation: {e}")
            return None
        
        except TimeoutError as e:
            logger.error(f"Priority evaluation timeout: {e}")
            return None
        
        except AIServiceUnavailable as e:
            logger.error(f"AI service unavailable: {e}")
            return None
        
        except Exception as e:
            logger.error(f"Unexpected error in priority evaluation: {type(e).__name__}: {e}")
            return None
    
    def set_engine(self, engine: PriorityEngine):
        """Replace engine at runtime (for testing or production switchover)."""
        self.engine = engine
        logger.info(f"Priority engine switched to: {engine.name}")


# Global evaluator instance
_evaluator: Optional[PriorityEvaluator] = None


def get_evaluator() -> PriorityEvaluator:
    """Get the global priority evaluator instance."""
    global _evaluator
    if _evaluator is None:
        # Try to initialize with AI model, fall back to mock if unavailable
        try:
            _evaluator = PriorityEvaluator(AIModelPriorityEngine())
            logger.info("✓ Priority evaluator initialized with AI Model engine")
        except Exception as e:
            logger.warning(f"AI Model not available ({e}), using Mock engine")
            _evaluator = PriorityEvaluator(MockPriorityEngine())
    return _evaluator


def set_evaluator(engine: PriorityEngine):
    """Set a custom priority engine."""
    global _evaluator
    _evaluator = PriorityEvaluator(engine)
