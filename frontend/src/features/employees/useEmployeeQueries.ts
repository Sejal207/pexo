import { useQuery } from '@tanstack/react-query';
import { httpClient } from '../../api/httpClient';
import type { Employee } from './types';

export const useEmployeeQueries = () => {
  const employeesQuery = useQuery({
    queryKey: ['employees'],
    queryFn: async () => {
      const { data } = await httpClient.get<Employee[]>('/employees/');
      return data;
    },
  });

  return { employeesQuery };
};
