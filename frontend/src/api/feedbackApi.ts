import apiClient from './axiosClient';
export const getFeedback = async () => (await apiClient.get('/feedback/')).data;