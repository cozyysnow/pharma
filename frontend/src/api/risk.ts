// api/risk.ts
import type { RiskResult, PaginatedResponse, RiskLevel } from '../types/domain';
import { USE_MOCKS, delay } from './client';
import { MOCK_RISK_RESULTS } from '../mocks';

export interface RiskFilters {
  search?: string;
  category_id?: string;
  risk_level?: RiskLevel;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_dir?: 'asc' | 'desc';
}

export async function getRiskResults(filters: RiskFilters = {}): Promise<PaginatedResponse<RiskResult>> {
  if (USE_MOCKS) {
    await delay();
    let items = [...MOCK_RISK_RESULTS];
    if (filters.search) {
      const q = filters.search.toLowerCase();
      items = items.filter(r => r.medicine?.display_name.toLowerCase().includes(q) || r.medicine?.generic_name.toLowerCase().includes(q) || r.medicine_id.toLowerCase().includes(q));
    }
    if (filters.category_id) items = items.filter(r => r.medicine?.category_id === filters.category_id);
    if (filters.risk_level) items = items.filter(r => r.risk_level === filters.risk_level);
    if (filters.sort_by === 'risk_score') items.sort((a, b) => filters.sort_dir === 'asc' ? a.risk_score - b.risk_score : b.risk_score - a.risk_score);
    const page = filters.page ?? 1;
    const page_size = filters.page_size ?? 20;
    const total = items.length;
    return { data: items.slice((page - 1) * page_size, page * page_size), total, page, page_size, total_pages: Math.ceil(total / page_size) };
  }
  const { apiFetch } = await import('./client');
  const params = new URLSearchParams(Object.entries(filters).filter(([, v]) => v != null).map(([k, v]) => [k, String(v)]));
  return apiFetch<PaginatedResponse<RiskResult>>(`/risk?${params}`);
}

export async function getRiskResult(medicine_id: string): Promise<RiskResult | undefined> {
  if (USE_MOCKS) { await delay(100); return MOCK_RISK_RESULTS.find(r => r.medicine_id === medicine_id); }
  const { apiFetch } = await import('./client');
  return apiFetch<RiskResult>(`/risk/${medicine_id}`);
}

export async function runRiskAnalysis(): Promise<{ triggered: boolean; run_id: string }> {
  if (USE_MOCKS) { await delay(1500); return { triggered: true, run_id: 'RSK_RUN_' + Date.now() }; }
  const { apiFetch } = await import('./client');
  return apiFetch('/risk/run', { method: 'POST' });
}
