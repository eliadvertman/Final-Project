import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services';
import type { TrainingConfig } from '../types';

// Query keys
const QUERY_KEYS = {
  MODELS: ['models'],
  MODEL_STATUS: (id: string) => ['models', id, 'status'],
} as const;

export const useModels = () => {
  return useQuery({
    queryKey: QUERY_KEYS.MODELS,
    queryFn: () => api.models.listModels(),
    refetchInterval: 5000, // Refetch every 5 seconds
  });
};

export const useModelStatus = (modelId: string, enabled = true) => {
  return useQuery({
    queryKey: QUERY_KEYS.MODEL_STATUS(modelId),
    queryFn: () => api.models.getModelStatus(modelId),
    refetchInterval: 2000, // More frequent updates for status
    enabled: enabled && !!modelId,
  });
};

export const useTrainModel = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (config: TrainingConfig) => api.models.trainModel(config),
    onSuccess: () => {
      // Invalidate models list to show new model
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.MODELS });
    },
    onError: (error) => {
      console.error('Training failed:', error);
    },
  });
};