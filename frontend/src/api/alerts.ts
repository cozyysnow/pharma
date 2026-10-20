// api/alerts.ts
import type { Alert, AlertStatus, AlertSeverity, AlertType } from '../types/domain';
import { USE_MOCKS, delay } from './client';
import { MOCK_ALERTS } from '../mocks';

let _alerts = [...MOCK_ALERTS];

export interface AlertFilters {
  status?: AlertStatus;
  severity?: AlertSeverity;
  alert_type?: AlertType;
  medicine_id?: string;
}

export async function getAlerts(filters: AlertFilters = {}): Promise<Alert[]> {
  if (USE_MOCKS) {
    await delay();
    let items = [..._alerts];
    if (filters.status) items = items.filter(a => a.status === filters.status);
    if (filters.severity) items = items.filter(a => a.severity === filters.severity);
    if (filters.alert_type) items = items.filter(a => a.alert_type === filters.alert_type);
    if (filters.medicine_id) items = items.filter(a => a.medicine_id === filters.medicine_id);
    return items.sort((a, b) => b.created_at.localeCompare(a.created_at));
  }
  const { apiFetch } = await import('./client');
  const params = new URLSearchParams(Object.entries(filters).filter(([, v]) => v != null).map(([k, v]) => [k, String(v)]));
  return apiFetch<Alert[]>(`/alerts?${params}`);
}

export async function acknowledgeAlert(id: string, by: string): Promise<Alert> {
  if (USE_MOCKS) {
    await delay(300);
    const alert = _alerts.find(a => a.id === id)!;
    Object.assign(alert, { status: 'ACKNOWLEDGED', acknowledged_at: new Date().toISOString(), acknowledged_by: by });
    return alert;
  }
  const { apiFetch } = await import('./client');
  return apiFetch<Alert>(`/alerts/${id}/acknowledge`, { method: 'POST' });
}

export async function resolveAlert(id: string, by: string): Promise<Alert> {
  if (USE_MOCKS) {
    await delay(300);
    const alert = _alerts.find(a => a.id === id)!;
    Object.assign(alert, { status: 'RESOLVED', resolved_at: new Date().toISOString(), resolved_by: by });
    return alert;
  }
  const { apiFetch } = await import('./client');
  return apiFetch<Alert>(`/alerts/${id}/resolve`, { method: 'POST' });
}

export async function dismissAlert(id: string): Promise<Alert> {
  if (USE_MOCKS) {
    await delay(300);
    const alert = _alerts.find(a => a.id === id)!;
    Object.assign(alert, { status: 'DISMISSED' });
    return alert;
  }
  const { apiFetch } = await import('./client');
  return apiFetch<Alert>(`/alerts/${id}/dismiss`, { method: 'POST' });
}

export async function bulkAcknowledge(ids: string[], by: string): Promise<void> {
  if (USE_MOCKS) {
    await delay(500);
    _alerts.filter(a => ids.includes(a.id)).forEach(a => Object.assign(a, { status: 'ACKNOWLEDGED', acknowledged_at: new Date().toISOString(), acknowledged_by: by }));
    return;
  }
  const { apiFetch } = await import('./client');
  return apiFetch('/alerts/bulk-acknowledge', { method: 'POST', body: JSON.stringify({ ids }) });
}

export function getUnreadCount(): number {
  return _alerts.filter(a => a.status === 'UNREAD').length;
}
