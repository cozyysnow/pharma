import type { Category } from '../types/domain';
import { apiFetch, delay, USE_MOCKS } from './client';
import { MOCK_CATEGORIES } from '../mocks';

let _cachedCategories: Category[] | null = null;

export async function getCategories(): Promise<Category[]> {
  if (USE_MOCKS) {
    await delay(100);
    return MOCK_CATEGORIES;
  }
  if (_cachedCategories) {
    return _cachedCategories;
  }
  const data = await apiFetch<Category[]>('/categories');
  _cachedCategories = data;
  return data;
}

