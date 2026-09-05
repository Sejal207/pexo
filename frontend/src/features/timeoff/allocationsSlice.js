import { createSlice } from '@reduxjs/toolkit';

const initialState = { searchTerm: '' };

export const allocationsSlice = createSlice({
  name: 'allocations',
  initialState,
  reducers: {
    setSearchTerm: (state, action) => {
      state.searchTerm = action.payload;
    },
  },
});

export const { setSearchTerm } = allocationsSlice.actions;
export default allocationsSlice.reducer;
