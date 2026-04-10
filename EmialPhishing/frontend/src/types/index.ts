export interface EmailAnalysisRequest {
  email_text: string;
  headers: {
    from: string;
    [key: string]: string;
  };
}

export interface MLAnalysis {
  prediction: string;
  probabilities: {
    phishing: number;
    legitimate: number;
  };
  features?: Record<string, number>;
}

export interface OSINTAnalysis {
  risk_score: number;
  suspicious_urls?: string[];
  suspicious_emails?: string[];
  suspicious_phones?: string[];
  indicators: string[];
}

export interface AnalysisResponse {
  final_decision: 'Phishing' | 'Legitimate';
  confidence: number;
  stage: 'OSINT' | 'ML' | 'Hybrid';
  reason: string;
  ml_analysis?: MLAnalysis;
  osint_analysis?: OSINTAnalysis;
  timestamp?: string;
  id?: string;
}

export interface HealthResponse {
  status: string;
  version?: string;
  models_loaded?: boolean;
}

export interface TrainModelRequest {
  dataset_path?: string;
  epochs?: number;
}

export interface TrainModelResponse {
  status: string;
  metrics: {
    accuracy: number;
    f1_score: number;
    precision: number;
    recall: number;
  };
}

export interface Thresholds {
  ml_confidence_threshold: number;
  osint_risk_threshold: number;
  hybrid_weight_ml: number;
  hybrid_weight_osint: number;
}
