import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '../../utils/cn';

export interface StatDeltaProps {
  value: number;
  suffix?: string;
  isInverse?: boolean; // When higher is worse (e.g., risk score or stockouts)
  className?: string;
}

export const StatDelta: React.FC<StatDeltaProps> = ({
  value,
  suffix = '%',
  isInverse = false,
  className,
}) => {
  if (value === 0) {
    return (
      <span className={cn('inline-flex items-center gap-1 text-xs text-slate-500 font-medium', className)}>
        <Minus className="w-3.5 h-3.5" />
        <span>0{suffix}</span>
      </span>
    );
  }

  const isPositive = value > 0;
  const isGood = isInverse ? !isPositive : isPositive;

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 text-xs font-semibold tabular-nums',
        isGood ? 'text-emerald-600' : 'text-rose-600',
        className
      )}
    >
      {isPositive ? (
        <TrendingUp className="w-3.5 h-3.5" />
      ) : (
        <TrendingDown className="w-3.5 h-3.5" />
      )}
      <span>
        {isPositive ? '+' : ''}
        {value}
        {suffix}
      </span>
    </span>
  );
};
