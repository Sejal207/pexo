import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { httpClient } from '../../api/httpClient';

// ---------------------------------------------------------------------
// Salary Structures / Rules
// ---------------------------------------------------------------------

export const usePayrollQueries = () => {
  const fetcher = (url) => async () => (await httpClient.get(url)).data;
  const payrunsQuery = useQuery({ queryKey: ['payruns'], queryFn: fetcher('/payruns/') });
  const payslipsQuery = useQuery({ queryKey: ['payslips'], queryFn: fetcher('/payslips/') });
  const structuresQuery = useQuery({ queryKey: ['salaryStructures'], queryFn: fetcher('/salary-structures/') });
  const rulesQuery = useQuery({ queryKey: ['salaryRules'], queryFn: fetcher('/salary-rules/') });
  return { payrunsQuery, payslipsQuery, structuresQuery, rulesQuery };
};

export const useSalaryStructureDetailQuery = (id) => useQuery({
  queryKey: ['salaryStructures', id],
  queryFn: async () => (await httpClient.get(`/salary-structures/${id}`)).data,
  enabled: Boolean(id) && id !== 'new',
});

export const useCreateSalaryStructure = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload) => (await httpClient.post('/salary-structures/', payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['salaryStructures'] }),
  });
};

export const useCreateSalaryRule = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload) => (await httpClient.post('/salary-rules/', payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['salaryRules'] }),
  });
};

export const useAttachRuleToStructure = (structureId) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ salary_rule_id, sequence }) =>
      (await httpClient.post(`/salary-structures/${structureId}/rules`, { salary_rule_id, sequence })).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['salaryStructures', structureId] }),
  });
};

// ---------------------------------------------------------------------
// Payrun wizard
// ---------------------------------------------------------------------

export const useEligibleEmployeesMutation = () => useMutation({
  mutationFn: async ({ salary_structure_id, period_start, period_end, department_id, contract_type }) =>
    (await httpClient.post('/payruns/eligible-employees', {
      salary_structure_id,
      period_start,
      period_end,
      ...(department_id ? { department_id } : {}),
      ...(contract_type ? { contract_type } : {}),
    })).data,
});

export const useCreatePayrun = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload) => (await httpClient.post('/payruns/', payload)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['payruns'] }),
  });
};

export const usePayrunDetailQuery = (id) => useQuery({
  queryKey: ['payruns', id],
  queryFn: async () => (await httpClient.get(`/payruns/${id}`)).data,
  enabled: Boolean(id) && id !== 'new',
});

// ---------------------------------------------------------------------
// Payrun workflow: compute -> validate -> mark paid -> send payslips
// ---------------------------------------------------------------------

const useWorkflowAction = (path) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payrunId) => (await httpClient.post(path(payrunId))).data,
    onSuccess: (_data, payrunId) => {
      queryClient.invalidateQueries({ queryKey: ['payruns', payrunId] });
      queryClient.invalidateQueries({ queryKey: ['payruns'] });
      queryClient.invalidateQueries({ queryKey: ['payslips'] });
    },
  });
};

export const useComputePayrun = () => useWorkflowAction((id) => `/payruns/${id}/compute`);
export const useValidatePayrun = () => useWorkflowAction((id) => `/payruns/${id}/validate`);
export const useMarkPaidPayrun = () => useWorkflowAction((id) => `/payruns/${id}/mark-paid`);
export const useSendPayslips = () => useWorkflowAction((id) => `/payruns/${id}/send-payslips`);

// ---------------------------------------------------------------------
// Payslips
// ---------------------------------------------------------------------

export const usePayslipDetailQuery = (id) => useQuery({
  queryKey: ['payslips', id],
  queryFn: async () => (await httpClient.get(`/payslips/${id}`)).data,
  enabled: Boolean(id),
});

export const usePayslipPdfMutation = () => useMutation({
  mutationFn: async (payslipId) => (await httpClient.get(`/payslips/${payslipId}/pdf`)).data,
});
