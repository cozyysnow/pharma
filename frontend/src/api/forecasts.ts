// api/forecasts.ts
import type { ForecastResult, ForecastHorizon, ForecastModel } from '../types/domain';
import { USE_MOCKS, delay } from './client';
import { MOCK_FORECASTS } from '../mocks';

export async function getForecast(medicine_id: string, horizon?: ForecastHorizon, model?: ForecastModel): Promise<ForecastResult | undefined> {
  if (USE_MOCKS) {
    await delay(400);
    return MOCK_FORECASTS.find(f => f.medicine_id === medicine_id && (!model || f.model === model));
  }
  const { apiFetch } = await import('./client');
  const params = new URLSearchParams();
  if (horizon) params.set('horizon', String(horizon));
  if (model) params.set('model', model);
  return apiFetch<ForecastResult>(`/forecasts/${medicine_id}?${params}`);
}

export async function getAllForecasts(): Promise<ForecastResult[]> {
  if (USE_MOCKS) { await delay(); return MOCK_FORECASTS; }
  const { apiFetch } = await import('./client');
  return apiFetch<ForecastResult[]>('/forecasts');
}

export async function triggerMLTraining(): Promise<{ message: string; status: string }> {
  if (USE_MOCKS) {
    await delay(500);
    return { message: 'ML Training started in background', status: 'RUNNING' };
  }
  const { apiFetch } = await import('./client');
  return apiFetch<{ message: string; status: string }>('/ml/train', { method: 'POST' });
}

export async function getMLRuns(): Promise<any[]> {
  if (USE_MOCKS) {
    await delay(300);
    return [];
  }
  const { apiFetch } = await import('./client');
  return apiFetch<any[]>('/ml/runs');
}

export async function generateForecasts(): Promise<{ message: string }> {
  if (USE_MOCKS) {
    await delay(500);
    return { message: 'Forecasts generated successfully' };
  }
  const { apiFetch } = await import('./client');
  return apiFetch<{ message: string }>('/forecasts/generate', { method: 'POST' });
}
