import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertOctagon,
  AlertTriangle,
  TrendingUp,
  CheckCircle2,
  CheckCheck,
  RefreshCw,
  Bell,
  X,
  Info,
  Clock,
  Filter,
} from 'lucide-react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Button } from '../../components/ui/Button';
import { FilterBar } from '../../components/ui/form/FilterBar';
import { Select } from '../../components/ui/Select';
import { Badge } from '../../components/ui/Badge';
import { Card } from '../../components/ui/Card';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../components/feedback/ToastContext';
import {
  getAlerts,
  acknowledgeAlert,
  resolveAlert,
  dismissAlert,
  bulkAcknowledge,
} from '../../api/alerts';
import type { Alert, AlertSeverity, AlertType, AlertStatus } from '../../types/domain';

export const AlertsPage: React.FC = () => {
  const { user } = useAuth();
  const { success, error: showError } = useToast();

  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selectedSeverity, setSelectedSeverity] = useState<AlertSeverity | ''>('');
  const [selectedType, setSelectedType] = useState<AlertType | ''>('');
  const [selectedStatus, setSelectedStatus] = useState<AlertStatus | ''>('');
  const [loading, setLoading] = useState(true);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getAlerts({
        severity: selectedSeverity || undefined,
        alert_type: selectedType || undefined,
        status: selectedStatus || undefined,
      });
      setAlerts(data);
    } catch (err) {
      showError('Failed to load system alerts', String(err));
    } finally {
      setLoading(false);
    }
  }, [selectedSeverity, selectedType, selectedStatus, showError]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleAcknowledge = async (id: string) => {
    try {
      await acknowledgeAlert(id, user?.name || 'Authorized Staff');
      success('Alert Acknowledged', 'Recorded review in audit log.');
      loadData();
    } catch (err) {
      showError('Action failed', String(err));
    }
  };

  const handleResolve = async (id: string) => {
    try {
      await resolveAlert(id, user?.name || 'Authorized Staff');
      success('Alert Resolved', 'Condition marked as mitigated.');
      loadData();
    } catch (err) {
      showError('Action failed', String(err));
    }
  };

  const handleDismiss = async (id: string) => {
    try {
      await dismissAlert(id);
      success('Alert Dismissed', 'Removed alert notification.');
      loadData();
    } catch (err) {
      showError('Action failed', String(err));
    }
  };

  const handleBulkAcknowledge = async () => {
    if (selectedIds.length === 0) return;
    try {
      await bulkAcknowledge(selectedIds, user?.name || 'Authorized Staff');
      success('Bulk Acknowledged', `Acknowledged ${selectedIds.length} alerts.`);
      setSelectedIds([]);
      loadData();
    } catch (err) {
      showError('Bulk action failed', String(err));
    }
  };

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const unreadCount = alerts.filter((a) => a.status === 'UNREAD').length;

  const getAlertIcon = (type: AlertType, severity: AlertSeverity) => {
    if (severity === 'CRITICAL') {
      return <AlertOctagon className="w-5 h-5 text-rose-600 shrink-0" />;
    }
    if (type === 'DEMAND_SPIKE' || type === 'FORECAST_DEVIATION') {
      return <TrendingUp className="w-5 h-5 text-amber-500 shrink-0" />;
    }
    return <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0" />;
  };

  return (
    <div>
      <PageHeader
        title="Inventory Notifications & Exception Alerts"
        subtitle="Real-time detection of impending stock-outs, demand surges, forecast variances, and reorder breaches."
        actions={
          <div className="flex items-center gap-2">
            {selectedIds.length > 0 && (
              <Button
                variant="primary"
                size="sm"
                leftIcon={<CheckCheck className="w-4 h-4" />}
                onClick={handleBulkAcknowledge}
              >
                Acknowledge ({selectedIds.length})
              </Button>
            )}
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

      {/* Filter strip */}
      <Card className="p-4 mb-6">
        <FilterBar>
          <div className="w-44">
            <Select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value as AlertStatus)}
            >
              <option value="">All Statuses ({alerts.length})</option>
              <option value="UNREAD">Unread Only ({unreadCount})</option>
              <option value="ACKNOWLEDGED">Acknowledged</option>
              <option value="RESOLVED">Resolved</option>
              <option value="DISMISSED">Dismissed</option>
            </Select>
          </div>

          <div className="w-44">
            <Select
              value={selectedSeverity}
              onChange={(e) => setSelectedSeverity(e.target.value as AlertSeverity)}
            >
              <option value="">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="WARNING">Warning</option>
              <option value="INFO">Information</option>
            </Select>
          </div>

          <div className="w-56">
            <Select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value as AlertType)}
            >
              <option value="">All Alert Types</option>
              <option value="HIGH_RISK">High Risk (Stock-Out)</option>
              <option value="LOW_STOCK">Low Stock Depletion</option>
              <option value="REPLENISHMENT_REQUIRED">Replenishment Required</option>
              <option value="DEMAND_SPIKE">Demand Spike Anomaly</option>
              <option value="FORECAST_DEVIATION">Forecast Model Deviation</option>
            </Select>
          </div>
        </FilterBar>
      </Card>

      {/* Alerts list */}
      <div className="space-y-3">
        {loading && (
          <div className="text-center py-12">
            <div className="w-8 h-8 border-2 border-teal-600 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="mt-2 text-xs text-slate-500">Checking alert conditions...</p>
          </div>
        )}

        {!loading && alerts.length === 0 && (
          <Card className="p-12 text-center">
            <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-slate-900">No Active Exceptions</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              All inventory levels are within configured safety margins. No stock-out threats or demand spikes detected.
            </p>
          </Card>
        )}

        {!loading &&
          alerts.map((alert) => (
            <Card
              key={alert.id}
              className={`p-4 transition-all hover:border-slate-300 ${
                alert.status === 'UNREAD' ? 'border-l-4 border-l-teal-600 bg-white' : 'bg-slate-50/60 opacity-90'
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3 flex-1">
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(alert.id)}
                    onChange={() => toggleSelect(alert.id)}
                    className="mt-1 rounded border-slate-300 text-teal-600 focus:ring-teal-500"
                  />

                  {getAlertIcon(alert.alert_type, alert.severity)}

                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className="font-semibold text-sm text-slate-900">{alert.title}</span>
                      <Badge
                        variant={alert.severity === 'CRITICAL' ? 'danger' : alert.severity === 'WARNING' ? 'warning' : 'neutral'}
                        size="sm"
                      >
                        {alert.severity}
                      </Badge>
                      <Badge variant="neutral" size="sm">
                        {alert.alert_type.replace(/_/g, ' ')}
                      </Badge>
                      {alert.status === 'UNREAD' && (
                        <span className="w-2 h-2 rounded-full bg-teal-500 inline-block" title="Unread" />
                      )}
                    </div>

                    <p className="text-xs text-slate-600 leading-relaxed mb-2">{alert.message}</p>

                    <div className="flex flex-wrap items-center gap-4 text-[11px] text-slate-400">
                      <span>
                        Medicine:{' '}
                        <Link
                          to={`/medicines/${alert.medicine_id}`}
                          className="font-medium text-teal-700 hover:underline"
                        >
                          {alert.medicine?.display_name || alert.medicine_id} ({alert.medicine_id})
                        </Link>
                      </span>
                      <span>•</span>
                      <span className="inline-flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(alert.created_at).toLocaleString()}
                      </span>
                      {alert.acknowledged_by && (
                        <>
                          <span>•</span>
                          <span>Ack: {alert.acknowledged_by}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  {alert.status === 'UNREAD' && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleAcknowledge(alert.id)}
                      title="Acknowledge Alert"
                    >
                      Acknowledge
                    </Button>
                  )}
                  {alert.status !== 'RESOLVED' && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleResolve(alert.id)}
                      title="Mark as Resolved"
                    >
                      Resolve
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDismiss(alert.id)}
                    title="Dismiss Notification"
                  >
                    <X className="w-3.5 h-3.5 text-slate-400 hover:text-slate-600" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
      </div>
    </div>
  );
};
