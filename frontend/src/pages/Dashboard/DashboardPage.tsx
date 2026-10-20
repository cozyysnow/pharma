import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  Boxes, PackageCheck, AlertOctagon, AlertTriangle,
  Truck, Bell, Play, ArrowUpRight, RefreshCw,
} from 'lucide-react';
import { PageHeader } from '../../components/layout/PageHeader';
import { KpiCard } from '../../components/domain/KpiCard';
import { Button } from '../../components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { RiskDonut } from '../../components/charts/RiskDonut';
import { BarChart } from '../../components/charts/BarChart';
import { LineForecastChart } from '../../components/charts/LineForecastChart';
import { RiskBadge } from '../../components/domain/RiskBadge';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../components/feedback/ToastContext';
import { getDashboardKpis } from '../../api/dashboard';
import { getRiskResults } from '../../api/risk';
import { runRiskAnalysis } from '../../api/risk';
import { getAlerts } from '../../api/alerts';
import {
  MOCK_CATEGORY_DISTRIBUTION,
  MOCK_DEMAND_TREND,
  MOCK_RISK_RESULTS,
} from '../../mocks';
import type { DashboardKpis } from '../../types/domain';
import type { RiskResult, Alert } from '../../types/domain';

export const DashboardPage: React.FC = () => {
  const { role } = useAuth();
  const { success, error: showError } = useToast();
  const [kpis, setKpis] = useState<DashboardKpis | null>(null);
  const [topRisk, setTopRisk] = useState<RiskResult[]>([]);
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([]);
  const [running, setRunning] = useState(false);

  const load = useCallback(async () => {
    try {
      const [kpiData, riskData, alertData] = await Promise.all([
        getDashboardKpis(),
        getRiskResults({ sort_by: 'risk_score', sort_dir: 'desc', page_size: 6 }),
        getAlerts({ status: 'UNREAD' }),
      ]);
      setKpis(kpiData);
      setTopRisk(riskData.data.slice(0, 6));
      setRecentAlerts(alertData.slice(0, 5));
    } catch (e) {
      showError('Failed to load dashboard', String(e));
    }
  }, [showError]);

  useEffect(() => { load(); }, [load]);

  const handleRunRisk = async () => {
    setRunning(true);
    try {
      await runRiskAnalysis();
      success('Risk Analysis Complete', 'Stock-out risk scores updated for all 85 medicines.');
      load();
    } catch (e) {
      showError('Risk analysis failed', String(e));
    } finally {
      setRunning(false);
    }
  };

  // Chart data derived from real mock data
  const categoryChartData = MOCK_CATEGORY_DISTRIBUTION.map(c => ({ name: c.name.split(' ')[0], value: c.count * 180 + Math.round(c.criticalCount * 420) }));
  const demandChart = MOCK_DEMAND_TREND.map(d => ({ date: d.date.slice(5), actualDemand: d.demand }));

  const riskSummary = {
    critical: MOCK_RISK_RESULTS.filter(r => r.risk_level === 'CRITICAL').length,
    high: MOCK_RISK_RESULTS.filter(r => r.risk_level === 'HIGH').length,
    medium: MOCK_RISK_RESULTS.filter(r => r.risk_level === 'MEDIUM').length,
    low: MOCK_RISK_RESULTS.filter(r => r.risk_level === 'LOW').length,
  };

  return (
    <div>
      <PageHeader
        title="Inventory & Stock-Out Intelligence"
        subtitle="Centralized operational monitoring, demand forecasts, and predictive stock-out risk assessment."
        actions={
          role !== 'PHARMACY_STAFF' && (
            <Button
              variant="primary" size="sm"
              leftIcon={running ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
              onClick={handleRunRisk}
              disabled={running}
            >
              {running ? 'Running Analysis…' : 'Run Risk Analysis'}
            </Button>
          )
        }
      />

      {/* KPI Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
        <KpiCard title="Total Medicines" value={kpis?.total_medicines ?? 85} subtitle="Across 11 categories" icon={<Boxes className="w-4 h-4" />} />
        <KpiCard title="Inventory Value" value={kpis ? `₹${(kpis.total_inventory_value_inr / 100000).toFixed(1)}L` : '₹28.5L'} subtitle="Reference date: 31 Dec" icon={<PackageCheck className="w-4 h-4" />} />
        <KpiCard title="Critical / High Risk" value={`${riskSummary.critical} / ${riskSummary.high}`} alert={riskSummary.critical > 0} alertText="Immediate Action" icon={<AlertOctagon className="w-4 h-4" />} />
        <KpiCard title="Medium Risk" value={riskSummary.medium} subtitle={`Avg coverage: ${kpis?.avg_coverage_days?.toFixed(1) ?? '28.4'}d`} icon={<AlertTriangle className="w-4 h-4 text-amber-600" />} />
        <KpiCard title="Pending Orders" value={kpis?.pending_recommendations ?? 5} subtitle="Awaiting review" icon={<Truck className="w-4 h-4" />} />
        <KpiCard title="Active Alerts" value={kpis?.unread_alerts ?? 8} alert={!!kpis && kpis.unread_alerts > 0} alertText={`${riskSummary.critical} Critical`} icon={<Bell className="w-4 h-4" />} />
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <Card className="flex flex-col">
          <CardHeader>
            <CardTitle>Stock-Out Risk Distribution</CardTitle>
            <p className="text-xs text-slate-500 mt-0.5">85 medicines as of 2025-12-31</p>
          </CardHeader>
          <CardContent className="flex-1 flex items-center justify-center pt-2">
            <RiskDonut low={riskSummary.low} medium={riskSummary.medium} high={riskSummary.high + riskSummary.critical} height={210} />
          </CardContent>
        </Card>

        <Card className="lg:col-span-2 flex flex-col">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Aggregate Daily Demand — December 2025</CardTitle>
              <p className="text-xs text-slate-500 mt-0.5">Total units demanded across all 85 medicines</p>
            </div>
            <span className="text-[11px] font-mono text-teal-800 bg-teal-50 px-2 py-0.5 rounded border border-teal-200">
              Model: XGBoost (v1.0)
            </span>
          </CardHeader>
          <CardContent className="pt-2">
            <LineForecastChart data={demandChart} height={230} splitDate="12/31" />
          </CardContent>
        </Card>
      </div>

      {/* Secondary Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Medicine Count by Category</CardTitle>
          </CardHeader>
          <CardContent className="pt-2">
            <BarChart data={categoryChartData} height={240} yAxisLabel="Units" />
          </CardContent>
        </Card>

        {/* Critical Watchlist */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Critical Stock-Out Watchlist</CardTitle>
              <p className="text-xs text-slate-500">Coverage {'<'} lead time — immediate action required</p>
            </div>
            <Link to="/risk">
              <Button variant="ghost" size="sm" rightIcon={<ArrowUpRight className="w-3.5 h-3.5" />}>
                View All
              </Button>
            </Link>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-slate-100">
              {topRisk.filter(r => r.risk_level === 'CRITICAL' || r.risk_level === 'HIGH').slice(0, 5).map((r) => (
                <Link key={r.id} to={`/medicines/${r.medicine_id}`}
                  className="p-4 flex items-center justify-between hover:bg-slate-50/70 transition-colors block"
                >
                  <div className="min-w-0 pr-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-semibold text-slate-500">{r.medicine_id}</span>
                      <span className="text-sm font-semibold text-slate-900 truncate">{r.medicine?.generic_name}</span>
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {r.medicine?.category?.category_name} • Stock: <strong className="text-slate-800 font-mono">{r.medicine ? (r.days_of_cover).toFixed(1) : '—'}d</strong> cover
                    </p>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <div className="text-right">
                      <span className="text-xs font-bold text-rose-600 font-mono">{r.days_of_cover.toFixed(1)}d</span>
                      <span className="text-[10px] text-slate-400 block">Score: {r.risk_score}</span>
                    </div>
                    <RiskBadge level={r.risk_level} size="sm" />
                  </div>
                </Link>
              ))}
              {topRisk.filter(r => r.risk_level === 'CRITICAL' || r.risk_level === 'HIGH').length === 0 && (
                <div className="p-8 text-center text-sm text-slate-400">No critical or high-risk medicines</div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Alerts */}
      {recentAlerts.length > 0 && (
        <Card className="mt-6">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Recent Unread Alerts</CardTitle>
            <Link to="/alerts">
              <Button variant="ghost" size="sm" rightIcon={<ArrowUpRight className="w-3.5 h-3.5" />}>View All</Button>
            </Link>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-slate-100">
              {recentAlerts.map(a => (
                <div key={a.id} className="p-4 flex items-start gap-3 hover:bg-slate-50/70">
                  <div className={`mt-0.5 w-2 h-2 rounded-full shrink-0 ${a.severity === 'CRITICAL' ? 'bg-rose-500' : a.severity === 'HIGH' ? 'bg-orange-500' : 'bg-amber-400'}`} />
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-slate-900">{a.title}</p>
                    <p className="text-xs text-slate-500 mt-0.5 line-clamp-1">{a.message}</p>
                  </div>
                  <span className="text-[11px] text-slate-400 shrink-0">{new Date(a.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Decision-support disclaimer */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-3 text-xs text-blue-800">
        <strong>Decision Support Only:</strong> All risk scores, forecasts, and recommendations are generated by machine learning models for informational purposes.
        They do not constitute medical advice or autonomous purchasing decisions. All replenishment actions require review and authorization by qualified pharmacy staff.
      </div>
    </div>
  );
};
