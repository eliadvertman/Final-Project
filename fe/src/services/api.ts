import axios from 'axios';
import type { AxiosResponse } from 'axios';
import type {
  TrainingConfig,
  ModelStatus,
  ModelSummary,
  PredictionRequest,
  PredictionResponse,
  PredictionStatus,
  PredictionSummary,
  TrainingResponse,
} from '../types';

const API_BASE_URL = 'http://localhost:8080/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor for logging
apiClient.interceptors.request.use((config) => {
  console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(`❌ API Error: ${error.response?.status} ${error.config?.url}`, error.response?.data);
    return Promise.reject(error);
  }
);

export const modelApi = {
  // Train a new model
  trainModel: async (config: TrainingConfig): Promise<TrainingResponse> => {
    const response: AxiosResponse<TrainingResponse> = await apiClient.post('/model/train', config);
    return response.data;
  },

  // Get model training status
  getModelStatus: async (modelId: string): Promise<ModelStatus> => {
    const response: AxiosResponse<ModelStatus> = await apiClient.get(`/model/${modelId}/status`);
    return response.data;
  },

  // List all models
  listModels: async (limit = 10, offset = 0): Promise<ModelSummary[]> => {
    const response: AxiosResponse<ModelSummary[]> = await apiClient.get('/model/list', {
      params: { limit, offset }
    });
    return response.data;
  },
};

export const predictionApi = {
  // Make a prediction
  makePrediction: async (request: PredictionRequest): Promise<PredictionResponse> => {
    const response: AxiosResponse<PredictionResponse> = await apiClient.post('/inference/predict', request);
    return response.data;
  },

  // Get prediction status
  getPredictionStatus: async (predictId: string): Promise<PredictionStatus> => {
    const response: AxiosResponse<PredictionStatus> = await apiClient.get(`/inference/${predictId}/status`);
    return response.data;
  },

  // List all predictions
  listPredictions: async (limit = 10, offset = 0): Promise<PredictionSummary[]> => {
    const response: AxiosResponse<PredictionSummary[]> = await apiClient.get('/inference/list', {
      params: { limit, offset }
    });
    return response.data;
  },
};

// Combined API object for easier imports
export const api = {
  models: modelApi,
  predictions: predictionApi,
};

export default api;