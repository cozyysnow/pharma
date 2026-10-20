import React, { useState } from 'react';
import { User, Sliders, Users, Cpu, Info, Check } from 'lucide-react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Tabs, TabList, TabTrigger, TabContent } from '../../components/ui/Tabs';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Badge } from '../../components/ui/Badge';
import { DataTable, type ColumnDef } from '../../components/ui/DataTable';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../components/feedback/ToastContext';

export const SettingsPage: React.FC = () => {
  const { user, role } = useAuth();
  const { success } = useToast();
  const [activeTab, setActiveTab] = useState('profile');

  // Parameter states
  const [horizonDays, setHorizonDays] = useState(30);
  const [serviceLevelZ, setServiceLevelZ] = useState(1.65); // 95% service level
  const [spikeThresholdPct, setSpikeThresholdPct] = useState(30);

  const sampleUsers = [
    { id: 1, name: 'Dr. Sarah Mitchell', email: 'admin@pharmastock.local', role: 'ADMIN', status: 'ACTIVE' },
    { id: 2, name: 'Rajesh Sharma', email: 'manager@pharmastock.local', role: 'INVENTORY_MANAGER', status: 'ACTIVE' },
    { id: 3, name: 'Ananya Patel', email: 'staff@pharmastock.local', role: 'PHARMACY_STAFF', status: 'ACTIVE' },
  ];

  const userCols: ColumnDef<any>[] = [
    { key: 'name', header: 'Name', cell: (r) => <span className="font-semibold text-slate-900">{r.name}</span> },
    { key: 'email', header: 'Email' },
    { key: 'role', header: 'System Role', cell: (r) => <Badge variant="default" size="sm">{r.role}</Badge> },
    { key: 'status', header: 'Status', cell: (r) => <Badge variant="success" size="sm">{r.status}</Badge> },
  ];

  return (
    <div>
      <PageHeader
        title="System Settings & Administration"
        subtitle="Manage user profiles, inventory threshold parameters, machine learning configurations, and system provenance."
      />

      <Tabs defaultValue="profile" value={activeTab} onValueChange={setActiveTab}>
        <TabList className="mb-6">
          <TabTrigger value="profile" icon={<User className="w-4 h-4" />}>
            My Profile
          </TabTrigger>
          {role === 'ADMIN' && (
            <>
              <TabTrigger value="thresholds" icon={<Sliders className="w-4 h-4" />}>
                Thresholds & Parameters
              </TabTrigger>
              <TabTrigger value="users" icon={<Users className="w-4 h-4" />}>
                User Management
              </TabTrigger>
              <TabTrigger value="model" icon={<Cpu className="w-4 h-4" />}>
                ML Model Config
              </TabTrigger>
            </>
          )}
          <TabTrigger value="about" icon={<Info className="w-4 h-4" />}>
            About & Disclaimer
          </TabTrigger>
        </TabList>

        {/* PROFILE TAB */}
        <TabContent value="profile">
          <Card className="max-w-2xl">
            <CardHeader>
              <CardTitle>User Profile</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input label="Full Name" defaultValue={user?.name || ''} readOnly />
              <Input label="Email Address" defaultValue={user?.email || ''} readOnly />
              <div>
                <label className="text-xs font-medium text-slate-700 block mb-1">
                  Assigned RBAC Role
                </label>
                <div className="flex items-center gap-2">
                  <Badge variant="default" size="md">
                    {role}
                  </Badge>
                  <span className="text-xs text-slate-500">Managed by System Administrator</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabContent>

        {/* THRESHOLDS TAB (ADMIN ONLY) */}
        {role === 'ADMIN' && (
          <TabContent value="thresholds">
            <Card className="max-w-2xl">
              <CardHeader>
                <CardTitle>Inventory & Risk Decision Parameters</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  label="Default Forecast Horizon (Days)"
                  type="number"
                  value={horizonDays}
                  onChange={(e) => setHorizonDays(parseInt(e.target.value) || 30)}
                  helperText="Standard number of future days projected during ML recursive inference (7, 14, or 30 days)."
                />
                <Input
                  label="Safety Stock Service Factor (Z-Score)"
                  type="number"
                  step="0.05"
                  value={serviceLevelZ}
                  onChange={(e) => setServiceLevelZ(parseFloat(e.target.value) || 1.65)}
                  helperText="Default 1.65 corresponds to a 95% cycle service level target."
                />
                <Input
                  label="Demand Spike Alert Trigger (%)"
                  type="number"
                  value={spikeThresholdPct}
                  onChange={(e) => setSpikeThresholdPct(parseInt(e.target.value) || 30)}
                  helperText="Percentage surge over historical rolling average to generate automated DEMAND_SPIKE alert."
                />
              </CardContent>
              <CardFooter className="justify-end">
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => success('Parameters Saved', 'Updated system threshold configuration.')}
                  leftIcon={<Check className="w-4 h-4" />}
                >
                  Save Parameters
                </Button>
              </CardFooter>
            </Card>
          </TabContent>
        )}

        {/* USERS TAB (ADMIN ONLY) */}
        {role === 'ADMIN' && (
          <TabContent value="users">
            <Card>
              <CardHeader>
                <CardTitle>System Users & Permissions</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <DataTable
                  columns={userCols}
                  data={sampleUsers}
                  keyExtractor={(r) => r.id}
                  showPagination={false}
                />
              </CardContent>
            </Card>
          </TabContent>
        )}

        {/* MODEL TAB (ADMIN ONLY) */}
        {role === 'ADMIN' && (
          <TabContent value="model">
            <Card className="max-w-2xl">
              <CardHeader>
                <CardTitle>Active Machine Learning Architecture</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 text-xs">
                <div className="p-3 bg-slate-50 border rounded-lg">
                  <span className="font-semibold text-slate-800">Selected Algorithm</span>
                  <p className="font-mono text-teal-800 font-bold mt-0.5">GradientBoostingRegressor (scikit-learn)</p>
                </div>
                <div className="p-3 bg-slate-50 border rounded-lg">
                  <span className="font-semibold text-slate-800">Training Strategy</span>
                  <p className="text-slate-600 mt-0.5">
                    Strict chronological split (Train: 2021-2023, Val: 2024, Test: 2025). No future lookahead or target leakage.
                  </p>
                </div>
                <div className="p-3 bg-slate-50 border rounded-lg">
                  <span className="font-semibold text-slate-800">Performance Metric</span>
                  <p className="text-slate-600 mt-0.5">
                    Test Period MAE: <strong>8.072</strong> (beats Naive Lag-1 baseline 10.984).
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabContent>
        )}

        {/* ABOUT & DISCLAIMER TAB */}
        <TabContent value="about">
          <Card className="max-w-3xl">
            <CardHeader>
              <CardTitle>Product Provenance & Legal Limitations</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-xs text-slate-700 leading-relaxed">
              <div className="p-4 bg-teal-50 border border-teal-200 rounded-lg text-teal-900">
                <h4 className="font-bold text-sm mb-1">PharmaStock IQ v1.0</h4>
                <p>
                  Pharmacy Stock-Out Prediction & Inventory Decision Support System. Developed as a demonstrable B.Tech live project.
                </p>
              </div>

              <div>
                <h4 className="font-bold text-slate-900 mb-1">Dataset Origin & Provenance</h4>
                <p>
                  The dataset contains approximately 155,210 structured daily records across 85 medicines and 15 suppliers from 2021 to 2025.
                  It contains no personal patient data, no medical health records, and no prescription identifiers.
                </p>
              </div>

              <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg text-amber-900">
                <h4 className="font-bold mb-1">Human-in-the-Loop Operational Scope</h4>
                <p>
                  This application functions strictly as a decision-support and forecasting tool for inventory replenishment.
                  It does NOT perform autonomous purchasing, does not contact suppliers directly, and does NOT provide medical diagnosis,
                  drug substitutions, dosage calculations, or clinical advice.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabContent>
      </Tabs>
    </div>
  );
};
