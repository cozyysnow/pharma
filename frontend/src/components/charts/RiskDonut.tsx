import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { cn } from '../../utils/cn';

export interface RiskDonutProps {
  low: number;
  medium: number;
  high: number;
  height?: number;
  className?: string;
}

export const RiskDonut: React.FC<RiskDonutProps> = ({
  low,
  medium,
  high,
  height = 200,
  className,
}) => {
  const data = [
    { name: 'Low Risk', value: low, color: '#16A34A' },
    { name: 'Medium Risk', value: medium, color: '#D97706' },
    { name: 'High Risk', value: high, color: '#DC2626' },
  ];

  const total = low + medium + high;

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0];
      const pct = total > 0 ? ((item.value / total) * 100).toFixed(1) : '0';
      return (
        <div className="bg-slate-900 text-white text-xs px-2.5 py-1.5 rounded shadow-lg">
          <p className="font-semibold">{item.name}</p>
          <p className="text-slate-300">
            {item.value} medicines ({pct}%)
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className={cn('flex flex-col items-center w-full', className)}>
      <div className="relative w-full" style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip content={<CustomTooltip />} />
            <Pie
              data={data}
              innerRadius="65%"
              outerRadius="90%"
              paddingAngle={3}
              dataKey="value"
              stroke="none"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        {/* Center label */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-2xl font-bold text-slate-800 tabular-nums">{total}</span>
          <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Total</span>
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-4 mt-2 text-xs">
        {data.map((d) => (
          <div key={d.name} className="flex items-center gap-1.5">
            <span
              className="w-2.5 h-2.5 rounded-full shrink-0"
              style={{ backgroundColor: d.color }}
            />
            <span className="text-slate-600">{d.name}</span>
            <span className="font-semibold text-slate-900 tabular-nums">({d.value})</span>
          </div>
        ))}
      </div>
    </div>
  );
};
