// MOCK DATA — dashboard KPIs, dataset imports, ML runs, settings
import type { DashboardKpis, DatasetImport, MlRun, AppSettings } from '../types/domain';

/* MOCK */
export const MOCK_DASHBOARD_KPIS: DashboardKpis = {
  total_medicines: 85,
  active_medicines: 85,
  critical_stock: 8,
  low_stock: 14,
  adequate_stock: 57,
  overstocked: 6,
  stockout_count: 3,
  pending_recommendations: 5,
  unread_alerts: 8,
  total_inventory_value_inr: 2847632,
  avg_coverage_days: 28.4,
  high_risk_count: 12,
};

export const MOCK_DATASET_IMPORTS: DatasetImport[] = [
  { id: 'DS001', filename: 'inventory_daily_2025_q4.csv', source: 'FILE_UPLOAD', status: 'COMPLETED', row_count: 7735, error_count: 0, warning_count: 3, started_at: '2025-12-31T00:05:00Z', completed_at: '2025-12-31T00:08:42Z', imported_by: 'Dr. Admin', notes: 'Q4 2025 inventory snapshot import' },
  { id: 'DS002', filename: 'demand_sales_dec2025.csv', source: 'FILE_UPLOAD', status: 'COMPLETED', row_count: 2635, error_count: 0, warning_count: 0, started_at: '2025-12-31T01:00:00Z', completed_at: '2025-12-31T01:02:11Z', imported_by: 'mgr_01', notes: 'December 2025 daily demand data' },
  { id: 'DS003', filename: 'stockout_predictions_dec31.csv', source: 'API_SYNC', status: 'COMPLETED', row_count: 85, error_count: 0, warning_count: 0, started_at: '2025-12-31T23:55:00Z', completed_at: '2025-12-31T23:55:30Z', imported_by: 'system', notes: 'Auto-sync from ML pipeline' },
  { id: 'DS004', filename: 'replenishment_orders_2025.csv', source: 'FILE_UPLOAD', status: 'COMPLETED', row_count: 1248, error_count: 2, warning_count: 12, started_at: '2025-12-28T09:00:00Z', completed_at: '2025-12-28T09:03:55Z', imported_by: 'Dr. Admin', notes: 'Annual replenishment order archive' },
  { id: 'DS005', filename: 'manual_correction_dec30.csv', source: 'MANUAL', status: 'FAILED', row_count: undefined, error_count: 14, warning_count: 0, started_at: '2025-12-30T15:00:00Z', completed_at: '2025-12-30T15:00:42Z', imported_by: 'staff_01', notes: 'Schema validation failed — missing required columns' },
];

export const MOCK_ML_RUNS: MlRun[] = [
  { id: 'MLR001', model: 'XGBoost', triggered_by: 'system_scheduler', started_at: '2025-12-31T23:00:00Z', completed_at: '2025-12-31T23:08:22Z', status: 'COMPLETED', medicines_processed: 85, mae: 6.82, rmse: 10.41, mape: 0.093, notes: 'Nightly scheduled forecast run' },
  { id: 'MLR002', model: 'Ensemble', triggered_by: 'Dr. Admin', started_at: '2025-12-30T10:00:00Z', completed_at: '2025-12-30T10:22:15Z', status: 'COMPLETED', medicines_processed: 85, mae: 5.94, rmse: 9.12, mape: 0.081, notes: 'Manual ensemble run triggered post data correction' },
  { id: 'MLR003', model: 'Prophet', triggered_by: 'system_scheduler', started_at: '2025-12-29T23:00:00Z', completed_at: '2025-12-29T23:05:48Z', status: 'COMPLETED', medicines_processed: 85, mae: 8.12, rmse: 12.67, mape: 0.112 },
  { id: 'MLR004', model: 'LSTM', triggered_by: 'mgr_01', started_at: '2025-12-28T14:00:00Z', status: 'FAILED', medicines_processed: 0, notes: 'Training job OOM — insufficient GPU memory' },
];

export const MOCK_APP_SETTINGS: AppSettings = {
  pharmacy_name: 'District General Hospital Pharmacy',
  reference_date: '2025-12-31',
  currency: 'INR',
  thresholds: {
    critical_days: 7,
    low_days: 14,
    overstock_days: 90,
    default_safety_stock_factor: 1.5,
  },
  model: {
    primary_model: 'XGBoost',
    ensemble_models: ['XGBoost', 'Prophet', 'SARIMA'],
    default_horizon_days: 30,
    retrain_schedule: '0 23 * * *',
    min_history_days: 90,
  },
  notification_email: 'pharmacy@dgh.hospital.in',
};

// Category distribution for charts
export const MOCK_CATEGORY_DISTRIBUTION = [
  { name: 'Analgesics & Antipyretics', count: 8, value: 8, criticalCount: 2 },
  { name: 'Antibiotics', count: 12, value: 12, criticalCount: 1 },
  { name: 'Cardiovascular', count: 14, value: 14, criticalCount: 1 },
  { name: 'Antidiabetics', count: 6, value: 6, criticalCount: 1 },
  { name: 'Gastrointestinal', count: 8, value: 8, criticalCount: 0 },
  { name: 'Respiratory & Allergy', count: 7, value: 7, criticalCount: 0 },
  { name: 'Antifungals & Antiparasitics', count: 7, value: 7, criticalCount: 1 },
  { name: 'Neurology & Psychiatry', count: 8, value: 8, criticalCount: 2 },
  { name: 'Vitamins & Supplements', count: 7, value: 7, criticalCount: 0 },
  { name: 'Dermatology & Topicals', count: 6, value: 6, criticalCount: 0 },
  { name: 'Endocrine & Others', count: 7, value: 7, criticalCount: 0 },
];

// Demand trend (30 days)
export const MOCK_DEMAND_TREND = Array.from({ length: 30 }, (_, i) => {
  const date = new Date('2025-12-01');
  date.setDate(date.getDate() + i);
  const base = 1850;
  const noise = Math.sin(i * 0.4) * 120 + Math.random() * 80;
  return {
    date: date.toISOString().slice(0, 10),
    demand: Math.round(base + noise),
    sales: Math.round((base + noise) * 0.95),
  };
});
