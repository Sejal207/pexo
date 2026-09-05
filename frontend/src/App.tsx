import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './routes/DashboardPage';
import { EmployeesPage } from './routes/EmployeesPage';
import { EmployeeDetailPage } from './routes/EmployeeDetailPage';
import { ContractsPage } from './routes/ContractsPage';
import { ContractDetailPage } from './routes/ContractDetailPage';
import { AttendancePage } from './routes/AttendancePage';
import { AttendanceDetailPage } from './routes/AttendanceDetailPage';
import { AllocationsPage } from './routes/AllocationsPage';
import { AllocationDetailPage } from './routes/AllocationDetailPage';
import { TimeOffRequestsPage } from './routes/TimeOffRequestsPage';
import { TimeOffRequestDetailPage } from './routes/TimeOffRequestDetailPage';
import { WorkingSchedulesPage } from './routes/WorkingSchedulesPage';
import { WorkingScheduleDetailPage } from './routes/WorkingScheduleDetailPage';
import { TimeOffTypesPage } from './routes/TimeOffTypesPage';
import { TimeOffTypeDetailPage } from './routes/TimeOffTypeDetailPage';
import { SalaryStructuresPage, SalaryStructureDetailPage, SalaryRulesPage, SalaryRuleDetailPage, NewPayrunWizard, PayrunsPage, PayrunDetailPage, PayslipsPage, PayslipDetailPage, PayrollDashboardPage } from './routes/PayrollPages';
import { SignupPage } from './routes/SignupPage';

const AppShell: React.FC = () => {
  const { pathname } = useLocation();
  const isAuthPage = pathname === '/signup';
  return (
      <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col">
        {!isAuthPage && <Navbar />}
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/employees" element={<EmployeesPage />} />
            <Route path="/employees/:id" element={<EmployeeDetailPage />} />
            <Route path="/contracts" element={<ContractsPage />} />
            <Route path="/contracts/:id" element={<ContractDetailPage />} />
            <Route path="/attendance" element={<AttendancePage />} />
            <Route path="/attendance/:id" element={<AttendanceDetailPage />} />

            <Route path="/time-off" element={<div className="p-8 text-slate-300">Time Off Dashboard</div>} />
            <Route path="/time-off/requests" element={<TimeOffRequestsPage />} />
            <Route path="/time-off/requests/:id" element={<TimeOffRequestDetailPage />} />
            <Route path="/time-off/types" element={<TimeOffTypesPage />} />
            <Route path="/time-off/types/:id" element={<TimeOffTypeDetailPage />} />
            <Route path="/time-off/allocations" element={<AllocationsPage />} />
            <Route path="/time-off/allocations/:id" element={<AllocationDetailPage />} />
            <Route path="/schedules" element={<WorkingSchedulesPage />} />
            <Route path="/schedules/:id" element={<WorkingScheduleDetailPage />} />

            <Route path="/payroll" element={<PayrollDashboardPage />} />
            <Route path="/payroll/payruns" element={<PayrunsPage />} />
            <Route path="/payroll/payruns/new" element={<NewPayrunWizard />} />
            <Route path="/payroll/payruns/:id" element={<PayrunDetailPage />} />
            <Route path="/payroll/payslips" element={<PayslipsPage />} />
            <Route path="/payroll/payslips/:id" element={<PayslipDetailPage />} />
            <Route path="/payroll/structures" element={<SalaryStructuresPage />} />
            <Route path="/payroll/structures/:id" element={<SalaryStructureDetailPage />} />
            <Route path="/payroll/rules" element={<SalaryRulesPage />} />
            <Route path="/payroll/rules/:id" element={<SalaryRuleDetailPage />} />
          </Routes>
        </main>
      </div>
  );
};

export const App: React.FC = () => <Router><AppShell /></Router>;

export default App;
