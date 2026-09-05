import { useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useAppDispatch, useAppSelector } from '../../app/hooks';
import { httpClient, setAccessToken } from '../../api/httpClient';
import { setAuthStatus, setCredentials, logout as logoutAction } from './authSlice';

export const useAuth = () => {
  const dispatch = useAppDispatch();
  const auth = useAppSelector((state) => state.auth);

  const loginMutation = useMutation({
    mutationFn: async ({ email, password }) => {
      const { data } = await httpClient.post('/auth/login', { email, password });
      return data;
    },
    onSuccess: (data) => {
      setAccessToken(data.access_token);
      dispatch(setCredentials({ user: data.user }));
    },
  });

  const logout = async () => {
    try {
      await httpClient.post('/auth/logout');
    } catch {
      // best-effort — clear local session state regardless of network outcome
    }
    setAccessToken(null);
    dispatch(logoutAction());
  };

  return {
    ...auth,
    login: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    loginError: loginMutation.error,
    logout,
  };
};

// Runs once on app load: trades the httpOnly refresh cookie (if any) for a
// fresh in-memory access token, so a page reload doesn't force a re-login.
export const useAuthBootstrap = () => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    let cancelled = false;

    (async () => {
      dispatch(setAuthStatus('loading'));
      try {
        const { data } = await httpClient.post('/auth/refresh');
        if (cancelled) return;
        setAccessToken(data.access_token);
        dispatch(setCredentials({ user: data.user }));
      } catch {
        if (!cancelled) dispatch(logoutAction());
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [dispatch]);
};
