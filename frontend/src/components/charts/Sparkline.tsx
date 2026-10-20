import React from 'react';
import { cn } from '../../utils/cn';

export interface SparklineProps {
  data: number[];
  color?: string;
  width?: number;
  height?: number;
  showFill?: boolean;
  className?: string;
}

export const Sparkline: React.FC<SparklineProps> = ({
  data,
  color = '#0F766E',
  width = 90,
  height = 24,
  showFill = true,
  className,
}) => {
  if (!data || data.length < 2) {
    return <div className="h-6 w-20 bg-slate-100 rounded" />;
  }

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;

  const points = data.map((val, i) => {
    const x = (i / (data.length - 1)) * (width - 4) + 2;
    const y = height - 4 - ((val - min) / range) * (height - 8) + 2;
    return `${x},${y}`;
  });

  const pathD = `M ${points.join(' L ')}`;
  const fillD = `${pathD} L ${width - 2},${height} L 2,${height} Z`;

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      className={cn('overflow-visible shrink-0', className)}
    >
      {showFill && (
        <path
          d={fillD}
          fill={color}
          fillOpacity={0.15}
          stroke="none"
        />
      )}
      <path
        d={pathD}
        fill="none"
        stroke={color}
        strokeWidth={1.75}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};
