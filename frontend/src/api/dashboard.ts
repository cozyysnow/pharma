// api/dashboard.ts
import type { DashboardKpis } from '../types/domain';
import { USE_MOCKS, delay } from './client';
import { MOCK_DASHBOARD_KPIS } from '../mocks';

export async function getDashboardKpis(): Promise<DashboardKpis> {
  if (USE_MOCKS) { await delay(); return MOCK_DASHBOARD_KPIS; }
  const { apiFetch } = await import('./client');
  return apiFetch<DashboardKpis>('/dashboard/kpis');
}
