import React, { useState, useEffect, useCallback } from 'react';
import { Truck, Check, Download, AlertTriangle, X, RefreshCw, ShoppingCart } from 'lucide-react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Button } from '../../components/ui/Button';
import { Tabs, TabList, TabTrigger, TabContent } from '../../components/ui/Tabs';
import { DataTable, type ColumnDef } from '../../components/ui/DataTable';
import { Badge } from '../../components/ui/Badge';
import { Modal } from '../../components/ui/Modal';
import { Input } from '../../components/ui/Input';
import { TextArea } from '../../components/ui/form/TextArea';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../components/feedback/ToastContext';
import {
  getRecommendations,
  acceptRecommendation,
  markOrdered,
  dismissRecommendation,
} from '../../api/replenishment';
import type { Recommendation, RecommendationStatus } from '../../types/domain';

export const ReplenishmentPage: React.FC = () => {
  const { role, user } = useAuth();
  const { success, error: showError } = useToast();

  const [activeTab, setActiveTab] = useState<RecommendationStatus | 'ALL'>('PENDING');
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);

  // Action Modals
  const [orderModalItem, setOrderModalItem] = useState<Recommendation | null>(null);
  const [dismissModalItem, setDismissModalItem] = useState<Recommendation | null>(null);
  const [dismissReason, setDismissReason] = useState('');
  const [poRef, setPoRef] = useState('');

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getRecommendations(activeTab === 'ALL' ? undefined : activeTab);
      setRecommendations(data);
    } catch (err) {
      showError('Failed to load replenishment recommendations', String(err));
    } finally {
      setLoading(false);
    }
  }, [activeTab, showError]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleAccept = async (rec: Recommendation) => {
    try {
      await acceptRecommendation(rec.id, user?.name || 'Authorized Manager');
      success('Recommendation Accepted', `Approved procurement of ${rec.recommended_quantity} units for ${rec.medicine?.display_name || rec.medicine_id}.`);
      loadData();
    } catch (err) {
      showError('Action Failed', String(err));
    }
  };

  const handleMarkOrdered = async () => {
    if (!orderModalItem) return;
    try {
      await markOrdered(orderModalItem.id);
      success('Order Recorded', `Marked ${orderModalItem.recommended_quantity} units as on-order with supplier. Open order position updated.`);
      setOrderModalItem(null);
      setPoRef('');
      loadData();
    } catch (err) {
      showError('Failed to mark order', String(err));
    }
  };

  const handleDismiss = async () => {
    if (!dismissModalItem) return;
    if (!dismissReason.trim()) {
      showError('Reason Required', 'Please provide an audit justification for dismissing this replenishment recommendation.');
      return;
    }
    try {
      await dismissRecommendation(dismissModalItem.id, user?.name || 'Authorized Manager', dismissReason);
      success('Recommendation Dismissed', `Recommendation for ${dismissModalItem.medicine?.display_name} marked as dismissed.`);
      setDismissModalItem(null);
      setDismissReason('');
      loadData();
    } catch (err) {
      showError('Failed to dismiss', String(err));
    }
  };

  const handleExportCSV = () => {
    const headers = ['ID', 'Medicine ID', 'Medicine Name', 'Supplier', 'Recommended Qty', 'Current Stock', 'Required Stock', 'Status', 'Urgency'];
    const rows = recommendations.map((r) => [
      r.id,
      r.medicine_id,
      `"${r.medicine?.display_name || ''}"`,
      `"${r.supplier?.supplier_name || ''}"`,
      r.recommended_quantity,
      r.current_stock,
      r.required_stock ?? r.reorder_point,
      r.status,
      r.is_urgent || r.urgency_level === 'HIGH' || r.urgency_level === 'CRITICAL' ? 'URGENT' : 'STANDARD',
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `replenishment_orders_${new Date().toISOString().substring(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    success('CSV Exported', `Downloaded ${recommendations.length} replenishment entries.`);
  };

  const columns: ColumnDef<Recommendation>[] = [
    {
      key: 'medicine_id',
      header: 'Medicine',
      sortable: true,
      cell: (r) => (
        <div>
          <span className="font-semibold text-slate-900 block">{r.medicine?.display_name || r.medicine_id}</span>
          <span className="text-xs font-mono text-teal-700">{r.medicine_id}</span>
        </div>
      ),
    },
    {
      key: 'supplier',
      header: 'Supplier & Lead Time',
      sortable: true,
      cell: (r) => (
        <div>
          <span className="text-xs font-medium text-slate-800 block">{r.supplier?.supplier_name || 'Authorized Wholesaler'}</span>
          <span className="text-[11px] text-slate-500">{r.lead_time_days} days lead time • MOQ {r.moq_applied ? 'Applied' : '50'}</span>
        </div>
      ),
    },
    {
      key: 'current_stock',
      header: 'Current Stock',
      isNumeric: true,
      cell: (r) => r.current_stock.toLocaleString(),
    },
    {
      key: 'open_orders',
      header: 'Open Orders',
      isNumeric: true,
      cell: (r) => (r.open_order_qty ?? 0).toLocaleString(),
    },
    {
      key: 'required_stock',
      header: 'Target / ROP',
      isNumeric: true,
      cell: (r) => (r.required_stock ?? r.reorder_point).toLocaleString(),
    },
    {
      key: 'recommended_order_quantity',
      header: 'Recommended Qty',
      isNumeric: true,
      sortable: true,
      cell: (r) => (
        <span className="font-mono font-bold text-teal-800 text-sm">
          {r.recommended_quantity.toLocaleString()} units
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status & Priority',
      cell: (r) => (
        <div className="flex items-center gap-1.5">
          <Badge
            variant={
              r.status === 'ACCEPTED'
                ? 'success'
                : r.status === 'ORDERED'
                ? 'info'
                : r.status === 'DISMISSED'
                ? 'neutral'
                : 'warning'
            }
            size="sm"
          >
            {r.status}
          </Badge>
          {(r.is_urgent || r.urgency_level === 'HIGH' || r.urgency_level === 'CRITICAL') && (
            <Badge variant="danger" size="sm">
              Urgent
            </Badge>
          )}
        </div>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      cell: (r) => (
        <div className="flex items-center gap-1.5">
          {role !== 'PHARMACY_STAFF' && r.status === 'PENDING' && (
            <>
              <Button
                variant="primary"
                size="sm"
                onClick={() => handleAccept(r)}
                leftIcon={<Check className="w-3.5 h-3.5" />}
              >
                Accept
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setDismissModalItem(r)}
                leftIcon={<X className="w-3.5 h-3.5 text-rose-500" />}
              >
                Dismiss
              </Button>
            </>
          )}
          {role !== 'PHARMACY_STAFF' && r.status === 'ACCEPTED' && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => {
                setOrderModalItem(r);
                setPoRef(`PO-${Date.now().toString().slice(-6)}`);
              }}
              leftIcon={<ShoppingCart className="w-3.5 h-3.5" />}
            >
              Order Placed
            </Button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Automated Replenishment & Procurement Support"
        subtitle="Generates optimal order quantities bounded by Minimum Order Quantities (MOQ), lead-time demand, and current open orders."
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              leftIcon={<Download className="w-4 h-4" />}
              onClick={handleExportCSV}
            >
              Export Order Sheet (CSV)
            </Button>
            <Button
              variant="outline"
              size="sm"
              leftIcon={<RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />}
              onClick={loadData}
            >
              Refresh
            </Button>
          </div>
        }
      />

      {/* Critical Decision Support Disclaimer Banner */}
      <div className="mb-6 p-4 rounded-xl bg-amber-50 border border-amber-200/80 flex items-start gap-3 text-amber-900 shadow-2xs">
        <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
        <div className="text-xs leading-relaxed">
          <strong className="font-semibold block mb-0.5">Decision-Support Workflow Notice:</strong>
          Accepting a recommendation or recording "Order Placed" records internal pharmacy managerial approval.
          The system <strong>never autonomously contacts external suppliers</strong> or places binding financial orders. All purchase order transmissions must be executed through your accredited vendor procurement channels.
        </div>
      </div>

      <Tabs defaultValue="PENDING" value={activeTab} onValueChange={(val) => setActiveTab(val as any)}>
        <TabList className="mb-6">
          <TabTrigger value="PENDING" icon={<Truck className="w-4 h-4" />}>
            Pending Review
          </TabTrigger>
          <TabTrigger value="ACCEPTED" icon={<Check className="w-4 h-4" />}>
            Accepted & Ready
          </TabTrigger>
          <TabTrigger value="ORDERED" icon={<ShoppingCart className="w-4 h-4" />}>
            Order Dispatched
          </TabTrigger>
          <TabTrigger value="DISMISSED" icon={<X className="w-4 h-4" />}>
            Dismissed
          </TabTrigger>
          <TabTrigger value="ALL">
            All Recommendations
          </TabTrigger>
        </TabList>

        <TabContent value={activeTab}>
          <DataTable
            columns={columns}
            data={recommendations}
            keyExtractor={(r) => r.id}
            isLoading={loading}
            emptyMessage={`No ${activeTab.toLowerCase()} replenishment recommendations at this time.`}
          />
        </TabContent>
      </Tabs>

      {/* Mark Order Placed Modal */}
      <Modal
        isOpen={!!orderModalItem}
        onClose={() => setOrderModalItem(null)}
        title="Record Supplier Purchase Order"
        description="Logging this purchase order will increase the item's Open Order quantity, preventing duplicate recommendations."
        footer={
          <>
            <Button variant="outline" size="sm" onClick={() => setOrderModalItem(null)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" onClick={handleMarkOrdered}>
              Confirm Order Placed
            </Button>
          </>
        }
      >
        {orderModalItem && (
          <div className="space-y-4 text-sm">
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
              <span className="font-bold text-slate-800">{orderModalItem.medicine?.display_name}</span>
              <p className="text-xs text-slate-500 mt-1">
                Supplier: {orderModalItem.supplier?.supplier_name} • Quantity: {orderModalItem.recommended_quantity} units
              </p>
            </div>

            <Input
              label="Purchase Order / Vendor Reference"
              placeholder="e.g. PO-88910"
              value={poRef}
              onChange={(e) => setPoRef(e.target.value)}
              required
            />

            <p className="text-xs text-slate-500">
              When physical shipment arrives at the store, log a <strong>Stock Receipt</strong> under Transactions to convert open orders into active closing stock.
            </p>
          </div>
        )}
      </Modal>

      {/* Dismiss Modal */}
      <Modal
        isOpen={!!dismissModalItem}
        onClose={() => setDismissModalItem(null)}
        title="Dismiss Replenishment Recommendation"
        description="Provide a justification for rejecting this calculated order suggestion for audit compliance."
        footer={
          <>
            <Button variant="outline" size="sm" onClick={() => setDismissModalItem(null)}>
              Cancel
            </Button>
            <Button variant="danger" size="sm" onClick={handleDismiss}>
              Dismiss Recommendation
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <TextArea
            label="Dismissal Justification"
            placeholder="e.g. Expected clinical demand drop, temporary clinic holiday closure, or alternate substitute stock available..."
            value={dismissReason}
            onChange={(e) => setDismissReason(e.target.value)}
            required
            rows={3}
          />
        </div>
      </Modal>
    </div>
  );
};
