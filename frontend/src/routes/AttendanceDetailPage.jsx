import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Edit3, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { useAttendanceDetailQuery, useCorrectAttendance } from '../features/attendance/useAttendanceQueries';

const Field = ({ label, value }) => (
  <div>
    <p className="mb-2 text-sm text-slate-400">{label}</p>
    <div className="rounded-lg border border-slate-700/60 bg-slate-800 px-3 py-2 text-white">{value ?? '—'}</div>
  </div>
);

const toDateTimeLocal = (isoString) => {
  if (!isoString) return '';
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return '';
    const offsetMs = d.getTimezoneOffset() * 60000;
    return new Date(d.getTime() - offsetMs).toISOString().slice(0, 16);
  } catch (_) {
    return '';
  }
};

export const AttendanceDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: attendance, isLoading, isError, refetch } = useAttendanceDetailQuery(id);
  const correctMutation = useCorrectAttendance(id);

  const [isEditing, setIsEditing] = useState(false);
  const [checkInTime, setCheckInTime] = useState('');
  const [checkOutTime, setCheckOutTime] = useState('');
  const [reason, setReason] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleOpenEdit = () => {
    setCheckInTime(toDateTimeLocal(attendance?.rawCheckIn));
    setCheckOutTime(toDateTimeLocal(attendance?.rawCheckOut));
    setReason(attendance?.correctionReason || '');
    setErrorMsg('');
    setIsEditing(true);
  };

  const handleSaveCorrection = async () => {
    if (!reason.trim()) {
      setErrorMsg('A correction reason is required by HR compliance.');
      return;
    }
    setErrorMsg('');
    try {
      await correctMutation.mutateAsync({
        check_in: checkInTime ? new Date(checkInTime).toISOString() : null,
        check_out: checkOutTime ? new Date(checkOutTime).toISOString() : null,
        reason: reason.trim(),
      });
      await refetch();
      setIsEditing(false);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setErrorMsg(typeof detail === 'string' ? detail : 'Unable to update attendance.');
    }
  };

  if (isLoading) return <div className="p-8 max-w-7xl mx-auto text-slate-400">Loading attendance record...</div>;
  if (isError || !attendance) return <div className="p-8 max-w-7xl mx-auto text-rose-400">Unable to load attendance record.</div>;

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <button
            type="button"
            onClick={() => navigate('/attendance')}
            className="mb-3 inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Attendance
          </button>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Attendance / {attendance.employeeName} / {attendance.date}
          </h1>
          <p className="text-slate-400 mt-1">Form view of verified attendance punch</p>
        </div>
        <button
          type="button"
          onClick={handleOpenEdit}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-medium text-slate-300 hover:bg-slate-700/60 hover:text-white transition-colors"
        >
          <Edit3 className="w-4 h-4" /> Edit Punch
        </button>
      </div>

      {attendance.isManualCorrection && (
        <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-4 text-sm text-amber-300">
          This record was manually corrected: <span className="font-semibold">{attendance.correctionReason || 'Manual adjustment'}</span>
        </div>
      )}

      <div className="grid grid-cols-2 gap-x-8 gap-y-5">
        <div className="space-y-5">
          <Field label="Employee" value={attendance.employeeName} />
          <Field label="Check In" value={attendance.checkIn} />
          <Field label="Check Out" value={attendance.checkOut} />
          <Field label="Worked Hours" value={`${attendance.workedHours.toFixed(2)} hrs`} />
        </div>
        <div className="space-y-5">
          <Field label="Department" value={attendance.department} />
          <Field label="Manager" value={attendance.manager} />
          <Field label="Status" value={attendance.status} />
          <Field label="Overtime" value={`${attendance.overtimeHours.toFixed(2)} hrs`} />
        </div>
      </div>

      <section className="rounded-lg border border-slate-700/60 bg-slate-800 p-5">
        <h2 className="text-sm font-semibold text-white">Audit & Notes</h2>
        <p className="mt-3 text-slate-400">{attendance.notes}</p>
      </section>

      {/* Manual Correction Modal */}
      {isEditing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg rounded-2xl border border-slate-700 bg-slate-800 p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-700 pb-3">
              <h3 className="text-lg font-bold text-white">Manual Punch Correction</h3>
              <button
                type="button"
                onClick={() => setIsEditing(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {errorMsg && (
              <div className="flex items-center gap-2 rounded-lg bg-rose-500/10 border border-rose-500/40 p-3 text-xs text-rose-300">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">Check In Time</label>
                <input
                  type="datetime-local"
                  value={checkInTime}
                  onChange={(e) => setCheckInTime(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-900 p-2.5 text-sm text-white"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">Check Out Time</label>
                <input
                  type="datetime-local"
                  value={checkOutTime}
                  onChange={(e) => setCheckOutTime(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-900 p-2.5 text-sm text-white"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">Correction Reason *</label>
                <textarea
                  rows={3}
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="E.g., Employee forgot to punch out due to offsite client meeting"
                  className="w-full rounded-lg border border-slate-700 bg-slate-900 p-2.5 text-sm text-white placeholder:text-slate-500"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-2 border-t border-slate-700">
              <button
                type="button"
                disabled={correctMutation.isPending}
                onClick={() => setIsEditing(false)}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={correctMutation.isPending}
                onClick={handleSaveCorrection}
                className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
              >
                {correctMutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
                Save Correction
              </button>
            </div>
          </div>
        </div>
      )}

      <p className="pt-2 text-xs text-slate-500">
        Worked hours and overtime are recalculated server-side upon correction against the applicable working schedule.
      </p>
    </div>
  );
};
