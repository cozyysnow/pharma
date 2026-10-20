import React from 'react';
import { CheckCircle2, AlertCircle, XCircle, ArrowUpCircle } from 'lucide-react';
import { cn } from '../../utils/cn';

import type { StockStatus } from '../../types/domain';
export type { StockStatus };

export interface StockStatusBadgeProps {
  status: StockStatus;
  size?: 'sm' | 'md';
  className?: string;
}

export const StockStatusBadge: React.FC<StockStatusBadgeProps> = ({
  status,
  size = 'md',
  className,
}) => {
  const configs = {
    IN_STOCK: {
      label: 'In Stock',
      icon: <CheckCircle2 className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />,
      classes: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    },
    LOW_STOCK: {
      label: 'Low Stock',
      icon: <AlertCircle className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />,
      classes: 'bg-amber-50 text-amber-700 border-amber-200',
    },
    OUT_OF_STOCK: {
      label: 'Out of Stock',
      icon: <XCircle className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />,
      classes: 'bg-rose-50 text-rose-700 border-rose-200 font-semibold',
    },
    EXCESS: {
      label: 'Overstocked',
      icon: <ArrowUpCircle className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />,
      classes: 'bg-blue-50 text-blue-700 border-blue-200',
    },
    LOW: {
      label: 'Low Stock',
      icon: <AlertCircle className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />,
      classes: 'bg-amber-50 text-amber-700 border-amber-200',
    },
    CRITICAL: {
      label: 'Critical Stockout',
      icon: <XCircle className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />,
      classes: 'bg-rose-50 text-rose-700 border-rose-200 font-semibold',
    },
    ADEQUATE: {
      label: 'Adequate',
      icon: <CheckCircle2 className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />,
      classes: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    },
    OVERSTOCKED: {
      label: 'Overstocked',
      icon: <ArrowUpCircle className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />,
      classes: 'bg-blue-50 text-blue-700 border-blue-200',
    },
  };

  const config = (configs as Record<string, any>)[status] || configs.IN_STOCK;

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 border rounded-full font-medium select-none',
        size === 'sm' ? 'text-[11px] px-2 py-0.5' : 'text-xs px-2.5 py-1',
        config.classes,
        className
      )}
    >
      <span className="shrink-0">{config.icon}</span>
      <span>{config.label}</span>
    </span>
  );
};
