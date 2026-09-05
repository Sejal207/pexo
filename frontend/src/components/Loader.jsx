export const Spinner = () => <span className="inline-block h-5 w-5 animate-spin rounded-full border-2 border-slate-500 border-t-indigo-400" aria-label="Loading" />;
export const PageLoader = () => <div className="flex min-h-[40vh] items-center justify-center"><Spinner /></div>;
export const TableSkeleton = ({ columns = 5, rows = 5 }) => <>{Array.from({ length: rows }, (_, row) => <tr key={row}>{Array.from({ length: columns }, (_, col) => <td key={col} className="p-4"><div className="h-4 animate-pulse rounded bg-slate-700/60" /></td>)}</tr>)}</>;
