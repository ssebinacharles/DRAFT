import apiClient from './axiosClient';

// Ensure these paths match your Django urls.py exactly
export const getUsers = async () => {
  const response = await apiClient.get('/users/');
  return response.data;
};

export const getStudents = async () => {
  const response = await apiClient.get('/students/');
  return response.data;
};

export const getSupervisors = async () => {
  const response = await apiClient.get('/supervisors/');
  return response.data;
};

export const getAdministrators = async () => {
  const response = await apiClient.get('/administrators/');
  return response.data;
};