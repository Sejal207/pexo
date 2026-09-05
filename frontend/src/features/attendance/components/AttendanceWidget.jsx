import { useEffect, useRef, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Power, Loader2 } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '../../../app/hooks';
import { httpClient } from '../../../api/httpClient';
import { checkIn, checkOut, syncWidgetStatus, togglePopup, closePopup } from '../attendanceWidgetSlice';

const formatClock = (isoString) => {
  if (!isoString) return '';
  try {
    return new Date(isoString).toLocaleTimeString('en-US', {
      hour: 'numeric', minute: '2-digit',
    });
  } catch (_) {
    return String(isoString);
  }
};

const formatDuration = (fromIso) => {
  if (!fromIso) return '0h00';
  const ms = Date.now() - new Date(fromIso).getTime();
  const totalMinutes = Math.max(0, Math.floor(ms / 60000));
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  return `${hours}h${minutes.toString().padStart(2, '0')}`;
};

export const AttendanceWidget = () => {
  const dispatch = useAppDispatch();
  const queryClient = useQueryClient();
  const { isOpen, isCheckedIn, checkInAt, attendanceId } = useAppSelector((state) => state.attendanceWidget);
  const userEmail = useAppSelector((state) => state.auth.user?.email);
  const userName = userEmail ? userEmail.split('@')[0].replace(/[._]/g, ' ') : 'there';

  const [elapsed, setElapsed] = useState(checkInAt ? formatDuration(checkInAt) : '0h00');
  const [errorMessage, setErrorMessage] = useState('');
  const panelRef = useRef(null);

  // Sync with backend widget status on load
  const { data: statusData } = useQuery({
    queryKey: ['attendance', 'widget-status'],
    queryFn: async () => {
      try {
        const { data } = await httpClient.get('/attendance/widget-status');
        return data;
      } catch (_) {
        return { open: false, since: null, elapsed_seconds: null, attendance_id: null };
      }
    },
    refetchInterval: 30000,
  });

  useEffect(() => {
    if (statusData) {
      dispatch(syncWidgetStatus(statusData));
    }
  }, [statusData, dispatch]);

  useEffect(() => {
    if (!isCheckedIn || !checkInAt) return undefined;
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

  // Real backend check-in endpoint
  const checkInMutation = useMutation({
    mutationFn: async () => {
      const { data } = await httpClient.post('/attendance/check-in');
      return data;
    },
    onSuccess: (data) => {
      setErrorMessage('');
      dispatch(checkIn({ checkInAt: data.check_in, attendanceId: data.id }));
      queryClient.invalidateQueries({ queryKey: ['attendance'] });
    },
    onError: (err) => {
      const detail = err?.response?.data?.detail;
      setErrorMessage(typeof detail === 'string' ? detail : 'Unable to check in. Please try again.');
    },
  });

  // Real backend check-out endpoint with schedule overtime computation
  const checkOutMutation = useMutation({
    mutationFn: async () => {
      let targetId = attendanceId;
      if (!targetId) {
        const { data: st } = await httpClient.get('/attendance/widget-status');
        targetId = st?.attendance_id;
      }
      if (!targetId) {
        throw new Error('No active attendance session found to check out');
      }
      const { data } = await httpClient.post(`/attendance/${targetId}/check-out`);
      return data;
    },
    onSuccess: () => {
      setErrorMessage('');
      dispatch(checkOut());
      queryClient.invalidateQueries({ queryKey: ['attendance'] });
    },
    onError: (err) => {
      const detail = err?.response?.data?.detail;
      setErrorMessage(typeof detail === 'string' ? detail : 'Unable to check out. Please try again.');
    },
  });

  const isPending = checkInMutation.isPending || checkOutMutation.isPending;

  const handleCheckIn = () => {
    setErrorMessage('');
    checkInMutation.mutate();
  };

  const handleCheckOut = () => {
    setErrorMessage('');
    checkOutMutation.mutate();
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
                  <span className="text-slate-300">Session Elapsed</span>
                  <span className="font-semibold text-white">{elapsed}</span>
                </div>
              </>
            ) : (
              <p className="mt-4 border-b border-slate-700/50 pb-4 text-sm text-slate-500">No active session today.</p>
            )}

            {errorMessage && (
              <p className="mt-2 text-xs text-rose-400 leading-tight">{errorMessage}</p>
            )}

            <button
              type="button"
              disabled={isPending}
              onClick={isCheckedIn ? handleCheckOut : handleCheckIn}
              className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-indigo-500 disabled:opacity-50"
            >
              {isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              {isCheckedIn ? 'Check Out' : 'Check In'}
            </button>
          </div>

          <p className="border-t border-slate-700/60 px-5 py-3 text-xs text-slate-500">
            Punches are recorded to the attendance service and verified against your working schedule.
          </p>
        </div>
      )}
    </div>
  );
};
