import { useQuery } from '@tanstack/react-query';
import { httpClient } from '../../api/httpClient';

export const usePayrollQueries = () => {
  const payrunsQuery = useQuery({
    queryKey: ['payruns'],
    queryFn: async () => {
      const { data } = await httpClient.get('/payruns/');
      return data;
    },
  });

  return { payrunsQuery };
};
