import apiClient from './axiosClient';

export const getPlacements = async () => {
  const response = await apiClient.get('/placements/');
  return response.data;
};

export const getApprovedPlacements = async () => {
  const response = await apiClient.get('/placements/?status=APPROVED');
  return response.data;
};

// NEW: Action for Administrators to approve a placement
export const approvePlacement = async (id: number | string) => {
  const response = await apiClient.post(`/placements/${id}/approve/`);
  return response.data;
};