import { Plus, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../app/hooks';
import { setSearchTerm } from '../features/timeoff/allocationsSlice';
import { useAllocationsQuery } from '../features/timeoff/useAllocationQueries';

const STATUS_STYLES = {
  Approved: 'text-emerald-400',
  'To Approve': 'text-amber-400',
  Refused: 'text-rose-400',
};

export const AllocationsPage = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const searchTerm = useAppSelector((state) => state.allocations.searchTerm);
  const { data: allocations = [], isLoading, isError } = useAllocationsQuery();

  const displayedAllocations = allocations.filter((allocation) => (
    allocation.employeeName.toLowerCase().includes(searchTerm.toLowerCase())
  ));

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div><h1 className="text-3xl font-extrabold text-white tracking-tight">Allocations</h1><p className="text-slate-400 mt-1">List view opened from Time Off ▾ → Allocations</p></div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <button type="button" className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-indigo-500"><Plus className="w-4 h-4" />New</button>
        <label className="relative block">
          <Search className="absolute left-3 top-1/2 w-4 h-4 -translate-y-1/2 text-slate-500" />
          <input type="search" value={searchTerm} onChange={(event) => dispatch(setSearchTerm(event.target.value))} placeholder="Search allocations..." className="w-full sm:w-72 rounded-lg border border-slate-700/60 bg-slate-800 py-2.5 pl-10 pr-4 text-sm text-white placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none" />
        </label>
      </div>

      {isLoading && <p className="text-slate-400">Loading allocations...</p>}
      {isError && <p className="text-rose-400">Unable to load allocations.</p>}

      {!isLoading && !isError && (
        <div className="overflow-hidden rounded-lg border border-slate-700/60 bg-slate-800">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-700/60 text-slate-400">
                <tr>
                  <th className="p-4 font-medium">Employee</th>
                  <th className="p-4 font-medium">Type</th>
                  <th className="p-4 font-medium">Allocated</th>
                  <th className="p-4 font-medium">Taken</th>
                  <th className="p-4 font-medium">Remaining</th>
                  <th className="p-4 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {displayedAllocations.map((allocation) => (
                  <tr key={allocation.id} onClick={() => navigate(`/time-off/allocations/${allocation.id}`)} className="cursor-pointer border-b border-slate-700/40 last:border-0 hover:border-slate-600">
                    <td className="p-4 font-medium text-white">{allocation.employeeName}</td>
                    <td className="p-4 text-slate-400">{allocation.type}</td>
                    <td className="p-4 text-slate-400">{allocation.allocatedDays} days</td>
                    <td className="p-4 text-slate-400">{allocation.takenDays} days</td>
                    <td className="p-4 text-slate-400">{allocation.remainingDays} days</td>
                    <td className={`p-4 font-medium ${STATUS_STYLES[allocation.status] ?? 'text-slate-400'}`}>{allocation.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {!isLoading && !isError && displayedAllocations.length === 0 && <p className="text-sm text-slate-500">No allocations found.</p>}

      <p className="pt-2 text-xs text-slate-500">Useful note: the list should expose the balance math at a glance — Allocated, Taken and Remaining.</p>
    </div>
  );
};
