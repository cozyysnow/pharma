import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Download, Filter, Search } from 'lucide-react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Button } from '../../components/ui/Button';
import { Card, CardContent } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { RiskBadge } from '../../components/domain/RiskBadge';
import { useToast } from '../../components/feedback/ToastContext';
import { getInventory } from '../../api/inventory';
import { MOCK_CATEGORIES } from '../../mocks';
import type { InventoryItem, StockStatus } from '../../types/domain';

const STATUS_COLORS: Record<string, string> = {
  CRITICAL: 'bg-rose-500',
  LOW: 'bg-orange-400',
  LOW_STOCK: 'bg-orange-400',
  ADEQUATE: 'bg-teal-500',
  IN_STOCK: 'bg-teal-500',
  OVERSTOCKED: 'bg-violet-400',
  OUT_OF_STOCK: 'bg-rose-500',
};

const STATUS_LABELS: Record<string, string> = {
  CRITICAL: 'Critical',
  LOW: 'Low Stock',
  ADEQUATE: 'Adequate',
  OVERSTOCKED: 'Overstocked',
};

export const InventoryPage: React.FC = () => {
  const { error: showError } = useToast();
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState<StockStatus | ''>('');
  const PAGE_SIZE = 20;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getInventory({
        search: search || undefined,
        category_id: categoryFilter || undefined,
        stock_status: (statusFilter as StockStatus) || undefined,
        page,
        page_size: PAGE_SIZE,
        sort_by: 'days_of_cover',
        sort_dir: 'asc',
      });
      setItems(res.data);
      setTotal(res.total);
    } catch (e) {
      showError('Failed to load inventory', String(e));
    } finally {
      setLoading(false);
    }
  }, [search, categoryFilter, statusFilter, page, showError]);

  useEffect(() => { setPage(1); }, [search, categoryFilter, statusFilter]);
  useEffect(() => { load(); }, [load]);

  const handleExportCsv = () => {
    const rows = [
      ['Medicine ID', 'Display Name', 'Category', 'Closing Stock', 'Days of Cover', 'Reorder Point', 'Status'],
      ...items.map(i => [i.medicine_id, i.medicine?.display_name ?? '', i.medicine?.category?.category_name ?? '', i.closing_stock, i.days_of_cover, i.reorder_point, i.stock_status]),
    ];
    const csv = rows.map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'inventory_snapshot_2025-12-31.csv'; a.click();
    URL.revokeObjectURL(url);
  };

  const statusCounts: Record<string, number> = { CRITICAL: 0, LOW: 0, ADEQUATE: 0, OVERSTOCKED: 0 };
  items.forEach(i => {
    const st = i.stock_status === 'OUT_OF_STOCK' ? 'CRITICAL' : i.stock_status === 'LOW_STOCK' ? 'LOW' : i.stock_status === 'IN_STOCK' ? 'ADEQUATE' : i.stock_status;
    if (st in statusCounts) statusCounts[st]++;
  });

  return (
    <div>
      <PageHeader
        title="Inventory Snapshot"
        subtitle="Reference date: 31 December 2025 — stock levels, coverage, and reorder status for all 85 medicines."
        actions={
          <Button variant="secondary" size="sm" leftIcon={<Download className="w-4 h-4" />} onClick={handleExportCsv}>
            Export CSV
          </Button>
        }
      />

      {/* Status KPI strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
        {(Object.entries(STATUS_LABELS) as [StockStatus, string][]).map(([status, label]) => (
          <button key={status}
            onClick={() => setStatusFilter(statusFilter === status ? '' : status)}
            className={`rounded-lg border p-3 text-left transition-all ${statusFilter === status ? 'ring-2 ring-offset-1 ring-teal-500 border-teal-300' : 'border-slate-200 hover:border-slate-300'} bg-white`}
          >
            <div className="flex items-center gap-2 mb-1">
              <span className={`w-2.5 h-2.5 rounded-full ${STATUS_COLORS[status]}`} />
              <span className="text-xs font-medium text-slate-600">{label}</span>
            </div>
            <span className="text-2xl font-bold text-slate-900">
              {statusCounts[status]}
            </span>
          </button>
        ))}
      </div>

      {/* Filters */}
      <Card className="mb-4">
        <CardContent className="p-3">
          <div className="flex flex-wrap gap-3">
            <div className="relative flex-1 min-w-48">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-400 outline-none"
                placeholder="Search medicine name or ID…"
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>
            <select
              className="px-3 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-teal-500 outline-none bg-white min-w-44"
              value={categoryFilter}
              onChange={e => setCategoryFilter(e.target.value)}
            >
              <option value="">All Categories</option>
              {MOCK_CATEGORIES.map(c => <option key={c.category_id} value={c.category_id}>{c.category_name}</option>)}
            </select>
            <div className="flex items-center gap-1.5 text-xs text-slate-500">
              <Filter className="w-3.5 h-3.5" />
              <span>{total} medicines</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50/60">
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 w-24">ID</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500">Medicine</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 hidden md:table-cell">Category</th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500">Stock</th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500">On Order</th>
                <th className="px-4 py-3 text-xs font-semibold text-slate-500 min-w-32">Coverage</th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 hidden lg:table-cell">Reorder Pt.</th>
                <th className="text-center px-4 py-3 text-xs font-semibold text-slate-500">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading && Array.from({ length: 8 }).map((_, i) => (
                <tr key={i} className="animate-pulse">
                  {Array.from({ length: 7 }).map((_, j) => (
                    <td key={j} className="px-4 py-3"><div className="h-4 bg-slate-100 rounded w-full" /></td>
                  ))}
                </tr>
              ))}
              {!loading && items.map(inv => {
                const maxCoverage = 60;
                const pct = Math.min(100, (inv.days_of_cover / maxCoverage) * 100);
                const barColor = inv.stock_status === 'CRITICAL' ? 'bg-rose-500' : inv.stock_status === 'LOW' ? 'bg-orange-400' : inv.stock_status === 'OVERSTOCKED' ? 'bg-violet-400' : 'bg-teal-500';
                return (
                  <tr key={inv.medicine_id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-4 py-3">
                      <Link to={`/medicines/${inv.medicine_id}`} className="font-mono text-xs text-teal-700 hover:text-teal-900 font-semibold">
                        {inv.medicine_id}
                      </Link>
                    </td>
                    <td className="px-4 py-3">
                      <Link to={`/medicines/${inv.medicine_id}`} className="font-medium text-slate-900 hover:text-teal-700 transition-colors line-clamp-1">
                        {inv.medicine?.display_name}
                      </Link>
                      <p className="text-xs text-slate-400 hidden sm:block">{inv.medicine?.primary_supplier?.supplier_name}</p>
                    </td>
                    <td className="px-4 py-3 hidden md:table-cell">
                      <span className="text-xs text-slate-600">{inv.medicine?.category?.category_name}</span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span className="font-mono font-semibold text-slate-800">{inv.closing_stock.toLocaleString()}</span>
                      <span className="text-xs text-slate-400 block">{inv.medicine?.unit_of_measure}</span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span className="font-mono text-slate-600">{inv.on_order_units.toLocaleString()}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                          <div className={`h-full ${barColor} rounded-full transition-all`} style={{ width: `${pct}%` }} />
                        </div>
                        <span className="font-mono text-xs text-slate-700 shrink-0 w-12 text-right">{inv.days_of_cover.toFixed(1)}d</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right hidden lg:table-cell">
                      <span className="font-mono text-xs text-slate-600">{inv.reorder_point.toLocaleString()}</span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <Badge
                        variant={inv.stock_status === 'CRITICAL' || inv.stock_status === 'OUT_OF_STOCK' ? 'danger' : inv.stock_status === 'LOW' || inv.stock_status === 'LOW_STOCK' ? 'warning' : inv.stock_status === 'OVERSTOCKED' ? 'info' : 'success'}
                        size="sm"
                      >
                        {STATUS_LABELS[inv.stock_status] || inv.stock_status}
                      </Badge>
                    </td>
                  </tr>
                );
              })}
              {!loading && items.length === 0 && (
                <tr>
                  <td colSpan={8} className="px-4 py-12 text-center text-sm text-slate-400">
                    No inventory items match your filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {total > PAGE_SIZE && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-slate-100">
            <span className="text-xs text-slate-500">Page {page} of {Math.ceil(total / PAGE_SIZE)}</span>
            <div className="flex gap-2">
              <Button variant="secondary" size="sm" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Previous</Button>
              <Button variant="secondary" size="sm" onClick={() => setPage(p => p + 1)} disabled={page >= Math.ceil(total / PAGE_SIZE)}>Next</Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};
