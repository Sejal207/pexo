import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface EmployeesUIState {
  searchTerm: string;
  selectedDepartmentId: number | null;
  viewMode: 'kanban' | 'list';
}

const initialState: EmployeesUIState = {
  searchTerm: '',
  selectedDepartmentId: null,
  viewMode: 'list',
};

export const employeesSlice = createSlice({
  name: 'employees',
  initialState,
  reducers: {
    setSearchTerm: (state, action: PayloadAction<string>) => {
      state.searchTerm = action.payload;
    },
    setSelectedDepartment: (state, action: PayloadAction<number | null>) => {
      state.selectedDepartmentId = action.payload;
    },
    setViewMode: (state, action: PayloadAction<'kanban' | 'list'>) => {
      state.viewMode = action.payload;
    },
  },
});

export const { setSearchTerm, setSelectedDepartment, setViewMode } = employeesSlice.actions;
export default employeesSlice.reducer;
