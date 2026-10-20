// api/datasets.ts
import { USE_MOCKS, delay, apiFetch } from './client';

export interface RawFile {
  filename: string;
  size_bytes: number;
  is_expected: boolean;
}

export interface DatasetStatus {
  raw_data_dir: string;
  raw_files_count: number;
  raw_files: RawFile[];
  is_imported: boolean;
  total_daily_records: number;
  total_medicines: number;
  total_suppliers: number;
  total_categories: number;
  last_import?: {
    import_id: string;
    file_name: string;
    row_count: string;
    status: string;
    imported_at: string;
  };
}

export interface PreviewData {
  filename: string;
  columns: Array<{ name: string; dtype: string }>;
  rows: string[][];
  sample_count: number;
  total_rows_estimate: number;
}

export interface ValidationCheck {
  category: string;
  check_name: string;
  passed: boolean;
  details: string;
  error_count: number;
}

export interface ValidationReport {
  overall_passed: boolean;
  files_checked: number;
  total_checks: number;
  passed_checks: number;
  failed_checks: number;
  quality_checks: ValidationCheck[];
}

export interface ImportResult {
  categories_count: number;
  suppliers_count: number;
  medicines_count: number;
  daily_records_count: number;
  inventory_synced_count: number;
  was_already_imported: boolean;
  duration_seconds: number;
  message: string;
}

export interface DatasetStatistics {
  total_daily_records: number;
  expected_daily_records: number;
  total_medicines: number;
  expected_medicines: number;
  total_suppliers: number;
  expected_suppliers: number;
  total_categories: number;
  expected_categories: number;
  date_range: {
    start_date: string | null;
    end_date: string | null;
  };
  stockout_next_7d_count: number;
  stockout_prevalence_pct: number;
  is_complete: boolean;
}

export async function getDatasetStatus(): Promise<DatasetStatus> {
  if (USE_MOCKS) {
    await delay(100);
    return {
      raw_data_dir: 'data/raw',
      raw_files_count: 14,
      raw_files: [
        { filename: 'stockout_prediction_dataset.csv', size_bytes: 19265902, is_expected: true },
        { filename: 'medicines.csv', size_bytes: 19563, is_expected: true },
        { filename: 'suppliers.csv', size_bytes: 1489, is_expected: true },
        { filename: 'categories.csv', size_bytes: 822, is_expected: true },
      ],
      is_imported: true,
      total_daily_records: 155210,
      total_medicines: 85,
      total_suppliers: 15,
      total_categories: 11,
    };
  }
  return apiFetch<DatasetStatus>('/datasets/status');
}

export async function getDatasetPreview(filename = 'stockout_prediction_dataset.csv', limit = 10): Promise<PreviewData> {
  if (USE_MOCKS) {
    await delay(150);
    return {
      filename,
      columns: [
        { name: 'record_id', dtype: 'str' },
        { name: 'date', dtype: 'date' },
        { name: 'medicine_id', dtype: 'str' },
        { name: 'closing_stock', dtype: 'int' },
        { name: 'units_demanded', dtype: 'int' },
        { name: 'stockout_next_7d', dtype: 'int' },
      ],
      rows: [
        ['REC000001', '2021-01-01', 'MED001', '994', '85', '0'],
        ['REC000002', '2021-01-02', 'MED001', '904', '90', '0'],
      ],
      sample_count: 2,
      total_rows_estimate: 155210,
    };
  }
  return apiFetch<PreviewData>(`/datasets/preview?filename=${encodeURIComponent(filename)}&limit=${limit}`);
}

export async function validateDataset(): Promise<ValidationReport> {
  if (USE_MOCKS) {
    await delay(300);
    return {
      overall_passed: true,
      files_checked: 11,
      total_checks: 9,
      passed_checks: 9,
      failed_checks: 0,
      quality_checks: [
        { category: 'Structure', check_name: 'Total daily records count (155,210)', passed: true, details: '155,210 rows', error_count: 0 },
        { category: 'Structure', check_name: 'Distinct medicines count (85)', passed: true, details: '85 medicines', error_count: 0 },
      ],
    };
  }
  return apiFetch<ValidationReport>('/datasets/validate', { method: 'POST' });
}

export async function importDataset(forceReload = false): Promise<ImportResult> {
  if (USE_MOCKS) {
    await delay(600);
    return {
      categories_count: 11,
      suppliers_count: 15,
      medicines_count: 85,
      daily_records_count: 155210,
      inventory_synced_count: 85,
      was_already_imported: false,
      duration_seconds: 4.5,
      message: 'Successfully imported 155,210 daily records',
    };
  }
  return apiFetch<ImportResult>('/datasets/import', {
    method: 'POST',
    body: JSON.stringify({ force_reload: forceReload }),
  });
}

export async function getDatasetStatistics(): Promise<DatasetStatistics> {
  if (USE_MOCKS) {
    await delay(100);
    return {
      total_daily_records: 155210,
      expected_daily_records: 155210,
      total_medicines: 85,
      expected_medicines: 85,
      total_suppliers: 15,
      expected_suppliers: 15,
      total_categories: 11,
      expected_categories: 11,
      date_range: { start_date: '2021-01-01', end_date: '2025-12-31' },
      stockout_next_7d_count: 29164,
      stockout_prevalence_pct: 18.79,
      is_complete: true,
    };
  }
  return apiFetch<DatasetStatistics>('/datasets/statistics');
}
