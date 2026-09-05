import { useQuery } from '@tanstack/react-query';
import { httpClient } from '../../api/httpClient';

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
