import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  searchText: '',
  employeeIdFilter: null,
  employeeNameFilter: null,
  dateFilter: null,
  isTodayFilterActive: false,
};

const attendanceSlice = createSlice({
  name: 'attendance',
  initialState,
  reducers: {
    setSearchText(state, action) {
      state.searchText = action.payload;
    },
    setEmployeeFilter(state, action) {
      const { employeeId, employeeName } = action.payload || {};
      state.employeeIdFilter = employeeId ?? null;
      state.employeeNameFilter = employeeName ?? null;
    },
    clearEmployeeFilter(state) {
      state.employeeIdFilter = null;
      state.employeeNameFilter = null;
    },
    toggleTodayFilter(state) {
      state.isTodayFilterActive = !state.isTodayFilterActive;
      state.dateFilter = state.isTodayFilterActive
        ? new Date().toISOString().slice(0, 10)
        : null;
    },
    clearTodayFilter(state) {
      state.isTodayFilterActive = false;
      state.dateFilter = null;
    },
  },
});

export const {
  setSearchText,
  setEmployeeFilter,
  clearEmployeeFilter,
  toggleTodayFilter,
  clearTodayFilter,
} = attendanceSlice.actions;

export default attendanceSlice.reducer;