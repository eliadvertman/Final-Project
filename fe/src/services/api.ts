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
  TrainingSummary,
  EvaluationRequest,
  EvaluationResponse,
  EvaluationStatus,
  EvaluationSummary,
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
  // Get model status
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

export const trainingApi = {
  // Train a new model
  trainModel: async (config: TrainingConfig): Promise<TrainingResponse> => {
    const response: AxiosResponse<TrainingResponse> = await apiClient.post('/training/train', config);
    return response.data;
  },

  // Get training status
  getTrainingStatus: async (trainingId: string): Promise<ModelStatus> => {
    const response: AxiosResponse<ModelStatus> = await apiClient.get(`/training/${trainingId}/status`);
    return response.data;
  },

  // List all trainings
  listTrainings: async (limit = 10, offset = 0): Promise<TrainingSummary[]> => {
    const response: AxiosResponse<TrainingSummary[]> = await apiClient.get('/training/list', {
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

export const evaluationApi = {
  // Run an evaluation
  runEvaluation: async (request: EvaluationRequest): Promise<EvaluationResponse> => {
    const response: AxiosResponse<EvaluationResponse> = await apiClient.post('/evaluation/evaluate', request);
    return response.data;
  },

  // Get evaluation status
  getEvaluationStatus: async (evaluationId: string): Promise<EvaluationStatus> => {
    const response: AxiosResponse<EvaluationStatus> = await apiClient.get(`/evaluation/${evaluationId}/status`);
    return response.data;
  },

  // List all evaluations
  listEvaluations: async (limit = 10, offset = 0): Promise<EvaluationSummary[]> => {
    const response: AxiosResponse<EvaluationSummary[]> = await apiClient.get('/evaluation/list', {
      params: { limit, offset }
    });
    return response.data;
  },
};

// Combined API object for easier imports
export const api = {
  models: modelApi,
  training: trainingApi,
  predictions: predictionApi,
  evaluations: evaluationApi,
};

export default api;