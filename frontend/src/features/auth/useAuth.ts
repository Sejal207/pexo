import { useAppDispatch, useAppSelector } from '../../app/hooks';
import { logout } from './authSlice';

export const useAuth = () => {
  const dispatch = useAppDispatch();
  const auth = useAppSelector((state) => state.auth);

  const handleLogout = () => {
    dispatch(logout());
  };

  return {
    ...auth,
    logout: handleLogout,
  };
};
