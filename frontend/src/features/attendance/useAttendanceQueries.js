import { useQuery } from '@tanstack/react-query';
import { httpClient } from '../../api/httpClient';

/**
 * @typedef {Object} Attendance
 * @property {number} id
 * @property {number} employeeId
 * @property {string} employeeName
 * @property {string} date
 * @property {string|null} checkIn
 * @property {string|null} checkOut
 * @property {number} workedHours
 * @property {'Present'|'Absent'|'Half Day'|'Late'} status
 */

/**
 * @typedef {Object} AttendanceDetail
 * @property {number} id
 * @property {string} employeeName
 * @property {string} date
 * @property {string} checkIn
 * @property {string} checkOut
 * @property {number} workedHours
 * @property {number} overtimeHours
 * @property {'Present'|'Absent'|'Half Day'|'Late'} status
 * @property {string} department
 * @property {string} manager
 * @property {string} notes
 */

export const useAttendanceQuery = (employeeId) => useQuery({
  queryKey: ['attendance', 'list', employeeId],
  queryFn: async () => {
    const { data } = await httpClient.get('/attendance/', {
      params: employeeId ? { employeeId } : undefined,
    });
    return data;
  },
});

export const useAttendanceDetailQuery = (id) => useQuery({
  queryKey: ['attendance', id],
  queryFn: async () => {
    const { data } = await httpClient.get(`/attendance/${id}`);
    return data;
  },
  enabled: Boolean(id),
});
