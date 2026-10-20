// ─── CATEGORY ──────────────────────────────────────────────────────────────────
export interface Category {
  category_id: string;
  category_name: string;
  description: string;
}

// ─── SUPPLIER ──────────────────────────────────────────────────────────────────
export type SupplierType =
  | 'Wholesaler'
  | 'Regional Distributor'
  | 'Manufacturer-Direct'
  | 'Specialist (Cold Chain)'
  | 'Cooperative';

export interface Supplier {
  supplier_id: string;
  supplier_name: string;
  supplier_type: SupplierType;
  city: string;
  state: string;
  lead_time_mean_days: number;
  lead_time_sd_days: number;
  on_time_probability: number;
  full_fill_probability: number;
  payment_terms_days: number;
  is_active: boolean;
}

// ─── MEDICINE ──────────────────────────────────────────────────────────────────
export type CompositionStatus =
  | 'VERIFIED_STANDARD_REFERENCE'
  | 'UNVERIFIED_REQUIRES_REVIEW'
  | (string & {});

export interface Medicine {
  medicine_id: string;
  generic_name: string;
  display_name: string;
  active_ingredients: string;
  strength: string;
  dosage_form: string;
  route: string;
  category_id: string;
  primary_supplier_id: string;
  unit_of_measure: string;
  pack_size: number;
  storage_condition: string;
  unit_cost_inr: number;
  unit_price_inr: number;
  composition_status: CompositionStatus;
  composition_note: string;
  is_active: boolean;
  category?: Category;
  primary_supplier?: Supplier;
}

export interface MedicineSupplier {
  medicine_id: string;
  supplier_id: string;
  is_primary: boolean;
  unit_cost_inr: number;
  lead_time_override_days?: number;
  supplier?: Supplier;
}

// ─── INVENTORY ────────────────────────────────────────────────────────────────
export type StockStatus =
  | 'CRITICAL'
  | 'LOW'
  | 'ADEQUATE'
  | 'OVERSTOCKED'
  | 'IN_STOCK'
  | 'LOW_STOCK'
  | 'OUT_OF_STOCK'
  | 'EXCESS'
  | (string & {});

export interface InventoryItem {
  medicine_id: string;
  date?: string;
  opening_stock: number;
  units_received?: number;
  units_sold?: number;
  units_received_today?: number;
  units_sold_today?: number;
  units_adjusted_today?: number;
  wastage_units: number;
  closing_stock: number;
  units_ordered_today: number;
  on_order_units: number;
  open_order_qty?: number;
  reorder_point: number;
  order_up_to_level: number;
  days_of_cover: number;
  coverage_days?: number;
  stock_status: StockStatus;
  safety_stock?: number;
  moq?: number;
  expected_daily_demand?: number;
  updated_at?: string;
  medicine?: Medicine;
}

// ─── TRANSACTION ──────────────────────────────────────────────────────────────
export type TransactionType =
  | 'SALE'
  | 'RECEIPT'
  | 'ADJUSTMENT_POSITIVE'
  | 'ADJUSTMENT_NEGATIVE'
  | 'WASTAGE'
  | 'RETURN_FROM_PATIENT'
  | 'TRANSFER_OUT'
  | (string & {});

export interface Transaction {
  id: string;
  transaction_date: string;
  medicine_id: string;
  transaction_type: TransactionType;
  quantity: number;
  unit_price_inr?: number;
  total_value_inr?: number;
  stock_before: number;
  stock_after: number;
  reference_number?: string;
  notes?: string;
  created_by: string;
  medicine?: Medicine;
}

// ─── DAILY RECORD ─────────────────────────────────────────────────────────────
export interface DailyRecord {
  record_id: string;
  date: string;
  medicine_id: string;
  category_id: string;
  supplier_id: string;
  closing_stock: number;
  on_order_units: number;
  reorder_point: number;
  units_demanded: number;
  units_sold: number;
  sales_7d_avg: number;
  sales_30d_avg: number;
  days_of_cover: number;
  stock_position_cover_days: number;
  days_since_last_receipt: number;
  stockout_days_last_30d: number;
  supplier_lead_time_mean_days: number;
  supplier_full_fill_probability: number;
  supplier_disruption_active: boolean;
  unit_price_inr: number;
  stockout_today: boolean;
  stockout_next_7d: boolean;
}

// ─── FORECAST ─────────────────────────────────────────────────────────────────
export type ForecastModel = 'XGBoost' | 'LSTM' | 'Prophet' | 'SARIMA' | 'Ensemble' | 'GRADIENT_BOOSTING' | 'RANDOM_FOREST' | 'ARIMA' | 'EXPONENTIAL_SMOOTHING' | 'LINEAR_REGRESSION' | (string & {});
export type ForecastHorizon = 7 | 14 | 30 | 60 | 90;

export interface ForecastPoint {
  date: string;
  predicted_demand: number;
  lower_bound: number;
  upper_bound: number;
  is_forecast: boolean;
}

