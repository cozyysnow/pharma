import React from 'react';
import { Card } from '../ui/Card';
import { StatDelta } from './StatDelta';
import { Skeleton } from '../ui/Skeleton';
import { cn } from '../../utils/cn';

export interface KpiCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  delta?: number;
  deltaSuffix?: string;
  isInverseDelta?: boolean;
  deltaContext?: string;
  isLoading?: boolean;
  alert?: boolean;
  alertText?: string;
  className?: string;
  onClick?: () => void;
}

export const KpiCard: React.FC<KpiCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  delta,
  deltaSuffix = '%',
  isInverseDelta = false,
  deltaContext,
  isLoading = false,
  alert = false,
  alertText,
  className,
  onClick,
}) => {
  return (
    <Card
      className={cn(
        'p-5 flex flex-col justify-between transition-all relative overflow-hidden',
        alert && 'border-rose-200 bg-rose-50/20',
        onClick && 'cursor-pointer hover:border-slate-300 hover:shadow-md',
        className
      )}
      onClick={onClick}
    >
      <div>
        <div className="flex items-center justify-between gap-2 mb-2">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</span>
          {icon && (
            <div
              className={cn(
                'w-8 h-8 rounded-lg flex items-center justify-center shrink-0',
                alert ? 'bg-rose-100 text-rose-700' : 'bg-primary-50 text-primary-700'
              )}
            >
              {icon}
            </div>
          )}
        </div>

        {isLoading ? (
          <Skeleton className="h-8 w-28 my-1" />
        ) : (
          <div className="text-2xl font-bold tracking-tight text-slate-900 tabular-nums">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </div>
        )}
      </div>

      <div className="mt-3 flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100">
        {isLoading ? (
          <Skeleton className="h-4 w-36" />
        ) : (
          <>
            <div className="flex items-center gap-1.5 flex-wrap">
              {delta !== undefined && (
                <StatDelta
                  value={delta}
                  suffix={deltaSuffix}
                  isInverse={isInverseDelta}
                />
              )}
              {deltaContext && <span className="text-slate-400">{deltaContext}</span>}
              {!delta && subtitle && <span>{subtitle}</span>}
            </div>

            {alert && alertText && (
              <span className="text-[11px] font-semibold text-rose-600 bg-rose-100/80 px-2 py-0.5 rounded-full">
                {alertText}
              </span>
            )}
          </>
        )}
      </div>
    </Card>
  );
};
