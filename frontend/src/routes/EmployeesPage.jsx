import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Search, LayoutGrid, List as ListIcon, AlertCircle, RotateCw } from 'lucide-react';
import { useAppDispatch, useAppSelector } from '../app/hooks';
import { useEmployeeQueries } from '../features/employees/useEmployeeQueries';
import { setSearchTerm, setViewMode } from '../features/employees/employeesSlice';
import { EmployeeCard } from '../features/employees/components/EmployeeCard';

export const EmployeesPage = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { searchTerm, viewMode } = useAppSelector((state) => state.employees);
  const { employeesQuery } = useEmployeeQueries();

  const all = employeesQuery.data ?? [];
  const employees = all.filter((e) => e.name.toLowerCase().includes(searchTerm.toLowerCase()));
  const activeCount = all.filter((e) => e.status === 'active').length;

  const handleCardClick = (employee) => navigate(`/employees/${employee.id}`);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Employees</h1>
        <p className="text-slate-400 mt-1">
          {all.length > 0
            ? `${all.length} people · ${activeCount} active · viewing as ${viewMode}`
            : `Default view: ${viewMode}`}
        </p>
      </div>

      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-3 flex-1 min-w-[280px]">
          <button className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm px-4 py-2.5 rounded-lg transition-colors">
            <Plus className="w-4 h-4" />
            New
          </button>
          <div className="relative flex-1 max-w-sm">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              value={searchTerm}
              onChange={(e) => dispatch(setSearchTerm(e.target.value))}
              placeholder="Search employees"
              className="w-full bg-slate-800 border border-slate-700/60 rounded-lg pl-9 pr-3 py-2.5 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>
        </div>

        <div className="relative inline-flex rounded-lg border border-slate-700/60 bg-slate-800 p-1">
          <span
            className={`absolute inset-y-1 w-[calc(50%-2px)] rounded-md bg-indigo-600 transition-transform duration-200 ${
              viewMode === 'list' ? 'translate-x-full' : 'translate-x-0'
            }`}
          />
          <button
            onClick={() => dispatch(setViewMode('kanban'))}
            className={`relative z-10 flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              viewMode === 'kanban' ? 'text-white' : 'text-slate-400'
            }`}
          >
            <LayoutGrid className="w-4 h-4" />
            Kanban
          </button>
          <button
            onClick={() => dispatch(setViewMode('list'))}
            className={`relative z-10 flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              viewMode === 'list' ? 'text-white' : 'text-slate-400'
            }`}
          >
            <ListIcon className="w-4 h-4" />
            List
          </button>
        </div>
      </div>

      {employeesQuery.isError && (
        <div className="flex items-center justify-between gap-3 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3">
          <div className="flex items-center gap-2 text-red-300 text-sm">
            <AlertCircle className="w-4 h-4 shrink-0" />
            Couldn't load employees. The HR service might be offline.
          </div>
          <button
            onClick={() => employeesQuery.refetch()}
            className="flex items-center gap-1.5 text-sm font-medium text-red-300 hover:text-red-200 shrink-0"
          >
            <RotateCw className="w-3.5 h-3.5" />
            Retry
          </button>
        </div>
      )}

      {!employeesQuery.isError && employees.length === 0 && (
        <p className="text-sm text-slate-500 py-8 text-center">
          {searchTerm ? `No one matches "${searchTerm}".` : 'No employees yet — add your first one.'}
        </p>
      )}

      {viewMode === 'kanban' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {employees.map((employee) => (
            <EmployeeCard key={employee.id} employee={employee} onClick={handleCardClick} />
          ))}
        </div>
      ) : (
        employees.length > 0 && (
          <div className="rounded-lg border border-slate-700/60 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-400 border-b border-slate-700/60">
                  <th className="p-4 font-medium">Name</th>
                  <th className="p-4 font-medium">Role</th>
                  <th className="p-4 font-medium">Department</th>
                  <th className="p-4 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {employees.map((employee) => (
                  <tr
                    key={employee.id}
                    onClick={() => handleCardClick(employee)}
                    className="border-b border-slate-700/40 last:border-0 hover:border-slate-600 cursor-pointer"
                  >
                    <td className="p-4 text-white font-medium">{employee.name}</td>
                    <td className="p-4 text-slate-400">{employee.role}</td>
                    <td className="p-4 text-slate-400">{employee.department}</td>
                    <td className="p-4">
                      <span className={employee.status === 'active' ? 'text-emerald-400' : 'text-rose-400'}>
                        {employee.status === 'active' ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}

      <p className="text-xs text-slate-500 pt-2">
        Kanban is good for browsing; clicking a card opens the same Employee Form used everywhere else.
      </p>
    </div>
  );
};

export default EmployeesPage;