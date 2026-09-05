import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { httpClient } from '../../api/httpClient';

export const usePayrollQueries = () => {
  const fetcher = (url: string) => async () => (await httpClient.get(url)).data;
  const payrunsQuery = useQuery({ queryKey: ['payruns'], queryFn: fetcher('/payruns/') });
  const payslipsQuery = useQuery({ queryKey: ['payslips'], queryFn: fetcher('/payslips/') });
  const structuresQuery = useQuery({ queryKey: ['salaryStructures'], queryFn: fetcher('/structures/') });
  const rulesQuery = useQuery({ queryKey: ['salaryRules'], queryFn: fetcher('/rules/') });
  return { payrunsQuery, payslipsQuery, structuresQuery, rulesQuery };
};

export const usePayrollCreateMutation = (path: string, key: string) => {
  const queryClient = useQueryClient();
  return useMutation({ mutationFn: async (payload: unknown) => (await httpClient.post(path, payload)).data, onSuccess: () => queryClient.invalidateQueries({ queryKey: [key] }) });
};
