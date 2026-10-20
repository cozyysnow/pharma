import React, { useState } from 'react';
import { Download } from 'lucide-react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Button } from '../../components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Select } from '../../components/ui/Select';
import { DataTable, type ColumnDef } from '../../components/ui/DataTable';
import { Badge } from '../../components/ui/Badge';
import { useToast } from '../../components/feedback/ToastContext';

type ReportType =
  | 'RISK_SUMMARY'
  | 'DEMAND_ACCURACY'
  | 'REPLENISHMENT_LOG'
  | 'STOCK_VALUATION'
  | 'SUPPLIER_RELIABILITY'
  | 'WASTAGE_LOG'
  | 'COVERAGE_DISTRIBUTION';

interface ReportMeta {
  title: string;
  description: string;
  columns: ColumnDef<any>[];
  data: any[];
}

const REPORT_DEFINITIONS: Record<ReportType, ReportMeta> = {
  RISK_SUMMARY: {
    title: 'Stock-Out Risk Audit Summary',
    description: 'System-wide risk classifications across high, medium, and low categories with coverage metrics.',
    columns: [
      { key: 'category', header: 'Therapeutic Category' },
      { key: 'highRisk', header: 'High Risk SKUs', isNumeric: true, cell: (r) => <span className="text-rose-600 font-bold">{r.highRisk}</span> },
      { key: 'medRisk', header: 'Medium Risk SKUs', isNumeric: true, cell: (r) => <span className="text-amber-600 font-medium">{r.medRisk}</span> },
      { key: 'lowRisk', header: 'Low Risk SKUs', isNumeric: true, cell: (r) => <span className="text-emerald-600 font-medium">{r.lowRisk}</span> },
      { key: 'meanCoverage', header: 'Avg Coverage (Days)', isNumeric: true, cell: (r) => `${r.meanCoverage}d` },
      { key: 'actionRequired', header: 'Urgent Replenishments', isNumeric: true, cell: (r) => <Badge variant={r.actionRequired > 0 ? 'danger' : 'neutral'} size="sm">{r.actionRequired}</Badge> },
    ],
    data: [
      { id: 1, category: 'Antibiotics', highRisk: 3, medRisk: 4, lowRisk: 3, meanCoverage: 5.4, actionRequired: 3 },
      { id: 2, category: 'Cardiovascular', highRisk: 2, medRisk: 5, lowRisk: 5, meanCoverage: 8.2, actionRequired: 2 },
      { id: 3, category: 'Analgesics', highRisk: 1, medRisk: 2, lowRisk: 7, meanCoverage: 14.5, actionRequired: 1 },
      { id: 4, category: 'Antidiabetic', highRisk: 2, medRisk: 3, lowRisk: 4, meanCoverage: 6.8, actionRequired: 2 },
      { id: 5, category: 'Gastrointestinal', highRisk: 1, medRisk: 3, lowRisk: 6, meanCoverage: 11.2, actionRequired: 1 },
      { id: 6, category: 'Respiratory', highRisk: 2, medRisk: 4, lowRisk: 3, meanCoverage: 7.1, actionRequired: 2 },
      { id: 7, category: 'Dermatological', highRisk: 0, medRisk: 2, lowRisk: 6, meanCoverage: 16.0, actionRequired: 0 },
    ],
  },
  DEMAND_ACCURACY: {
    title: 'Demand Forecast Accuracy Report',
    description: 'Empirical multi-step backtest evaluation across ML candidates vs historical baseline models.',
    columns: [
      { key: 'model', header: 'Algorithm / Model' },
      { key: 'maeH1', header: 'MAE (h=1)', isNumeric: true },
      { key: 'maeH7', header: 'MAE (h=7)', isNumeric: true },
      { key: 'maeH14', header: 'MAE (h=14)', isNumeric: true },
      { key: 'maeH30', header: 'MAE (h=30)', isNumeric: true },
      { key: 'wape', header: 'WAPE', isNumeric: true },
      { key: 'status', header: 'Production Status', cell: (r) => <Badge variant={r.status === 'Active' ? 'success' : 'neutral'} size="sm">{r.status}</Badge> },
    ],
    data: [
      { id: 1, model: 'Gradient Boosting Regressor', maeH1: 8.07, maeH7: 8.92, maeH14: 9.45, maeH30: 10.12, wape: '14.1%', status: 'Active' },
      { id: 2, model: 'Random Forest (100 Trees)', maeH1: 8.45, maeH7: 9.15, maeH14: 9.80, maeH30: 10.45, wape: '15.0%', status: 'Candidate' },
      { id: 3, model: 'Ridge Linear Regression', maeH1: 9.10, maeH7: 9.85, maeH14: 10.20, maeH30: 10.95, wape: '16.2%', status: 'Candidate' },
      { id: 4, model: 'Baseline: 7-Day Rolling Mean', maeH1: 10.40, maeH7: 11.20, maeH14: 11.90, maeH30: 12.80, wape: '18.3%', status: 'Baseline' },
      { id: 5, model: 'Baseline: Lag-1 Naive', maeH1: 10.98, maeH7: 12.40, maeH14: 13.10, maeH30: 14.50, wape: '20.1%', status: 'Baseline' },
    ],
  },
  REPLENISHMENT_LOG: {
    title: 'Procurement & Replenishment Log',
    description: 'Audit log of recommended purchase orders, approvals, and order dispatch events.',
    columns: [
      { key: 'date', header: 'Approval Date' },
      { key: 'poRef', header: 'PO Reference' },
      { key: 'medicine', header: 'Medicine' },
      { key: 'supplier', header: 'Supplier' },
      { key: 'qty', header: 'Ordered Qty', isNumeric: true },
      { key: 'approvedBy', header: 'Approved By' },
      { key: 'status', header: 'Workflow State', cell: (r) => <Badge variant="info" size="sm">{r.status}</Badge> },
    ],
    data: [
      { id: 1, date: '2025-12-30', poRef: 'PO-88291', medicine: 'Amoxicillin 500mg', supplier: 'Apex Pharma Distributors', qty: 600, approvedBy: 'Rajesh Sharma', status: 'ORDER_PLACED' },
      { id: 2, date: '2025-12-28', poRef: 'PO-88104', medicine: 'Atorvastatin 20mg', supplier: 'Zenith Labs Healthcare', qty: 600, approvedBy: 'Rajesh Sharma', status: 'ORDER_PLACED' },
      { id: 3, date: '2025-12-25', poRef: 'PO-87950', medicine: 'Metformin 500mg', supplier: 'Yamuna Healthcare', qty: 800, approvedBy: 'Dr. Sarah Mitchell', status: 'ORDER_PLACED' },
      { id: 4, date: '2025-12-22', poRef: 'PO-87612', medicine: 'Azithromycin 250mg', supplier: 'Aravali Pharma', qty: 400, approvedBy: 'Rajesh Sharma', status: 'ORDER_PLACED' },
    ],
  },
  STOCK_VALUATION: {
    title: 'Category Inventory Valuation',
    description: 'Financial capitalization and unit valuation breakdown across warehouse categories.',
    columns: [
      { key: 'category', header: 'Category' },
      { key: 'skuCount', header: 'SKU Count', isNumeric: true },
      { key: 'totalUnits', header: 'Total Units in Stock', isNumeric: true },
      { key: 'totalCostInr', header: 'Inventory Value at Cost (₹)', isNumeric: true },
      { key: 'totalRetailInr', header: 'Retail Potential (₹)', isNumeric: true },
      { key: 'marginPct', header: 'Avg Gross Margin', isNumeric: true },
    ],
    data: [
      { id: 1, category: 'Antibiotics', skuCount: 10, totalUnits: '14,250', totalCostInr: '₹7,12,500', totalRetailInr: '₹10,68,750', marginPct: '33.3%' },
      { id: 2, category: 'Cardiovascular', skuCount: 12, totalUnits: '18,400', totalCostInr: '₹11,04,000', totalRetailInr: '₹16,56,000', marginPct: '33.3%' },
      { id: 3, category: 'Analgesics & Antipyretics', skuCount: 10, totalUnits: '24,500', totalCostInr: '₹4,90,000', totalRetailInr: '₹7,35,000', marginPct: '33.3%' },
      { id: 4, category: 'Antidiabetic', skuCount: 9, totalUnits: '16,800', totalCostInr: '₹8,40,000', totalRetailInr: '₹12,60,000', marginPct: '33.3%' },
      { id: 5, category: 'Gastrointestinal', skuCount: 10, totalUnits: '12,900', totalCostInr: '₹6,45,000', totalRetailInr: '₹9,67,500', marginPct: '33.3%' },
    ],
  },
  SUPPLIER_RELIABILITY: {
    title: 'Supplier Lead Time & Reliability Scorecard',
    description: 'Performance metrics for supplier lead time mean, variance, on-time delivery, and full-fill probabilities.',
    columns: [
      { key: 'supplier', header: 'Supplier Name' },
      { key: 'type', header: 'Distributor Type' },
      { key: 'leadTime', header: 'Mean Lead Time', isNumeric: true },
      { key: 'onTime', header: 'On-Time Fill Rate', isNumeric: true },
      { key: 'fullFill', header: 'Full Fill Rate', isNumeric: true },
      { key: 'reliability', header: 'Reliability Rating', cell: (r) => <Badge variant={r.reliability === 'High' ? 'success' : 'warning'} size="sm">{r.reliability}</Badge> },
    ],
    data: [
      { id: 1, supplier: 'Aravali Pharma Distributors', type: 'Wholesaler', leadTime: '2.9d (±1.6d)', onTime: '89%', fullFill: '96%', reliability: 'High' },
      { id: 2, supplier: 'Yamuna Healthcare Supplies', type: 'Wholesaler', leadTime: '4.9d (±1.7d)', onTime: '86%', fullFill: '95%', reliability: 'High' },
      { id: 3, supplier: 'Kurukshetra Medico Traders', type: 'Regional Distributor', leadTime: '4.7d (±0.8d)', onTime: '93%', fullFill: '94%', reliability: 'High' },
      { id: 4, supplier: 'Capital Drug House', type: 'Wholesaler', leadTime: '4.3d (±1.3d)', onTime: '89%', fullFill: '90%', reliability: 'High' },
      { id: 5, supplier: 'Himalaya Valley Pharma Supply', type: 'Manufacturer-Direct', leadTime: '5.8d (±1.6d)', onTime: '96%', fullFill: '92%', reliability: 'High' },
    ],
  },
  WASTAGE_LOG: {
    title: 'Expired & Wastage Register',
    description: 'Records of discarded, expired, and damaged pharmacy packages for compliance and loss tracking.',
    columns: [
      { key: 'date', header: 'Incident Date' },
      { key: 'medicine', header: 'Medicine' },
      { key: 'batch', header: 'Batch / Lot No.' },
      { key: 'units', header: 'Units Lost', isNumeric: true },
      { key: 'reason', header: 'Reason' },
      { key: 'value', header: 'Cost Value (₹)', isNumeric: true },
    ],
    data: [
      { id: 1, date: '2025-12-20', medicine: 'Insulin Glargine 100IU', batch: 'LOT-9921', units: 8, reason: 'Cold-chain thermal excursion', value: '₹4,800' },
      { id: 2, date: '2025-12-14', medicine: 'Amoxicillin Syrup', batch: 'LOT-8812', units: 12, reason: 'Packaging seal broken', value: '₹720' },
      { id: 3, date: '2025-11-28', medicine: 'Eye Drops Polymyxin', batch: 'LOT-7734', units: 15, reason: 'Past manufacturer expiry', value: '₹1,050' },
    ],
  },
  COVERAGE_DISTRIBUTION: {
    title: 'Stock Coverage Distribution',
    description: 'Stratification of inventory across critical, lean, adequate, and surplus days of cover.',
    columns: [
      { key: 'bucket', header: 'Days of Coverage Bucket' },
      { key: 'skuCount', header: 'Number of SKUs', isNumeric: true },
      { key: 'pct', header: 'Share of Portfolio', isNumeric: true },
      { key: 'assessment', header: 'Operational Assessment', cell: (r) => <Badge variant={r.assessment === 'Critical Deficit' ? 'danger' : r.assessment === 'Lean Buffer' ? 'warning' : 'success'} size="sm">{r.assessment}</Badge> },
    ],
    data: [
      { id: 1, bucket: '< 3 Days Coverage', skuCount: 8, pct: '9.4%', assessment: 'Critical Deficit' },
      { id: 2, bucket: '3 – 7 Days Coverage', skuCount: 14, pct: '16.5%', assessment: 'Lean Buffer' },
      { id: 3, bucket: '7 – 21 Days Coverage', skuCount: 42, pct: '49.4%', assessment: 'Adequate Buffer' },
      { id: 4, bucket: '21 – 45 Days Coverage', skuCount: 16, pct: '18.8%', assessment: 'Adequate Buffer' },
      { id: 5, bucket: '> 45 Days Coverage', skuCount: 5, pct: '5.9%', assessment: 'Surplus Holding' },
    ],
  },
};

