// api/dashboard.ts
import type { DashboardKpis } from '../types/domain';
import { USE_MOCKS, delay } from './client';
import { MOCK_DASHBOARD_KPIS } from '../mocks';

export interface DashboardSummary extends DashboardKpis {
  risk_distribution?: {
    CRITICAL: number;
    HIGH: number;
    MEDIUM: number;
    LOW: number;
  };
  category_distribution?: Array<{
    category_id: string;
    category_name: string;
    short_name: string;
    medicine_count: number;
    total_stock_value: number;
  }>;
  demand_trend?: Array<{
    date: string;
    actualDemand: number;
  }>;
}

export async function getDashboardKpis(): Promise<DashboardSummary> {
  if (USE_MOCKS) {
    await delay();
    return MOCK_DASHBOARD_KPIS as DashboardSummary;
  }
  const { apiFetch } = await import('./client');
  return apiFetch<DashboardSummary>('/dashboard/summary');
}
