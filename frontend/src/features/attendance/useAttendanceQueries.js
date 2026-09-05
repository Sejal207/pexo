import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import httpClient from '../../api/httpClient';
// ⚠️ Adjust the import path above to match wherever httpClient actually lives
// (check the top of useContractQueries.js for the exact relative path).

const ATTENDANCE_KEY = 'attendance';

export function useAttendanceQuery({ employeeId, date, search } = {}) {
  return useQuery({
    queryKey: [ATTENDANCE_KEY, { employeeId, date, search }],
    queryFn: async () => {
      const params = {};
      if (employeeId) params.employee_id = employeeId; // ⚠️ confirm this matches the backend's actual query param name
      if (date) params.date = date;
      if (search) params.search = search;

      const { data } = await httpClient.get('/attendance', { params });
      return data;
    },
  });
}

export function useCreateAttendanceMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload) => {
      const { data } = await httpClient.post('/attendance', payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [ATTENDANCE_KEY] });
    },
  });
}