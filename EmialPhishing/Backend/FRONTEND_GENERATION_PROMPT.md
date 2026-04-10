# Frontend Generation Prompt for Phishing Detection System

## Project Overview
Create a modern, responsive web frontend for a production-grade phishing email detection system that uses TinyBERT and OSINT analysis. The backend API is already built and running.

## API Endpoints Documentation

### Base URL: `http://localhost:8000/api/v1`

---

## 1. **POST /analyze-email**
**Purpose**: Analyze email for phishing using hybrid ML and OSINT approach

**Request Body**:
```json
{
  "email_text": "string (required, min 1 char, max 100KB)",
  "headers": {
    "from": "string (optional)",
    "spf": "string (optional)",
    "dkim": "string (optional)", 
    "dmarc": "string (optional)",
    "return_path": "string (optional)"
  }
}
```

**Response**:
```json
{
  "final_decision": "Phishing|Legitimate|Error",
  "confidence": 0.85,
  "stage": "OSINT|ML|Hybrid|Error",
  "reason": "Detailed explanation of decision",
  "ml_analysis": {
    "prediction": "Phishing|Legitimate",
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
    "analysis": {
      "urls": {...},
      "emails": {...},
      "phones": {...},
      "text": {...},
      "headers": {...}
    }
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

---

## 2. **GET /health**
**Purpose**: Health check endpoint

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": true,
  "device": "cuda|cpu",
  "uptime": "0:05:30",
  "timestamp": "2024-01-01T12:00:00"
}
```

---

## 3. **GET /model-info**
**Purpose**: Get model information

**Response**:
```json
{
  "model_name": "huawei-noah/TinyBERT_General_4L_312D",
  "max_length": 512,
  "device": "cuda",
  "model_loaded": true,
  "tokenizer_loaded": true,
  "cache_dir": "./models"
}
```

---

## 4. **GET /thresholds**
**Purpose**: Get current decision thresholds

**Response**:
```json
{
  "osint_weight": 0.3,
  "ml_weight": 0.7,
  "high_risk_threshold": 0.8,
  "low_risk_threshold": 0.2
}
```

---

## 5. **PUT /thresholds**
**Purpose**: Update decision thresholds

**Request Body**:
```json
{
  "osint_weight": 0.4,
  "ml_weight": 0.6,
  "high_risk_threshold": 0.75,
  "low_risk_threshold": 0.25
}
```

**Response**: Same as GET /thresholds with updated values

---

## 6. **POST /train-model**
**Purpose**: Train the TinyBERT model on the dataset

**Request Body**:
```json
{
  "dataset_path": "./dataset/Phishing_Email.csv",
  "epochs": 3,
  "batch_size": 16
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Model training completed successfully",
  "training_results": {
    "eval_accuracy": 0.95,
    "eval_f1": 0.94,
    "eval_precision": 0.93,
    "eval_recall": 0.95
  },
  "model_path": "./models",
  "timestamp": "2024-01-01T12:00:00"
}
```

---

## 7. **POST /evaluate-model**
**Purpose**: Evaluate model on test dataset

**Response**:
```json
{
  "status": "success",
  "message": "Model evaluation completed",
  "results": {
    "metrics": {...},
    "classification_report": "...",
    "predictions": [...],
    "true_labels": [...]
  }
}
```

---

## 8. **GET /**
**Purpose**: Root endpoint

**Response**:
```json
{
  "message": "Phishing Detection API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "health": "/api/v1/health"
}
```

---

## Frontend Requirements

### **Technology Stack**
- **Framework**: React.js with TypeScript
- **UI Library**: Tailwind CSS + Headless UI
- **State Management**: React Context API or Redux Toolkit
- **HTTP Client**: Axios
- **Charts**: Chart.js or Recharts for visualization
- **Icons**: Lucide React or Heroicons

### **Pages/Components Needed**

#### 1. **Dashboard/Home Page**
- System health status
- Quick analysis form
- Recent analysis history
- Model status information
- Statistics cards

#### 2. **Email Analysis Page**
- Large text area for email input
- Optional headers input section
- Analyze button with loading state
- Results display with:
  - Decision badge (Phishing/Legitimate)
  - Confidence meter
  - Stage indicator
  - Detailed breakdown (ML + OSINT)
  - Risk factors visualization
  - URL/email/phone extraction results

#### 3. **Model Management Page**
- Model information display
- Training controls
- Training progress indicator
- Model evaluation results
- Performance metrics charts

#### 4. **Settings Page**
- Threshold configuration sliders
- Model parameters
- API settings
- Export/Import configuration

#### 5. **History Page**
- Table of past analyses
- Search and filter functionality
- Export results
- Detailed view for each analysis

### **Design Requirements**

