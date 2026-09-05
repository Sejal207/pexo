import { Link } from 'react-router-dom';
import { Users, Calendar, CalendarClock, DollarSign, FileText, LayoutDashboard, LogOut } from 'lucide-react';
import { AttendanceWidget } from '../features/attendance/components/AttendanceWidget';
import { NavDropdown } from './NavDropdown';
import { useAuth } from '../features/auth/useAuth';

export const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <header className="bg-slate-800/80 backdrop-blur border-b border-slate-700/60 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-bold text-white shadow-lg shadow-cyan-500/20">360</div>
          <span className="font-bold text-lg text-slate-100 tracking-tight">Pexo</span>
        </div>
        <nav className="flex space-x-1">
          <Link to="/" className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-700/50 hover:text-white transition"><LayoutDashboard className="w-4 h-4" /><span>Dashboard</span></Link>
          <Link to="/employees" className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-700/50 hover:text-white transition"><Users className="w-4 h-4" /><span>Employees</span></Link>
          <Link to="/contracts" className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-700/50 hover:text-white transition"><FileText className="w-4 h-4" /><span>Contracts</span></Link>
          <Link to="/attendance" className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-700/50 hover:text-white transition"><Calendar className="w-4 h-4" /><span>Attendance</span></Link>
          <NavDropdown
            label="Time Off"
            icon={CalendarClock}
            items={[
              { label: 'Dashboard', to: '/time-off' },
              { label: 'Time offs', to: '/time-off/requests' },
              { label: 'Time off Types', to: '/time-off/types' },
              { label: 'Allocations', to: '/time-off/allocations' },
            ]}
          />
          <NavDropdown
            label="Payroll"
            icon={DollarSign}
            items={[
              { label: 'Dashboard', to: '/payroll' },
              { label: 'Payruns', to: '/payroll/payruns' },
              { label: 'Payslips', to: '/payroll/payslips' },
              { label: 'Structures', to: '/payroll/structures' },
              { label: 'Rules', to: '/payroll/rules' },
            ]}
          />
        </nav>
        <div className="flex items-center gap-3">
          <AttendanceWidget />
          {user && (
            <div className="flex items-center gap-2 pl-3 border-l border-slate-700/60">
              <span className="text-sm font-medium text-slate-300 hidden sm:inline">{user.full_name ?? user.email}</span>
              <button
                type="button"
                onClick={logout}
                aria-label="Log out"
                className="flex h-8 w-8 items-center justify-center rounded-full text-slate-400 transition-colors hover:bg-slate-700/50 hover:text-white"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
