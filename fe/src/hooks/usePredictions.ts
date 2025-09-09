import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services';
import type { PredictionRequest } from '../types';

// Query keys
const QUERY_KEYS = {
  PREDICTIONS: ['predictions'],
  PREDICTION_STATUS: (id: string) => ['predictions', id, 'status'],
} as const;

export const usePredictions = () => {
  return useQuery({
    queryKey: QUERY_KEYS.PREDICTIONS,
    queryFn: () => api.predictions.listPredictions(),
    refetchInterval: 5000,
  });
};

export const usePredictionStatus = (predictId: string, enabled = true) => {
  return useQuery({
    queryKey: QUERY_KEYS.PREDICTION_STATUS(predictId),
    queryFn: () => api.predictions.getPredictionStatus(predictId),
    refetchInterval: 2000,
    enabled: enabled && !!predictId,
  });
};

export const useMakePrediction = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: PredictionRequest) => api.predictions.makePrediction(request),
    onSuccess: () => {
      // Invalidate predictions list to show new prediction
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.PREDICTIONS });
    },
    onError: (error) => {
      console.error('Prediction failed:', error);
    },
  });
};