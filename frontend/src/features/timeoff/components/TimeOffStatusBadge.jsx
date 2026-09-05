export default function TimeOffStatusBadge({ status }) {
  const getStatusStyles = () => {
    switch (status) {
      case 'APPROVED':
        return {
          bg: 'bg-emerald-500/10',
          text: 'text-emerald-400',
          border: 'border-emerald-500/40',
        };
      case 'REFUSED':
        return {
          bg: 'bg-rose-500/10',
          text: 'text-rose-400',
          border: 'border-rose-500/40',
        };
      case 'SUBMITTED':
        return {
          bg: 'bg-amber-500/10',
          text: 'text-amber-400',
          border: 'border-amber-500/40',
        };
      case 'CANCELLED':
        return {
          bg: 'bg-slate-500/10',
          text: 'text-slate-400',
          border: 'border-slate-500/40',
        };
      default:
        return {
          bg: 'bg-slate-500/10',
          text: 'text-slate-400',
          border: 'border-slate-500/40',
        };
    }
  };

  const styles = getStatusStyles();
  const displayText = status === 'SUBMITTED' ? 'Pending' : status;

  return (
    <span className={`inline-flex px-2.5 py-1 rounded-md text-xs font-medium border ${styles.bg} ${styles.text} ${styles.border}`}>
      {displayText}
    </span>
  );
}
