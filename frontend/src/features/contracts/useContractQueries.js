import { useQuery } from '@tanstack/react-query';
import { httpClient } from '../../api/httpClient';

/**
 * @typedef {Object} Contract
 * @property {number} id
 * @property {string} code
 * @property {number} employeeId
 * @property {string} employeeName
 * @property {string} startDate
 * @property {string|null} endDate
 * @property {number} wagePerMonth
 * @property {'running'|'expired'} status
 */

/**
 * @typedef {Object} ContractDetail
 * @property {number} id
 * @property {string} code
 * @property {string} employeeName
 * @property {string} startDate
 * @property {string|null} endDate
 * @property {'running'|'expired'} status
 * @property {string} department
 * @property {string} jobPosition
 * @property {number} wagePerMonth
 * @property {string} workingSchedule
 * @property {string} structureType
 * @property {string} notes
 */

export const useContractsQuery = (employeeId) => useQuery({
  queryKey: ['contracts', employeeId],
  queryFn: async () => {
    const { data } = await httpClient.get('/contracts/', {
      params: employeeId ? { employeeId } : undefined,
    });
    return data;
  },
});

export const useContractDetailQuery = (id) => useQuery({
  queryKey: ['contracts', id],
  queryFn: async () => {
    const { data } = await httpClient.get(`/contracts/${id}`);
    return data;
  },
  enabled: Boolean(id),
});
