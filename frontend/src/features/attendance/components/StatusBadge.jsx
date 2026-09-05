const STATUS_STYLES = {
  PRESENT: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  LATE: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  HALF_DAY: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
  ON_LEAVE: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
  ABSENT: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
  MISSING_CHECKOUT: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
};

const STATUS_LABELS = {
  PRESENT: 'Present',
  LATE: 'Late',
  HALF_DAY: 'Half day',
  ON_LEAVE: 'On leave',
  ABSENT: 'Absent',
  MISSING_CHECKOUT: 'Missing punch',
};

export default function StatusBadge({ status }) {
  const style = STATUS_STYLES[status] || 'bg-slate-700/40 text-slate-300 border-slate-600/40';
  const label = STATUS_LABELS[status] || status || '—';

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${style}`}>
      {label}
    </span>
  );
}