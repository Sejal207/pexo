import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  isOpen: false,
  isCheckedIn: false,
  checkInAt: null,
};

export const attendanceWidgetSlice = createSlice({
  name: 'attendanceWidget',
  initialState,
  reducers: {
    togglePopup: (state) => {
      state.isOpen = !state.isOpen;
    },
    closePopup: (state) => {
      state.isOpen = false;
    },
    checkIn: (state, action) => {
      state.isCheckedIn = true;
      state.checkInAt = action.payload;
    },
    checkOut: (state) => {
      state.isCheckedIn = false;
      state.checkInAt = null;
    },
  },
});

export const {
  togglePopup, closePopup, checkIn, checkOut,
} = attendanceWidgetSlice.actions;
export default attendanceWidgetSlice.reducer;
