import { useContext } from 'react';
import AuthContext from './AuthContextInternal';

export const useAuth = () => useContext(AuthContext);
