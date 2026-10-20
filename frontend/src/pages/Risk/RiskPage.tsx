import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { RefreshCw, ChevronDown, X, Info } from 'lucide-react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Button } from '../../components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/Card';
import { RiskBadge } from '../../components/domain/RiskBadge';
import { useToast } from '../../components/feedback/ToastContext';
import { getRiskResults, runRiskAnalysis } from '../../api/risk';
import { MOCK_CATEGORIES } from '../../mocks';
import type { RiskResult, RiskLevel, RiskFactor } from '../../types/domain';

const RISK_ORDER: Record<string, number> = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };

function FactorBar({ factor }: { factor: RiskFactor }) {
  const pct = Math.round(factor.contribution * 100);
  return (
    <div className="mb-3">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-medium text-slate-700">{factor.factor}</span>
        <span className="text-xs font-mono text-slate-500">{typeof factor.value === 'number' ? factor.value.toFixed(2) : factor.value}</span>
      </div>
      <div className="flex items-center gap-2">
        <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div className="h-full bg-teal-500 rounded-full" style={{ width: `${pct}%` }} />
        </div>
        <span className="text-[11px] text-slate-400 w-8 text-right">{pct}%</span>
      </div>
      <p className="text-[11px] text-slate-500 mt-0.5">{factor.explanation}</p>
    </div>
  );
}

