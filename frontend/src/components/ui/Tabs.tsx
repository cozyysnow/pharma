import React, { createContext, useContext } from 'react';
import { cn } from '../../utils/cn';

interface TabsContextType {
  activeTab: string;
  setActiveTab: (id: string) => void;
}

const TabsContext = createContext<TabsContextType | undefined>(undefined);

export interface TabsProps {
  defaultValue: string;
  value?: string;
  onValueChange?: (val: string) => void;
  children: React.ReactNode;
  className?: string;
}

export const Tabs: React.FC<TabsProps> = ({
  defaultValue,
  value,
  onValueChange,
  children,
  className,
}) => {
  const [selectedTab, setSelectedTab] = React.useState(value || defaultValue);

  const activeTab = value !== undefined ? value : selectedTab;
  const setActiveTab = (val: string) => {
    if (value === undefined) setSelectedTab(val);
    onValueChange?.(val);
  };

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className={cn('w-full flex flex-col', className)}>{children}</div>
    </TabsContext.Provider>
  );
};

export const TabList: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className,
}) => (
  <div
    className={cn(
      'flex items-center gap-1 border-b border-slate-200 overflow-x-auto custom-scrollbar pb-px',
      className
    )}
    role="tablist"
  >
    {children}
  </div>
);

export const TabTrigger: React.FC<{
  value: string;
  children: React.ReactNode;
  className?: string;
  badge?: React.ReactNode;
  icon?: React.ReactNode;
}> = ({ value, children, className, badge, icon }) => {
  const context = useContext(TabsContext);
  if (!context) throw new Error('TabTrigger must be used inside Tabs');

  const isActive = context.activeTab === value;

  return (
    <button
      type="button"
      role="tab"
      aria-selected={isActive}
      onClick={() => context.setActiveTab(value)}
      className={cn(
        'inline-flex items-center gap-2 px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px whitespace-nowrap cursor-pointer select-none',
        isActive
          ? 'border-primary-700 text-primary-700 font-semibold'
          : 'border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300',
        className
      )}
    >
      {icon && <span className="shrink-0">{icon}</span>}
      {children}
      {badge && <span className="shrink-0">{badge}</span>}
    </button>
  );
};

export const TabContent: React.FC<{
  value: string;
  children: React.ReactNode;
  className?: string;
}> = ({ value, children, className }) => {
  const context = useContext(TabsContext);
  if (!context) throw new Error('TabContent must be used inside Tabs');

  if (context.activeTab !== value) return null;

  return (
    <div role="tabpanel" className={cn('pt-4 animate-in fade-in duration-150', className)}>
      {children}
    </div>
  );
};
