import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './routes/DashboardPage';
import { EmployeesPage } from './routes/EmployeesPage';
import { EmployeeDetailPage } from './routes/EmployeeDetailPage';
import { ContractsPage } from './routes/ContractsPage';
import { ContractDetailPage } from './routes/ContractDetailPage';
import { AttendancePage } from './routes/AttendancePage';
import { TimeOffRequestsPage } from './routes/TimeOffRequestsPage';
import { TimeOffRequestDetailPage } from './routes/TimeOffRequestDetailPage';

export const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/employees" element={<EmployeesPage />} />
            <Route path="/employees/:id" element={<EmployeeDetailPage />} />
            <Route path="/contracts" element={<ContractsPage />} />
            <Route path="/contracts/:id" element={<ContractDetailPage />} />
            <Route path="/attendance" element={<AttendancePage />} />

            <Route path="/time-off" element={<div className="p-8 text-slate-300">Time Off Dashboard</div>} />
            <Route path="/time-off/requests" element={<TimeOffRequestsPage />} />
            <Route path="/time-off/requests/:id" element={<TimeOffRequestDetailPage />} />
            <Route path="/time-off/types" element={<div className="p-8 text-slate-300">Time Off Types</div>} />
            <Route path="/time-off/allocations" element={<div className="p-8 text-slate-300">Allocations</div>} />

            <Route path="/payroll" element={<div className="p-8 text-slate-300">Payroll Dashboard</div>} />
            <Route path="/payroll/payruns" element={<div className="p-8 text-slate-300">Payruns</div>} />
            <Route path="/payroll/payslips" element={<div className="p-8 text-slate-300">Payslips</div>} />
            <Route path="/payroll/structures" element={<div className="p-8 text-slate-300">Salary Structures</div>} />
            <Route path="/payroll/rules" element={<div className="p-8 text-slate-300">Salary Rules</div>} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;