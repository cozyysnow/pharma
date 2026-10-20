// api/suppliers.ts
import type { Supplier } from '../types/domain';
import { USE_MOCKS, delay } from './client';
import { MOCK_SUPPLIERS } from '../mocks';

let _suppliers = [...MOCK_SUPPLIERS];

export async function getSuppliers(): Promise<Supplier[]> {
  if (USE_MOCKS) {
    await delay();
    return _suppliers;
  }
  const { apiFetch } = await import('./client');
  return apiFetch<Supplier[]>('/suppliers');
}

export async function getSupplier(supplier_id: string): Promise<Supplier | undefined> {
  if (USE_MOCKS) {
    await delay(100);
    return _suppliers.find(s => s.supplier_id === supplier_id);
  }
  const { apiFetch } = await import('./client');
  return apiFetch<Supplier>(`/suppliers/${supplier_id}`);
}

export async function createSupplier(data: Partial<Supplier>): Promise<Supplier> {
  if (USE_MOCKS) {
    await delay(400);
    const newSup: Supplier = {
      supplier_id: `SUP${String(_suppliers.length + 1).padStart(2, '0')}`,
      supplier_name: data.supplier_name || 'New Supplier',
      supplier_type: data.supplier_type || 'Wholesaler',
      city: data.city || 'Delhi',
      state: data.state || 'Delhi',
      lead_time_mean_days: data.lead_time_mean_days || 4.5,
      lead_time_sd_days: data.lead_time_sd_days || 1.2,
      on_time_probability: data.on_time_probability || 0.9,
      full_fill_probability: data.full_fill_probability || 0.92,
      payment_terms_days: data.payment_terms_days || 30,
      is_active: true,
      ...data,
    };
    _suppliers.push(newSup);
    return newSup;
  }
  const { apiFetch } = await import('./client');
  return apiFetch<Supplier>('/suppliers', { method: 'POST', body: JSON.stringify(data) });
}
