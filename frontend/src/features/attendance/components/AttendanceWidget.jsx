import { useEffect, useRef, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Power } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '../../../app/hooks';
import { httpClient } from '../../../api/httpClient';
import { checkIn, checkOut, togglePopup, closePopup } from '../attendanceWidgetSlice';

const formatClock = (isoString) => new Date(isoString).toLocaleTimeString('en-US', {
  hour: 'numeric', minute: '2-digit',
});

const formatDuration = (fromIso) => {
  const ms = Date.now() - new Date(fromIso).getTime();
  const totalMinutes = Math.max(0, Math.floor(ms / 60000));
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  return `${hours}h${minutes.toString().padStart(2, '0')}`;
};

export const AttendanceWidget = () => {
  const dispatch = useAppDispatch();
  const { isOpen, isCheckedIn, checkInAt } = useAppSelector((state) => state.attendanceWidget);
  const userEmail = useAppSelector((state) => state.auth.user?.email);
  const userName = userEmail ? userEmail.split('@')[0].replace(/[._]/g, ' ') : 'there';

  const [elapsed, setElapsed] = useState(checkInAt ? formatDuration(checkInAt) : '0h00');
  const panelRef = useRef(null);

  useEffect(() => {
    if (!isCheckedIn) return undefined;
    setElapsed(formatDuration(checkInAt));
    const interval = setInterval(() => setElapsed(formatDuration(checkInAt)), 1000);
    return () => clearInterval(interval);
  }, [isCheckedIn, checkInAt]);

  useEffect(() => {
    if (!isOpen) return undefined;
    const handleClickOutside = (event) => {
      if (panelRef.current && !panelRef.current.contains(event.target)) {
        dispatch(closePopup());
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, dispatch]);

  // TODO: swap for a real check-in/check-out endpoint once the attendance
  // service supports partial updates — for now this is fire-and-forget.
  const recordAttendance = useMutation({
    mutationFn: (payload) => httpClient.post('/attendance/', payload),
  });

  const handleCheckIn = () => {
    const now = new Date().toISOString();
    dispatch(checkIn(now));
    recordAttendance.mutate({
      date: now.slice(0, 10),
      check_in: now,
      status: 'PRESENT',
    });
  };

  const handleCheckOut = () => {
    const now = new Date().toISOString();
    recordAttendance.mutate({
      date: checkInAt.slice(0, 10),
      check_in: checkInAt,
      check_out: now,
      status: 'PRESENT',
    });
    dispatch(checkOut());
  };

  return (
    <div className="relative" ref={panelRef}>
      <button
        type="button"
        onClick={() => dispatch(togglePopup())}
        aria-label="Attendance"
        className={`flex h-8 w-8 items-center justify-center rounded-full border transition-colors ${
          isCheckedIn ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-400' : 'border-rose-500/40 bg-rose-500/10 text-rose-400'
        }`}
      >
        <Power className="h-4 w-4" />
      </button>

      {isOpen && (
        <div className="absolute right-0 top-11 z-50 w-80 rounded-2xl border border-slate-700/60 bg-slate-800 shadow-2xl">
          <div className="flex items-center justify-between rounded-t-2xl border-b border-slate-700/60 bg-slate-900/40 px-5 py-3">
            <span className="text-sm font-semibold text-white">Attendance Widget</span>
            <span className={`h-2.5 w-2.5 rounded-full ${isCheckedIn ? 'bg-emerald-400' : 'bg-slate-500'}`} />
          </div>

          <div className="px-5 py-4">
            <p className="text-sm text-slate-400">Welcome back</p>
            <p className="text-xl font-bold text-white capitalize">{userName}!</p>

            {isCheckedIn ? (
              <>
                <div className="mt-4 flex items-center justify-between border-b border-slate-700/50 pb-3 text-sm">
                  <span className="text-slate-300">{formatClock(checkInAt)} — Now</span>
                  <span className="font-semibold text-white">{elapsed}</span>
                </div>
                <div className="flex items-center justify-between py-3 text-sm">
                  <span className="text-slate-300">Today</span>
                  <span className="font-semibold text-white">{elapsed}</span>
                </div>
              </>
            ) : (
              <p className="mt-4 border-b border-slate-700/50 pb-4 text-sm text-slate-500">No active session today.</p>
            )}

            <button
              type="button"
              onClick={isCheckedIn ? handleCheckOut : handleCheckIn}
              className="mt-4 w-full rounded-lg bg-indigo-600 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-indigo-500"
            >
              {isCheckedIn ? 'Check Out' : 'Check In'}
            </button>
          </div>

          <p className="border-t border-slate-700/60 px-5 py-3 text-xs text-slate-500">
            Employees can mark attendance from the quick widget and review records from the Attendance module.
          </p>
        </div>
      )}
    </div>
  );
};
