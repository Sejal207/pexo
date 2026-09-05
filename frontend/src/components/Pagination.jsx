export const Pagination = ({ page = 1, pageSize = 10, total = 0, onPageChange }) => {
  const pages = Math.max(1, Math.ceil(total / pageSize));
  const start = total ? (page - 1) * pageSize + 1 : 0;
  const end = Math.min(page * pageSize, total);
  return <div className="flex flex-wrap items-center justify-between gap-3 pt-4 text-sm text-slate-400">
    <span>Showing {start}–{end} of {total}</span>
    <div className="flex gap-2"><button type="button" disabled={page <= 1} onClick={() => onPageChange(page - 1)} className="rounded border border-slate-700 px-3 py-1.5 disabled:opacity-40">Previous</button><span className="px-2 py-1.5">{page} / {pages}</span><button type="button" disabled={page >= pages} onClick={() => onPageChange(page + 1)} className="rounded border border-slate-700 px-3 py-1.5 disabled:opacity-40">Next</button></div>
  </div>;
};
export default Pagination;
