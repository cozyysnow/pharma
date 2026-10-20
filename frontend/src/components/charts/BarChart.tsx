import React from 'react';
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { cn } from '../../utils/cn';

export interface BarChartItem {
  name: string;
  value: number;
  color?: string;
  secondaryValue?: number;
}

export interface BarChartProps {
  data: BarChartItem[];
  height?: number;
  color?: string;
  layout?: 'horizontal' | 'vertical';
  xAxisLabel?: string;
  yAxisLabel?: string;
  className?: string;
}

export const BarChart: React.FC<BarChartProps> = ({
  data,
  height = 260,
  color = '#0F766E',
  layout = 'horizontal',
  xAxisLabel,
  yAxisLabel,
  className,
}) => {
  const isVertical = layout === 'vertical';

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-900 text-white text-xs px-3 py-2 rounded shadow-lg border border-slate-700">
          <p className="font-semibold text-slate-100">{label}</p>
          <p className="text-primary-300 font-mono mt-0.5">
            {payload[0].value.toLocaleString()} {xAxisLabel || ''}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className={cn('w-full', className)} style={{ height }} title={yAxisLabel}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsBarChart
          data={data}
          layout={isVertical ? 'vertical' : 'horizontal'}
          margin={{ top: 10, right: 10, left: isVertical ? 60 : 0, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={!isVertical} />
          {isVertical ? (
            <>
              <XAxis
                type="number"
                tick={{ fill: '#64748B', fontSize: 11 }}
                axisLine={{ stroke: '#E2E8F0' }}
                tickLine={false}
              />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fill: '#475569', fontSize: 11 }}
                axisLine={{ stroke: '#E2E8F0' }}
                tickLine={false}
                width={80}
              />
            </>
          ) : (
            <>
              <XAxis
                dataKey="name"
                tick={{ fill: '#64748B', fontSize: 11 }}
                axisLine={{ stroke: '#E2E8F0' }}
                tickLine={false}
                interval={0}
                angle={data.length > 7 ? -25 : 0}
                textAnchor={data.length > 7 ? 'end' : 'middle'}
              />
              <YAxis
                tick={{ fill: '#64748B', fontSize: 11 }}
                axisLine={{ stroke: '#E2E8F0' }}
                tickLine={false}
                width={40}
              />
            </>
          )}
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="value" fill={color} radius={isVertical ? [0, 4, 4, 0] : [4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color || color} />
            ))}
          </Bar>
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  );
};
