import React, { useState } from 'react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { Input } from '../../components/ui/Input';
import { Select } from '../../components/ui/Select';
import { Modal } from '../../components/ui/Modal';
import { Drawer } from '../../components/ui/Drawer';
import { Tooltip } from '../../components/ui/Tooltip';
import { EmptyState } from '../../components/feedback/EmptyState';
import { ErrorState } from '../../components/feedback/ErrorState';
import { LoadingState } from '../../components/feedback/LoadingState';
import { ConfirmDialog } from '../../components/feedback/ConfirmDialog';
import { useToast } from '../../components/feedback/ToastContext';
import { KpiCard } from '../../components/domain/KpiCard';
import { RiskBadge } from '../../components/domain/RiskBadge';
import { StockStatusBadge } from '../../components/domain/StockStatusBadge';
import { StatDelta } from '../../components/domain/StatDelta';
import { StockGauge } from '../../components/charts/StockGauge';
import { Sparkline } from '../../components/charts/Sparkline';
import { RiskDonut } from '../../components/charts/RiskDonut';
import { BarChart } from '../../components/charts/BarChart';
import { LineForecastChart } from '../../components/charts/LineForecastChart';
import { SearchInput } from '../../components/ui/form/SearchInput';
import { DateRangePicker } from '../../components/ui/form/DateRangePicker';
import { DataTable, type ColumnDef } from '../../components/ui/DataTable';
import { HelpCircle, Boxes, PackageCheck, AlertOctagon } from 'lucide-react';