export const ReportsPage: React.FC = () => {
  const { success } = useToast();
  const [reportType, setReportType] = useState<ReportType>('RISK_SUMMARY');

  const activeDef = REPORT_DEFINITIONS[reportType];

  const handleExportCSV = () => {
    const keys = activeDef.columns.map((c) => c.key);
    const headers = activeDef.columns.map((c) => c.header);
    const rows = activeDef.data.map((row) =>
      keys.map((k) => {
        const val = row[k];
        return typeof val === 'string' && val.includes(',') ? `"${val}"` : val ?? '';
      })
    );

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `${reportType.toLowerCase()}_${new Date().toISOString().substring(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    success('Report Exported', `Downloaded ${activeDef.title} CSV report.`);
  };

  return (
    <div>
      <PageHeader
        title="Audit & Operational Reports"
        subtitle="Generate and export structured analytical summaries of stockouts, replenishment accuracy, and consumption trends."
        actions={
          <Button
            variant="primary"
            size="sm"
            leftIcon={<Download className="w-4 h-4" />}
            onClick={handleExportCSV}
          >
            Export CSV ({activeDef.title})
          </Button>
        }
      />

      <Card className="p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div className="w-80">
            <Select
              label="Select Standard Report Type"
              value={reportType}
              onChange={(e) => setReportType(e.target.value as ReportType)}
            >
              <option value="RISK_SUMMARY">1. Stock-Out Risk Audit Summary</option>
              <option value="DEMAND_ACCURACY">2. Demand Forecast Accuracy Report</option>
              <option value="REPLENISHMENT_LOG">3. Procurement & Replenishment Log</option>
              <option value="STOCK_VALUATION">4. Category Inventory Valuation</option>
              <option value="SUPPLIER_RELIABILITY">5. Supplier Lead Time Reliability</option>
              <option value="WASTAGE_LOG">6. Expired & Wastage Log</option>
              <option value="COVERAGE_DISTRIBUTION">7. Stock Coverage Distribution</option>
            </Select>
          </div>

          <div className="text-xs text-slate-500 pt-5">
            Report Window: <span className="font-semibold text-slate-700">2021-01-01 to 2025-12-31</span> (Reference: 2025-12-31)
          </div>
        </div>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>{activeDef.title}</CardTitle>
            <p className="text-xs text-slate-500 mt-1">{activeDef.description}</p>
          </div>
          <Badge variant="info" size="sm">
            {activeDef.data.length} Records Preview
          </Badge>
        </CardHeader>
        <CardContent>
          <DataTable
            columns={activeDef.columns}
            data={activeDef.data}
            keyExtractor={(r) => r.id}
          />
        </CardContent>
      </Card>
    </div>
  );
};
