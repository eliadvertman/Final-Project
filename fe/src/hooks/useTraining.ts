import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services';
import type { TrainingConfig } from '../types';

export const useTrainModel = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (config: TrainingConfig) => api.training.trainModel(config),
    onSuccess: () => {
      // Invalidate models list as successful training creates a model
      queryClient.invalidateQueries({ queryKey: ['models'] });
    },
    onError: (error) => {
      console.error('Training failed:', error);
    },
  });
};