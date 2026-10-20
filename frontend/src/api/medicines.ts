// api/medicines.ts
import type { Medicine, PaginatedResponse } from '../types/domain';
import { USE_MOCKS, delay } from './client';
import { MOCK_MEDICINES } from '../mocks';

export interface MedicineFilters {
  search?: string;
  category_id?: string;
  supplier_id?: string;
  is_active?: boolean;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_dir?: 'asc' | 'desc';
}

export async function getMedicines(filters: MedicineFilters = {}): Promise<PaginatedResponse<Medicine>> {
  if (USE_MOCKS) {
    await delay();
    let items = [...MOCK_MEDICINES];
    if (filters.search) {
      const q = filters.search.toLowerCase();
      items = items.filter(m => m.display_name.toLowerCase().includes(q) || m.generic_name.toLowerCase().includes(q) || m.medicine_id.toLowerCase().includes(q));
    }
    if (filters.category_id) items = items.filter(m => m.category_id === filters.category_id);
    if (filters.supplier_id) items = items.filter(m => m.primary_supplier_id === filters.supplier_id);
    if (filters.is_active !== undefined) items = items.filter(m => m.is_active === filters.is_active);
    const page = filters.page ?? 1;
    const page_size = filters.page_size ?? 20;
    const total = items.length;
    return { data: items.slice((page - 1) * page_size, page * page_size), total, page, page_size, total_pages: Math.ceil(total / page_size) };
  }
  const { apiFetch } = await import('./client');
  const params = new URLSearchParams(Object.entries(filters).filter(([, v]) => v != null).map(([k, v]) => [k, String(v)]));
  return apiFetch<PaginatedResponse<Medicine>>(`/medicines?${params}`);
}

export async function getMedicine(medicine_id: string): Promise<Medicine | undefined> {
  if (USE_MOCKS) { await delay(100); return MOCK_MEDICINES.find(m => m.medicine_id === medicine_id); }
  const { apiFetch } = await import('./client');
  return apiFetch<Medicine>(`/medicines/${medicine_id}`);
}

export async function createMedicine(data: Partial<Medicine>): Promise<Medicine> {
  if (USE_MOCKS) { await delay(500); return { ...data, medicine_id: 'MED_NEW', is_active: true } as Medicine; }
  const { apiFetch } = await import('./client');
  return apiFetch<Medicine>('/medicines', { method: 'POST', body: JSON.stringify(data) });
}

export async function updateMedicine(medicine_id: string, data: Partial<Medicine>): Promise<Medicine> {
  if (USE_MOCKS) { await delay(500); return { ...MOCK_MEDICINES.find(m => m.medicine_id === medicine_id)!, ...data }; }
  const { apiFetch } = await import('./client');
  return apiFetch<Medicine>(`/medicines/${medicine_id}`, { method: 'PATCH', body: JSON.stringify(data) });
}

export async function deactivateMedicine(medicine_id: string): Promise<void> {
  if (USE_MOCKS) { await delay(500); return; }
  const { apiFetch } = await import('./client');
  return apiFetch<void>(`/medicines/${medicine_id}/deactivate`, { method: 'POST' });
}
