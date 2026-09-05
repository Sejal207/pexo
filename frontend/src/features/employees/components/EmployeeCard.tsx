import React from 'react';
import clsx from 'clsx';
import type { Employee } from '../types';

interface EmployeeCardProps {
  employee: Employee;
  onClick: (employee: Employee) => void;
}

const getInitials = (name: string) => name
  .split(' ')
  .filter(Boolean)
  .map((part) => part[0])
  .slice(0, 2)
  .join('')
  .toUpperCase();

export const EmployeeCard: React.FC<EmployeeCardProps> = ({ employee, onClick }) => {
  return (
    <button
      type="button"
      onClick={() => onClick(employee)}
      className="w-full p-5 rounded-2xl bg-slate-800/60 border border-slate-700/50 backdrop-blur shadow-xl text-left transition hover:border-brand-500/60 hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500"
    >
      <div className="flex items-start gap-4">
        <div className="w-11 h-11 shrink-0 rounded-xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center text-sm font-bold text-brand-100">
          {getInitials(employee.name)}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <h2 className="font-semibold text-white truncate">{employee.name}</h2>
              <p className="text-sm text-slate-400 mt-1 truncate">{employee.role}</p>
            </div>
            <span className={clsx(
              'mt-1.5 w-2.5 h-2.5 shrink-0 rounded-full',
              employee.status === 'active' ? 'bg-emerald-400' : 'bg-slate-500',
            )} />
          </div>
          <p className="text-sm text-slate-300 mt-4">{employee.department}</p>
        </div>
      </div>
    </button>
  );
};
