// API Types based on swagger.yaml specification

export interface TrainingConfig {
  modelName: string;
  imagesPath?: string;
  labelsPath?: string;
  foldIndex?: number;
  taskNumber?: number;
}

export interface ModelStatus {
  modelId: string;
  status: 'PENDING' | 'TRAINING' | 'TRAINED' | 'FAILED' | 'DEPLOYED';
  progress: number;
  startTime?: string;
  endTime?: string;
  errorMessage?: string;
}

export interface ModelSummary {
  modelId: string;
  modelName: string;
  modelPath: string;
  status: 'PENDING' | 'TRAINING' | 'TRAINED' | 'FAILED' | 'DEPLOYED';
  trainingStatus: 'PENDING' | 'TRAINING' | 'TRAINED' | 'FAILED' | 'DEPLOYED';
  createdAt: string;
}

export interface PredictionRequest {
  modelId: string;
  inputPath: string;
}

export interface PredictionResponse {
  predictId: string;
  prediction: Record<string, any>;
  modelId: string;
  timestamp: string;
}

export interface PredictionStatus {
  predictId: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  modelId: string;
  startTime?: string;
  endTime?: string;
  errorMessage?: string;
}

export interface PredictionSummary {
  predictId: string;
  modelId: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  createdAt: string;
}

export interface ApiError {
  code: number;
  message: string;
}

export interface TrainingResponse {
  message: string;
  modelId: string;
}

export interface TrainingSummary {
  trainingId: string;
  trainingName: string;
  status: 'PENDING' | 'TRAINING' | 'TRAINED' | 'FAILED';
  createdAt: string;
}

// API Response types for list endpoints
export interface ModelsListResponse {
  models: ModelSummary[];
  total: number;
}

export interface PredictionsListResponse {
  predictions: PredictionSummary[];
  total: number;
}