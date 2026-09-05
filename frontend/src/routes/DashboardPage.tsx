import React from 'react';
import { Users, CreditCard, Clock, CheckCircle2 } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Enterprise Overview</h1>
        <p className="text-slate-400 mt-1">Real-time metrics across HR, Attendance, and Payroll systems.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="p-6 rounded-2xl bg-slate-800/60 border border-slate-700/50 backdrop-blur shadow-xl">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold text-slate-400">Total Workforce</span>
            <Users className="w-5 h-5 text-cyan-400" />
          </div>
          <p className="text-3xl font-bold text-white mt-4">1,248</p>
          <span className="text-xs text-emerald-400 font-medium mt-1 inline-block">+12 this month</span>
        </div>

        <div className="p-6 rounded-2xl bg-slate-800/60 border border-slate-700/50 backdrop-blur shadow-xl">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold text-slate-400">Active Payrun</span>
            <CreditCard className="w-5 h-5 text-blue-400" />
          </div>
          <p className="text-3xl font-bold text-white mt-4">$482,900</p>
          <span className="text-xs text-amber-400 font-medium mt-1 inline-block">Draft (Cycle 09)</span>
        </div>

        <div className="p-6 rounded-2xl bg-slate-800/60 border border-slate-700/50 backdrop-blur shadow-xl">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold text-slate-400">Present Today</span>
            <Clock className="w-5 h-5 text-indigo-400" />
          </div>
          <p className="text-3xl font-bold text-white mt-4">96.4%</p>
          <span className="text-xs text-emerald-400 font-medium mt-1 inline-block">1,203 checked-in</span>
        </div>

        <div className="p-6 rounded-2xl bg-slate-800/60 border border-slate-700/50 backdrop-blur shadow-xl">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold text-slate-400">Pending Leaves</span>
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          </div>
          <p className="text-3xl font-bold text-white mt-4">14</p>
          <span className="text-xs text-slate-400 font-medium mt-1 inline-block">Requires HR approval</span>
        </div>
      </div>
    </div>
  );
};
