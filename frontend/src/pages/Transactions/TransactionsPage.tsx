import React, { useState, useEffect, useCallback } from 'react';
import { Plus, Download, ArrowUpRight, ArrowDownLeft, AlertCircle, RefreshCw } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import { PageHeader } from '../../components/layout/PageHeader';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { FilterBar } from '../../components/ui/form/FilterBar';
import { SearchInput } from '../../components/ui/form/SearchInput';
import { Select } from '../../components/ui/Select';
import { DataTable, type ColumnDef } from '../../components/ui/DataTable';
import { Modal } from '../../components/ui/Modal';
import { Input } from '../../components/ui/Input';
import { TextArea } from '../../components/ui/form/TextArea';
import { Badge } from '../../components/ui/Badge';
import { Pagination } from '../../components/ui/Pagination';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../components/feedback/ToastContext';
import { getTransactions, createTransaction } from '../../api/transactions';
import { getMedicines } from '../../api/medicines';
import { getInventoryItem } from '../../api/inventory';
import type { Transaction, TransactionType, Medicine } from '../../types/domain';

const TX_TYPES: { label: string; value: TransactionType; effect: 'add' | 'sub' }[] = [
  { label: 'Sale (Dispensed to Patient)', value: 'SALE', effect: 'sub' },
  { label: 'Stock Receipt (Purchase Order Fulfilled)', value: 'RECEIPT', effect: 'add' },
  { label: 'Patient Return (Restocked)', value: 'RETURN_FROM_PATIENT', effect: 'add' },
  { label: 'Supplier Return / Outward Transfer', value: 'TRANSFER_OUT', effect: 'sub' },
  { label: 'Inventory Adjustment (+)', value: 'ADJUSTMENT_POSITIVE', effect: 'add' },
  { label: 'Inventory Adjustment (-)', value: 'ADJUSTMENT_NEGATIVE', effect: 'sub' },
  { label: 'Wastage / Damaged / Expired', value: 'WASTAGE', effect: 'sub' },
];

