import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { RoleSwitcher } from '../dev/RoleSwitcher';
import { Info } from 'lucide-react';

export const AppShell: React.FC = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen flex bg-surface-page font-sans text-slate-800 antialiased">
      {/* Sidebar navigation */}
      <Sidebar
        isCollapsed={isCollapsed}
        onToggleCollapse={() => setIsCollapsed(!isCollapsed)}
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header onOpenMobileMenu={() => setMobileOpen(true)} />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-layout w-full mx-auto">
          <Outlet />
        </main>

        {/* Global persistent decision support disclaimer per Sec. 6.3 */}
        <footer className="border-t border-slate-200/80 bg-white py-3 px-6 text-center text-xs text-slate-500">
          <div className="flex items-center justify-center gap-1.5 max-w-4xl mx-auto">
            <Info className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span>
              <strong>Decision support only.</strong> Recommendations require review and approval by authorized pharmacy staff. This system provides no medical diagnosis, treatment, or clinical advice.
            </span>
          </div>
        </footer>

        {/* Dev Role Switcher */}
        <RoleSwitcher />
      </div>
    </div>
  );
};