#### **Color Scheme**
- **Primary**: Blue (#3B82F6)
- **Success**: Green (#10B981)
- **Warning**: Yellow (#F59E0B)
- **Danger**: Red (#EF4444)
- **Dark**: Gray (#1F2937)
- **Light**: Gray (#F9FAFB)

#### **Components**
- Modern card-based layout
- Responsive design (mobile-first)
- Dark/light mode toggle
- Loading skeletons
- Toast notifications
- Modal dialogs
- Tooltips

#### **Visual Elements**
- Confidence meters (progress bars)
- Risk score gauges
- Decision badges with icons
- Charts for metrics
- Tables with sorting/filtering
- Expandable sections for detailed analysis

### **Key Features**

#### **Real-time Updates**
- WebSocket connection for training progress
- Live status updates
- Real-time analysis results

#### **User Experience**
- Drag and drop email files
- Paste email content
- Auto-save drafts
- Keyboard shortcuts
- Copy results to clipboard

#### **Data Visualization**
- Confidence gauges
- Risk factor charts
- Model performance graphs
- Historical analysis trends

#### **Error Handling**
- Network error handling
- API error display
- Graceful degradation
- Retry mechanisms

### **Sample Data for Testing**

```javascript
const sampleEmails = {
  phishing: [
    {
      subject: "URGENT: Your Account Will Be Suspended",
      text: "Dear User, Your account will be suspended unless you click here: http://bit.ly/suspicious",
      headers: {
        from: "security@paypal.com",
        spf: "fail",
        dkim: "fail"
      }
    }
  ],
  legitimate: [
    {
      subject: "Team Meeting Tomorrow",
      text: "Hi everyone, Just a reminder about our meeting tomorrow at 10 AM.",
      headers: {
        from: "john@company.com",
        spf: "pass",
        dkim: "pass"
      }
    }
  ]
};
```

### **Development Instructions**

1. **Setup**:
   ```bash
   npx create-react-app phishing-detection-frontend --template typescript
   cd phishing-detection-frontend
   npm install axios tailwindcss @headlessui/react chart.js react-chartjs-2 lucide-react
   ```

2. **API Configuration**:
   ```typescript
   const API_BASE_URL = 'http://localhost:8000/api/v1';
   ```

3. **Component Structure**:
   ```
   src/
   |- components/
   |  |- common/
   |  |- analysis/
   |  |- model/
   |  |- settings/
   |- pages/
   |- hooks/
   |- services/
   |- types/
   |- utils/
   ```

4. **TypeScript Types**:
   ```typescript
   interface AnalysisResponse {
     final_decision: 'Phishing' | 'Legitimate' | 'Error';
     confidence: number;
     stage: 'OSINT' | 'ML' | 'Hybrid' | 'Error';
     reason: string;
     ml_analysis: MLAnalysis;
     osint_analysis: OSINTAnalysis;
     timestamp: string;
   }
   ```

### **Testing Requirements**
- Unit tests for components
- Integration tests for API calls
- E2E tests for user flows
- Mock API responses for development

### **Performance Considerations**
- Lazy loading for components
- Debounced API calls
- Caching for repeated requests
- Optimized re-renders
- Bundle size optimization

### **Security Considerations**
- Input sanitization
- XSS prevention
- CSRF protection
- Rate limiting indicators
- Secure storage of sensitive data

---

## Complete Prompt for AI Assistant

"Create a modern, responsive React.js frontend for a phishing email detection system with TypeScript, Tailwind CSS, and Chart.js. The frontend should include:

1. **Dashboard** with system health, quick analysis form, and statistics
2. **Email Analysis Page** with text input, results display, confidence meters, and detailed breakdowns
3. **Model Management** with training controls and performance metrics
4. **Settings Page** with threshold configuration
5. **History Page** with analysis logs and export functionality

The API base URL is `http://localhost:8000/api/v1` with endpoints for:
- POST /analyze-email (main analysis)
- GET /health (system status)
- GET /model-info (model details)
- GET/PUT /thresholds (configuration)
- POST /train-model (training)
- POST /evaluate-model (evaluation)

Use modern UI patterns, dark/light mode, real-time updates, comprehensive error handling, and data visualization for confidence scores and risk factors. Include TypeScript types for all API responses and implement proper loading states, form validation, and user feedback mechanisms."

---

## Quick Start Commands

```bash
# Create React App
npx create-react-app phishing-frontend --template typescript
cd phishing-frontend

# Install dependencies
npm install axios tailwindcss @headlessui/react chart.js react-chartjs-2 lucide-react react-router-dom

# Setup Tailwind
npx tailwindcss init -p

# Start development server
npm start
```

The frontend should connect to the backend at `http://localhost:8000` and provide a complete user interface for the phishing detection system.
