import React from 'react';
import { ShieldCheck, AlertTriangle, AlertOctagon } from 'lucide-react';
import { cn } from '../../utils/cn';

import type { RiskLevel } from '../../types/domain';
export type { RiskLevel };

export interface RiskBadgeProps {
  level: RiskLevel;
  score?: number;
  showScore?: boolean;
  size?: 'sm' | 'md';
  className?: string;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  level,
  score,
  showScore = false,
  size = 'md',
  className,
}) => {
  const configs = {
    LOW: {
      label: 'Low Risk',
      icon: <ShieldCheck className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />,
      classes: 'bg-risk-low-bg text-risk-low-text border-risk-low-border',
    },
    MEDIUM: {
      label: 'Medium Risk',
      icon: <AlertTriangle className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />,
      classes: 'bg-risk-medium-bg text-risk-medium-text border-risk-medium-border',
    },
    HIGH: {
      label: 'High Risk',
      icon: <AlertOctagon className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />,
      classes: 'bg-risk-high-bg text-risk-high-text border-risk-high-border font-semibold',
    },
    CRITICAL: {
      label: 'Critical Risk',
      icon: <AlertOctagon className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />,
      classes: 'bg-rose-100 text-rose-800 border-rose-300 font-bold',
    },
  };

  const config = (configs as Record<string, any>)[level] || configs.LOW;

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
      {showScore && score !== undefined && (
        <span className="opacity-80 font-mono text-[11px] ml-0.5">({score}%)</span>
      )}
    </span>
  );
};
