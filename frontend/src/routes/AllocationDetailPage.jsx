import { useParams } from 'react-router-dom';
import { useAllocationDetailQuery } from '../features/timeoff/useAllocationQueries';

const Field = ({ label, value }) => <div><p className="mb-2 text-sm text-slate-400">{label}</p><div className="rounded-lg border border-slate-700/60 bg-slate-800 px-3 py-2 text-white">{value}</div></div>;

export const AllocationDetailPage = () => {
  const { id } = useParams();
  const { data: allocation, isLoading, isError } = useAllocationDetailQuery(id);
  if (isLoading) return <div className="p-8 max-w-7xl mx-auto text-slate-400">Loading allocation...</div>;
  if (isError || !allocation) return <div className="p-8 max-w-7xl mx-auto text-rose-400">Unable to load allocation.</div>;

  // TODO: wire up to real approve/refuse endpoints once the time-off service exposes them.
  const handleApprove = () => console.log('approve allocation', allocation.id);
  const handleRefuse = () => console.log('refuse allocation', allocation.id);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Allocation / {allocation.employeeName}</h1>
        <p className="text-slate-400 mt-1">Form view of one allocation record</p>
      </div>

      <div className="flex gap-3">
        <button type="button" onClick={handleApprove} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-500">Approve</button>
        <button type="button" onClick={handleRefuse} className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 hover:bg-slate-800">Refuse</button>
      </div>

      <div className="grid grid-cols-2 gap-x-8 gap-y-5">
        <div className="space-y-5">
          <Field label="Employee" value={allocation.employeeName} />
          <Field label="Time Off Type" value={allocation.type} />
          <Field label="Allocated" value={`${allocation.allocatedDays} Days`} />
          <Field label="Status" value={allocation.status} />
        </div>
        <div className="space-y-5">
          <Field label="Taken" value={`${allocation.takenDays} Days`} />
          <Field label="Remaining" value={`${allocation.remainingDays} Days`} />
          <Field label="Approver" value={allocation.approver} />
          <Field label="Validity" value={allocation.validity} />
        </div>
      </div>

      <section className="rounded-lg border border-slate-700/60 bg-slate-800 p-5">
        <h2 className="text-sm font-semibold text-white">Description</h2>
        <p className="mt-3 text-slate-400">{allocation.description}</p>
      </section>

      <p className="pt-2 text-xs text-slate-500">Useful note: approved allocation is what creates available leave balance for the employee.</p>
    </div>
  );
};
