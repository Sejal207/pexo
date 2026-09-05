import { useParams } from 'react-router-dom';
import { useContractDetailQuery } from '../features/contracts/useContractQueries';

const formatCurrency = (amount) => new Intl.NumberFormat('en-IN', {
  style: 'currency', currency: 'INR', maximumFractionDigits: 0,
}).format(amount);

const Field = ({ label, value, monetary }) => <div><p className="mb-2 text-sm text-slate-400">{label}</p><div className={`rounded-lg border border-slate-700/60 bg-slate-800 px-3 py-2 ${monetary ? 'text-amber-400 font-semibold' : 'text-white'}`}>{value}</div></div>;

export const ContractDetailPage = () => {
  const { id } = useParams();
  const { data: contract, isLoading, isError } = useContractDetailQuery(id);
  if (isLoading) return <div className="p-8 max-w-7xl mx-auto text-slate-400">Loading contract...</div>;
  if (isError || !contract) return <div className="p-8 max-w-7xl mx-auto text-rose-400">Unable to load contract.</div>;

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div><h1 className="text-3xl font-extrabold text-white tracking-tight">Contract / {contract.code}</h1><p className="text-slate-400 mt-1">Form view of one contract</p></div>
      <div className="grid grid-cols-2 gap-x-8 gap-y-5"><div className="space-y-5"><Field label="Employee" value={contract.employeeName} /><Field label="Start Date" value={contract.startDate} /><Field label="End Date" value={contract.endDate || '—'} /><Field label="Status" value={contract.status === 'running' ? 'Running' : 'Expired'} /></div><div className="space-y-5"><Field label="Department" value={contract.department} /><Field label="Job Position" value={contract.jobPosition} /><Field label="Wage / Month" value={formatCurrency(contract.wagePerMonth)} monetary /><Field label="Working Schedule" value={contract.workingSchedule} /></div></div>
      <section className="rounded-lg border border-slate-700/60 bg-slate-800 p-5"><h2 className="text-sm font-semibold text-white">Salary Structure / Notes</h2><p className="mt-3 text-slate-400">Structure Type: {contract.structureType}</p><p className="mt-3 text-slate-400">{contract.notes}</p></section>
      <p className="pt-2 text-xs text-slate-500">Useful note: for the problem statement, one employee should not have multiple Running contracts in the same period.</p>
    </div>
  );
};
