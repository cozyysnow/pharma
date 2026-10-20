// api/replenishment.ts
import type { Recommendation, RecommendationStatus } from '../types/domain';
import { USE_MOCKS, delay } from './client';
import { MOCK_RECOMMENDATIONS } from '../mocks';

let _recs = [...MOCK_RECOMMENDATIONS];

export async function getRecommendations(status?: RecommendationStatus): Promise<Recommendation[]> {
  if (USE_MOCKS) {
    await delay();
    return status ? _recs.filter(r => r.status === status) : _recs;
  }
  const { apiFetch } = await import('./client');
  const params = status ? `?status=${status}` : '';
  return apiFetch<Recommendation[]>(`/replenishment${params}`);
}

export async function acceptRecommendation(id: string, by: string): Promise<Recommendation> {
  if (USE_MOCKS) {
    await delay(500);
    const rec = _recs.find(r => r.id === id)!;
    Object.assign(rec, { status: 'ACCEPTED', accepted_by: by, accepted_at: new Date().toISOString() });
    return rec;
  }
  const { apiFetch } = await import('./client');
  return apiFetch<Recommendation>(`/replenishment/${id}/accept`, { method: 'POST' });
}

export async function markOrdered(id: string): Promise<Recommendation> {
  if (USE_MOCKS) {
    await delay(500);
    const rec = _recs.find(r => r.id === id)!;
    Object.assign(rec, { status: 'ORDERED', ordered_at: new Date().toISOString() });
    return rec;
  }
  const { apiFetch } = await import('./client');
  return apiFetch<Recommendation>(`/replenishment/${id}/order-placed`, { method: 'POST' });
}

export async function dismissRecommendation(id: string, by: string, reason: string): Promise<Recommendation> {
  if (USE_MOCKS) {
    await delay(500);
    const rec = _recs.find(r => r.id === id)!;
    Object.assign(rec, { status: 'DISMISSED', dismissed_by: by, dismissed_at: new Date().toISOString(), dismiss_reason: reason });
    return rec;
  }
  const { apiFetch } = await import('./client');
  return apiFetch<Recommendation>(`/replenishment/${id}/dismiss`, { method: 'POST', body: JSON.stringify({ reason }) });
}
