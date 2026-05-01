import apiClient from './axiosClient';
export const getSupervisorAssignments = async () => (await apiClient.get('/supervisor-assignments/')).data;