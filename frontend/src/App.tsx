import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './routes/DashboardPage';
import { EmployeesPage } from './routes/EmployeesPage';
import { EmployeeDetailPage } from './routes/EmployeeDetailPage';
import { ContractsPage } from './routes/ContractsPage';
import { ContractDetailPage } from './routes/ContractDetailPage';

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
            <Route path="/time-off" element={<div className="p-8 text-slate-300">Time Off module</div>} />
            <Route path="/attendance" element={<div className="p-8 text-slate-300">Attendance & Leave Tracking Module</div>} />
            <Route path="/payroll" element={<div className="p-8 text-slate-300">Payroll Calculation & Payrun Wizard Module</div>} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;

