// API Types based on swagger.yaml specification

export type ConfigurationType = '2d' | '3d_fullres' | '3d_lowres' | '3d_cascade_lowres';

export interface TrainingConfig {
  modelName: string;
  imagesPath?: string;
  labelsPath?: string;
  configuration: ConfigurationType;
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
  status: 'PENDING' | 'TRAINING' | 'TRAINED' | 'FAILED' | 'DEPLOYED';
  createdAt: string;
}

export interface PredictionRequest {
  modelId: string;
  inputPath: string;
  foldIndex: number;
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

// Evaluation types
export interface EvaluationRequest {
  modelName: string;
  evaluationPath: string;
  configurations: ConfigurationType[];
}

export interface EvaluationResponse {
  message: string;
  evaluationId: string;
  batchJobId: string;
}

export interface EvaluationStatus {
  evaluationId: string;
  modelId: string;
  modelName: string;
  status: 'PENDING' | 'EVALUATING' | 'COMPLETED' | 'FAILED';
  configurations: ConfigurationType[];
  evaluationPath: string;
  startTime?: string;
  endTime?: string;
  errorMessage?: string;
  results?: Record<string, any>;
}

export interface EvaluationSummary {
  evaluationId: string;
  modelName: string;
  evaluationPath: string;
  status: 'PENDING' | 'EVALUATING' | 'COMPLETED' | 'FAILED';
  configurations: ConfigurationType[];
  createdAt: string;
}