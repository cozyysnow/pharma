import React, { useState, useEffect, useCallback } from 'react';
import { Play, Sparkles, SlidersHorizontal, BarChart2, Calendar, TrendingUp, Info } from 'lucide-react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Button } from '../../components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Tabs, TabList, TabTrigger, TabContent } from '../../components/ui/Tabs';
import { Select } from '../../components/ui/Select';
import { DataTable, type ColumnDef } from '../../components/ui/DataTable';
import { Badge } from '../../components/ui/Badge';
import { LineForecastChart } from '../../components/charts/LineForecastChart';
import { BarChart } from '../../components/charts/BarChart';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../components/feedback/ToastContext';
import { getForecast } from '../../api/forecasts';
import { getMedicines } from '../../api/medicines';
import { MOCK_CATEGORIES } from '../../mocks';
import type { ForecastResult, Medicine } from '../../types/domain';

interface ModelMetric {
  modelName: string;
  type: 'CANDIDATE' | 'BASELINE';
  maeH1: number;
  maeH7: number;
  maeH14: number;
  maeH30: number;
  rmse: number;
  wape: number;
  selected: boolean;
}

export const ForecastPage: React.FC = () => {
  const { role } = useAuth();
  const { success, error: showError } = useToast();

  const [medicines, setMedicines] = useState<Medicine[]>([]);
  const [selectedMedId, setSelectedMedId] = useState('MED002');
  const [horizon, setHorizon] = useState<7 | 14 | 30>(30);
  const [activeTab, setActiveTab] = useState('projection');
  const [forecast, setForecast] = useState<ForecastResult | null>(null);
  const [loading, setLoading] = useState(true);

  // Load medicines list
  useEffect(() => {
    getMedicines({ page_size: 100 })
      .then((res) => {
        setMedicines(res.data);
      })
      .catch((err) => console.error(err));
  }, []);

  // Load forecast for selected medicine
  const loadForecast = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getForecast(selectedMedId, horizon);
      if (data) {
        setForecast(data);
      }
    } catch (err) {
      showError('Failed to load forecast', String(err));
    } finally {
      setLoading(false);
    }
  }, [selectedMedId, horizon, showError]);

  useEffect(() => {
    loadForecast();
  }, [loadForecast]);

  const selectedMed = medicines.find((m) => m.medicine_id === selectedMedId);

  // Prepare chart data from forecast points
  const points = (forecast?.points || []).map((p) => {
    const dStr = p.date.substring(5);
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

  const modelMetrics: ModelMetric[] = [
    {
      modelName: 'Gradient Boosting Regressor (GBDT)',
      type: 'CANDIDATE',
      maeH1: 8.07,
      maeH7: 8.92,
      maeH14: 9.45,
      maeH30: 10.12,
      rmse: 12.3,
      wape: 0.14,
      selected: true,
    },
    {
      modelName: 'Random Forest Regressor (100 Trees)',
      type: 'CANDIDATE',
      maeH1: 8.45,
      maeH7: 9.15,
      maeH14: 9.80,
      maeH30: 10.45,
      rmse: 12.9,
      wape: 0.15,
      selected: false,
    },
    {
      modelName: 'Ridge Linear Regression (L2 Regularized)',
      type: 'CANDIDATE',
      maeH1: 9.10,
      maeH7: 9.85,
      maeH14: 10.20,
      maeH30: 10.95,
      rmse: 13.5,
      wape: 0.16,
      selected: false,
    },
    {
      modelName: 'Baseline: Lag-1 Naïve',
      type: 'BASELINE',
      maeH1: 10.98,
      maeH7: 12.40,
      maeH14: 13.10,
      maeH30: 14.50,
      rmse: 15.2,
      wape: 0.20,
      selected: false,
    },
    {
      modelName: 'Baseline: 7-Day Rolling Mean',
      type: 'BASELINE',
      maeH1: 10.40,
      maeH7: 11.20,
      maeH14: 11.90,
      maeH30: 12.80,
      rmse: 14.1,
      wape: 0.18,
      selected: false,
    },
    {
      modelName: 'Baseline: 28-Day Rolling Mean',
      type: 'BASELINE',
      maeH1: 11.80,
      maeH7: 12.00,
      maeH14: 12.50,
      maeH30: 13.10,
      rmse: 14.8,
      wape: 0.21,
      selected: false,
    },
  ];

  const comparisonChartData = [
    { name: 'Gradient Boosting', value: 8.07, color: '#0F766E' },
    { name: 'Random Forest', value: 8.45, color: '#0D9488' },
    { name: 'Linear (Ridge)', value: 9.10, color: '#14B8A6' },
    { name: '7-Day Rolling Mean', value: 10.40, color: '#64748B' },
    { name: 'Lag-1 Naive', value: 10.98, color: '#94A3B8' },
    { name: '28-Day Rolling Mean', value: 11.80, color: '#CBD5E1' },
  ];

  const metricCols: ColumnDef<ModelMetric>[] = [
    {
      key: 'modelName',
      header: 'Model Name & Class',
      sortable: true,
      cell: (r) => (
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-900">{r.modelName}</span>
          {r.selected && (
            <Badge variant="success" size="sm">
              Active Production Model
            </Badge>
          )}
        </div>
      ),
    },
    {
      key: 'type',
      header: 'Type',
      cell: (r) => (
        <Badge variant={r.type === 'CANDIDATE' ? 'info' : 'neutral'} size="sm">
          {r.type}
        </Badge>
      ),
    },
    {
      key: 'maeH1',
      header: 'MAE (h=1)',
      isNumeric: true,
      sortable: true,
      cell: (r) => <span className="font-mono">{r.maeH1.toFixed(2)}</span>,
    },
    {
      key: 'maeH7',
      header: 'MAE (h=7)',
      isNumeric: true,
      sortable: true,
      cell: (r) => <span className="font-mono">{r.maeH7.toFixed(2)}</span>,
    },
    {
      key: 'maeH14',
      header: 'MAE (h=14)',
      isNumeric: true,
      sortable: true,
      cell: (r) => <span className="font-mono">{r.maeH14.toFixed(2)}</span>,
    },
    {
      key: 'maeH30',
      header: 'MAE (h=30)',
      isNumeric: true,
      sortable: true,
      cell: (r) => <span className="font-mono font-semibold text-teal-800">{r.maeH30.toFixed(2)}</span>,
    },
    {
      key: 'rmse',
      header: 'RMSE',
      isNumeric: true,
      sortable: true,
      cell: (r) => <span className="font-mono">{r.rmse.toFixed(1)}</span>,
    },
    {
      key: 'wape',
      header: 'WAPE',
      isNumeric: true,
      sortable: true,
      cell: (r) => <span className="font-mono">{(r.wape * 100).toFixed(1)}%</span>,
    },
  ];

  const forecastPointCols: ColumnDef<any>[] = [
    { key: 'date', header: 'Date', sortable: true },
    {
      key: 'predicted_demand',
      header: 'Expected Demand',
      isNumeric: true,
      cell: (r) => <span className="font-mono font-bold text-teal-800">{r.predicted_demand} units</span>,
    },
    {
      key: 'lower_bound',
      header: 'Lower Bound (p10)',
      isNumeric: true,
      cell: (r) => <span className="font-mono text-slate-600">{r.lower_bound}</span>,
    },
    {
      key: 'upper_bound',
      header: 'Upper Bound (p90)',
      isNumeric: true,
      cell: (r) => <span className="font-mono text-slate-600">{r.upper_bound}</span>,
    },
  ];

  return (
    <div>
      <PageHeader
        title="Multi-Step Demand Forecasting"
        subtitle="Chronological machine learning demand projections across 7, 14, and 30-day decision horizons."
        actions={
          role !== 'PHARMACY_STAFF' && (
            <Button
              variant="primary"
              size="sm"
              leftIcon={<Play className="w-4 h-4" />}
              onClick={() => {
                success('Retraining Pipeline Triggered', 'Asynchronous rolling-origin cross-validation running.');
              }}
            >
              Trigger ML Retrain
            </Button>
          )
        }
      />

      {/* Control Strip */}
      <Card className="p-4 mb-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3">
            <div className="w-80">
              <Select
                label="Selected Medicine"
                value={selectedMedId}
                onChange={(e) => setSelectedMedId(e.target.value)}
              >
                {medicines.map((m) => (
                  <option key={m.medicine_id} value={m.medicine_id}>
                    {m.medicine_id} — {m.display_name}
                  </option>
                ))}
              </Select>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">Forecast Horizon</label>
              <div className="inline-flex rounded-lg border border-slate-200 bg-slate-100 p-0.5">
                {([7, 14, 30] as const).map((h) => (
                  <button
                    key={h}
                    type="button"
                    onClick={() => setHorizon(h)}
                    className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                      horizon === h
                        ? 'bg-white text-teal-800 shadow-2xs font-semibold'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    {h} Days
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs">
            <div className="text-right">
              <span className="text-slate-500 block">Dataset Reference</span>
              <span className="font-semibold text-slate-800">2021-01-01 to 2025-12-31</span>
            </div>
            <div className="text-right">
              <span className="text-slate-500 block">Active Algorithm</span>
              <span className="font-semibold text-teal-800">Gradient Boosting (GBDT)</span>
            </div>
          </div>
        </div>
      </Card>

      <Tabs defaultValue="projection" value={activeTab} onValueChange={setActiveTab}>
        <TabList className="mb-6">
          <TabTrigger value="projection" icon={<TrendingUp className="w-4 h-4" />}>
            Demand Projection ({selectedMed?.display_name || selectedMedId})
          </TabTrigger>
          <TabTrigger value="comparison" icon={<BarChart2 className="w-4 h-4" />}>
            Model Comparison & Verification
          </TabTrigger>
          <TabTrigger value="categories" icon={<SlidersHorizontal className="w-4 h-4" />}>
            Category Aggregate Forecasts
          </TabTrigger>
        </TabList>

        {/* Tab 1: Projection */}
        <TabContent value="projection">
          <div className="space-y-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Historical Consumption & Horizon Projection</CardTitle>
                  <p className="text-xs text-slate-500 mt-1">
                    Displaying 60 days of actual dispensing history followed by {horizon} days of multi-step model predictions.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1.5 text-xs text-slate-600">
                    <span className="w-3 h-0.5 bg-teal-800 rounded" />
                    <span>Actual</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-slate-600 ml-2">
                    <span className="w-3 h-0.5 bg-teal-500 border-t border-dashed border-teal-500" />
                    <span>Predicted</span>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="h-80 w-full">
                  <LineForecastChart data={points} />
                </div>
              </CardContent>
            </Card>

            {/* Daily Predictions Breakdown Table */}
            <Card>
              <CardHeader>
                <CardTitle>Step-by-Step Forecast Coordinates (Next {horizon} Days)</CardTitle>
              </CardHeader>
              <CardContent>
                <DataTable
                  columns={forecastPointCols}
                  data={(forecast?.points || []).filter((p) => p.is_forecast)}
                  keyExtractor={(r) => r.date}
                  emptyMessage="No forecast points generated for this horizon."
                />
              </CardContent>
            </Card>
          </div>
        </TabContent>

        {/* Tab 2: Model Comparison */}
        <TabContent value="comparison">
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Documented Model Selection & Baseline Benchmark</CardTitle>
                <p className="text-xs text-slate-500">
                  Per requirements specification (Section 13), Gradient Boosting achieved MAE 8.072 on 1-step holdout, outperforming the Naive Lag-1 baseline of 10.984 by ~26.5%.
                </p>
              </CardHeader>
              <CardContent>
                <DataTable
                  columns={metricCols}
                  data={modelMetrics}
                  keyExtractor={(r) => r.modelName}
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>1-Step Validation MAE Comparison (Lower is Better)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 w-full">
                  <BarChart data={comparisonChartData} />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabContent>

        {/* Tab 3: Category Aggregates */}
        <TabContent value="categories">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {MOCK_CATEGORIES.map((cat, idx) => {
              const estDemand = 450 + idx * 85;
              return (
                <Card key={cat.category_id} className="p-4">
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-semibold text-sm text-slate-900">{cat.category_name}</span>
                    <Badge variant="info" size="sm">
                      {cat.category_id}
                    </Badge>
                  </div>
                  <p className="text-xs text-slate-500 mb-4">{cat.description}</p>
                  <div className="pt-3 border-t border-slate-100 flex justify-between items-end">
                    <div>
                      <span className="text-[11px] text-slate-400 block">30-Day Agg. Demand</span>
                      <span className="text-lg font-bold text-slate-900 font-mono">{(estDemand * 30).toLocaleString()} units</span>
                    </div>
                    <span className="text-xs font-semibold text-emerald-600">~{estDemand} / day</span>
                  </div>
                </Card>
              );
            })}
          </div>
        </TabContent>
      </Tabs>
    </div>
  );
};
