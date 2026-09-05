import { useQuery } from '@tanstack/react-query';
import { httpClient } from '../../api/httpClient';

export const normalizeEmployee = (e) => {
  if (!e) return null;
  const fullName = [e.first_name, e.last_name].filter(Boolean).join(' ').trim() || e.name || e.employee_code || 'Unnamed Employee';
  const statusStr = (e.employment_status || e.status || 'ACTIVE').toLowerCase();
  const isActive = statusStr === 'active';

  return {
    ...e,
    id: e.id,
    name: fullName,
    role: e.job_position_title || e.jobPosition || e.role || 'Employee',
    department: e.department_name || e.department || 'General',
    status: isActive ? 'active' : 'inactive',
    employmentStatus: e.employment_status || (isActive ? 'ACTIVE' : 'INACTIVE'),
    email: e.email || e.workEmail || '',
    phone: e.phone || '',
    dateJoined: e.date_joined || e.dateJoined || '',
    employeeCode: e.employee_code || e.employeeCode || '',
  };
};

export const normalizeEmployeeDetail = (e) => {
  if (!e) return null;
  const base = normalizeEmployee(e);
  return {
    ...base,
    timeOffCount: e.time_off_count ?? e.timeOffCount ?? 0,
    contractsCount: e.contracts_count ?? e.contractsCount ?? 0,
    attendanceCount: e.attendance_count ?? e.attendanceCount ?? 0,
    jobPosition: e.job_position_title || e.jobPosition || 'Employee',
    manager: e.manager_name || e.manager || 'None',
    workingSchedule: e.working_schedule_name || e.workingSchedule || 'Standard 40h',
    workLocation: e.work_location || e.workLocation || (e.city ? `${e.city}, ${e.state || ''}` : 'Headquarters'),
    company: e.company || 'Pexo',
    workEmail: e.email || e.workEmail || '',
    addressLine: e.address_line || e.addressLine || '',
    city: e.city || '',
    state: e.state || '',
    pincode: e.pincode || '',
  };
};

export const useEmployeeQueries = () => {
  const employeesQuery = useQuery({
    queryKey: ['employees'],
    queryFn: async () => {
      const { data } = await httpClient.get('/employees/');
      return Array.isArray(data) ? data.map(normalizeEmployee) : [];
    },
  });

  return { employeesQuery };
};

export const useEmployeeDetailQuery = (id) => useQuery({
  queryKey: ['employees', id],
  queryFn: async () => {
    const { data } = await httpClient.get(`/employees/${id}`);
    return normalizeEmployeeDetail(data);
  },
  enabled: Boolean(id),
});
