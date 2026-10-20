import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  FileText,
  Calculator,
  History,
  TrendingUp,
  ShieldCheck,
} from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Tabs, TabList, TabTrigger, TabContent } from '../../components/ui/Tabs';
import { RiskBadge } from '../../components/domain/RiskBadge';
import { StockStatusBadge } from '../../components/domain/StockStatusBadge';
import { LineForecastChart } from '../../components/charts/LineForecastChart';
import { DataTable, type ColumnDef } from '../../components/ui/DataTable';
import { Badge } from '../../components/ui/Badge';
import { useToast } from '../../components/feedback/ToastContext';
import { getMedicine } from '../../api/medicines';
import { getInventoryItem } from '../../api/inventory';
import { getForecast } from '../../api/forecasts';
import { getRiskResult } from '../../api/risk';
import { getTransactions } from '../../api/transactions';
import type { Medicine, InventoryItem, ForecastResult, RiskResult, Transaction } from '../../types/domain';

export const MedicineDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { error: showError } = useToast();

  const [activeTab, setActiveTab] = useState('overview');
  const [medicine, setMedicine] = useState<Medicine | null>(null);
  const [inventory, setInventory] = useState<InventoryItem | null>(null);
  const [forecast, setForecast] = useState<ForecastResult | null>(null);
  const [risk, setRisk] = useState<RiskResult | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  const medId = id || 'MED001';

  const loadAll = useCallback(async () => {
    setLoading(true);
    try {
      const [medData, invData, fcData, riskData, txData] = await Promise.all([
        getMedicine(medId),
        getInventoryItem(medId),
        getForecast(medId),
        getRiskResult(medId),
        getTransactions({ medicine_id: medId, page_size: 20 }),
      ]);
      if (medData) setMedicine(medData);
      if (invData) setInventory(invData);
      if (fcData) setForecast(fcData);
      if (riskData) setRisk(riskData);
      setTransactions(txData.data);
    } catch (err) {
      showError('Failed to load medicine details', String(err));
    } finally {
      setLoading(false);
    }
  }, [medId, showError]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  if (loading && !medicine) {
    return (
      <div className="py-12 flex flex-col items-center justify-center">
        <div className="w-8 h-8 border-2 border-teal-600 border-t-transparent rounded-full animate-spin" />
        <p className="mt-3 text-sm text-slate-500">Loading medicine dossier...</p>
      </div>
    );
  }

  // Format chart data from forecast points
  const chartPoints = (forecast?.points || []).map((p) => {
    const dStr = p.date.substring(5); // MM-DD
    if (p.is_forecast) {
      return {
        date: dStr,
        predictedDemand: p.predicted_demand,
        lowerBound: p.lower_bound,
        upperBound: p.upper_bound,
      };
    }
    return {
      date: dStr,
      actualDemand: p.predicted_demand,
    };
  });

  const txCols: ColumnDef<Transaction>[] = [
    {
      key: 'transaction_date',
      header: 'Date & Time',
      sortable: true,
      cell: (r) => new Date(r.transaction_date).toLocaleDateString() + ' ' + new Date(r.transaction_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
    {
      key: 'transaction_type',
      header: 'Type',
      cell: (r) => (
        <Badge
          variant={
            r.transaction_type === 'RECEIPT' || r.transaction_type === 'RETURN_FROM_PATIENT'
              ? 'success'
              : r.transaction_type === 'SALE'
              ? 'info'
              : 'danger'
          }
          size="sm"
        >
          {r.transaction_type}
        </Badge>
      ),
    },
    {
      key: 'quantity',
      header: 'Quantity',
      isNumeric: true,
      cell: (r) => (
        <span
          className={`font-mono font-medium ${
            ['SALE', 'WASTAGE', 'ADJUSTMENT_NEGATIVE', 'TRANSFER_OUT'].includes(r.transaction_type)
              ? 'text-rose-600'
              : 'text-emerald-600'
          }`}
        >
          {['SALE', 'WASTAGE', 'ADJUSTMENT_NEGATIVE', 'TRANSFER_OUT'].includes(r.transaction_type) ? '-' : '+'}
          {r.quantity}
        </span>
      ),
    },
    {
      key: 'stock_before',
      header: 'Before',
      isNumeric: true,
      cell: (r) => r.stock_before.toLocaleString(),
    },
    {
      key: 'stock_after',
      header: 'After',
      isNumeric: true,
      cell: (r) => <span className="font-semibold text-slate-900">{r.stock_after.toLocaleString()}</span>,
    },
    {
      key: 'reference_number',
      header: 'Reference',
      cell: (r) => <span className="text-xs font-mono text-slate-500">{r.reference_number || '—'}</span>,
    },
  ];

  return (
    <div>
      <div className="mb-4">
        <Button
          variant="ghost"
          size="sm"
          leftIcon={<ArrowLeft className="w-4 h-4" />}
          onClick={() => navigate('/medicines')}
        >
          Back to Medicines Directory
        </Button>
      </div>

      {/* Header section with status badges */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 mb-6 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <span className="font-mono text-xs px-2.5 py-1 rounded-md bg-teal-50 text-teal-800 font-semibold border border-teal-200">
                {medicine?.medicine_id}
              </span>
              <h1 className="text-xl font-bold text-slate-900">{medicine?.display_name}</h1>
              {risk && <RiskBadge level={risk.risk_level} size="md" />}
              {inventory && <StockStatusBadge status={inventory.stock_status} size="md" />}
            </div>
            <p className="text-sm text-slate-500 mt-1">
              Generic: <span className="font-medium text-slate-700">{medicine?.generic_name}</span> •{' '}
              {medicine?.category?.category_name || medicine?.category_id} •{' '}
              Supplier: <span className="font-medium text-slate-700">{medicine?.primary_supplier?.supplier_name || medicine?.primary_supplier_id}</span>
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link to={`/transactions?med=${medicine?.medicine_id}`}>
              <Button variant="outline" size="sm">
                Log Transaction
              </Button>
            </Link>
            <Link to={`/replenishment?med=${medicine?.medicine_id}`}>
              <Button variant="primary" size="sm">
                Replenish Item
              </Button>
            </Link>
          </div>
        </div>

        {/* Quick KPI Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4 mt-6 pt-6 border-t border-slate-100">
          <div>
            <span className="text-xs text-slate-500">Current Stock</span>
            <div className="text-xl font-bold text-slate-900 mt-0.5">
              {inventory?.closing_stock.toLocaleString() ?? '—'}{' '}
              <span className="text-xs font-normal text-slate-500">{medicine?.unit_of_measure}</span>
            </div>
          </div>
          <div>
            <span className="text-xs text-slate-500">Stock Coverage</span>
            <div className="text-xl font-bold text-slate-900 mt-0.5">
              {(inventory?.coverage_days ?? inventory?.days_of_cover ?? 0).toFixed(1)}{' '}
              <span className="text-xs font-normal text-slate-500">days</span>
            </div>
          </div>
          <div>
            <span className="text-xs text-slate-500">Exp. Daily Demand</span>
            <div className="text-xl font-bold text-slate-900 mt-0.5">
              {(inventory?.expected_daily_demand ?? 10).toFixed(1)}
            </div>
          </div>
          <div>
            <span className="text-xs text-slate-500">Supplier Lead Time</span>
            <div className="text-xl font-bold text-slate-900 mt-0.5">
              {medicine?.primary_supplier?.lead_time_mean_days ?? 7} <span className="text-xs font-normal text-slate-500">days</span>
            </div>
          </div>
          <div>
            <span className="text-xs text-slate-500">Open Orders</span>
            <div className="text-xl font-bold text-slate-900 mt-0.5">
              {(inventory?.open_order_qty ?? inventory?.on_order_units ?? 0).toLocaleString()}
            </div>
          </div>
          <div>
            <span className="text-xs text-slate-500">Risk Score</span>
            <div className="text-xl font-bold text-rose-600 mt-0.5">
              {risk ? `${risk.risk_score} / 100` : '—'}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview" value={activeTab} onValueChange={setActiveTab}>
        <TabList className="mb-6">
          <TabTrigger value="overview" icon={<FileText className="w-4 h-4" />}>
            Overview & Specifications
          </TabTrigger>
          <TabTrigger value="forecast" icon={<TrendingUp className="w-4 h-4" />}>
            Demand Forecast (30 Days)
          </TabTrigger>
          <TabTrigger value="calculation" icon={<Calculator className="w-4 h-4" />}>
            Calculation Chain & Risk
          </TabTrigger>
          <TabTrigger value="transactions" icon={<History className="w-4 h-4" />}>
            Transaction History
          </TabTrigger>
        </TabList>

        {/* Tab 1: Overview */}
        <TabContent value="overview">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Pharmaceutical Metadata</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Dosage Form</span>
                  <span className="font-medium text-slate-800">{medicine?.dosage_form}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Strength</span>
                  <span className="font-medium text-slate-800">{medicine?.strength}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Route of Administration</span>
                  <span className="font-medium text-slate-800">{medicine?.route || 'Oral'}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Pack Size</span>
                  <span className="font-medium text-slate-800">{medicine?.pack_size} units / {medicine?.unit_of_measure}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Storage Conditions</span>
                  <span className="font-medium text-slate-800">{medicine?.storage_condition || 'Room Temperature (15-25°C)'}</span>
                </div>
                <div className="flex justify-between py-1.5">
                  <span className="text-slate-500">Composition Status</span>
                  <span className="inline-flex items-center gap-1 text-emerald-700 font-medium">
                    <ShieldCheck className="w-4 h-4" />
                    {medicine?.composition_status.replace(/_/g, ' ')}
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Procurement & Commercials</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Primary Supplier</span>
                  <span className="font-medium text-slate-800">{medicine?.primary_supplier?.supplier_name}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Supplier Location</span>
                  <span className="font-medium text-slate-800">{medicine?.primary_supplier?.city}, {medicine?.primary_supplier?.state}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Unit Cost Price</span>
                  <span className="font-mono font-medium text-slate-800">₹{medicine?.unit_cost_inr.toFixed(2)}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Unit Selling Price</span>
                  <span className="font-mono font-medium text-slate-800">₹{medicine?.unit_price_inr.toFixed(2)}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Reorder Threshold (Safety Stock)</span>
                  <span className="font-mono font-medium text-slate-800">{inventory?.safety_stock ?? 100} units</span>
                </div>
                <div className="flex justify-between py-1.5">
                  <span className="text-slate-500">Minimum Order Quantity (MOQ)</span>
                  <span className="font-mono font-medium text-slate-800">{inventory?.moq ?? 50} units</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabContent>

        {/* Tab 2: Forecast */}
        <TabContent value="forecast">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Demand Forecast & Historical Consumption</CardTitle>
                <p className="text-xs text-slate-500 mt-1">
                  Active Model: <span className="font-medium text-slate-700">{forecast?.model || 'Gradient Boosting Regressor'}</span> • Horizon: 30 Days
                </p>
              </div>
              <Badge variant="info" size="sm">
                90% Confidence Interval
              </Badge>
            </CardHeader>
            <CardContent>
              <div className="h-80 w-full mt-2">
                <LineForecastChart data={chartPoints} />
              </div>
            </CardContent>
          </Card>
        </TabContent>

        {/* Tab 3: Calculation Chain */}
        <TabContent value="calculation">
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Deterministic Risk & Sufficiency Calculation Chain</CardTitle>
                <p className="text-xs text-slate-500">Step-by-step formula breakdown used to classify this item's stock-out vulnerability.</p>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 text-sm">
                  <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                    <span className="font-semibold text-teal-800 block mb-1">Step 1 — Expected Daily Demand (EDD)</span>
                    <p className="text-slate-600 mb-2">Calculated from the mean forecasted daily consumption over the next 30 days:</p>
                    <code className="px-2 py-1 bg-white border border-slate-200 rounded text-xs font-mono text-slate-800">
                      EDD = {(inventory?.expected_daily_demand ?? 10).toFixed(2)} units/day
                    </code>
                  </div>

                  <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                    <span className="font-semibold text-teal-800 block mb-1">Step 2 — Stock Coverage (Days)</span>
                    <p className="text-slate-600 mb-2">Ratio of current physical stock to expected daily demand:</p>
                    <code className="px-2 py-1 bg-white border border-slate-200 rounded text-xs font-mono text-slate-800">
                      Coverage = Current Stock ({inventory?.closing_stock ?? 0}) / EDD ({(inventory?.expected_daily_demand ?? 10).toFixed(2)}) = {(inventory?.coverage_days ?? inventory?.days_of_cover ?? 0).toFixed(1)} Days
                    </code>
                  </div>

                  <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                    <span className="font-semibold text-teal-800 block mb-1">Step 3 — Lead Time Demand & Safety Stock</span>
                    <p className="text-slate-600 mb-2">
                      Supplier lead time is {medicine?.primary_supplier?.lead_time_mean_days ?? 7} days. Safety stock buffer (z = 1.65):
                    </p>
                    <code className="px-2 py-1 bg-white border border-slate-200 rounded text-xs font-mono text-slate-800">
                      Safety Stock = {inventory?.safety_stock ?? 120} units • Required Stock = {inventory?.reorder_point ?? 250} units
                    </code>
                  </div>

                  <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                    <span className="font-semibold text-teal-800 block mb-1">Step 4 — Final Risk Score Assessment</span>
                    <p className="text-slate-700 font-medium">
                      {risk?.explanation || 'Coverage is critically below safety thresholds.'}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {risk?.factors && risk.factors.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Top Contributing Risk Factors</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {risk.factors.map((f, i) => (
                    <div key={i} className="border-b border-slate-100 last:border-0 pb-3 last:pb-0">
                      <div className="flex justify-between items-center text-sm font-medium">
                        <span className="text-slate-800">{f.factor}</span>
                        <span className="text-teal-700 font-mono">{(f.contribution * 100).toFixed(0)}% weight</span>
                      </div>
                      <p className="text-xs text-slate-500 mt-1">{f.explanation}</p>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}
          </div>
        </TabContent>

        {/* Tab 4: Transactions */}
        <TabContent value="transactions">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Audit Trail & Recent Inventory Movements</CardTitle>
              <Link to={`/transactions?med=${medicine?.medicine_id}`}>
                <Button variant="ghost" size="sm">
                  Full Transaction Register
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              <DataTable
                columns={txCols}
                data={transactions}
                keyExtractor={(r) => r.id}
                emptyMessage="No recent inventory movements recorded for this medicine."
              />
            </CardContent>
          </Card>
        </TabContent>
      </Tabs>
    </div>
  );
};
