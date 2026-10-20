// api/transactions.ts
import type { Transaction, TransactionType, PaginatedResponse } from '../types/domain';
import { USE_MOCKS, delay } from './client';
import { MOCK_TRANSACTIONS } from '../mocks';

export interface TransactionFilters {
  medicine_id?: string;
  transaction_type?: TransactionType;
  date_from?: string;
  date_to?: string;
  search?: string;
  page?: number;
  page_size?: number;
}

export async function getTransactions(filters: TransactionFilters = {}): Promise<PaginatedResponse<Transaction>> {
  if (USE_MOCKS) {
    await delay();
    let items = [...MOCK_TRANSACTIONS];
    if (filters.medicine_id) items = items.filter(t => t.medicine_id === filters.medicine_id);
    if (filters.transaction_type) items = items.filter(t => t.transaction_type === filters.transaction_type);
    if (filters.date_from) items = items.filter(t => t.transaction_date >= filters.date_from!);
    if (filters.date_to) items = items.filter(t => t.transaction_date <= filters.date_to! + 'T23:59:59Z');
    if (filters.search) {
      const q = filters.search.toLowerCase();
      items = items.filter(t => t.medicine?.display_name.toLowerCase().includes(q) || t.reference_number?.toLowerCase().includes(q));
    }
    items.sort((a, b) => b.transaction_date.localeCompare(a.transaction_date));
    const page = filters.page ?? 1;
    const page_size = filters.page_size ?? 25;
    const total = items.length;
    return { data: items.slice((page - 1) * page_size, page * page_size), total, page, page_size, total_pages: Math.ceil(total / page_size) };
  }
  const { apiFetch } = await import('./client');
  const params = new URLSearchParams(Object.entries(filters).filter(([, v]) => v != null).map(([k, v]) => [k, String(v)]));
  return apiFetch<PaginatedResponse<Transaction>>(`/transactions?${params}`);
}

export interface NewTransactionPayload {
  medicine_id: string;
  transaction_type: TransactionType;
  quantity: number;
  reference_number?: string;
  notes?: string;
}

export async function createTransaction(payload: NewTransactionPayload): Promise<Transaction> {
  if (USE_MOCKS) {
    await delay(500);
    const { inventoryMap } = await import('../mocks');
    const inv = inventoryMap[payload.medicine_id];
    const sign = ['SALE', 'WASTAGE', 'ADJUSTMENT_NEGATIVE', 'TRANSFER_OUT'].includes(payload.transaction_type) ? -1 : 1;
    const stock_before = inv?.closing_stock ?? 0;
    const stock_after = stock_before + sign * payload.quantity;
    if (stock_after < 0) throw new Error('Insufficient stock — transaction would result in negative inventory.');
    return {
      id: 'TX_NEW_' + Date.now(),
      transaction_date: new Date().toISOString(),
      medicine_id: payload.medicine_id,
      transaction_type: payload.transaction_type,
      quantity: payload.quantity,
      stock_before,
      stock_after,
      reference_number: payload.reference_number,
      notes: payload.notes,
      created_by: 'current_user',
    };
  }
  const { apiFetch } = await import('./client');
  return apiFetch<Transaction>('/transactions', { method: 'POST', body: JSON.stringify(payload) });
}
