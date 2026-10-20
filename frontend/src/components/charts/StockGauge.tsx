import React from 'react';
import { cn } from '../../utils/cn';

export interface StockGaugeProps {
  days: number;
  leadTimeDays?: number;
  maxDays?: number;
  showLabel?: boolean;
  className?: string;
}

export const StockGauge: React.FC<StockGaugeProps> = ({
  days,
  leadTimeDays = 7,
  maxDays = 30,
  showLabel = true,
  className,
}) => {
  const percentage = Math.min(100, Math.max(0, (days / maxDays) * 100));

  // Risk thresholds based on lead time
  // Critical: coverage < lead time (stockout inevitable without expediting)
  // Warning: coverage between lead time and lead time + 5 days
  // Safe: coverage > lead time + 5 days
  const isCritical = days <= leadTimeDays;
  const isWarning = days > leadTimeDays && days <= leadTimeDays + 5;

  const colorClass = isCritical
    ? 'bg-rose-500'
    : isWarning
    ? 'bg-amber-500'
    : 'bg-emerald-600';

  const textClass = isCritical
    ? 'text-rose-700 font-bold'
    : isWarning
    ? 'text-amber-700 font-semibold'
    : 'text-emerald-700 font-semibold';

  return (
    <div className={cn('w-full flex flex-col gap-1', className)}>
      {showLabel && (
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-500 font-medium">Coverage</span>
          <span className={cn('tabular-nums font-mono', textClass)}>
            {days.toFixed(1)} days
          </span>
        </div>
      )}
      <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden relative">
        {/* Lead time marker */}
        {leadTimeDays > 0 && leadTimeDays < maxDays && (
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-slate-400 z-10"
            style={{ left: `${(leadTimeDays / maxDays) * 100}%` }}
            title={`Lead Time (${leadTimeDays}d)`}
          />
        )}
        <div
          className={cn('h-full rounded-full transition-all duration-300', colorClass)}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
