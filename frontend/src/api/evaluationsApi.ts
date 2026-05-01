import apiClient from './axiosClient';

export const getEvaluations = async () => {
  const response = await apiClient.get('/evaluations/');
  return response.data;
};

// NEW: Submit a completed evaluation
export const submitEvaluation = async (id: number | string) => {
  const response = await apiClient.post(`/evaluations/${id}/submit/`);
  return response.data;
};

// NEW: Post a raw score for a specific evaluation criterion
export const createEvaluationScore = async (payload: {
  evaluation_id: number;
  criterion_id: number;
  raw_score: string | number;
}) => {
  const response = await apiClient.post('/evaluation-scores/', payload);
  return response.data;
};