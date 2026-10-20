// api/inventory.ts
import type { InventoryItem, PaginatedResponse, StockStatus } from '../types/domain';
import { USE_MOCKS, delay } from './client';
import { MOCK_INVENTORY } from '../mocks';

export interface InventoryFilters {
  search?: string;
  category_id?: string;
  supplier_id?: string;
  stock_status?: StockStatus;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_dir?: 'asc' | 'desc';
}

export async function getInventory(filters: InventoryFilters = {}): Promise<PaginatedResponse<InventoryItem>> {
  if (USE_MOCKS) {
    await delay();
    let items = [...MOCK_INVENTORY];
    if (filters.search) {
      const q = filters.search.toLowerCase();
      items = items.filter(i => i.medicine?.display_name.toLowerCase().includes(q) || i.medicine?.generic_name.toLowerCase().includes(q) || i.medicine_id.toLowerCase().includes(q));
    }
    if (filters.category_id) items = items.filter(i => i.medicine?.category_id === filters.category_id);
    if (filters.supplier_id) items = items.filter(i => i.medicine?.primary_supplier_id === filters.supplier_id);
    if (filters.stock_status) items = items.filter(i => i.stock_status === filters.stock_status);
    if (filters.sort_by) {
      const dir = filters.sort_dir === 'desc' ? -1 : 1;
      items.sort((a, b) => {
        const aVal = ((a as any)[filters.sort_by!] ?? (a.medicine as any)?.[filters.sort_by!]) as any;
        const bVal = ((b as any)[filters.sort_by!] ?? (b.medicine as any)?.[filters.sort_by!]) as any;
        return aVal < bVal ? -dir : aVal > bVal ? dir : 0;
      });
    }
    const page = filters.page ?? 1;
    const page_size = filters.page_size ?? 20;
    const total = items.length;
    return { data: items.slice((page - 1) * page_size, page * page_size), total, page, page_size, total_pages: Math.ceil(total / page_size) };
  }
  const { apiFetch } = await import('./client');
  const params = new URLSearchParams(Object.entries(filters).filter(([, v]) => v != null).map(([k, v]) => [k, String(v)]));
  return apiFetch<PaginatedResponse<InventoryItem>>(`/inventory?${params}`);
}

export async function getInventoryItem(medicine_id: string): Promise<InventoryItem | undefined> {
  if (USE_MOCKS) { await delay(100); return MOCK_INVENTORY.find(i => i.medicine_id === medicine_id); }
  const { apiFetch } = await import('./client');
  return apiFetch<InventoryItem>(`/inventory/${medicine_id}`);
}
