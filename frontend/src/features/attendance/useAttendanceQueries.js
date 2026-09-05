import { useQuery } from '@tanstack/react-query';
import { httpClient } from '../../api/httpClient';

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

export const useAttendanceDetailQuery = (id) => useQuery({
  queryKey: ['attendance', id],
  queryFn: async () => {
    const { data } = await httpClient.get(`/attendance/${id}`);
    return data;
  },
  enabled: Boolean(id),
});
