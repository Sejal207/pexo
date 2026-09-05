import { useParams } from 'react-router-dom';
import { useAttendanceDetailQuery } from '../features/attendance/useAttendanceQueries';

const Field = ({ label, value }) => <div><p className="mb-2 text-sm text-slate-400">{label}</p><div className="rounded-lg border border-slate-700/60 bg-slate-800 px-3 py-2 text-white">{value}</div></div>;

export const AttendanceDetailPage = () => {
  const { id } = useParams();
  const { data: attendance, isLoading, isError } = useAttendanceDetailQuery(id);
  if (isLoading) return <div className="p-8 max-w-7xl mx-auto text-slate-400">Loading attendance record...</div>;
  if (isError || !attendance) return <div className="p-8 max-w-7xl mx-auto text-rose-400">Unable to load attendance record.</div>;

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Attendance / {attendance.employeeName} / {attendance.date}</h1>
        <p className="text-slate-400 mt-1">Form view of one attendance record</p>
      </div>

      <button type="button" className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 hover:bg-slate-800">Edit</button>

      <div className="grid grid-cols-2 gap-x-8 gap-y-5">
        <div className="space-y-5">
          <Field label="Employee" value={attendance.employeeName} />
          <Field label="Check In" value={attendance.checkIn} />
          <Field label="Check Out" value={attendance.checkOut} />
          <Field label="Worked Hours" value={attendance.workedHours} />
        </div>
        <div className="space-y-5">
          <Field label="Department" value={attendance.department} />
          <Field label="Manager" value={attendance.manager} />
          <Field label="Status" value={attendance.status} />
          <Field label="Overtime" value={`${attendance.overtimeHours.toFixed(2)} hrs`} />
        </div>
      </div>

      <section className="rounded-lg border border-slate-700/60 bg-slate-800 p-5">
        <h2 className="text-sm font-semibold text-white">Notes</h2>
        <p className="mt-3 text-slate-400">{attendance.notes}</p>
      </section>

      <p className="pt-2 text-xs text-slate-500">Useful note: worked hours and overtime should be easy to read because they may later influence payroll or reporting.</p>
    </div>
  );
};
