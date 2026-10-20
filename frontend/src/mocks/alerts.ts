// MOCK DATA — alerts
import type { Alert } from '../types/domain';
import { medicineMap } from './medicines';
import { supplierMap } from './suppliers';

/* MOCK */
export const MOCK_ALERTS: Alert[] = [
  { id: 'ALT001', alert_type: 'STOCKOUT_RISK', severity: 'CRITICAL', status: 'UNREAD', medicine_id: 'MED033', title: 'Critical Stockout Risk: Metformin 500mg', message: 'Metformin 500 mg Tablet has only 4.2 days of cover remaining, below the 7-day critical threshold. Immediate replenishment action required.', created_at: '2025-12-31T08:00:00Z' },
  { id: 'ALT002', alert_type: 'STOCKOUT_RISK', severity: 'CRITICAL', status: 'UNREAD', medicine_id: 'MED009', title: 'Critical Stockout Risk: Amoxicillin 500mg', message: 'Amoxicillin 500 mg Capsule has only 3.8 days of cover. Stock may run out before next scheduled delivery.', created_at: '2025-12-31T08:05:00Z' },
  { id: 'ALT003', alert_type: 'LOW_STOCK', severity: 'HIGH', status: 'UNREAD', medicine_id: 'MED001', title: 'Low Stock: Paracetamol 500mg', message: 'Paracetamol 500 mg Tablet has 9.1 days of cover, approaching the 7-day critical threshold.', created_at: '2025-12-31T08:10:00Z' },
  { id: 'ALT004', alert_type: 'SUPPLIER_DISRUPTION', severity: 'HIGH', status: 'UNREAD', supplier_id: 'SUP09', title: 'Supplier Disruption: Ganga Plains Pharma', message: 'Active disruption event reported for Ganga Plains Pharma (SUP09). Deliveries may be delayed by 5-10 days. Review affected medicines and consider alternate sourcing.', created_at: '2025-12-30T14:00:00Z' },
  { id: 'ALT005', alert_type: 'DEMAND_SPIKE', severity: 'HIGH', status: 'UNREAD', medicine_id: 'MED003', title: 'Demand Spike Detected: Ibuprofen 400mg', message: 'Ibuprofen 400 mg Tablet demand increased 47% above 30-day average over the past 7 days. Review inventory and consider early replenishment.', created_at: '2025-12-30T09:00:00Z' },
  { id: 'ALT006', alert_type: 'LOW_STOCK', severity: 'MEDIUM', status: 'UNREAD', medicine_id: 'MED020', title: 'Low Stock: Atenolol 50mg', message: 'Atenolol 50 mg Tablet has 11.5 days of cover, within the low stock range (7-14 days).', created_at: '2025-12-31T08:15:00Z' },
  { id: 'ALT007', alert_type: 'EXPIRY_APPROACHING', severity: 'MEDIUM', status: 'ACKNOWLEDGED', medicine_id: 'MED052', title: 'Expiry Approaching: Clotrimazole Cream', message: 'Clotrimazole 1% Cream batch #B2025-110 expires on 2026-03-15. 42 tubes in stock. Consider expedited dispensing or return.', created_at: '2025-12-28T10:00:00Z', acknowledged_at: '2025-12-29T09:00:00Z', acknowledged_by: 'Dr. Admin' },
  { id: 'ALT008', alert_type: 'STOCKOUT_RISK', severity: 'HIGH', status: 'ACKNOWLEDGED', medicine_id: 'MED079', title: 'High Risk: Levothyroxine 50mcg', message: 'Levothyroxine 50 mcg Tablet (critical medication) shows 68% stockout probability in next 14 days.', created_at: '2025-12-29T08:00:00Z', acknowledged_at: '2025-12-30T11:00:00Z', acknowledged_by: 'mgr_01' },
  { id: 'ALT009', alert_type: 'LOW_STOCK', severity: 'LOW', status: 'RESOLVED', medicine_id: 'MED066', title: 'Low Stock Resolved: Folic Acid 5mg', message: 'Folic Acid 5 mg Tablet stock has been replenished. Coverage now 28.5 days.', created_at: '2025-12-20T08:00:00Z', resolved_at: '2025-12-22T10:00:00Z', resolved_by: 'mgr_01' },
  { id: 'ALT010', alert_type: 'DEMAND_SPIKE', severity: 'INFO', status: 'DISMISSED', medicine_id: 'MED069', title: 'Demand Note: Vitamin C Seasonal Uptick', message: 'Ascorbic Acid 500 mg tablet demand increased 22% week-on-week. Within expected seasonal variation for winter months.', created_at: '2025-12-27T08:00:00Z' },
  { id: 'ALT011', alert_type: 'STOCKOUT_RISK', severity: 'CRITICAL', status: 'UNREAD', medicine_id: 'MED062', title: 'Critical Stockout Risk: Alprazolam 0.25mg', message: 'Alprazolam 0.25 mg Tablet (Schedule H) has 2.1 days of cover. Controlled substance — requires pharmacist authorization for emergency reorder.', created_at: '2025-12-31T07:00:00Z' },
  { id: 'ALT012', alert_type: 'SUPPLIER_DISRUPTION', severity: 'MEDIUM', status: 'UNREAD', supplier_id: 'SUP06', title: 'Lead Time Increase: Satluj Generics Direct', message: 'Satluj Generics Direct (SUP06) has reported manufacturing delays. Lead times may increase by 3-5 days for affected products through January 2026.', created_at: '2025-12-30T16:00:00Z' },
].map(a => ({
  ...a,
  medicine: a.medicine_id ? medicineMap[a.medicine_id] : undefined,
  supplier: a.supplier_id ? supplierMap[a.supplier_id] : undefined,
}));
