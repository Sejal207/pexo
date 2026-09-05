import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  searchText: '',
  myTeamOnly: false,
};

export const timeOffSlice = createSlice({
  name: 'timeOff',
  initialState,
  reducers: {
    setSearchText: (state, action) => {
      state.searchText = action.payload;
    },
    toggleMyTeamOnly: (state) => {
      state.myTeamOnly = !state.myTeamOnly;
    },
  },
});

export const { setSearchText, toggleMyTeamOnly } = timeOffSlice.actions;
export default timeOffSlice.reducer;
