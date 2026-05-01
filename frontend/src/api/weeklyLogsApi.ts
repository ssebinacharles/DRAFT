import apiClient from './axiosClient';

export const getWeeklyLogs = async () => {
  const response = await apiClient.get('/weekly-logs/');
  return response.data;
};

// NEW: Action for Students to officially submit a draft log
export const submitWeeklyLog = async (id: number | string) => {
  const response = await apiClient.post(`/weekly-logs/${id}/submit/`);
  return response.data;
};