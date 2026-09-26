import api from './api';

export const login = async (email: string, password: string) => {
  const response = await api.post('/auth/login', { email, password });
  localStorage.setItem('token', response.data.access_token);
  localStorage.setItem('user', JSON.stringify(response.data));
  return response.data;
};

export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

export const isAuthenticated = () => !!localStorage.getItem('token');

export const getCurrentUser = () => {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
};