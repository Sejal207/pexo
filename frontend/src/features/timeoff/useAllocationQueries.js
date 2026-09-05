import { useQuery } from '@tanstack/react-query';
import { httpClient } from '../../api/httpClient';

/**
 * @typedef {Object} Allocation
 * @property {number} id
 * @property {string} employeeName
 * @property {string} type
 * @property {number} allocatedDays
 * @property {number} takenDays
 * @property {number} remainingDays
 * @property {'Approved'|'To Approve'|'Refused'} status
 */

/**
 * @typedef {Object} AllocationDetail
 * @property {number} id
 * @property {string} employeeName
 * @property {string} type
 * @property {number} allocatedDays
 * @property {number} takenDays
 * @property {number} remainingDays
 * @property {'Approved'|'To Approve'|'Refused'} status
 * @property {string} approver
 * @property {string} validity
 * @property {string} description
 */

export const useAllocationsQuery = () => useQuery({
  queryKey: ['allocations'],
  queryFn: async () => {
    const { data } = await httpClient.get('/time-off/allocations');
    return data;
  },
});

export const useAllocationDetailQuery = (id) => useQuery({
  queryKey: ['allocations', id],
  queryFn: async () => {
    const { data } = await httpClient.get(`/time-off/allocations/${id}`);
    return data;
  },
  enabled: Boolean(id),
});
