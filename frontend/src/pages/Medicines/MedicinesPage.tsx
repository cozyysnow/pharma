import React, { useState, useEffect, useCallback } from 'react';
import { Plus, Pill, Truck, ExternalLink, RefreshCw, Edit, Trash2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '../../components/layout/PageHeader';
import { Button } from '../../components/ui/Button';
import { Tabs, TabList, TabTrigger, TabContent } from '../../components/ui/Tabs';
import { DataTable, type ColumnDef } from '../../components/ui/DataTable';
import { FilterBar } from '../../components/ui/form/FilterBar';
import { SearchInput } from '../../components/ui/form/SearchInput';
import { Modal } from '../../components/ui/Modal';
import { Input } from '../../components/ui/Input';
import { Select } from '../../components/ui/Select';
import { Badge } from '../../components/ui/Badge';
import { Pagination } from '../../components/ui/Pagination';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../components/feedback/ToastContext';
import { getMedicines, createMedicine, updateMedicine, deactivateMedicine } from '../../api/medicines';
import { getSuppliers } from '../../api/suppliers';
import { MOCK_CATEGORIES } from '../../mocks';
import type { Medicine, Supplier } from '../../types/domain';

export const MedicinesPage: React.FC = () => {
  const { role } = useAuth();
  const navigate = useNavigate();
  const { success, error: showError } = useToast();

  const [activeTab, setActiveTab] = useState('medicines');
  const [medicines, setMedicines] = useState<Medicine[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [totalMeds, setTotalMeds] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);

  // Modal states
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [editingMed, setEditingMed] = useState<Medicine | null>(null);
  const [formData, setFormData] = useState({
    medicine_id: '',
    display_name: '',
    generic_name: '',
    category_id: 'CAT01',
    primary_supplier_id: 'SUP01',
    dosage_form: 'Tablet',
    strength: '500mg',
    pack_size: 10,
    unit_of_measure: 'strip',
    unit_cost_inr: 50,
    unit_price_inr: 75,
  });

  const PAGE_SIZE = 15;

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [medsRes, suppsRes] = await Promise.all([
        getMedicines({
          search: search || undefined,
          category_id: categoryFilter || undefined,
          is_active: statusFilter === 'active' ? true : statusFilter === 'inactive' ? false : undefined,
          page,
          page_size: PAGE_SIZE,
        }),
        getSuppliers(),
      ]);
      setMedicines(medsRes.data);
      setTotalMeds(medsRes.total);
      setSuppliers(suppsRes);
    } catch (err) {
      showError('Failed to load medicines directory', String(err));
    } finally {
      setLoading(false);
    }
  }, [search, categoryFilter, statusFilter, page, showError]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSaveMedicine = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingMed) {
        await updateMedicine(editingMed.medicine_id, formData);
        success('Medicine Updated', `Updated details for ${formData.display_name}.`);
      } else {
        await createMedicine(formData);
        success('Medicine Registered', `Added ${formData.display_name} to the catalogue.`);
      }
      setIsAddModalOpen(false);
      setEditingMed(null);
      loadData();
    } catch (err) {
      showError('Action failed', String(err));
    }
  };

  const handleDeactivate = async (id: string, name: string) => {
    if (!window.confirm(`Are you sure you want to toggle active status for ${name}?`)) return;
    try {
      await deactivateMedicine(id);
      success('Status Changed', `Medicine status updated.`);
      loadData();
    } catch (err) {
      showError('Failed to update status', String(err));
    }
  };

  const openAddModal = () => {
    setEditingMed(null);
    setFormData({
      medicine_id: `MED${String(totalMeds + 1).padStart(3, '0')}`,
      display_name: '',
      generic_name: '',
      category_id: 'CAT01',
      primary_supplier_id: 'SUP01',
      dosage_form: 'Tablet',
      strength: '500mg',
      pack_size: 10,
      unit_of_measure: 'strip',
      unit_cost_inr: 50,
      unit_price_inr: 75,
    });
    setIsAddModalOpen(true);
  };

  const openEditModal = (med: Medicine) => {
    setEditingMed(med);
    setFormData({
      medicine_id: med.medicine_id,
      display_name: med.display_name,
      generic_name: med.generic_name,
      category_id: med.category_id,
      primary_supplier_id: med.primary_supplier_id,
      dosage_form: med.dosage_form,
      strength: med.strength,
      pack_size: med.pack_size,
      unit_of_measure: med.unit_of_measure,
      unit_cost_inr: med.unit_cost_inr,
      unit_price_inr: med.unit_price_inr,
    });
    setIsAddModalOpen(true);
  };

  const medicineCols: ColumnDef<Medicine>[] = [
    {
      key: 'medicine_id',
      header: 'Code',
      sortable: true,
      cell: (row) => (
        <span
          className="font-mono font-semibold text-teal-800 hover:underline cursor-pointer"
          onClick={() => navigate(`/medicines/${row.medicine_id}`)}
        >
          {row.medicine_id}
        </span>
      ),
    },
    {
      key: 'display_name',
      header: 'Brand / Display Name',
      sortable: true,
      cell: (row) => (
        <div>
          <div className="font-medium text-slate-900">{row.display_name}</div>
          <div className="text-xs text-slate-500">{row.generic_name} • {row.strength}</div>
        </div>
      ),
    },
    {
      key: 'category',
      header: 'Category',
      sortable: true,
      cell: (row) => (
        <span className="text-xs font-medium text-slate-700">
          {row.category?.category_name || row.category_id}
        </span>
      ),
    },
    {
      key: 'primary_supplier',
      header: 'Primary Supplier',
      cell: (row) => (
        <span className="text-xs text-slate-700">
          {row.primary_supplier?.supplier_name || row.primary_supplier_id}
        </span>
      ),
    },
    {
      key: 'dosage_form',
      header: 'Form & Pack',
      cell: (row) => (
        <span className="text-xs text-slate-600">
          {row.dosage_form} (Pack of {row.pack_size})
        </span>
      ),
    },
    {
      key: 'unit_price_inr',
      header: 'Price (INR)',
      isNumeric: true,
      sortable: true,
      cell: (row) => `₹${row.unit_price_inr.toFixed(2)}`,
    },
    {
      key: 'is_active',
      header: 'Status',
      cell: (row) => (
        <Badge variant={row.is_active ? 'success' : 'neutral'} size="sm">
          {row.is_active ? 'Active' : 'Inactive'}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      cell: (row) => (
        <div className="flex items-center gap-1.5">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate(`/medicines/${row.medicine_id}`)}
            title="View Details"
          >
            <ExternalLink className="w-3.5 h-3.5" />
          </Button>
          {role !== 'PHARMACY_STAFF' && (
            <>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => openEditModal(row)}
                title="Edit Master Record"
              >
                <Edit className="w-3.5 h-3.5 text-slate-600" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleDeactivate(row.medicine_id, row.display_name)}
                title="Toggle Active/Inactive"
              >
                <Trash2 className="w-3.5 h-3.5 text-rose-500" />
              </Button>
            </>
          )}
        </div>
      ),
    },
  ];

  const supplierCols: ColumnDef<Supplier>[] = [
    {
      key: 'supplier_id',
      header: 'Code',
      sortable: true,
      cell: (row) => <span className="font-mono font-semibold text-slate-700">{row.supplier_id}</span>,
    },
    {
      key: 'supplier_name',
      header: 'Supplier Name',
      sortable: true,
      cell: (row) => (
        <div>
          <span className="font-semibold text-slate-900">{row.supplier_name}</span>
          <div className="text-xs text-slate-500">{row.supplier_type} • {row.city}, {row.state}</div>
        </div>
      ),
    },
    {
      key: 'lead_time_mean_days',
      header: 'Mean Lead Time',
      isNumeric: true,
      sortable: true,
      cell: (row) => `${row.lead_time_mean_days}d (±${row.lead_time_sd_days}d)`,
    },
    {
      key: 'on_time_probability',
      header: 'On-Time Fill',
      isNumeric: true,
      sortable: true,
      cell: (row) => `${(row.on_time_probability * 100).toFixed(0)}%`,
    },
    {
      key: 'full_fill_probability',
      header: 'Full Fill',
      isNumeric: true,
      sortable: true,
      cell: (row) => `${(row.full_fill_probability * 100).toFixed(0)}%`,
    },
    {
      key: 'payment_terms_days',
      header: 'Terms',
      isNumeric: true,
      cell: (row) => `${row.payment_terms_days} days`,
    },
    {
      key: 'is_active',
      header: 'Status',
      cell: (row) => (
        <Badge variant={row.is_active ? 'success' : 'neutral'} size="sm">
          {row.is_active ? 'Active' : 'Inactive'}
        </Badge>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Medicines & Supplier Directory"
        subtitle="Maintain verified pharmaceutical master records, composition references, and supplier logistics profiles."
        actions={
          <div className="flex items-center gap-2">
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
                onClick={openAddModal}
              >
                Add Medicine
              </Button>
            )}
          </div>
        }
      />

      <Tabs defaultValue="medicines" value={activeTab} onValueChange={setActiveTab}>
        <TabList className="mb-4">
          <TabTrigger value="medicines" icon={<Pill className="w-4 h-4" />}>
            Medicines ({totalMeds})
          </TabTrigger>
          <TabTrigger value="suppliers" icon={<Truck className="w-4 h-4" />}>
            Suppliers ({suppliers.length})
          </TabTrigger>
        </TabList>

        <TabContent value="medicines">
          <FilterBar className="mb-4">
            <SearchInput
              placeholder="Search code, brand, or generic..."
              onSearch={(val) => { setSearch(val); setPage(1); }}
              className="w-72"
            />
            <div className="w-48">
              <Select
                value={categoryFilter}
                onChange={(e) => { setCategoryFilter(e.target.value); setPage(1); }}
              >
                <option value="">All Categories</option>
                {MOCK_CATEGORIES.map((c) => (
                  <option key={c.category_id} value={c.category_id}>
                    {c.category_name}
                  </option>
                ))}
              </Select>
            </div>
            <div className="w-36">
              <Select
                value={statusFilter}
                onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
              >
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </Select>
            </div>
          </FilterBar>

          <DataTable
            columns={medicineCols}
            data={medicines}
            keyExtractor={(row) => row.medicine_id}
            isLoading={loading}
          />

          <div className="mt-4 flex justify-between items-center text-xs text-slate-500">
            <span>Showing {(page - 1) * PAGE_SIZE + 1} to {Math.min(page * PAGE_SIZE, totalMeds)} of {totalMeds} medicines</span>
            <Pagination
              currentPage={page}
              totalPages={Math.ceil(totalMeds / PAGE_SIZE) || 1}
              onPageChange={setPage}
            />
          </div>
        </TabContent>

        <TabContent value="suppliers">
          <DataTable
            columns={supplierCols}
            data={suppliers}
            keyExtractor={(row) => row.supplier_id}
            isLoading={loading}
          />
        </TabContent>
      </Tabs>

      {/* Add / Edit Medicine Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title={editingMed ? `Edit ${editingMed.display_name}` : 'Register New Medicine'}
        description="Maintain verified master record properties, packaging, and supplier linkage."
        footer={
          <>
            <Button variant="outline" size="sm" onClick={() => setIsAddModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" onClick={handleSaveMedicine}>
              {editingMed ? 'Save Changes' : 'Create Medicine'}
            </Button>
          </>
        }
      >
        <form onSubmit={handleSaveMedicine} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Medicine Code (ID)"
              value={formData.medicine_id}
              disabled={!!editingMed}
              onChange={(e) => setFormData({ ...formData, medicine_id: e.target.value })}
              required
            />
            <Input
              label="Brand / Display Name"
              placeholder="e.g. Paracetamol 500mg"
              value={formData.display_name}
              onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
              required
            />
          </div>

          <Input
            label="Generic Name & Active Ingredients"
            placeholder="e.g. Acetaminophen"
            value={formData.generic_name}
            onChange={(e) => setFormData({ ...formData, generic_name: e.target.value })}
            required
          />

          <div className="grid grid-cols-2 gap-3">
            <Select
              label="Category"
              value={formData.category_id}
              onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
              required
            >
              {MOCK_CATEGORIES.map((c) => (
                <option key={c.category_id} value={c.category_id}>
                  {c.category_name}
                </option>
              ))}
            </Select>

            <Select
              label="Primary Supplier"
              value={formData.primary_supplier_id}
              onChange={(e) => setFormData({ ...formData, primary_supplier_id: e.target.value })}
              required
            >
              {suppliers.map((s) => (
                <option key={s.supplier_id} value={s.supplier_id}>
                  {s.supplier_name}
                </option>
              ))}
            </Select>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <Input
              label="Form"
              value={formData.dosage_form}
              onChange={(e) => setFormData({ ...formData, dosage_form: e.target.value })}
              required
            />
            <Input
              label="Strength"
              value={formData.strength}
              onChange={(e) => setFormData({ ...formData, strength: e.target.value })}
              required
            />
            <Input
              label="Pack Size"
              type="number"
              value={formData.pack_size}
              onChange={(e) => setFormData({ ...formData, pack_size: parseInt(e.target.value) || 1 })}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Cost Price (₹)"
              type="number"
              step="0.01"
              value={formData.unit_cost_inr}
              onChange={(e) => setFormData({ ...formData, unit_cost_inr: parseFloat(e.target.value) || 0 })}
              required
            />
            <Input
              label="Selling Price (₹)"
              type="number"
              step="0.01"
              value={formData.unit_price_inr}
              onChange={(e) => setFormData({ ...formData, unit_price_inr: parseFloat(e.target.value) || 0 })}
              required
            />
          </div>
        </form>
      </Modal>
    </div>
  );
};
