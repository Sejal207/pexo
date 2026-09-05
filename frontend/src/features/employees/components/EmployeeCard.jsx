import React from 'react';

const DEPARTMENT_ACCENT = {
  Finance: { bar: 'bg-amber-400', tint: 'bg-amber-400/10 border-amber-400/30 text-amber-300' },
  HR: { bar: 'bg-violet-400', tint: 'bg-violet-400/10 border-violet-400/30 text-violet-300' },
  Engineering: { bar: 'bg-emerald-400', tint: 'bg-emerald-400/10 border-emerald-400/30 text-emerald-300' },
};
const DEFAULT_ACCENT = { bar: 'bg-slate-500', tint: 'bg-slate-500/10 border-slate-500/30 text-slate-300' };

function getInitials(name) {
  return name.split(' ').map((p) => p[0]).join('').slice(0, 2).toUpperCase();
}

export const EmployeeCard = ({ employee, onClick }) => {
  const accent = DEPARTMENT_ACCENT[employee.department] ?? DEFAULT_ACCENT;
  const isActive = employee.status === 'active';

  return (
    <button
      onClick={() => onClick(employee)}
      className="group relative flex items-start gap-3 text-left p-5 pl-6 rounded-lg bg-slate-800 border border-slate-700/60 hover:border-slate-600 transition-colors overflow-hidden"
    >
      <span className={`absolute left-0 top-0 bottom-0 w-1 ${accent.bar}`} />

      <div className={`w-11 h-11 shrink-0 rounded-full border flex items-center justify-center font-bold text-sm ${accent.tint}`}>
        {getInitials(employee.name)}
      </div>

      <div className="min-w-0 flex-1">
        <p className="font-semibold text-white truncate group-hover:text-white">{employee.name}</p>
        <p className="text-sm text-slate-400 truncate">{employee.role}</p>

        <div className="mt-3 flex items-center justify-between">
          <span className="text-xs text-slate-500">{employee.department}</span>
          <span className={`flex items-center gap-1.5 text-xs font-medium ${isActive ? 'text-emerald-400' : 'text-slate-500'}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${isActive ? 'bg-emerald-400' : 'bg-slate-500'}`} />
            {isActive ? 'Active' : 'Inactive'}
          </span>
        </div>
      </div>
    </button>
  );
};