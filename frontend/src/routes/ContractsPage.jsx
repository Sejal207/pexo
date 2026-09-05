import { Plus, Search } from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../app/hooks';
import { setSearchTerm } from '../features/contracts/contractsSlice';
import { useContractsQuery } from '../features/contracts/useContractQueries';

const formatCurrency = (amount) => new Intl.NumberFormat('en-IN', {
  style: 'currency', currency: 'INR', maximumFractionDigits: 0,
}).format(amount);

export const ContractsPage = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const employeeId = searchParams.get('employeeId');
  const searchTerm = useAppSelector((state) => state.contracts.searchTerm);
  const { data: contracts = [], isLoading, isError } = useContractsQuery(employeeId);
  const displayedContracts = contracts.filter((contract) => (
    contract.code.toLowerCase().includes(searchTerm.toLowerCase())
    || contract.employeeName.toLowerCase().includes(searchTerm.toLowerCase())
  ));

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div><h1 className="text-3xl font-extrabold text-white tracking-tight">Contracts</h1><p className="text-slate-400 mt-1">List view of employee contracts</p></div>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <button type="button" className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-indigo-500"><Plus className="w-4 h-4" />New</button>
        <label className="relative block"><Search className="absolute left-3 top-1/2 w-4 h-4 -translate-y-1/2 text-slate-500" /><input type="search" value={searchTerm} onChange={(event) => dispatch(setSearchTerm(event.target.value))} placeholder="Search contracts" className="w-full sm:w-72 rounded-lg border border-slate-700/60 bg-slate-800 py-2.5 pl-10 pr-4 text-sm text-white placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none" /></label>
      </div>
      {isLoading && <p className="text-slate-400">Loading contracts...</p>}
      {isError && <p className="text-rose-400">Unable to load contracts.</p>}
      {!isLoading && !isError && <div className="overflow-hidden rounded-lg border border-slate-700/60 bg-slate-800"><div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="border-b border-slate-700/60 text-slate-400"><tr><th className="p-4 font-medium">Contract</th><th className="p-4 font-medium">Employee</th><th className="p-4 font-medium">Start</th><th className="p-4 font-medium">End</th><th className="p-4 font-medium">Wage / Month</th><th className="p-4 font-medium">Status</th></tr></thead><tbody>{displayedContracts.map((contract) => <tr key={contract.id} onClick={() => navigate(`/contracts/${contract.id}`)} className="cursor-pointer border-b border-slate-700/40 last:border-0 hover:border-slate-600"><td className="p-4 font-medium text-white">{contract.code}</td><td className="p-4 text-slate-400">{contract.employeeName}</td><td className="p-4 text-slate-400">{contract.startDate}</td><td className="p-4 text-slate-400">{contract.endDate || '—'}</td><td className="p-4 text-amber-400 font-semibold">{formatCurrency(contract.wagePerMonth)}</td><td className={`p-4 font-medium ${contract.status === 'running' ? 'text-emerald-400' : 'text-rose-400'}`}><span className={`mr-2 inline-block h-2 w-2 rounded-full ${contract.status === 'running' ? 'bg-emerald-400' : 'bg-rose-400'}`} />{contract.status === 'running' ? 'Running' : 'Expired'}</td></tr>)}</tbody></table></div></div>}
      {!isLoading && !isError && displayedContracts.length === 0 && <p className="text-sm text-slate-500">No contracts found.</p>}
      <p className="pt-2 text-xs text-slate-500">Useful note: retain contract history, but make the active Running contract obvious because payroll depends on it.</p>
    </div>
  );
};
