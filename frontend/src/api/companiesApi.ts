import apiClient from './axiosClient';

export const getCompanies = async () => {
  const response = await apiClient.get('/companies/');
  return response.data;
};