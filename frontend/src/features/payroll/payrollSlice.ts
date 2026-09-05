import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface PayrollUIState {
  activeWizardStep: number;
  selectedPayrunId: number | null;
}

const initialState: PayrollUIState = {
  activeWizardStep: 1,
  selectedPayrunId: null,
};

export const payrollSlice = createSlice({
  name: 'payroll',
  initialState,
  reducers: {
    setWizardStep: (state, action: PayloadAction<number>) => {
      state.activeWizardStep = action.payload;
    },
    setSelectedPayrun: (state, action: PayloadAction<number | null>) => {
      state.selectedPayrunId = action.payload;
    },
  },
});

export const { setWizardStep, setSelectedPayrun } = payrollSlice.actions;
export default payrollSlice.reducer;
