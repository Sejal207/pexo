import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginPage } from './routes/LoginPage';
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

export const App = () => {
  useAuthBootstrap();

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

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
          <Route path="/time-off/types" element={<div className="p-8 text-slate-300">Time Off Types</div>} />
          <Route path="/time-off/allocations" element={<AllocationsPage />} />
          <Route path="/time-off/allocations/:id" element={<AllocationDetailPage />} />

          <Route path="/payroll" element={<div className="p-8 text-slate-300">Payroll Dashboard</div>} />
          <Route path="/payroll/payruns" element={<div className="p-8 text-slate-300">Payruns</div>} />
          <Route path="/payroll/payslips" element={<div className="p-8 text-slate-300">Payslips</div>} />
          <Route path="/payroll/structures" element={<div className="p-8 text-slate-300">Salary Structures</div>} />
          <Route path="/payroll/rules" element={<div className="p-8 text-slate-300">Salary Rules</div>} />
        </Route>
      </Routes>
    </Router>
  );
};

export default App;
