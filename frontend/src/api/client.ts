// api/client.ts — shared HTTP client + mock flag
export const USE_MOCKS = import.meta.env.VITE_USE_MOCKS !== 'false';
export const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000/api/v1';

/** Simulates a network delay in mock mode */
export function delay(ms = 300): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}
