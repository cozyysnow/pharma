import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Boxes,
  Pill,
  ArrowLeftRight,
  TrendingUp,
  AlertOctagon,
  Truck,
  Bell,
  Database,
  FileBarChart,
  Settings,
  ChevronLeft,
  ChevronRight,
  Shield,
  Palette,
  X,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import type { UserRole } from '../../types/auth';
import { cn } from '../../utils/cn';

interface SidebarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  mobileOpen: boolean;
  onCloseMobile: () => void;
}

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string | number;
  roles?: UserRole[];
}

export const Sidebar: React.FC<SidebarProps> = ({
  isCollapsed,
  onToggleCollapse,
  mobileOpen,
  onCloseMobile,
}) => {
  const { role, setRole } = useAuth();

  const navigation: NavItem[] = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Inventory', href: '/inventory', icon: Boxes },
    { name: 'Medicines', href: '/medicines', icon: Pill },
    { name: 'Transactions', href: '/transactions', icon: ArrowLeftRight },
    { name: 'Demand Forecast', href: '/forecast', icon: TrendingUp },
    { name: 'Stock-Out Risk', href: '/risk', icon: AlertOctagon, badge: 'High' },
    { name: 'Replenishment', href: '/replenishment', icon: Truck },
    { name: 'Alerts', href: '/alerts', icon: Bell, badge: 5 },
    { name: 'Datasets', href: '/datasets', icon: Database, roles: ['ADMIN'] },
    { name: 'Reports', href: '/reports', icon: FileBarChart },
    { name: 'Settings', href: '/settings', icon: Settings },
    { name: 'UI Styleguide', href: '/_styleguide', icon: Palette },
  ];

  const filteredNav = navigation.filter((item) => {
    if (!item.roles) return true;
    return item.roles.includes(role);
  });

  const sidebarContent = (
    <div className="flex flex-col h-full bg-slate-900 text-slate-300">
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-slate-800 shrink-0">
        <NavLink
          to="/"
          className="flex items-center gap-3 overflow-hidden text-white group"
          onClick={onCloseMobile}
        >
          <div className="w-9 h-9 rounded-lg bg-teal-600 flex items-center justify-center text-white font-bold shadow-md shadow-teal-900/40 shrink-0">
            <Pill className="w-5 h-5 text-white" />
          </div>
          {!isCollapsed && (
            <div className="flex flex-col">
              <span className="font-bold text-sm tracking-tight text-white group-hover:text-teal-300 transition-colors">
                PharmaStock IQ
              </span>
              <span className="text-[10px] text-teal-400 font-medium -mt-0.5">
                Predictive Decision Support
              </span>
            </div>
          )}
        </NavLink>

        {/* Mobile close button */}
        <button
          type="button"
          onClick={onCloseMobile}
          className="md:hidden text-slate-400 hover:text-white p-1"
          aria-label="Close sidebar"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Navigation links */}
      <div className="flex-1 py-4 px-2 space-y-1 overflow-y-auto custom-scrollbar">
        {filteredNav.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.name}
              to={item.href}
              end={item.href === '/'}
              onClick={onCloseMobile}
              title={isCollapsed ? item.name : undefined}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-colors select-none group',
                  isActive
                    ? 'bg-teal-700/80 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/80'
                )
              }
            >
              <Icon className="w-4 h-4 shrink-0 transition-transform group-hover:scale-105" />
              {!isCollapsed && (
                <span className="flex-1 truncate text-xs">{item.name}</span>
              )}
              {!isCollapsed && item.badge && (
                <span
                  className={cn(
                    'text-[10px] px-1.5 py-0.5 rounded-full font-semibold',
                    item.name === 'Stock-Out Risk'
                      ? 'bg-rose-950 text-rose-300 border border-rose-800'
                      : 'bg-teal-950 text-teal-300 border border-teal-800'
                  )}
                >
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </div>

      {/* Dev Role Switcher */}
      <div className="p-3 border-t border-slate-800 shrink-0 bg-slate-950/60">
        {!isCollapsed ? (
          <div>
            <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1.5">
              <span className="flex items-center gap-1 font-semibold text-teal-400">
                <Shield className="w-3 h-3" />
                Active Role
              </span>
              <span className="text-[10px] text-slate-500">Dev Switcher</span>
            </div>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as UserRole)}
              className="w-full text-xs bg-slate-800 border border-slate-700 text-slate-200 rounded px-2 py-1.5 focus:outline-none focus:border-teal-500"
            >
              <option value="ADMIN">Admin (Full Access)</option>
              <option value="INVENTORY_MANAGER">Inventory Manager</option>
              <option value="PHARMACY_STAFF">Pharmacy Staff (Read/Ops)</option>
            </select>
          </div>
        ) : (
          <div className="flex justify-center" title={`Current Role: ${role}`}>
            <span className="w-2.5 h-2.5 rounded-full bg-teal-400" />
          </div>
        )}
      </div>

      {/* Collapse Desktop Toggle */}
      <div className="hidden md:flex items-center justify-end p-2 border-t border-slate-800 shrink-0">
        <button
          type="button"
          onClick={onToggleCollapse}
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside
        className={cn(
          'hidden md:block shrink-0 transition-all duration-200 border-r border-slate-800 z-20 h-screen sticky top-0',
          isCollapsed ? 'w-16' : 'w-60'
        )}
      >
        {sidebarContent}
      </aside>

      {/* Mobile Off-canvas Drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div
            className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs"
            onClick={onCloseMobile}
            aria-hidden="true"
          />
          <div className="fixed inset-y-0 left-0 w-64 shadow-2xl z-50 animate-in slide-in-from-left duration-200">
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
};