export interface ForecastResult {
  id: string;
  medicine_id: string;
  model: ForecastModel;
  horizon_days: ForecastHorizon;
  run_date: string;
  points: ForecastPoint[];
  mae: number;
  rmse: number;
  mape: number;
  medicine?: Medicine;
}

// ─── RISK ─────────────────────────────────────────────────────────────────────
export type RiskLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | (string & {});

export interface RiskFactor {
  factor: string;
  value: string | number;
  contribution: number;
  explanation: string;
}

export interface RiskResult {
  id: string;
  medicine_id: string;
  computed_at: string;
  risk_score: number;
  risk_level: RiskLevel;
  stockout_probability_7d: number;
  stockout_probability_14d: number;
  stockout_probability_30d: number;
  days_of_cover: number;
  reorder_point: number;
  avg_daily_demand: number;
  supplier_reliability: number;
  factors: RiskFactor[];
  explanation?: string;
  medicine?: Medicine;
}

// ─── REPLENISHMENT ────────────────────────────────────────────────────────────
export type RecommendationStatus = 'PENDING' | 'ACCEPTED' | 'ORDERED' | 'DISMISSED' | (string & {});

export interface Recommendation {
  id: string;
  medicine_id: string;
  supplier_id: string;
  generated_at: string;
  status: RecommendationStatus;
  recommended_quantity: number;
  recommended_order_quantity?: number;
  estimated_cost_inr: number;
  urgency_level: RiskLevel;
  is_urgent?: boolean;
  reorder_point: number;
  current_stock: number;
  days_of_cover: number;
  lead_time_days: number;
  rationale: string;
  required_stock?: number;
  moq_applied?: boolean;
  open_order_qty?: number;
  accepted_by?: string;
  accepted_at?: string;
  ordered_at?: string;
  dismissed_by?: string;
  dismissed_at?: string;
  dismiss_reason?: string;
  medicine?: Medicine;
  supplier?: Supplier;
}

// ─── ALERT ────────────────────────────────────────────────────────────────────
export type AlertSeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO' | 'WARNING' | (string & {});
export type AlertType = 'STOCKOUT_RISK' | 'LOW_STOCK' | 'SUPPLIER_DISRUPTION' | 'EXPIRY_APPROACHING' | 'DEMAND_SPIKE' | 'FORECAST_DEVIATION' | (string & {});
export type AlertStatus = 'UNREAD' | 'ACKNOWLEDGED' | 'RESOLVED' | 'DISMISSED' | (string & {});

export interface Alert {
  id: string;
  alert_type: AlertType;
  severity: AlertSeverity;
  status: AlertStatus;
  medicine_id?: string;
  supplier_id?: string;
  title: string;
  message: string;
  created_at: string;
  acknowledged_at?: string;
  acknowledged_by?: string;
  resolved_at?: string;
  resolved_by?: string;
  medicine?: Medicine;
  supplier?: Supplier;
}

// ─── DATASET IMPORT ───────────────────────────────────────────────────────────
export type ImportStatus = 'PENDING' | 'VALIDATING' | 'MAPPING' | 'PREPROCESSING' | 'IMPORTING' | 'COMPLETED' | 'FAILED';
export type DatasetSource = 'FILE_UPLOAD' | 'API_SYNC' | 'MANUAL';

export interface DatasetImport {
  id: string;
  filename: string;
  source: DatasetSource;
  status: ImportStatus;
  row_count?: number;
  error_count?: number;
  warning_count?: number;
  started_at: string;
  completed_at?: string;
  imported_by: string;
  notes?: string;
}

// ─── ML RUN ───────────────────────────────────────────────────────────────────
export type MlRunStatus = 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED';

export interface MlRun {
  id: string;
  model: ForecastModel;
  triggered_by: string;
  started_at: string;
  completed_at?: string;
  status: MlRunStatus;
  medicines_processed: number;
  mae?: number;
  rmse?: number;
  mape?: number;
  notes?: string;
}

// ─── APP SETTINGS ─────────────────────────────────────────────────────────────
export interface StockThresholds {
  critical_days: number;
  low_days: number;
  overstock_days: number;
  default_safety_stock_factor: number;
}

export interface ModelSettings {
  primary_model: ForecastModel;
  ensemble_models: ForecastModel[];
  default_horizon_days: ForecastHorizon;
  retrain_schedule: string;
  min_history_days: number;
}

export interface AppSettings {
  pharmacy_name: string;
  reference_date: string;
  currency: string;
  thresholds: StockThresholds;
  model: ModelSettings;
  notification_email?: string;
}

// ─── PAGINATION ───────────────────────────────────────────────────────────────
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ─── DASHBOARD ────────────────────────────────────────────────────────────────
export interface DashboardKpis {
  total_medicines: number;
  active_medicines: number;
  critical_stock: number;
  low_stock: number;
  adequate_stock: number;
  overstocked: number;
  stockout_count: number;
  pending_recommendations: number;
  unread_alerts: number;
  total_inventory_value_inr: number;
  avg_coverage_days: number;
  high_risk_count: number;
}
