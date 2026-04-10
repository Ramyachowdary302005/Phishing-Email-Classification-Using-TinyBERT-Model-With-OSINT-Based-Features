from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict
import logging
from datetime import datetime
import psutil
import os

from app.models.schemas import (
    EmailAnalysisRequest,
    EmailAnalysisResponse,
    TrainingRequest,
    TrainingResponse,
    HealthResponse,
    ModelInfoResponse,
    ThresholdsResponse,
    ThresholdsUpdateRequest,
    ErrorResponse
)
from app.services.decision_engine import DecisionEngine
from app.services.ml_service import MLService
from app.utils.preprocessor import EmailPreprocessor
from app.config.settings import settings

logger = logging.getLogger(__name__)

# Global variables for services
decision_engine = None
ml_service = None
preprocessor = None
start_time = datetime.now()

router = APIRouter()


def get_decision_engine():
    global decision_engine
    if decision_engine is None:
        decision_engine = DecisionEngine()
    return decision_engine


def get_ml_service():
    global ml_service
    if ml_service is None:
        ml_service = MLService()
    return ml_service


def get_preprocessor():
    global preprocessor
    if preprocessor is None:
        preprocessor = EmailPreprocessor()
    return preprocessor


@router.post("/analyze-email", response_model=EmailAnalysisResponse)
async def analyze_email(
    request: EmailAnalysisRequest,
    engine: DecisionEngine = Depends(get_decision_engine)
):
    """Analyze email for phishing using hybrid ML and OSINT approach."""
    try:
        logger.info(f"Received email analysis request: {len(request.email_text)} characters")
        
        # Perform analysis
        result = engine.analyze_email(request.email_text, request.headers)
        
        # Normalize osint_analysis so frontend receives 'indicators' key
        osint_raw = result['osint_analysis']
        osint_normalized = {
            **osint_raw,
            'indicators': osint_raw.get('reasons', [])
        }

        # Ensure ml_analysis has probabilities key
        ml_raw = result['ml_analysis']
        if 'probabilities' not in ml_raw:
            ml_raw['probabilities'] = {'phishing': 0.0, 'legitimate': 1.0}

        # Convert to response model
        response = EmailAnalysisResponse(
            final_decision=result['final_decision'],
            confidence=result['confidence'],
            stage=result['stage'],
            reason=result['reason'],
            ml_analysis=ml_raw,
            osint_analysis=osint_normalized
        )
        
        logger.info(f"Analysis completed: {result['final_decision']} (confidence: {result['confidence']:.2f})")
        return response
        
    except Exception as e:
        logger.error(f"Error in email analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/train-model", response_model=TrainingResponse)
async def train_model(
    request: TrainingRequest,
    ml_service: MLService = Depends(get_ml_service),
    preprocessor: EmailPreprocessor = Depends(get_preprocessor)
):
    """Train the TinyBERT model on the dataset."""
    try:
        logger.info("Starting model training")
        
        # Use provided path or default
        dataset_path = request.dataset_path or settings.dataset_path
        
        # Load and preprocess dataset
        df = preprocessor.load_and_preprocess_dataset(dataset_path)
        train_df, test_df = preprocessor.split_dataset(df)
        
        # Train model
        training_results = ml_service.train_model(train_df, test_df)
        
        response = TrainingResponse(
            status="success",
            message="Model training completed successfully",
            training_results=training_results['training_results'],
            model_path=training_results['model_path']
        )
        
        logger.info(f"Model training completed: {training_results['training_results']}")
        return response
        
    except Exception as e:
        logger.error(f"Error in model training: {e}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Calculate uptime
        uptime = datetime.now() - start_time
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        
        # Get system info
        device = "cuda" if psutil.cpu_percent() < 90 else "cpu"  # Simple device detection
        
        # Check if model is loaded
        ml_service = get_ml_service()
        model_loaded = ml_service.model is not None
        
        response = HealthResponse(
            status="healthy",
            version=settings.app_version,
            model_loaded=model_loaded,
            device=device,
            uptime=uptime_str
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/model-info", response_model=ModelInfoResponse)
async def get_model_info(ml_service: MLService = Depends(get_ml_service)):
    """Get model information."""
    try:
        info = ml_service.get_model_info()
        
        response = ModelInfoResponse(
            model_name=info['model_name'],
            max_length=info['max_length'],
            device=info['device'],
            model_loaded=info['model_loaded'],
            tokenizer_loaded=info['tokenizer_loaded'],
            cache_dir=info['cache_dir']
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")


@router.get("/thresholds", response_model=ThresholdsResponse)
async def get_thresholds(engine: DecisionEngine = Depends(get_decision_engine)):
    """Get current decision thresholds."""
    try:
        thresholds = engine.get_decision_thresholds()
        
        response = ThresholdsResponse(
            osint_weight=thresholds['osint_weight'],
            ml_weight=thresholds['ml_weight'],
            high_risk_threshold=thresholds['high_risk_threshold'],
            low_risk_threshold=thresholds['low_risk_threshold']
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting thresholds: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get thresholds: {str(e)}")


@router.put("/thresholds", response_model=ThresholdsResponse)
async def update_thresholds(
    request: ThresholdsUpdateRequest,
    engine: DecisionEngine = Depends(get_decision_engine)
):
    """Update decision thresholds."""
    try:
        # Update thresholds
        engine.update_thresholds(
            osint_weight=request.osint_weight,
            ml_weight=request.ml_weight,
            high_risk_threshold=request.high_risk_threshold,
            low_risk_threshold=request.low_risk_threshold
        )
        
        # Get updated thresholds
        thresholds = engine.get_decision_thresholds()
        
        response = ThresholdsResponse(
            osint_weight=thresholds['osint_weight'],
            ml_weight=thresholds['ml_weight'],
            high_risk_threshold=thresholds['high_risk_threshold'],
            low_risk_threshold=thresholds['low_risk_threshold']
        )
        
        logger.info(f"Thresholds updated: {thresholds}")
        return response
        
    except Exception as e:
        logger.error(f"Error updating thresholds: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update thresholds: {str(e)}")


@router.post("/evaluate-model")
async def evaluate_model(
    ml_service: MLService = Depends(get_ml_service),
    preprocessor: EmailPreprocessor = Depends(get_preprocessor)
):
    """Evaluate model on test dataset."""
    try:
        logger.info("Starting model evaluation")
        
        # Load and preprocess dataset
        df = preprocessor.load_and_preprocess_dataset(settings.dataset_path)
        _, test_df = preprocessor.split_dataset(df)
        
        # Evaluate model
        results = ml_service.evaluate_model(test_df)
        
        return {
            "status": "success",
            "message": "Model evaluation completed",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in model evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


