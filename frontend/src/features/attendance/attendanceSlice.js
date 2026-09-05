import { createSlice } from '@reduxjs/toolkit';

const initialState = { searchTerm: '', todayOnly: false };

export const attendanceSlice = createSlice({
  name: 'attendance',
  initialState,
  reducers: {
    setSearchTerm: (state, action) => {
      state.searchTerm = action.payload;
    },
    toggleTodayOnly: (state) => {
      state.todayOnly = !state.todayOnly;
    },
  },
});

export const { setSearchTerm, toggleTodayOnly } = attendanceSlice.actions;
export default attendanceSlice.reducer;
