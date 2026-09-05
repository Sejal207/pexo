import { useParams, useNavigate } from 'react-router-dom';
import {
  useTimeOffRequestQuery,
  useApproveRequestMutation,
  useRefuseRequestMutation,
} from '../features/timeoff/useTimeOffQueries';
import TimeOffStatusBadge from '../features/timeoff/components/TimeOffStatusBadge';

function ReadOnlyField({ label, value }) {
  return (
    <div>
      <label className="block text-xs font-medium text-slate-400 mb-1">{label}</label>
      <div className="w-full px-3 py-2 rounded-md bg-slate-900 border border-slate-700/60 text-sm text-slate-200">
        {value ?? '—'}
      </div>
    </div>
  );
}

export const TimeOffRequestDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: request, isLoading, isError } = useTimeOffRequestQuery(id);
  const approveMutation = useApproveRequestMutation();
  const refuseMutation = useRefuseRequestMutation();

  if (isLoading) {
    return (
      <div className="w-full max-w-screen-xl mx-auto px-4 sm:px-6 py-6 text-slate-400">
        Loading request...
      </div>
    );
  }

  if (isError || !request) {
    return (
      <div className="w-full max-w-screen-xl mx-auto px-4 sm:px-6 py-6 text-rose-400">
        Failed to load this time off request.
      </div>
    );
  }

  const isPending = request.status === 'SUBMITTED';

  return (
    <div className="w-full max-w-screen-xl mx-auto px-4 sm:px-6 py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-100">
          Time Off Request / {request.employee_name || request.employee_id}
        </h1>
        <p className="text-sm text-slate-400 mt-1">Form view of one request</p>
      </div>

      <div className="flex flex-wrap items-center gap-3 mb-6">
        <button
          type="button"
          disabled={!isPending || approveMutation.isPending}
          onClick={() => approveMutation.mutate(id)}
          className="px-4 py-2 rounded-md bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium transition-colors"
        >
          Approve
        </button>
        <button
          type="button"
          disabled={!isPending || refuseMutation.isPending}
          onClick={() => refuseMutation.mutate(id)}
          className="px-4 py-2 rounded-md bg-slate-700 hover:bg-slate-600 disabled:opacity-40 disabled:cursor-not-allowed text-slate-200 text-sm font-medium transition-colors"
        >
          Refuse
        </button>
      </div>

      <div className="rounded-lg border border-slate-700/60 bg-slate-800 p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">
          <ReadOnlyField label="Employee" value={request.employee_name || request.employee_id} />
          <ReadOnlyField
            label="Duration"
            value={`${request.duration} ${request.duration === 1 ? 'Day' : 'Days'}`}
          />

          <ReadOnlyField label="Time Off Type" value={request.time_off_type_name || request.time_off_type_id} />
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Status</label>
            <div className="w-full px-3 py-2 rounded-md bg-slate-900 border border-slate-700/60">
              <TimeOffStatusBadge status={request.status} />
            </div>
          </div>

          <ReadOnlyField label="Start Date" value={request.start_date} />
          <ReadOnlyField label="Approver" value={request.approved_by_name || request.approved_by_user_id || '—'} />

          <ReadOnlyField label="End Date" value={request.end_date} />
          <ReadOnlyField label="Allocation Used" value={request.allocation_label || request.allocation_id || '—'} />
        </div>

        <div className="mt-6">
          <label className="block text-xs font-medium text-slate-400 mb-1">Reason</label>
          <div className="w-full min-h-[80px] px-3 py-2 rounded-md bg-slate-900 border border-slate-700/60 text-sm text-slate-200">
            {request.reason || '—'}
          </div>
        </div>
      </div>

      <p className="mt-4 text-xs text-slate-500">
        Useful note: if the selected type requires allocation, the request should clearly show which balance was consumed.
      </p>

      <button
        type="button"
        onClick={() => navigate('/time-off/requests')}
        className="mt-4 text-sm text-indigo-400 hover:text-indigo-300 transition-colors"
      >
        ← Back to requests
      </button>
    </div>
  );
};

export default TimeOffRequestDetailPage;