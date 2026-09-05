import { useQuery } from '@tanstack/react-query';
import { httpClient } from '../../api/httpClient';

export const normalizeContract = (c) => {
  if (!c) return null;
  const shortId = typeof c.id === 'string' ? c.id.slice(0, 8).toUpperCase() : String(c.id);
  const isRunning = (c.status || '').toUpperCase() === 'ACTIVE' || (c.status || '').toLowerCase() === 'running';

  return {
    ...c,
    id: c.id,
    code: c.code || `CTR-${shortId}`,
    employeeId: c.employee_id || c.employeeId,
    employeeName: c.employee_name || c.employeeName || `Employee ${c.employee_id ? String(c.employee_id).slice(0, 8) : ''}`,
    startDate: c.start_date || c.startDate || '',
    endDate: c.end_date || c.endDate || null,
    wagePerMonth: Number(c.wage_amount ?? c.wagePerMonth ?? 0),
    wageType: c.wage_type || 'MONTHLY',
    contractType: c.contract_type || 'PERMANENT',
    status: isRunning ? 'running' : 'expired',
    rawStatus: c.status || 'ACTIVE',
  };
};

export const normalizeContractDetail = (c) => {
  if (!c) return null;
  const base = normalizeContract(c);
  return {
    ...base,
    department: c.department_name || c.department || 'General',
    jobPosition: c.job_position_title || c.jobPosition || 'Employee',
    workingSchedule: c.working_schedule_name || c.workingSchedule || 'Standard 40h',
    structureType: c.salary_structure_name || c.structureType || 'Regular Salary Structure',
    notes: c.notes || `Contract type: ${c.contract_type || 'PERMANENT'}, Wage type: ${c.wage_type || 'MONTHLY'}`,
  };
};

export const useContractsQuery = (employeeId) => useQuery({
  queryKey: ['contracts', employeeId],
  queryFn: async () => {
    const { data } = await httpClient.get('/contracts/', {
      params: employeeId ? { employeeId } : undefined,
    });
    return Array.isArray(data) ? data.map(normalizeContract) : [];
  },
});

export const useContractDetailQuery = (id) => useQuery({
  queryKey: ['contracts', id],
  queryFn: async () => {
    const { data } = await httpClient.get(`/contracts/${id}`);
    return normalizeContractDetail(data);
  },
  enabled: Boolean(id),
});
