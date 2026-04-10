# Phishing Email Detection System

A production-grade phishing email detection system using TinyBERT and OSINT analysis. This system combines machine learning predictions with open-source intelligence (OSINT) analysis to provide accurate phishing detection.

## Features

- **Machine Learning**: Fine-tuned TinyBERT model for email classification
- **OSINT Analysis**: URL analysis, domain reputation, spam indicators
- **Hybrid Decision Engine**: Combines ML and OSINT scores for optimal accuracy
- **Production Ready**: FastAPI backend with proper logging, error handling, and validation
- **Real-time Analysis**: Fast inference for email analysis
- **Model Training**: Automated training pipeline with evaluation metrics

## Architecture

```
├── app/
│   ├── config/
│   │   └── settings.py          # Configuration settings
│   ├── models/
│   │   └── schemas.py           # Pydantic models
│   ├── routes/
│   │   └── analysis.py          # API endpoints
│   ├── services/
│   │   ├── ml_service.py        # ML model service
│   │   ├── osint_service.py     # OSINT analysis service
│   │   └── decision_engine.py   # Hybrid decision engine
│   ├── utils/
│   │   ├── logger.py            # Logging configuration
│   │   └── preprocessor.py      # Data preprocessing
│   └── main.py                  # FastAPI application
├── dataset/
│   └── Phishing_Email.csv       # Training dataset
├── models/                      # Trained models storage
├── logs/                        # Application logs
├── tests/                       # Test files
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
├── train_model.py              # Training script
└── README.md                   # This file
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd phishing-detection-backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   - Copy `.env` file and update configuration as needed
   - Ensure dataset path is correct: `./dataset/Phishing_Email.csv`

## Usage

### 1. Train the Model

Before using the API, train the TinyBERT model:

```bash
python train_model.py
```

Optional parameters:
```bash
python train_model.py --dataset-path ./dataset/Phishing_Email.csv --epochs 3 --batch-size 16
```

### 2. Start the API Server

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or simply:
```bash
python app/main.py
```

### 3. Access the API

- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

## API Endpoints

### POST /api/v1/analyze-email
Analyze email for phishing using hybrid ML and OSINT approach.

**Request Body**:
```json
{
  "email_text": "Your email content here...",
  "headers": {
    "from": "sender@example.com",
    "spf": "pass",
    "dkim": "pass",
    "dmarc": "pass"
  }
}
```

**Response**:
```json
{
  "final_decision": "Phishing",
  "confidence": 0.85,
  "stage": "Hybrid",
  "reason": "Hybrid analysis indicates phishing due to: 2 suspicious URLs, high ML confidence (95.0%)",
  "ml_analysis": {
    "prediction": "Phishing",
    "confidence": 0.95,
    "probabilities": {
      "legitimate": 0.05,
      "phishing": 0.95
    }
  },
  "osint_analysis": {
    "risk_score": 0.7,
    "url_count": 3,
    "email_count": 2,
    "phone_count": 0,
    "suspicious_urls": 2,
    "suspicious_emails": 1,
    "suspicious_phones": 0,
    "spam_indicators": 4,
    "phishing_indicators": 3,
    "reasons": ["Suspicious TLD detected: .tk", "Spam keyword detected: free"],
    "analysis": {...}
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

### POST /api/v1/train-model
Train the TinyBERT model on the dataset.

**Request Body**:
```json
{
  "dataset_path": "./dataset/Phishing_Email.csv",
  "epochs": 3,
  "batch_size": 16
}
```

### GET /api/v1/health
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": true,
  "device": "cuda",
  "uptime": "0:05:30",
  "timestamp": "2024-01-01T12:00:00"
}
```

### GET /api/v1/model-info
Get model information.

### GET /api/v1/thresholds
Get current decision thresholds.

### PUT /api/v1/thresholds
Update decision thresholds.

## Decision Logic

The system uses a hybrid approach combining:

1. **OSINT Analysis** (30% weight by default):
   - URL analysis (suspicious domains, TLDs, patterns)
   - Email address analysis
   - Phone number detection
   - Spam and phishing keyword detection
   - Header analysis (SPF, DKIM, DMARC)

2. **ML Prediction** (70% weight by default):
   - TinyBERT model fine-tuned on email dataset
   - Probability-based classification
   - Confidence scoring

3. **Decision Rules**:
   - High OSINT risk (>0.8) → Immediate phishing detection
   - Low OSINT risk (<0.2) → Immediate legitimate classification
   - Medium risk → Hybrid decision combining both scores

## Model Performance

Expected performance metrics (based on training):
- **Accuracy**: >95%
- **Precision**: >94%
- **Recall**: >95%
- **F1-Score**: >94%

## Configuration

Key configuration options in `.env`:

```env
# Model Configuration
MODEL_NAME=huawei-noah/TinyBERT_General_4L_312D
MAX_TOKEN_LENGTH=512
MODEL_CACHE_DIR=./models

# Decision Thresholds
OSINT_WEIGHT=0.3
ML_WEIGHT=0.7
HIGH_RISK_THRESHOLD=0.8
LOW_RISK_THRESHOLD=0.2

# Dataset Configuration
DATASET_PATH=./dataset/Phishing_Email.csv
TRAIN_SPLIT=0.8
```

## Dataset

The system uses a dataset with ~18,000 emails containing:
- **Email Text**: Raw email content (noisy, real-world emails)
- **Email Type**: Labels ("Safe Email" or "Phishing Email")

The dataset is automatically preprocessed:
- HTML tag removal
- URL/email/phone extraction
- Text cleaning and normalization
- Label conversion (Safe Email → 0, Phishing Email → 1)

## Logging

The system uses structured logging with:
- Console output with colors
- File logging with rotation
- Different log levels (DEBUG, INFO, WARNING, ERROR)
- Log files stored in `./logs/`

## Error Handling

- Comprehensive exception handling
- Input validation with Pydantic
- Graceful error responses
- Global exception handlers

## Production Considerations

- **Scalability**: FastAPI with async support
- **Security**: Input validation and sanitization
- **Monitoring**: Health checks and logging
- **Performance**: Model caching and efficient preprocessing
- **Reliability**: Error handling and graceful degradation

## Testing

Run tests with:
```bash
pytest tests/
```

## Contributing

1. Follow the existing code structure
2. Add proper logging for new features
3. Write tests for new functionality
4. Update documentation

## License

This project is licensed under the MIT License.
