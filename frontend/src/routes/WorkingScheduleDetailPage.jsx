import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { httpClient } from '../api/httpClient';
import { BackButton } from '../components/BackButton';
import { PageLoader } from '../components/Loader';
import { useToast } from '../components/ToastContext';

const DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];

const initialLines = DAYS.map((day) => ({
  day,
  start_time: day === 'SAT' || day === 'SUN' ? '' : '09:00',
  end_time: day === 'SAT' || day === 'SUN' ? '' : '17:00',
  break_minutes: 60,
}));

export const WorkingScheduleDetailPage = () => {
  const { id } = useParams();
  const isNew = id === 'new';
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  const { data, isLoading } = useQuery({
    queryKey: ['schedules', id],
    queryFn: async () => (await httpClient.get(`/schedules/${id}`)).data,
    enabled: !isNew,
  });

  const [draft, setDraft] = useState(null);

  const value = draft || (data ? {
    name: data.name || '',
    schedule_type: data.schedule_type || 'FULL_TIME',
    lines: DAYS.map((day) => {
      const found = (data.lines || []).find((l) => l.day === day);
      return found ? {
        day,
        start_time: (found.start_time || '').slice(0, 5),
        end_time: (found.end_time || '').slice(0, 5),
        break_minutes: Number(found.break_minutes ?? 0),
      } : {
        day,
        start_time: '',
        end_time: '',
        break_minutes: 0,
      };
    }),
  } : {
    name: '',
    schedule_type: 'FULL_TIME',
    lines: initialLines,
  });

  const set = (next) => setDraft(next);

  const weekly = value.lines.reduce((sum, line) => {
    if (!line.start_time || !line.end_time) return sum;
    const [sh, sm] = line.start_time.split(':').map(Number);
    const [eh, em] = line.end_time.split(':').map(Number);
    if (isNaN(sh) || isNaN(sm) || isNaN(eh) || isNaN(em)) return sum;
    const netMinutes = (eh * 60 + em) - (sh * 60 + sm) - Number(line.break_minutes || 0);
    return sum + Math.max(0, netMinutes / 60);
  }, 0);

  const mutation = useMutation({
    mutationFn: async () => {
      const activeLines = value.lines
        .filter((l) => Boolean(l.start_time && l.end_time))
        .map((l) => ({
          day: l.day,
          start_time: l.start_time.length === 5 ? `${l.start_time}:00` : l.start_time,
          end_time: l.end_time.length === 5 ? `${l.end_time}:00` : l.end_time,
          break_minutes: Number(l.break_minutes || 0),
        }));

      const payload = {
        name: value.name.trim(),
        schedule_type: value.schedule_type,
        lines: activeLines,
      };

      return isNew
        ? (await httpClient.post('/schedules/', payload)).data
        : (await httpClient.patch(`/schedules/${id}`, payload)).data;
    },
    onSuccess: (saved) => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] });
      showToast('Working schedule saved successfully.');
      navigate(`/schedules/${saved.id || id}`);
    },
    onError: (err) => {
      const detail = err?.response?.data?.detail;
      showToast(typeof detail === 'string' ? detail : 'Unable to save working schedule.', 'error');
    },
  });

  if (!isNew && isLoading) return <PageLoader />;

  return (
    <div className="mx-auto max-w-5xl p-4 sm:p-8 space-y-6">
      <BackButton to="/schedules" />
      <div>
        <h1 className="text-3xl font-extrabold text-white">
          {isNew ? 'New' : 'Edit'} Working Schedule
        </h1>
        <p className="mt-1 text-slate-400">
          Define weekly shift patterns, standard hours, and break deductions.
        </p>
      </div>

      <div className="mt-6 space-y-6 rounded-xl border border-slate-700/60 bg-slate-800 p-6">
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-xs font-semibold uppercase text-slate-400 mb-1.5">Schedule Name *</label>
            <input
              value={value.name}
              onChange={(e) => set({ ...value, name: e.target.value })}
              placeholder="E.g., Standard 40h (Mon-Fri 9-6)"
              className="w-full rounded-lg border border-slate-700 bg-slate-900 p-3 text-sm text-white focus:border-indigo-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase text-slate-400 mb-1.5">Schedule Type</label>
            <select
              value={value.schedule_type}
              onChange={(e) => set({ ...value, schedule_type: e.target.value })}
              className="w-full rounded-lg border border-slate-700 bg-slate-900 p-3 text-sm text-white focus:border-indigo-500 focus:outline-none"
            >
              <option value="FULL_TIME">FULL_TIME</option>
              <option value="PART_TIME">PART_TIME</option>
              <option value="FLEXIBLE">FLEXIBLE</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto rounded-lg border border-slate-700/50">
          <table className="w-full text-sm">
            <thead className="bg-slate-900/60 text-left text-slate-400 border-b border-slate-700/50">
              <tr>
                <th className="p-3">Day</th>
                <th className="p-3">Start Time</th>
                <th className="p-3">End Time</th>
                <th className="p-3">Break (minutes)</th>
              </tr>
            </thead>
            <tbody>
              {value.lines.map((line, index) => (
                <tr key={line.day} className="border-t border-slate-700/40 hover:bg-slate-700/20">
                  <td className="p-3 font-semibold text-white">{line.day}</td>
                  <td className="p-3">
                    <input
                      type="time"
                      value={line.start_time || ''}
                      onChange={(e) => {
                        const lines = [...value.lines];
                        lines[index] = { ...line, start_time: e.target.value };
                        set({ ...value, lines });
                      }}
                      className="w-full rounded-lg border border-slate-700 bg-slate-900 p-2 text-sm text-white focus:border-indigo-500 focus:outline-none"
                    />
                  </td>
                  <td className="p-3">
                    <input
                      type="time"
                      value={line.end_time || ''}
                      onChange={(e) => {
                        const lines = [...value.lines];
                        lines[index] = { ...line, end_time: e.target.value };
                        set({ ...value, lines });
                      }}
                      className="w-full rounded-lg border border-slate-700 bg-slate-900 p-2 text-sm text-white focus:border-indigo-500 focus:outline-none"
                    />
                  </td>
                  <td className="p-3">
                    <input
                      type="number"
                      min="0"
                      step="5"
                      value={line.break_minutes ?? 0}
                      onChange={(e) => {
                        const lines = [...value.lines];
                        lines[index] = { ...line, break_minutes: e.target.value };
                        set({ ...value, lines });
                      }}
                      className="w-full rounded-lg border border-slate-700 bg-slate-900 p-2 text-sm text-white focus:border-indigo-500 focus:outline-none"
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2">
          <p className="text-sm font-medium text-amber-400">
            Total Weekly Hours: <span className="font-bold text-amber-300">{weekly.toFixed(2)} hrs</span>
          </p>
          <button
            type="button"
            disabled={!value.name.trim() || mutation.isPending}
            onClick={() => mutation.mutate()}
            className="rounded-lg bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-50 transition-colors"
          >
            {mutation.isPending ? 'Saving...' : 'Save Schedule'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default WorkingScheduleDetailPage;
