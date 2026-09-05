import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { httpClient } from '../../api/httpClient';

/**
 * @typedef {Object} TimeOffRequest
 * @property {number} id
 * @property {string} employee_id
 * @property {string} employee_name
 * @property {string} time_off_type_id
 * @property {string} time_off_type_name
 * @property {string} start_date
 * @property {string} end_date
 * @property {number} duration
 * @property {'SUBMITTED'|'APPROVED'|'REFUSED'|'CANCELLED'} status
 */

export const useTimeOffRequestsQuery = (filters = {}) => useQuery({
  queryKey: ['timeOffRequests', filters],
  queryFn: async () => {
    const params = new URLSearchParams();
    if (filters.search) params.append('search', filters.search);
    if (filters.myTeamOnly) params.append('my_team_only', 'true');
    const { data } = await httpClient.get(`/time-off/requests?${params}`);
    return data;
  },
});

export const useTimeOffRequestQuery = (id) => useQuery({
  queryKey: ['timeOffRequests', id],
  queryFn: async () => {
    const { data } = await httpClient.get(`/time-off/requests/${id}`);
    return data;
  },
  enabled: Boolean(id),
});

export const useApproveRequestMutation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id) => {
      const { data } = await httpClient.post(`/time-off/requests/${id}/approve`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['timeOffRequests'] });
    },
  });
};

export const useRefuseRequestMutation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id) => {
      const { data } = await httpClient.post(`/time-off/requests/${id}/refuse`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['timeOffRequests'] });
    },
  });
};
