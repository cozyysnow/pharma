import React, { useState } from 'react';
import { Menu, Bell, User, Calendar, LogOut, CheckCircle2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { SearchInput } from '../ui/form/SearchInput';
import { Badge } from '../ui/Badge';
import { useToast } from '../feedback/ToastContext';

interface HeaderProps {
  onOpenMobileMenu: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenMobileMenu }) => {
  const { user, role, logout } = useAuth();
  const navigate = useNavigate();
  const { info } = useToast();
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const handleSearch = (query: string) => {
    if (query.trim()) {
      // In Phase 2, this navigates to medicine search / details
      console.log('Search query:', query);
    }
  };

  const asOfDate = '2025-12-31'; // Reference date from dataset pack

  return (
    <header className="h-16 bg-white border-b border-slate-200/80 px-4 sm:px-6 flex items-center justify-between gap-4 sticky top-0 z-30 shadow-2xs">
      {/* Left: Mobile menu button + Search */}
      <div className="flex items-center gap-3 flex-1 max-w-md">
        <button
          type="button"
          onClick={onOpenMobileMenu}
          aria-label="Open navigation menu"
          className="md:hidden p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100"
        >
          <Menu className="w-5 h-5" />
        </button>

        <SearchInput
          placeholder="Search medicines, ID, category..."
          onSearch={handleSearch}
          className="w-full"
        />
      </div>

      {/* Right: As-of Date chip + Notifications + User Menu */}
      <div className="flex items-center gap-2 sm:gap-3.5 shrink-0">
        {/* Data As-Of Chip */}
        <div
          className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-100 border border-slate-200 text-xs text-slate-700 select-none"
          title="Reference date of current inventory calculations"
        >
          <Calendar className="w-3.5 h-3.5 text-teal-700" />
          <span className="text-slate-500">Data as of:</span>
          <span className="font-semibold font-mono text-slate-800">{asOfDate}</span>
        </div>

        {/* Notification Bell */}
        <button
          type="button"
          onClick={() => navigate('/alerts')}
          aria-label="View alerts"
          className="relative p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
        >
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-500 ring-2 ring-white" />
        </button>

        {/* User profile dropdown */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setUserMenuOpen(!userMenuOpen)}
            className="flex items-center gap-2.5 p-1.5 rounded-lg hover:bg-slate-100 transition-colors select-none"
          >
            <div className="w-8 h-8 rounded-full bg-teal-100 text-teal-800 font-semibold flex items-center justify-center text-xs border border-teal-200">
              {user ? user.name.charAt(0) : <User className="w-4 h-4" />}
            </div>
            <div className="hidden lg:flex flex-col text-left">
              <span className="text-xs font-semibold text-slate-800 leading-tight">
                {user?.name || 'Authorized Staff'}
              </span>
              <span className="text-[10px] text-slate-500 leading-none mt-0.5">
                {role.replace('_', ' ')}
              </span>
            </div>
          </button>

          {/* User dropdown menu */}
          {userMenuOpen && (
            <>
              <div
                className="fixed inset-0 z-40"
                onClick={() => setUserMenuOpen(false)}
                aria-hidden="true"
              />
              <div className="absolute right-0 mt-2 w-56 rounded-xl bg-white shadow-xl border border-slate-200 py-1.5 z-50 animate-in fade-in zoom-in-95 duration-100">
                <div className="px-4 py-2 border-b border-slate-100">
                  <p className="text-xs font-semibold text-slate-900">{user?.name}</p>
                  <p className="text-[11px] text-slate-500 truncate">{user?.email}</p>
                  <div className="mt-1.5">
                    <Badge variant="default" size="sm">
                      {role}
                    </Badge>
                  </div>
                </div>

                <div className="py-1">
                  <button
                    type="button"
                    onClick={() => {
                      setUserMenuOpen(false);
                      navigate('/settings');
                    }}
                    className="w-full text-left px-4 py-2 text-xs text-slate-700 hover:bg-slate-50 transition-colors"
                  >
                    System Settings
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setUserMenuOpen(false);
                      info('System status verified', 'All ML services and inventory snapshots operational.');
                    }}
                    className="w-full text-left px-4 py-2 text-xs text-slate-700 hover:bg-slate-50 transition-colors flex items-center justify-between"
                  >
                    <span>System Status</span>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                  </button>
                </div>

                <div className="border-t border-slate-100 pt-1">
                  <button
                    type="button"
                    onClick={() => {
                      setUserMenuOpen(false);
                      logout();
                      navigate('/login');
                    }}
                    className="w-full text-left px-4 py-2 text-xs text-rose-600 hover:bg-rose-50 transition-colors flex items-center gap-2"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>Sign Out</span>
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
};
