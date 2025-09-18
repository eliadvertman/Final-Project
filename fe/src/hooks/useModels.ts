import { useQuery } from '@tanstack/react-query';
import { api } from '../services';

// Query keys
const QUERY_KEYS = {
  MODELS: ['models'],
  TRAININGS: ['trainings'],
  MODEL_STATUS: (id: string) => ['models', id, 'status'],
  TRAINING_STATUS: (id: string) => ['trainings', id, 'status'],
} as const;

// Hook for training sessions (used in Models overview page)
export const useModels = () => {
  return useQuery({
    queryKey: QUERY_KEYS.TRAININGS,
    queryFn: () => api.training.listTrainings(),
    refetchInterval: 5000, // Refetch every 5 seconds
  });
};

// Hook for actual trained models (used in Prediction page)
export const useTrainedModels = () => {
  return useQuery({
    queryKey: QUERY_KEYS.MODELS,
    queryFn: () => api.models.listModels(),
    refetchInterval: 5000, // Refetch every 5 seconds
  });
};

export const useModelStatus = (trainingId: string, enabled = true) => {
  return useQuery({
    queryKey: QUERY_KEYS.TRAINING_STATUS(trainingId),
    queryFn: () => api.training.getTrainingStatus(trainingId),
    refetchInterval: 2000, // More frequent updates for status
    enabled: enabled && !!trainingId,
  });
};