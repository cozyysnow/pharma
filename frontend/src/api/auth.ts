import { apiFetch, delay, USE_MOCKS } from './client';
import type { User } from '../types/auth';

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export async function loginApi(email: string, password: string): Promise<LoginResponse> {
  if (USE_MOCKS) {
    await delay(300);
    const mockUser: User = {
      id: 1,
      email,
      name: 'Dr. Sarah Mitchell',
      role: 'ADMIN',
      isActive: true,
      createdAt: new Date().toISOString(),
    };
    return {
      access_token: 'mock_jwt_token',
      refresh_token: 'mock_refresh_token',
      token_type: 'bearer',
      expires_in: 3600,
      user: mockUser,
    };
  }

  const res = await apiFetch<LoginResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  if (res.access_token) {
    localStorage.setItem('pharma_token', res.access_token);
    localStorage.setItem('pharma_refresh_token', res.refresh_token);
    localStorage.setItem('pharma_role', res.user.role);
  }
  return res;
}

export async function getCurrentUserApi(): Promise<User> {
  if (USE_MOCKS) {
    await delay(200);
    return {
      id: 1,
      email: 'admin@pharmastock.local',
      name: 'Dr. Sarah Mitchell',
      role: 'ADMIN',
      isActive: true,
      createdAt: new Date().toISOString(),
    };
  }
  return apiFetch<User>('/auth/me');
}

export function logoutApi(): void {
  localStorage.removeItem('pharma_token');
  localStorage.removeItem('pharma_refresh_token');
  localStorage.removeItem('pharma_role');
}