export const TransactionsPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const medParam = searchParams.get('med');

  const { role } = useAuth();
  const { success, error: showError } = useToast();

  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [medicines, setMedicines] = useState<Medicine[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState<TransactionType | ''>('');
  const [medFilter, setMedFilter] = useState(medParam || '');

  // Modal form state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedMedId, setSelectedMedId] = useState('MED001');
  const [currentStock, setCurrentStock] = useState<number>(0);
  const [stockLoading, setStockLoading] = useState(false);
  const [txType, setTxType] = useState<TransactionType>('SALE');
  const [txQty, setTxQty] = useState<number>(10);
  const [txRef, setTxRef] = useState('');
  const [txNotes, setTxNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const PAGE_SIZE = 20;

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [txRes, medsRes] = await Promise.all([
        getTransactions({
          medicine_id: medFilter || undefined,
          transaction_type: (typeFilter as TransactionType) || undefined,
          search: search || undefined,
          page,
          page_size: PAGE_SIZE,
        }),
        getMedicines({ page_size: 100 }),
      ]);
      setTransactions(txRes.data);
      setTotal(txRes.total);
      setMedicines(medsRes.data);
    } catch (err) {
      showError('Failed to load transaction register', String(err));
    } finally {
      setLoading(false);
    }
  }, [medFilter, typeFilter, search, page, showError]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Load stock when selected medicine in modal changes
  useEffect(() => {
    if (!isModalOpen) return;
    let isCurrent = true;
    setStockLoading(true);
    getInventoryItem(selectedMedId)
      .then((inv) => {
        if (isCurrent) setCurrentStock(inv?.closing_stock ?? 100);
      })
      .catch(() => {
        if (isCurrent) setCurrentStock(100);
      })
      .finally(() => {
        if (isCurrent) setStockLoading(false);
      });
    return () => {
      isCurrent = false;
    };
  }, [selectedMedId, isModalOpen]);

  // Projected stock preview
  const activeTxTypeMeta = TX_TYPES.find((t) => t.value === txType) || TX_TYPES[0];
  const delta = activeTxTypeMeta.effect === 'add' ? txQty : -txQty;
  const projectedStock = currentStock + delta;
  const hasNegativeStockError = projectedStock < 0;

  const handleCreateTransaction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (hasNegativeStockError) {
      showError('Negative Stock Rejection', 'Transaction would reduce stock below zero. In accordance with system safety rules, this action is prohibited.');
      return;
    }
    setSubmitting(true);
    try {
      await createTransaction({
        medicine_id: selectedMedId,
        transaction_type: txType,
        quantity: txQty,
        reference_number: txRef || `TX-${Date.now().toString().slice(-6)}`,
        notes: txNotes,
      });
      success('Transaction Recorded', `Successfully logged ${activeTxTypeMeta.label} of ${txQty} units.`);
      setIsModalOpen(false);
      setTxRef('');
      setTxNotes('');
      loadData();
    } catch (err) {
      showError('Transaction Failed', String(err));
    } finally {
      setSubmitting(false);
    }
  };

  const handleExportCSV = () => {
    const headers = ['Transaction ID', 'Date', 'Type', 'Medicine ID', 'Medicine Name', 'Quantity', 'Stock Before', 'Stock After', 'Reference'];
    const rows = transactions.map((t) => [
      t.id,
      t.transaction_date,
      t.transaction_type,
      t.medicine_id,
      `"${t.medicine?.display_name || ''}"`,
      t.quantity,
      t.stock_before,
      t.stock_after,
      `"${t.reference_number || ''}"`,
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `pharmacy_transactions_${new Date().toISOString().substring(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    success('CSV Exported', `Downloaded ${transactions.length} transaction entries.`);
  };

  const columns: ColumnDef<Transaction>[] = [
    {
      key: 'transaction_date',
      header: 'Date & Time',
      sortable: true,
      cell: (r) => (
        <span className="font-mono text-xs text-slate-700">
          {new Date(r.transaction_date).toLocaleDateString()} {new Date(r.transaction_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      ),
    },
    {
      key: 'transaction_type',
      header: 'Type',
      cell: (r) => {
        const isAdd = ['RECEIPT', 'RETURN_FROM_PATIENT', 'ADJUSTMENT_POSITIVE'].includes(r.transaction_type);
        return (
          <Badge variant={isAdd ? 'success' : r.transaction_type === 'SALE' ? 'info' : 'danger'} size="sm">
            {r.transaction_type}
          </Badge>
        );
      },
    },
    {
      key: 'medicine',
      header: 'Medicine',
      sortable: true,
      cell: (r) => (
        <div>
          <span className="font-medium text-slate-900 block">{r.medicine?.display_name || r.medicine_id}</span>
          <span className="font-mono text-[11px] text-teal-700">{r.medicine_id}</span>
        </div>
      ),
    },
    {
      key: 'quantity',
      header: 'Quantity',
      isNumeric: true,
      cell: (r) => {
        const isSub = ['SALE', 'WASTAGE', 'ADJUSTMENT_NEGATIVE', 'TRANSFER_OUT'].includes(r.transaction_type);
        return (
          <span className={`font-mono font-semibold ${isSub ? 'text-rose-600' : 'text-emerald-600'}`}>
            {isSub ? '-' : '+'}
            {r.quantity}
          </span>
        );
      },
    },
    {
      key: 'stock_before',
      header: 'Stock Before',
      isNumeric: true,
      cell: (r) => r.stock_before.toLocaleString(),
    },
    {
      key: 'stock_after',
      header: 'Stock After',
      isNumeric: true,
      cell: (r) => <span className="font-semibold text-slate-900">{r.stock_after.toLocaleString()}</span>,
    },
    {
      key: 'reference_number',
      header: 'Reference',
      cell: (r) => <span className="font-mono text-xs text-slate-500">{r.reference_number || '—'}</span>,
    },
    {
      key: 'created_by',
      header: 'User / Source',
      cell: (r) => <span className="text-xs text-slate-500">{r.created_by || 'System'}</span>,
    },
  ];

  return (
    <div>
      <PageHeader
        title="Stock Movements & Transaction Audit"
        subtitle="Complete immutable register of dispensing, warehouse receipts, adjustments, returns, and damages."
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              leftIcon={<Download className="w-4 h-4" />}
              onClick={handleExportCSV}
            >
              Export CSV
            </Button>
            <Button
              variant="outline"
              size="sm"
              leftIcon={<RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />}
              onClick={loadData}
            >
              Refresh
            </Button>
            {role !== 'PHARMACY_STAFF' && (
              <Button
                variant="primary"
                size="sm"
                leftIcon={<Plus className="w-4 h-4" />}
                onClick={() => setIsModalOpen(true)}
              >
                Log Transaction
              </Button>
            )}
          </div>
        }
      />

      {/* Summary KPI Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <Card className="p-4 flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-500">Total Recorded Movements</span>
            <div className="text-2xl font-bold text-slate-900 mt-1">{total.toLocaleString()}</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center">
            <ArrowUpRight className="w-5 h-5" />
          </div>
        </Card>
        <Card className="p-4 flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-500">Unique Medicines Filtered</span>
            <div className="text-2xl font-bold text-teal-800 mt-1">{medFilter ? '1 SKU' : `${medicines.length} SKUs`}</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center">
            <ArrowDownLeft className="w-5 h-5" />
          </div>
        </Card>
        <Card className="p-4 flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-500">Zero Stock Lock Status</span>
            <div className="text-2xl font-bold text-emerald-600 mt-1">Enforced</div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center">
            <AlertCircle className="w-5 h-5" />
          </div>
        </Card>
      </div>

      <Card className="p-4 mb-6">
        <FilterBar className="mb-4">
          <SearchInput
            placeholder="Search reference, notes, or medicine..."
            onSearch={(val) => { setSearch(val); setPage(1); }}
            className="w-72"
          />
          <div className="w-56">
            <Select
              value={medFilter}
              onChange={(e) => { setMedFilter(e.target.value); setPage(1); }}
            >
              <option value="">All Medicines</option>
              {medicines.map((m) => (
                <option key={m.medicine_id} value={m.medicine_id}>
                  {m.medicine_id} - {m.display_name}
                </option>
              ))}
            </Select>
          </div>
          <div className="w-48">
            <Select
              value={typeFilter}
              onChange={(e) => { setTypeFilter(e.target.value as TransactionType); setPage(1); }}
            >
              <option value="">All Movement Types</option>
              {TX_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </Select>
          </div>
        </FilterBar>

        <DataTable
          columns={columns}
          data={transactions}
          keyExtractor={(r) => r.id}
          isLoading={loading}
          emptyMessage="No transaction records match the specified criteria."
        />

        <div className="mt-4 flex justify-between items-center text-xs text-slate-500">
          <span>Showing {(page - 1) * PAGE_SIZE + 1} to {Math.min(page * PAGE_SIZE, total)} of {total} records</span>
          <Pagination
            currentPage={page}
            totalPages={Math.ceil(total / PAGE_SIZE) || 1}
            onPageChange={setPage}
          />
        </div>
      </Card>

      {/* New Transaction Modal with Live Stock Calculation Preview */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Record Stock Movement"
        description="Every transaction produces an immutable audit record and updates current stock positions."
        footer={
          <>
            <Button variant="outline" size="sm" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              disabled={hasNegativeStockError || submitting || txQty <= 0}
              onClick={handleCreateTransaction}
            >
              {submitting ? 'Recording...' : 'Commit Transaction'}
            </Button>
          </>
        }
      >
        <form onSubmit={handleCreateTransaction} className="space-y-4">
          <Select
            label="Medicine"
            value={selectedMedId}
            onChange={(e) => setSelectedMedId(e.target.value)}
            required
          >
            {medicines.map((m) => (
              <option key={m.medicine_id} value={m.medicine_id}>
                {m.medicine_id} — {m.display_name}
              </option>
            ))}
          </Select>

          <Select
            label="Movement Type"
            value={txType}
            onChange={(e) => setTxType(e.target.value as TransactionType)}
            required
          >
            {TX_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </Select>

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Quantity"
              type="number"
              min="1"
              value={txQty}
              onChange={(e) => setTxQty(Math.max(1, parseInt(e.target.value) || 0))}
              required
            />
            <Input
              label="Reference / Invoice No."
              placeholder="e.g. INV-2025-0992"
              value={txRef}
              onChange={(e) => setTxRef(e.target.value)}
            />
          </div>

          <TextArea
            label="Audit Notes / Reason"
            placeholder="Required for adjustments and wastage..."
            value={txNotes}
            onChange={(e) => setTxNotes(e.target.value)}
            rows={2}
          />

          {/* Live stock preview calculation card */}
          <div
            className={`p-4 rounded-xl border transition-all ${
              hasNegativeStockError
                ? 'bg-rose-50 border-rose-200'
                : 'bg-teal-50/50 border-teal-200'
            }`}
          >
            <div className="flex items-center justify-between text-xs mb-2">
              <span className="font-semibold text-slate-700">Stock Impact Preview</span>
              {stockLoading && <span className="text-teal-600 animate-pulse">Calculating...</span>}
            </div>

            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="bg-white p-2 rounded-lg border border-slate-200">
                <span className="text-[11px] text-slate-500 block">Current Stock</span>
                <span className="text-sm font-bold text-slate-800">{currentStock}</span>
              </div>
              <div className="bg-white p-2 rounded-lg border border-slate-200">
                <span className="text-[11px] text-slate-500 block">Delta</span>
                <span className={`text-sm font-bold ${delta < 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
                  {delta < 0 ? delta : `+${delta}`}
                </span>
              </div>
              <div
                className={`p-2 rounded-lg border ${
                  hasNegativeStockError ? 'bg-rose-100 border-rose-300' : 'bg-white border-slate-200'
                }`}
              >
                <span className="text-[11px] text-slate-500 block">Projected Stock</span>
                <span
                  className={`text-sm font-bold ${
                    hasNegativeStockError ? 'text-rose-700' : 'text-slate-900'
                  }`}
                >
                  {projectedStock}
                </span>
              </div>
            </div>

            {hasNegativeStockError && (
              <div className="mt-3 flex items-start gap-2 text-xs text-rose-700 bg-rose-100/80 p-2.5 rounded-lg border border-rose-200">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>
                  <strong>Negative Stock Violation:</strong> Physical pharmacy stock cannot drop below 0 units. Reduce quantity or log a stock receipt first.
                </span>
              </div>
            )}
          </div>
        </form>
      </Modal>
    </div>
  );
};
