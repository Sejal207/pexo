import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  isOpen: false,
  isCheckedIn: false,
  checkInAt: null,
  attendanceId: null,
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
      if (typeof action.payload === 'object' && action.payload !== null) {
        state.checkInAt = action.payload.checkInAt;
        state.attendanceId = action.payload.attendanceId ?? state.attendanceId;
      } else {
        state.checkInAt = action.payload;
      }
    },
    checkOut: (state) => {
      state.isCheckedIn = false;
      state.checkInAt = null;
      state.attendanceId = null;
    },
    syncWidgetStatus: (state, action) => {
      const { open, since, attendance_id } = action.payload || {};
      state.isCheckedIn = Boolean(open);
      state.checkInAt = open ? since : null;
      state.attendanceId = open ? attendance_id : null;
    },
  },
});

export const {
  togglePopup, closePopup, checkIn, checkOut, syncWidgetStatus,
} = attendanceWidgetSlice.actions;
export default attendanceWidgetSlice.reducer;
