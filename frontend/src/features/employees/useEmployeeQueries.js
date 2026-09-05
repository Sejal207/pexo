import { useQuery } from '@tanstack/react-query';
import { httpClient } from '../../api/httpClient';

/**
 * @typedef {Object} Employee
 * @property {number} id
 * @property {string} name
 * @property {string} role
 * @property {string} department
 * @property {'active'|'inactive'} status
 */

/**
 * @typedef {Object} EmployeeDetail
 * @property {number} id
 * @property {string} name
 * @property {string} role
 * @property {string} department
 * @property {'active'|'inactive'} status
 * @property {string} email
 * @property {string} phone
 * @property {string} jobPosition
 * @property {string} manager
 * @property {string} workingSchedule
 * @property {string} workLocation
 * @property {string} company
 * @property {string} workEmail
 * @property {number} timeOffCount
 * @property {number} contractsCount
 * @property {number} attendanceCount
 */

export const useEmployeeQueries = () => {
  const employeesQuery = useQuery({
    queryKey: ['employees'],
    queryFn: async () => {
      const { data } = await httpClient.get('/employees/');
      return data;
    },
  });

  return { employeesQuery };
};

export const useEmployeeDetailQuery = (id) => useQuery({
  queryKey: ['employees', id],
  queryFn: async () => {
    const { data } = await httpClient.get(`/employees/${id}`);
    return data;
  },
  enabled: Boolean(id),
});
