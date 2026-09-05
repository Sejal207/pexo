import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  activeWizardStep: 1,
  selectedPayrunId: null,
};

export const payrollSlice = createSlice({
  name: 'payroll',
  initialState,
  reducers: {
    setWizardStep: (state, action) => {
      state.activeWizardStep = action.payload;
    },
    setSelectedPayrun: (state, action) => {
      state.selectedPayrunId = action.payload;
    },
  },
});

export const { setWizardStep, setSelectedPayrun } = payrollSlice.actions;
export default payrollSlice.reducer;
