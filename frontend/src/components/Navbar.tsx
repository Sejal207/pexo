import React from 'react';
import { Link } from 'react-router-dom';
import { Users, Calendar, DollarSign, LayoutDashboard } from 'lucide-react';

export const Navbar: React.FC = () => {
  return (
    <header className="bg-slate-800/80 backdrop-blur border-b border-slate-700/60 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-bold text-white shadow-lg shadow-cyan-500/20">
            360
          </div>
          <span className="font-bold text-lg text-slate-100 tracking-tight">PeoplePay360</span>
        </div>
        <nav className="flex space-x-1">
          <Link to="/" className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-700/50 hover:text-white transition">
            <LayoutDashboard className="w-4 h-4" />
            <span>Dashboard</span>
          </Link>
          <Link to="/employees" className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-700/50 hover:text-white transition">
            <Users className="w-4 h-4" />
            <span>Employees</span>
          </Link>
          <Link to="/attendance" className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-700/50 hover:text-white transition">
            <Calendar className="w-4 h-4" />
            <span>Attendance</span>
          </Link>
          <Link to="/payroll" className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-700/50 hover:text-white transition">
            <DollarSign className="w-4 h-4" />
            <span>Payroll</span>
          </Link>
        </nav>
      </div>
    </header>
  );
};
