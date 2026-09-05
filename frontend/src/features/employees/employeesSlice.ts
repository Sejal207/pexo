import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface EmployeesUIState {
  searchTerm: string;
  selectedDepartmentId: number | null;
}

const initialState: EmployeesUIState = {
  searchTerm: '',
  selectedDepartmentId: null,
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
  },
});

export const { setSearchTerm, setSelectedDepartment } = employeesSlice.actions;
export default employeesSlice.reducer;
