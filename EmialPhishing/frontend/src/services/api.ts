import axios from 'axios';
import { 
  EmailAnalysisRequest, 
  AnalysisResponse, 
  HealthResponse, 
  TrainModelRequest, 
  TrainModelResponse,
  Thresholds
} from '../types';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  health: async (): Promise<HealthResponse> => {
    const response = await apiClient.get<HealthResponse>('/health');
    return response.data;
  },

  analyzeEmail: async (data: EmailAnalysisRequest): Promise<AnalysisResponse> => {
    const response = await apiClient.post<AnalysisResponse>('/analyze-email', data);
    return response.data;
  },

  trainModel: async (data?: TrainModelRequest): Promise<TrainModelResponse> => {
    const response = await apiClient.post<TrainModelResponse>('/train-model', data || {});
    return response.data;
  },

  getThresholds: async (): Promise<Thresholds> => {
    const response = await apiClient.get<Thresholds>('/thresholds');
    return response.data;
  },

  updateThresholds: async (data: Thresholds): Promise<Thresholds> => {
    const response = await apiClient.put<Thresholds>('/thresholds', data);
    return response.data;
  }
};