export const StyleguidePage: React.FC = () => {
  const { success, error, warning, info } = useToast();
  const [modalOpen, setModalOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [dateRange, setDateRange] = useState({ startDate: '2025-12-01', endDate: '2025-12-31' });

  const sampleTableData = [
    { id: 1, name: 'Paracetamol 500mg', code: 'MED001', stock: 2450, risk: 'LOW' as const, status: 'IN_STOCK' as const },
    { id: 2, name: 'Amoxicillin 500mg', code: 'MED002', stock: 120, risk: 'HIGH' as const, status: 'LOW_STOCK' as const },
    { id: 3, name: 'Ibuprofen 400mg', code: 'MED008', stock: 0, risk: 'HIGH' as const, status: 'OUT_OF_STOCK' as const },
  ];

  const tableCols: ColumnDef<any>[] = [
    { key: 'name', header: 'Medicine Name', sortable: true },
    { key: 'code', header: 'Code' },
    { key: 'stock', header: 'Units', isNumeric: true, sortable: true },
    { key: 'risk', header: 'Risk', cell: (r) => <RiskBadge level={r.risk} size="sm" /> },
    { key: 'status', header: 'Status', cell: (r) => <StockStatusBadge status={r.status} size="sm" /> },
  ];

  return (
    <div className="space-y-10 pb-16">
      <PageHeader
        title="UI Component Design System & Styleguide"
        subtitle="Live showcase of all atomic design tokens, interactive states, accessible patterns, and domain indicators."
      />

      {/* 1. PALETTE & TOKENS */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 border-b pb-2">1. Design Tokens & Color Palette</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 text-xs">
          <div className="p-3 rounded-lg bg-teal-700 text-white font-medium shadow-xs">
            <span className="block font-bold">Primary Brand</span>
            <span>teal-700 (#0F766E)</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-900 text-white font-medium">
            <span className="block font-bold">Deep Neutral</span>
            <span>slate-900 (#0F172A)</span>
          </div>
          <div className="p-3 rounded-lg bg-white border border-slate-300 text-slate-800 font-medium">
            <span className="block font-bold">Surface Page</span>
            <span>#F5F7F8</span>
          </div>
          <div className="p-3 rounded-lg bg-risk-low-bg text-risk-low-text border border-risk-low-border font-medium">
            <span className="block font-bold">Risk Low</span>
            <span>#16A34A</span>
          </div>
          <div className="p-3 rounded-lg bg-risk-medium-bg text-risk-medium-text border border-risk-medium-border font-medium">
            <span className="block font-bold">Risk Medium</span>
            <span>#D97706</span>
          </div>
          <div className="p-3 rounded-lg bg-risk-high-bg text-risk-high-text border border-risk-high-border font-medium">
            <span className="block font-bold">Risk High</span>
            <span>#DC2626</span>
          </div>
        </div>
      </section>

      {/* 2. BUTTONS & INTERACTIVE */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 border-b pb-2">2. Buttons & Actions</h2>
        <div className="flex flex-wrap items-center gap-3">
          <Button variant="primary">Primary Action</Button>
          <Button variant="secondary">Secondary Action</Button>
          <Button variant="outline">Outline Button</Button>
          <Button variant="ghost">Ghost Button</Button>
          <Button variant="destructive">Destructive</Button>
          <Button variant="primary" isLoading={true}>Saving Data</Button>
          <Button variant="primary" disabled>Disabled State</Button>
        </div>
        <div className="flex flex-wrap items-center gap-3 pt-2">
          <Button variant="primary" size="sm">Small (sm)</Button>
          <Button variant="primary" size="md">Medium (md)</Button>
          <Button variant="primary" size="lg">Large (lg)</Button>
          <Tooltip content="Tooltip helper text" side="top">
            <Button variant="outline" size="sm" leftIcon={<HelpCircle className="w-3.5 h-3.5" />}>
              Hover for Tooltip
            </Button>
          </Tooltip>
        </div>
      </section>

      {/* 3. BADGES & DOMAIN BADGES */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 border-b pb-2">3. Badges & Risk Status Indicators</h2>
        <div className="flex flex-wrap items-center gap-3">
          <Badge variant="default">Default Tag</Badge>
          <Badge variant="success">Success</Badge>
          <Badge variant="warning">Warning</Badge>
          <Badge variant="danger">Danger</Badge>
          <Badge variant="info">Info Accent</Badge>
          <Badge variant="neutral">Neutral</Badge>
          <Badge variant="outline">Outline</Badge>
        </div>

        <div className="flex flex-wrap items-center gap-4 pt-2">
          <span className="text-xs text-slate-500 font-semibold">Risk Badges:</span>
          <RiskBadge level="LOW" score={12} showScore={true} />
          <RiskBadge level="MEDIUM" score={58} showScore={true} />
          <RiskBadge level="HIGH" score={92} showScore={true} />
        </div>

        <div className="flex flex-wrap items-center gap-4 pt-2">
          <span className="text-xs text-slate-500 font-semibold">Stock Status Badges:</span>
          <StockStatusBadge status="IN_STOCK" />
          <StockStatusBadge status="LOW_STOCK" />
          <StockStatusBadge status="OUT_OF_STOCK" />
          <StockStatusBadge status="EXCESS" />
        </div>

        <div className="flex flex-wrap items-center gap-4 pt-2">
          <span className="text-xs text-slate-500 font-semibold">Stat Deltas:</span>
          <StatDelta value={15.4} suffix="%" />
          <StatDelta value={-8.2} suffix="%" />
          <StatDelta value={12.0} isInverse={true} suffix="%" />
          <StatDelta value={0} suffix="%" />
        </div>
      </section>

      {/* 4. FORM CONTROLS */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 border-b pb-2">4. Form Inputs & Filters</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Input label="Standard Input" placeholder="Type text here..." helperText="Helpful input guidance" />
          <Input label="Validation Error" defaultValue="Invalid text" error="This field requires a valid number." />
          <Select label="Dropdown Selector">
            <option>Option One</option>
            <option>Option Two</option>
          </Select>
        </div>
        <div className="flex flex-wrap items-center gap-4 pt-2">
          <SearchInput placeholder="Debounced 300ms search..." onSearch={(q) => console.log(q)} className="w-72" />
          <DateRangePicker value={dateRange} onChange={setDateRange} />
        </div>
      </section>

      {/* 5. TOAST NOTIFICATIONS */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 border-b pb-2">5. Toast Feedback System</h2>
        <div className="flex flex-wrap items-center gap-3">
          <Button variant="outline" size="sm" onClick={() => success('Operation Successful', 'Transaction committed to database.')}>
            Trigger Success Toast
          </Button>
          <Button variant="outline" size="sm" onClick={() => error('Action Rejected', 'Stock position cannot be negative.')}>
            Trigger Error Toast
          </Button>
          <Button variant="outline" size="sm" onClick={() => warning('Threshold Warning', 'Safety stock breached for 2 items.')}>
            Trigger Warning Toast
          </Button>
          <Button variant="outline" size="sm" onClick={() => info('Information Notice', 'Background sync finished.')}>
            Trigger Info Toast
          </Button>
        </div>
      </section>

      {/* 6. MODALS & DRAWERS */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 border-b pb-2">6. Overlays (Modal & Drawer)</h2>
        <div className="flex flex-wrap items-center gap-3">
          <Button variant="secondary" size="sm" onClick={() => setModalOpen(true)}>
            Open Sample Modal
          </Button>
          <Button variant="secondary" size="sm" onClick={() => setDrawerOpen(true)}>
            Open Sample Right Drawer
          </Button>
          <Button variant="destructive" size="sm" onClick={() => setConfirmOpen(true)}>
            Open Confirm Dialog
          </Button>
        </div>

        <Modal
          isOpen={modalOpen}
          onClose={() => setModalOpen(false)}
          title="Sample Dialog Modal"
          description="Accessible modal overlay testing keyboard escape and outside backdrop dismissal."
          footer={
            <Button variant="primary" size="sm" onClick={() => setModalOpen(false)}>
              Close Modal
            </Button>
          }
        >
          <p className="text-xs text-slate-600 leading-normal">
            This modal container can host complex forms, wizard steps, or transactional verification prompts.
          </p>
        </Modal>

        <Drawer
          isOpen={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          title="Detailed Side Drawer"
          subtitle="Sliding right inspection panel"
          width="md"
          footer={
            <Button variant="outline" size="sm" onClick={() => setDrawerOpen(false)}>
              Done
            </Button>
          }
        >
          <div className="space-y-3 text-xs">
            <p className="text-slate-600">
              Drawers are utilized for calculation chains, inline audit trails, and quick editing without losing table context.
            </p>
          </div>
        </Drawer>

        <ConfirmDialog
          isOpen={confirmOpen}
          onClose={() => setConfirmOpen(false)}
          onConfirm={() => {
            setConfirmOpen(false);
            success('Confirmed', 'Confirmed sensitive operation.');
          }}
          title="Deactivate Medicine?"
          message="Are you sure you want to soft-deactivate this item? Historical transaction data will remain preserved."
          confirmLabel="Deactivate"
          variant="danger"
        />
      </section>

      {/* 7. LOADING, SKELETON, EMPTY, AND ERROR STATES */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 border-b pb-2">7. State Feedback Components</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <EmptyState
            title="No Records Available"
            description="There are currently no items meeting your active filter criteria."
            actionLabel="Reset Search Filters"
            onAction={() => info('Reset Filters', 'All search filters cleared.')}
          />

          <ErrorState
            title="Network Connection Failed"
            message="Could not establish connection to the FastAPI backend service."
            technicalHint="ERR_CONNECTION_REFUSED at http://localhost:8000/api/v1/health"
            onRetry={() => info('Retrying Request', 'Attempting reconnect...')}
          />
        </div>

        <div className="pt-2">
          <span className="text-xs font-semibold text-slate-500 block mb-2">Skeleton Loading State:</span>
          <LoadingState type="stats" />
        </div>
      </section>

      {/* 8. DATA TABLE */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 border-b pb-2">8. Data Table Component</h2>
        <DataTable
          columns={tableCols}
          data={sampleTableData}
          keyExtractor={(r) => r.id}
          showPagination={false}
        />
      </section>

      {/* 9. CHARTS & GAUGES */}
      <section className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 border-b pb-2">9. Chart Visualizations</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <Card className="p-4">
            <h4 className="text-xs font-semibold text-slate-600 mb-3">Coverage Stock Gauges</h4>
            <div className="space-y-3">
              <StockGauge days={18.5} leadTimeDays={7} maxDays={30} />
              <StockGauge days={8.2} leadTimeDays={7} maxDays={30} />
              <StockGauge days={2.1} leadTimeDays={7} maxDays={30} />
            </div>
          </Card>

          <Card className="p-4">
            <h4 className="text-xs font-semibold text-slate-600 mb-3">Mini Inline Sparkline</h4>
            <div className="flex items-center justify-between py-2 border-b">
              <span className="text-xs text-slate-700">Antibiotics Trend:</span>
              <Sparkline data={[12, 14, 18, 15, 22, 28, 26, 32]} color="#0F766E" />
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-xs text-slate-700">Demand Fluctuation:</span>
              <Sparkline data={[45, 42, 38, 30, 24, 18, 12, 5]} color="#DC2626" />
            </div>
          </Card>

          <Card className="p-4">
            <h4 className="text-xs font-semibold text-slate-600 mb-1">Stock-Out Donut</h4>
            <RiskDonut low={45} medium={28} high={12} height={170} />
          </Card>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
          <KpiCard
            title="Total Medicines"
            value={85}
            subtitle="Across 11 categories"
            icon={<Boxes className="w-4 h-4" />}
          />
          <KpiCard
            title="Units in Stock"
            value={124800}
            delta={2.4}
            deltaContext="vs last week"
            icon={<PackageCheck className="w-4 h-4" />}
          />
          <KpiCard
            title="High Risk"
            value={12}
            alert={true}
            alertText="Immediate Action"
            delta={15.0}
            isInverseDelta={true}
            icon={<AlertOctagon className="w-4 h-4" />}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
          <Card className="p-4">
            <h4 className="text-xs font-semibold text-slate-600 mb-2">Category Demand (BarChart)</h4>
            <BarChart
              data={[
                { name: 'Antibiotics', value: 24500 },
                { name: 'Cardio', value: 31200 },
                { name: 'Analgesics', value: 18900 },
              ]}
              height={180}
            />
          </Card>

          <Card className="p-4">
            <h4 className="text-xs font-semibold text-slate-600 mb-2">Forecast Curve (LineForecastChart)</h4>
            <LineForecastChart
              data={[
                { date: '12/28', actualDemand: 50 },
                { date: '12/31', actualDemand: 55, predictedDemand: 55 },
                { date: '01/05', predictedDemand: 58, lowerBound: 50, upperBound: 66 },
              ]}
              height={180}
              splitDate="12/31"
            />
          </Card>
        </div>
      </section>
    </div>
  );
};
