import React from 'react';
import clsx from 'clsx';
import { LayoutGrid, List, Plus, Search } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '../app/hooks';
import { EmployeeCard } from '../features/employees/components/EmployeeCard';
import { setSearchTerm, setViewMode } from '../features/employees/employeesSlice';
import type { Employee } from '../features/employees/types';
import { useEmployeeQueries } from '../features/employees/useEmployeeQueries';

export const EmployeesPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const { searchTerm, viewMode } = useAppSelector((state) => state.employees);
  const { employeesQuery } = useEmployeeQueries();
  const employees = employeesQuery.data ?? [];
  const displayedEmployees = employees.filter((employee) => (
    employee.name.toLowerCase().includes(searchTerm.toLowerCase())
  ));

  const handleEmployeeClick = (employee: Employee) => {
    // TODO: open shared Employee Form
    console.log(employee.id);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Employees</h1>
        <p className="text-slate-400 mt-1">Default view: {viewMode}</p>
      </div>

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <button type="button" className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-brand-600 text-sm font-semibold text-white shadow-lg shadow-brand-600/20 transition hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-500">
            <Plus className="w-4 h-4" />
            New
          </button>
          <label className="relative block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="search"
              value={searchTerm}
              onChange={(event) => dispatch(setSearchTerm(event.target.value))}
              placeholder="Search employees"
              className="w-full sm:w-72 rounded-xl border border-slate-700 bg-slate-800/60 py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder:text-slate-500 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/30"
            />
          </label>
        </div>

        <div className="inline-flex self-start rounded-xl border border-slate-700 bg-slate-800/60 p-1">
          <button type="button" onClick={() => dispatch(setViewMode('kanban'))} className={clsx('inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition', viewMode === 'kanban' ? 'bg-brand-600 text-white shadow' : 'text-slate-400 hover:text-white')}>
            <LayoutGrid className="w-4 h-4" />
            Kanban
          </button>
          <button type="button" onClick={() => dispatch(setViewMode('list'))} className={clsx('inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition', viewMode === 'list' ? 'bg-brand-600 text-white shadow' : 'text-slate-400 hover:text-white')}>
            <List className="w-4 h-4" />
            List
          </button>
        </div>
      </div>

      {employeesQuery.isLoading && <p className="text-slate-400">Loading employees...</p>}
      {employeesQuery.isError && <p className="text-rose-400">Unable to load employees.</p>}
      {!employeesQuery.isLoading && !employeesQuery.isError && (
        viewMode === 'kanban' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {displayedEmployees.map((employee) => <EmployeeCard key={employee.id} employee={employee} onClick={handleEmployeeClick} />)}
          </div>
        ) : (
          <div className="overflow-hidden rounded-2xl bg-slate-800/60 border border-slate-700/50 backdrop-blur shadow-xl">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-slate-700/50 text-slate-400">
                  <tr>
                    <th className="px-6 py-4 font-semibold">Name</th>
                    <th className="px-6 py-4 font-semibold">Role</th>
                    <th className="px-6 py-4 font-semibold">Department</th>
                    <th className="px-6 py-4 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {displayedEmployees.map((employee) => (
                    <tr key={employee.id} onClick={() => handleEmployeeClick(employee)} className="cursor-pointer border-b border-slate-700/50 last:border-b-0 transition hover:bg-slate-700/30">
                      <td className="px-6 py-4 font-medium text-white">{employee.name}</td>
                      <td className="px-6 py-4 text-slate-300">{employee.role}</td>
                      <td className="px-6 py-4 text-slate-300">{employee.department}</td>
                      <td className="px-6 py-4"><span className="inline-flex items-center gap-2 text-slate-300"><span className={clsx('w-2.5 h-2.5 rounded-full', employee.status === 'active' ? 'bg-emerald-400' : 'bg-slate-500')} />{employee.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )
      )}

      {!employeesQuery.isLoading && !employeesQuery.isError && displayedEmployees.length === 0 && <p className="text-slate-400">No employees found.</p>}

      <p className="text-sm text-slate-500">Kanban is good for browsing; clicking a card opens the same Employee Form used everywhere else.</p>
    </div>
  );
};
