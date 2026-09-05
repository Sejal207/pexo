import { createSlice } from '@reduxjs/toolkit';

// The access token itself is never stored here (or anywhere persisted) — it
// lives only as an in-memory variable inside api/httpClient.js. This slice
// just tracks who's logged in, for UI purposes.
const initialState = {
  user: null,
  isAuthenticated: false,
  status: 'idle', // 'idle' | 'loading' | 'ready' — 'loading' while the silent-refresh bootstrap runs
};

export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setAuthStatus: (state, action) => {
      state.status = action.payload;
    },
    setCredentials: (state, action) => {
      state.user = action.payload.user;
      state.isAuthenticated = true;
      state.status = 'ready';
    },
    logout: (state) => {
      state.user = null;
      state.isAuthenticated = false;
      state.status = 'ready';
    },
  },
});

export const { setAuthStatus, setCredentials, logout } = authSlice.actions;
export default authSlice.reducer;
