import { createSlice } from '@reduxjs/toolkit';

const initialState = { searchTerm: '', selectedDepartmentId: null, viewMode: 'kanban' };

export const employeesSlice = createSlice({
  name: 'employees',
  initialState,
  reducers: {
    setSearchTerm: (state, action) => { state.searchTerm = action.payload; },
    setSelectedDepartment: (state, action) => { state.selectedDepartmentId = action.payload; },
    setViewMode: (state, action) => { state.viewMode = action.payload; },
  },
});

export const { setSearchTerm, setSelectedDepartment, setViewMode } = employeesSlice.actions;
export default employeesSlice.reducer;
