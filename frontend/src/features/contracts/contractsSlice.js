import { createSlice } from '@reduxjs/toolkit';

const initialState = { searchTerm: '' };

export const contractsSlice = createSlice({
  name: 'contracts',
  initialState,
  reducers: {
    setSearchTerm: (state, action) => {
      state.searchTerm = action.payload;
    },
  },
});

export const { setSearchTerm } = contractsSlice.actions;
export default contractsSlice.reducer;
