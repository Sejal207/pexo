import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  setSearchText,
  setEmployeeFilter,
  clearEmployeeFilter,
  toggleTodayFilter,
  clearTodayFilter,
} from '../features/attendance/attendanceSlice';
import {
  useAttendanceQuery,
  useCreateAttendanceMutation,
} from '../features/attendance/useAttendanceQueries';
import StatusBadge from '../features/attendance/components/StatusBadge';

function formatTime(value) {
  if (!value) return '—';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export default function AttendancePage() {
  const [searchParams] = useSearchParams();
  const dispatch = useDispatch();

  const { searchText, employeeIdFilter, employeeNameFilter, dateFilter, isTodayFilterActive } =
    useSelector((state) => state.attendance);

  const [isNewModalOpen, setIsNewModalOpen] = useState(false);

  useEffect(() => {
    const employeeId = searchParams.get('employeeId');
    const employeeName = searchParams.get('employeeName');
    if (employeeId) {
      dispatch(setEmployeeFilter({ employeeId, employeeName }));
    }
  }, [searchParams, dispatch]);

  const { data, isLoading, isError } = useAttendanceQuery({
    employeeId: employeeIdFilter,
    date: dateFilter,
    search: searchText,
  });

  // ⚠️ Adjust if your backend wraps results, e.g. `data?.items` instead of `data`
  const records = data?.results ?? data ?? [];

  const createAttendance = useCreateAttendanceMutation();

  return (
    <div className="w-full max-w-screen-xl mx-auto px-4 sm:px-6 py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-100">Attendance</h1>
        <p className="text-sm text-slate-400 mt-1">List view of employee attendance records</p>
      </div>

      <div className="flex flex-wrap items-center gap-3 mb-4">
        <button
          type="button"
          onClick={() => setIsNewModalOpen(true)}
          className="px-4 py-2 rounded-md bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition-colors"
        >
          New
        </button>

        <input
          type="text"
          value={searchText}
          onChange={(e) => dispatch(setSearchText(e.target.value))}
          placeholder="Search attendance..."
          className="flex-1 min-w-[200px] px-3 py-2 rounded-md bg-slate-800 border border-slate-700/60 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
        />

        <button
          type="button"
          onClick={() => (isTodayFilterActive ? dispatch(clearTodayFilter()) : dispatch(toggleTodayFilter()))}
          className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
            isTodayFilterActive
              ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/40'
              : 'bg-slate-800 text-slate-300 border-slate-700/60 hover:border-slate-600'
          }`}
        >
          Today
        </button>

        {employeeIdFilter && (
          <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/40">
            Employee: {employeeNameFilter || employeeIdFilter}
            <button
              type="button"
              onClick={() => dispatch(clearEmployeeFilter())}
              className="text-indigo-300 hover:text-white"
              aria-label="Clear employee filter"
            >
              ×
            </button>
          </span>
        )}
      </div>

      <div className="rounded-lg border border-slate-700/60 bg-slate-800 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700/60 text-left text-slate-400">
              <th className="px-4 py-3 font-medium whitespace-nowrap">Employee</th>
              <th className="px-4 py-3 font-medium whitespace-nowrap">Check In</th>
              <th className="px-4 py-3 font-medium whitespace-nowrap">Check Out</th>
              <th className="px-4 py-3 font-medium whitespace-nowrap">Worked Hours</th>
              <th className="px-4 py-3 font-medium whitespace-nowrap">Status</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-slate-500">
                  Loading attendance records...
                </td>
              </tr>
            )}

            {isError && !isLoading && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-rose-400">
                  Failed to load attendance records.
                </td>
              </tr>
            )}

            {!isLoading && !isError && records.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-slate-500">
                  No attendance records match the current filters.
                </td>
              </tr>
            )}

            {!isLoading &&
              !isError &&
              records.map((row) => {
                const isMissingPunch = !row.check_in || !row.check_out;
                return (
                  <tr
                    key={row.id}
                    className={`border-b border-slate-700/40 last:border-b-0 hover:bg-slate-700/30 transition-colors ${
                      isMissingPunch ? 'bg-rose-500/5' : ''
                    }`}
                  >
                    <td className="px-4 py-3 text-slate-200 whitespace-nowrap">
                      {row.employee_name || row.employee_id}
                    </td>
                    <td className="px-4 py-3 text-slate-300 whitespace-nowrap">{formatTime(row.check_in)}</td>
                    <td className="px-4 py-3 text-slate-300 whitespace-nowrap">{formatTime(row.check_out)}</td>
                    <td className="px-4 py-3 text-amber-400 font-semibold whitespace-nowrap">
                      {row.worked_hours != null ? Number(row.worked_hours).toFixed(2) : '0.00'}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <StatusBadge status={isMissingPunch ? 'MISSING_CHECKOUT' : row.status} />
                    </td>
                  </tr>
                );
              })}
          </tbody>
        </table>
      </div>

      <p className="mt-4 text-xs text-slate-500">
        Useful note: list view should help users review raw check-in / check-out data and identify missing punches quickly.
      </p>

      {isNewModalOpen && (
        <NewAttendanceModal
          onClose={() => setIsNewModalOpen(false)}
          onSubmit={(payload) =>
            createAttendance.mutate(payload, { onSuccess: () => setIsNewModalOpen(false) })
          }
          isSubmitting={createAttendance.isPending}
        />
      )}
    </div>
  );
}

function NewAttendanceModal({ onClose, onSubmit, isSubmitting }) {
  const [form, setForm] = useState({
    employee_id: '',
    work_date: new Date().toISOString().slice(0, 10),
    check_in: '',
    check_out: '',
  });

  const handleChange = (field) => (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(form);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4">
      <div className="w-full max-w-md rounded-lg border border-slate-700/60 bg-slate-800 p-6">
        <h2 className="text-lg font-semibold text-slate-100 mb-4">New attendance entry</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Employee ID</label>
            <input
              type="text"
              required
              value={form.employee_id}
              onChange={handleChange('employee_id')}
              className="w-full px-3 py-2 rounded-md bg-slate-900 border border-slate-700/60 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Work date</label>
            <input
              type="date"
              required
              value={form.work_date}
              onChange={handleChange('work_date')}
              className="w-full px-3 py-2 rounded-md bg-slate-900 border border-slate-700/60 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Check in</label>
              <input
                type="time"
                value={form.check_in}
                onChange={handleChange('check_in')}
                className="w-full px-3 py-2 rounded-md bg-slate-900 border border-slate-700/60 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Check out</label>
              <input
                type="time"
                value={form.check_out}
                onChange={handleChange('check_out')}
                className="w-full px-3 py-2 rounded-md bg-slate-900 border border-slate-700/60 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
              />
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-md text-sm font-medium text-slate-300 hover:bg-slate-700/40 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 rounded-md bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-medium transition-colors"
            >
              {isSubmitting ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}