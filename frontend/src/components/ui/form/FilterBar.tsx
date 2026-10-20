import React from 'react';
import { RotateCcw } from 'lucide-react';
import { cn } from '../../../utils/cn';

export interface FilterBarProps {
  children?: React.ReactNode;
  onReset?: () => void;
  hasActiveFilters?: boolean;
  className?: string;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  children,
  onReset,
  hasActiveFilters = false,
  className,
}) => {
  return (
    <div
      className={cn(
        'flex flex-wrap items-center justify-between gap-3 p-3 bg-white rounded-lg border border-slate-200/80 shadow-xs',
        className
      )}
    >
      <div className="flex flex-wrap items-center gap-2.5 flex-1">{children}</div>

      {hasActiveFilters && onReset && (
        <button
          type="button"
          onClick={onReset}
          className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500 hover:text-rose-600 transition-colors px-2 py-1 rounded hover:bg-slate-100"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset Filters</span>
        </button>
      )}
    </div>
  );
};
