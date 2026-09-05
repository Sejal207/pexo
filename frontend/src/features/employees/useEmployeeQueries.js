import { useQuery } from '@tanstack/react-query';
import { httpClient } from '../../api/httpClient';

const formatStatus = (status) => status
  .toLowerCase()
  .split('_')
  .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
  .join(' ');

export const useEmployeeQueries = () => {
  const departmentsQuery = useQuery({
    queryKey: ['departments'],
    queryFn: async () => {
      const { data } = await httpClient.get('/departments/');
      return data;
    },
  });

  const employeesQuery = useQuery({
    queryKey: ['employees'],
    queryFn: async () => {
      const { data } = await httpClient.get('/employees/');
      return data;
    },
  });

  const departmentsById = new Map((departmentsQuery.data ?? []).map((dept) => [dept.id, dept.name]));

  const employees = (employeesQuery.data ?? []).map((employee) => ({
    id: employee.id,
    name: `${employee.first_name} ${employee.last_name}`,
    workEmail: employee.email,
    jobPosition: employee.job_position_id ? `Position #${employee.job_position_id}` : '—',
    department: departmentsById.get(employee.department_id) ?? '—',
    status: formatStatus(employee.status),
  }));

  return {
    employees,
    isLoading: employeesQuery.isLoading || departmentsQuery.isLoading,
    isError: employeesQuery.isError || departmentsQuery.isError,
  };
};
