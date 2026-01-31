import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services';
import type { EvaluationRequest } from '../types';

// Query keys
const QUERY_KEYS = {
  EVALUATIONS: ['evaluations'],
  EVALUATION_STATUS: (id: string) => ['evaluations', id, 'status'],
} as const;

export const useEvaluations = () => {
  return useQuery({
    queryKey: QUERY_KEYS.EVALUATIONS,
    queryFn: () => api.evaluations.listEvaluations(),
    refetchInterval: 5000,
  });
};

export const useEvaluationStatus = (evaluationId: string, enabled = true) => {
  return useQuery({
    queryKey: QUERY_KEYS.EVALUATION_STATUS(evaluationId),
    queryFn: () => api.evaluations.getEvaluationStatus(evaluationId),
    refetchInterval: 2000,
    enabled: enabled && !!evaluationId,
  });
};

export const useRunEvaluation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: EvaluationRequest) => api.evaluations.runEvaluation(request),
    onSuccess: () => {
      // Invalidate evaluations list to show new evaluation
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.EVALUATIONS });
    },
    onError: (error) => {
      console.error('Evaluation failed:', error);
    },
  });
};


