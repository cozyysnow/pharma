import React, { useState } from 'react';
import { UserCheck, Shield, ChevronUp, ChevronDown } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import type { UserRole } from '../../types/auth';

const ROLES: { role: UserRole; name: string; title: string; color: string }[] = [
  { role: 'ADMIN', name: 'Dr. Sarah Mitchell', title: 'Admin (Full Access)', color: 'bg-teal-600 text-white' },
  { role: 'INVENTORY_MANAGER', name: 'Rajesh Sharma', title: 'Inventory Manager', color: 'bg-indigo-600 text-white' },
  { role: 'PHARMACY_STAFF', name: 'Ananya Patel', title: 'Pharmacy Staff (Read-Only Ops)', color: 'bg-slate-700 text-white' },
];

export const RoleSwitcher: React.FC = () => {
  const { role, setRole } = useAuth();
  const [isOpen, setIsOpen] = useState(false);

  const current = ROLES.find((r) => r.role === role) || ROLES[0];

  return (
    <div className="fixed bottom-4 right-4 z-50 select-none">
      <div className="bg-white/95 backdrop-blur shadow-xl border border-slate-300 rounded-xl overflow-hidden transition-all text-xs">
        {isOpen && (
          <div className="p-2 border-b border-slate-200 bg-slate-50 space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block px-2 py-0.5">
              Dev Role Switcher
            </span>
            {ROLES.map((r) => (
              <button
                key={r.role}
                type="button"
                onClick={() => {
                  setRole(r.role);
                  setIsOpen(false);
                }}
                className={`w-full text-left px-3 py-1.5 rounded-lg font-medium transition-all flex items-center justify-between ${
                  role === r.role
                    ? 'bg-teal-700 text-white shadow-2xs'
                    : 'text-slate-700 hover:bg-slate-200/70'
                }`}
              >
                <div>
                  <div className="font-semibold">{r.title}</div>
                  <div className={`text-[10px] ${role === r.role ? 'text-teal-100' : 'text-slate-400'}`}>
                    {r.name}
                  </div>
                </div>
                {role === r.role && <UserCheck className="w-4 h-4 ml-2 shrink-0" />}
              </button>
            ))}
          </div>
        )}

        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-2 px-3 py-2 text-slate-800 hover:bg-slate-50 w-full font-medium"
        >
          <Shield className="w-3.5 h-3.5 text-teal-700" />
          <span className="text-[11px] font-semibold">Active Role:</span>
          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${current.color}`}>
            {current.role}
          </span>
          {isOpen ? <ChevronDown className="w-3.5 h-3.5 text-slate-400 ml-1" /> : <ChevronUp className="w-3.5 h-3.5 text-slate-400 ml-1" />}
        </button>
      </div>
    </div>
  );
};
