import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../features/auth/authSlice';
import employeesReducer from '../features/employees/employeesSlice';
import contractsReducer from '../features/contracts/contractsSlice';
import payrollReducer from '../features/payroll/payrollSlice';
import attendanceReducer from '../features/attendance/attendanceSlice';
import attendanceWidgetReducer from '../features/attendance/attendanceWidgetSlice';
import allocationsReducer from '../features/timeoff/allocationsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    employees: employeesReducer,
    contracts: contractsReducer,
    payroll: payrollReducer,
    attendance: attendanceReducer,
    attendanceWidget: attendanceWidgetReducer,
    allocations: allocationsReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
