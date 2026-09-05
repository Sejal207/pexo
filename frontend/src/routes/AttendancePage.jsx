import { Plus, Search } from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../app/hooks';
import { setSearchTerm, toggleTodayOnly } from '../features/attendance/attendanceSlice';
import { useAttendanceQuery } from '../features/attendance/useAttendanceQueries';

const todayIso = () => new Date().toISOString().slice(0, 10);

export const AttendancePage = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const employeeId = searchParams.get('employeeId');
  const { searchTerm, todayOnly } = useAppSelector((state) => state.attendance);
  const { data: records = [], isLoading, isError } = useAttendanceQuery(employeeId);
  const filteredEmployeeName = employeeId ? records[0]?.employeeName : null;

  const displayedRecords = records
    .filter((record) => !todayOnly || record.date === todayIso())
    .filter((record) => record.employeeName.toLowerCase().includes(searchTerm.toLowerCase()));

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div><h1 className="text-3xl font-extrabold text-white tracking-tight">Attendance</h1><p className="text-slate-400 mt-1">List view of employee attendance records</p></div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <button type="button" className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-indigo-500"><Plus className="w-4 h-4" />New</button>
        <label className="relative block">
          <Search className="absolute left-3 top-1/2 w-4 h-4 -translate-y-1/2 text-slate-500" />
          <input type="search" value={searchTerm} onChange={(event) => dispatch(setSearchTerm(event.target.value))} placeholder="Search attendance..." className="w-full sm:w-72 rounded-lg border border-slate-700/60 bg-slate-800 py-2.5 pl-10 pr-4 text-sm text-white placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none" />
        </label>
        <button
          type="button"
          onClick={() => dispatch(toggleTodayOnly())}
          className={`rounded-lg border px-4 py-2.5 text-sm font-medium transition-colors ${todayOnly ? 'border-indigo-500 bg-indigo-600/20 text-indigo-300' : 'border-slate-700/60 bg-slate-800 text-slate-300 hover:text-white'}`}
        >
          Today
        </button>
        {employeeId && (
          <span className="inline-flex items-center gap-2 rounded-lg border border-indigo-500/40 bg-indigo-600/20 px-4 py-2.5 text-sm font-medium text-indigo-300">
            Employee: {filteredEmployeeName ?? 'this employee'}
            <button type="button" onClick={() => navigate('/attendance')} className="text-indigo-300 hover:text-white">×</button>
          </span>
        )}
      </div>

      {isLoading && <p className="text-slate-400">Loading attendance records...</p>}
      {isError && <p className="text-rose-400">Unable to load attendance records.</p>}

      {!isLoading && !isError && (
        <div className="overflow-hidden rounded-lg border border-slate-700/60 bg-slate-800">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-700/60 text-slate-400">
                <tr>
                  <th className="p-4 font-medium">Employee</th>
                  <th className="p-4 font-medium">Check In</th>
                  <th className="p-4 font-medium">Check Out</th>
                  <th className="p-4 font-medium">Worked Hours</th>
                  <th className="p-4 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {displayedRecords.map((record) => (
                  <tr key={record.id} onClick={() => navigate(`/attendance/${record.id}`)} className="cursor-pointer border-b border-slate-700/40 last:border-0 hover:border-slate-600">
                    <td className="p-4 font-medium text-white">{record.employeeName}</td>
                    <td className="p-4 text-slate-400">{record.checkIn ?? '—'}</td>
                    <td className="p-4 text-slate-400">{record.checkOut ?? '—'}</td>
                    <td className="p-4 text-slate-400">{record.workedHours.toFixed(2)}</td>
                    <td className={`p-4 font-medium ${record.status === 'Present' ? 'text-emerald-400' : 'text-rose-400'}`}>{record.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {!isLoading && !isError && displayedRecords.length === 0 && <p className="text-sm text-slate-500">No attendance records found.</p>}

      <p className="pt-2 text-xs text-slate-500">Useful note: list view should help users review raw check-in / check-out data and identify missing punches quickly.</p>
    </div>
  );
};
