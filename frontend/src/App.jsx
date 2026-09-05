import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginPage } from './routes/LoginPage';
import { SignupPage } from './routes/SignupPage';
import { useAuthBootstrap } from './features/auth/useAuth';
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
import {
  SalaryStructuresPage,
  SalaryStructureDetailPage,
  SalaryRulesPage,
  SalaryRuleDetailPage,
  NewPayrunWizard,
  PayrunsPage,
  PayrunDetailPage,
  PayslipsPage,
  PayslipDetailPage,
  PayrollDashboardPage,
} from './routes/PayrollPages';

export const App = () => {
  useAuthBootstrap();

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<DashboardPage />} />
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
        </Route>
      </Routes>
    </Router>
  );
};

export default App;
