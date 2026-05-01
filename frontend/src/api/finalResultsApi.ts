import apiClient from './axiosClient';

export const getFinalResults = async () => {
  const response = await apiClient.get('/final-results/');
  return response.data;
};

// NEW: Action for Administrators to publish a student's final result
export const publishFinalResult = async (id: number | string) => {
  const response = await apiClient.post(`/final-results/${id}/publish/`);
  return response.data;
};