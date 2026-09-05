import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { setSearchText, toggleMyTeamOnly } from '../features/timeoff/timeOffSlice';
import {
  useTimeOffRequestsQuery,
  useApproveRequestMutation,
  useRefuseRequestMutation,
} from '../features/timeoff/useTimeOffQueries';
import TimeOffStatusBadge from '../features/timeoff/components/TimeOffStatusBadge';

export const TimeOffRequestsPage = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { searchText, myTeamOnly } = useSelector((state) => state.timeOff);

  const { data, isLoading, isError } = useTimeOffRequestsQuery({
    search: searchText,
    myTeamOnly,
  });

  const requests = data?.results ?? data ?? [];

  const approveMutation = useApproveRequestMutation();
  const refuseMutation = useRefuseRequestMutation();

  const handleApprove = (e, id) => {
    e.stopPropagation();
    approveMutation.mutate(id);
  };

  const handleRefuse = (e, id) => {
    e.stopPropagation();
    refuseMutation.mutate(id);
  };

  return (
    <div className="w-full max-w-screen-xl mx-auto px-4 sm:px-6 py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-100">Time Off Requests</h1>
        <p className="text-sm text-slate-400 mt-1">List view opened from Time Off ▾ Requests</p>
      </div>

      <div className="flex flex-wrap items-center gap-3 mb-4">
        <button
          type="button"
          onClick={() => navigate('/time-off/requests/new')}
          className="px-4 py-2 rounded-md bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition-colors"
        >
          New
        </button>

        <input
          type="text"
          value={searchText}
          onChange={(e) => dispatch(setSearchText(e.target.value))}
          placeholder="Search requests..."
          className="flex-1 min-w-[200px] px-3 py-2 rounded-md bg-slate-800 border border-slate-700/60 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60"
        />

        <button
          type="button"
          onClick={() => dispatch(toggleMyTeamOnly())}
          className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
            myTeamOnly
              ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/40'
              : 'bg-slate-800 text-slate-300 border-slate-700/60 hover:border-slate-600'
          }`}
        >
          My Team
        </button>
      </div>

      <div className="rounded-lg border border-slate-700/60 bg-slate-800 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700/60 text-left text-slate-400">
              <th className="px-4 py-3 font-medium whitespace-nowrap">Employee</th>
              <th className="px-4 py-3 font-medium whitespace-nowrap">Type</th>
              <th className="px-4 py-3 font-medium whitespace-nowrap">Start</th>
              <th className="px-4 py-3 font-medium whitespace-nowrap">End</th>
              <th className="px-4 py-3 font-medium whitespace-nowrap">Duration</th>
              <th className="px-4 py-3 font-medium whitespace-nowrap">Status</th>
              <th className="px-4 py-3 font-medium whitespace-nowrap"></th>
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr>
                <td colSpan={7} className="px-4 py-6 text-center text-slate-500">
                  Loading requests...
                </td>
              </tr>
            )}

            {isError && !isLoading && (
              <tr>
                <td colSpan={7} className="px-4 py-6 text-center text-rose-400">
                  Failed to load time off requests.
                </td>
              </tr>
            )}

            {!isLoading && !isError && requests.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-6 text-center text-slate-500">
                  No time off requests match the current filters.
                </td>
              </tr>
            )}

            {!isLoading &&
              !isError &&
              requests.map((row) => {
                const isPending = row.status === 'SUBMITTED';
                return (
                  <tr
                    key={row.id}
                    onClick={() => navigate(`/time-off/requests/${row.id}`)}
                    className="border-b border-slate-700/40 last:border-b-0 hover:bg-slate-700/30 transition-colors cursor-pointer"
                  >
                    <td className="px-4 py-3 text-slate-200 whitespace-nowrap">
                      {row.employee_name || row.employee_id}
                    </td>
                    <td className="px-4 py-3 text-slate-300 whitespace-nowrap">
                      {row.time_off_type_name || row.time_off_type_id}
                    </td>
                    <td className="px-4 py-3 text-slate-300 whitespace-nowrap">{row.start_date}</td>
                    <td className="px-4 py-3 text-slate-300 whitespace-nowrap">{row.end_date}</td>
                    <td className="px-4 py-3 text-slate-300 whitespace-nowrap">
                      {row.duration} {row.duration === 1 ? 'Day' : 'Days'}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <TimeOffStatusBadge status={row.status} />
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          disabled={!isPending || approveMutation.isPending}
                          onClick={(e) => handleApprove(e, row.id)}
                          className="px-3 py-1.5 rounded-md bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-medium transition-colors"
                        >
                          Approve
                        </button>
                        <button
                          type="button"
                          disabled={!isPending || refuseMutation.isPending}
                          onClick={(e) => handleRefuse(e, row.id)}
                          className="px-3 py-1.5 rounded-md bg-slate-700 hover:bg-slate-600 disabled:opacity-40 disabled:cursor-not-allowed text-slate-200 text-xs font-medium transition-colors"
                        >
                          Refuse
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
          </tbody>
        </table>
      </div>

      <p className="mt-4 text-xs text-slate-500">
        Useful note: request status should show the approval lifecycle clearly.
      </p>
    </div>
  );
};

export default TimeOffRequestsPage;