export const RiskPage: React.FC = () => {
  const { success, error: showError } = useToast();
  const [items, setItems] = useState<RiskResult[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [levelFilter, setLevelFilter] = useState<RiskLevel | ''>('');
  const [selectedRisk, setSelectedRisk] = useState<RiskResult | null>(null);
  const PAGE_SIZE = 20;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getRiskResults({
        search: search || undefined,
        category_id: categoryFilter || undefined,
        risk_level: (levelFilter as RiskLevel) || undefined,
        page, page_size: PAGE_SIZE,
        sort_by: 'risk_score', sort_dir: 'desc',
      });
      setItems(res.data);
      setTotal(res.total);
    } catch (e) {
      showError('Failed to load risk results', String(e));
    } finally {
      setLoading(false);
    }
  }, [search, categoryFilter, levelFilter, page, showError]);

  useEffect(() => { setPage(1); }, [search, categoryFilter, levelFilter]);
  useEffect(() => { load(); }, [load]);

  const handleRunAnalysis = async () => {
    setRunning(true);
    try {
      await runRiskAnalysis();
      success('Risk Analysis Complete', 'All 85 medicines re-evaluated.');
      load();
    } catch (e) {
      showError('Analysis failed', String(e));
    } finally {
      setRunning(false);
    }
  };

  const levelCounts: Record<string, number> = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };
  items.forEach(r => { if (r.risk_level in levelCounts) levelCounts[r.risk_level]++; });

  return (
    <div>
      <PageHeader
        title="Stock-Out Risk Analysis"
        subtitle="ML-generated risk scores and stockout probability for all medicines as of 2025-12-31."
        actions={
          <Button variant="primary" size="sm"
            leftIcon={running ? <RefreshCw className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
            onClick={handleRunAnalysis} disabled={running}
          >
            {running ? 'Running…' : 'Run Risk Analysis'}
          </Button>
        }
      />

      {/* Risk level KPI strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
        {(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] as RiskLevel[]).map(level => (
          <button key={level}
            onClick={() => setLevelFilter(levelFilter === level ? '' : level)}
            className={`rounded-lg border p-3 text-left transition-all ${levelFilter === level ? 'ring-2 ring-offset-1 ring-teal-500 border-teal-300' : 'border-slate-200 hover:border-slate-300'} bg-white`}
          >
            <div className="flex items-center gap-2 mb-1">
              <RiskBadge level={level} size="sm" />
            </div>
            <span className="text-2xl font-bold text-slate-900">{levelCounts[level] ?? 0}</span>
          </button>
        ))}
      </div>

      <div className="flex flex-col lg:flex-row gap-5">
        {/* Main Table */}
        <div className="flex-1 min-w-0">
          <Card className="mb-3">
            <CardContent className="p-3">
              <div className="flex flex-wrap gap-3">
                <input
                  className="flex-1 min-w-48 px-3 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-teal-500 outline-none"
                  placeholder="Search medicine…"
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                />
                <select
                  className="px-3 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-teal-500 outline-none bg-white min-w-44"
                  value={categoryFilter}
                  onChange={e => setCategoryFilter(e.target.value)}
                >
                  <option value="">All Categories</option>
                  {MOCK_CATEGORIES.map(c => <option key={c.category_id} value={c.category_id}>{c.category_name}</option>)}
                </select>
              </div>
            </CardContent>
          </Card>

          <Card>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-100 bg-slate-50/60">
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500">Medicine</th>
                    <th className="text-center px-4 py-3 text-xs font-semibold text-slate-500 w-20">Score</th>
                    <th className="text-center px-4 py-3 text-xs font-semibold text-slate-500 w-24">Risk</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 hidden md:table-cell">P(7d)</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 hidden md:table-cell">P(30d)</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500">Cover</th>
                    <th className="text-center px-4 py-3 text-xs font-semibold text-slate-500 w-16" />
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {loading && Array.from({ length: 8 }).map((_, i) => (
                    <tr key={i} className="animate-pulse">
                      {Array.from({ length: 6 }).map((_, j) => (
                        <td key={j} className="px-4 py-3"><div className="h-4 bg-slate-100 rounded" /></td>
                      ))}
                    </tr>
                  ))}
                  {!loading && items.sort((a, b) => RISK_ORDER[a.risk_level] - RISK_ORDER[b.risk_level] || b.risk_score - a.risk_score).map(r => (
                    <tr key={r.id} className={`hover:bg-slate-50/60 transition-colors cursor-pointer ${selectedRisk?.id === r.id ? 'bg-teal-50/40' : ''}`}
                      onClick={() => setSelectedRisk(selectedRisk?.id === r.id ? null : r)}>
                      <td className="px-4 py-3">
                        <Link to={`/medicines/${r.medicine_id}`} className="font-medium text-slate-900 hover:text-teal-700 block" onClick={e => e.stopPropagation()}>
                          {r.medicine?.generic_name}
                        </Link>
                        <p className="text-xs text-slate-400">{r.medicine?.category?.category_name}</p>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={`font-mono font-bold text-base ${r.risk_score >= 75 ? 'text-rose-600' : r.risk_score >= 55 ? 'text-orange-500' : r.risk_score >= 30 ? 'text-amber-500' : 'text-teal-600'}`}>
                          {r.risk_score}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <RiskBadge level={r.risk_level} size="sm" />
                      </td>
                      <td className="px-4 py-3 text-right hidden md:table-cell">
                        <span className="font-mono text-xs text-slate-700">{(r.stockout_probability_7d * 100).toFixed(0)}%</span>
                      </td>
                      <td className="px-4 py-3 text-right hidden md:table-cell">
                        <span className="font-mono text-xs text-slate-700">{(r.stockout_probability_30d * 100).toFixed(0)}%</span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className={`font-mono text-xs font-semibold ${r.days_of_cover < 7 ? 'text-rose-600' : r.days_of_cover < 14 ? 'text-orange-500' : 'text-slate-700'}`}>
                          {r.days_of_cover.toFixed(1)}d
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${selectedRisk?.id === r.id ? 'rotate-180' : ''}`} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {total > PAGE_SIZE && (
              <div className="flex items-center justify-between px-4 py-3 border-t border-slate-100">
                <span className="text-xs text-slate-500">{total} medicines total</span>
                <div className="flex gap-2">
                  <Button variant="secondary" size="sm" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Prev</Button>
                  <Button variant="secondary" size="sm" onClick={() => setPage(p => p + 1)} disabled={page >= Math.ceil(total / PAGE_SIZE)}>Next</Button>
                </div>
              </div>
            )}
          </Card>
        </div>

        {/* Calculation Drawer — right panel when a row is selected */}
        {selectedRisk && (
          <div className="lg:w-80 shrink-0">
            <Card className="sticky top-4">
              <CardHeader className="flex flex-row items-start justify-between pb-2">
                <div>
                  <CardTitle className="text-base">{selectedRisk.medicine?.generic_name}</CardTitle>
                  <p className="text-xs text-slate-500 mt-0.5">Risk Calculation Explainability</p>
                </div>
                <button onClick={() => setSelectedRisk(null)} className="text-slate-400 hover:text-slate-600 mt-0.5">
                  <X className="w-4 h-4" />
                </button>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3 mb-4 p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="text-center">
                    <span className="block text-3xl font-bold text-slate-900">{selectedRisk.risk_score}</span>
                    <span className="text-[11px] text-slate-500">Risk Score</span>
                  </div>
                  <div className="flex-1">
                    <RiskBadge level={selectedRisk.risk_level} />
                    <p className="text-xs text-slate-500 mt-1">
                      Cover: <strong>{selectedRisk.days_of_cover.toFixed(1)}d</strong> | ROP: <strong>{selectedRisk.reorder_point}</strong>
                    </p>
                  </div>
                </div>

                <h4 className="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Stockout Probability</h4>
                <div className="grid grid-cols-3 gap-2 mb-4">
                  {[['7d', selectedRisk.stockout_probability_7d], ['14d', selectedRisk.stockout_probability_14d], ['30d', selectedRisk.stockout_probability_30d]].map(([label, prob]) => (
                    <div key={label as string} className="text-center p-2 rounded-lg bg-slate-50 border border-slate-200">
                      <span className={`block text-lg font-bold ${(prob as number) > 0.5 ? 'text-rose-600' : 'text-slate-900'}`}>
                        {((prob as number) * 100).toFixed(0)}%
                      </span>
                      <span className="text-[11px] text-slate-500">{label as string}</span>
                    </div>
                  ))}
                </div>

                <h4 className="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Feature Contributions</h4>
                {selectedRisk.factors.map(f => <FactorBar key={f.factor} factor={f} />)}

                <div className="mt-4 p-2.5 rounded-lg bg-blue-50 border border-blue-200 flex gap-2">
                  <Info className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
                  <p className="text-[11px] text-blue-700">
                    Risk scores are produced by the XGBoost model trained on historical stockout events. For informational use only — not a substitute for pharmacist judgment.
                  </p>
                </div>

                <div className="mt-3 flex gap-2">
                  <Link to={`/medicines/${selectedRisk.medicine_id}`} className="flex-1">
                    <Button variant="secondary" size="sm" className="w-full">Medicine Details</Button>
                  </Link>
                  <Link to="/replenishment" className="flex-1">
                    <Button variant="primary" size="sm" className="w-full">Replenish</Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};
