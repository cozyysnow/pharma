// api/client.ts — shared HTTP client + mock flag
export const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === 'true';
export const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000/api/v1';

/** Simulates a network delay in mock mode */
export function delay(ms = 300): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('pharma_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options?.headers as Record<string, string>),
  };

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    const errorMsg =
      err.error?.message ||
      err.message ||
      err.detail ||
      `Request failed with HTTP ${res.status}`;
    throw new Error(errorMsg);
  }

  return res.json() as Promise<T>;
}

