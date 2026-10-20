import React from 'react';
import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { cn } from '../../utils/cn';

export interface ForecastPoint {
  date: string;
  actualDemand?: number;
  predictedDemand?: number;
  lowerBound?: number;
  upperBound?: number;
  isForecast?: boolean;
}

export interface LineForecastChartProps {
  data: ForecastPoint[];
  height?: number;
  leadTimeDays?: number;
  splitDate?: string;
  unit?: string;
  className?: string;
}

export const LineForecastChart: React.FC<LineForecastChartProps> = ({
  data,
  height = 320,
  splitDate,
  unit = 'units',
  className,
}) => {
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-900 text-white text-xs p-3 rounded-lg shadow-xl border border-slate-700 min-w-[160px]">
          <p className="font-semibold text-slate-200 border-b border-slate-700 pb-1 mb-1.5">{label}</p>
          {payload.map((p: any, i: number) => {
            if (p.dataKey === 'actualDemand' && p.value !== undefined) {
              return (
                <div key={i} className="flex justify-between items-center gap-2 py-0.5">
                  <span className="text-slate-400">Actual Demand:</span>
                  <span className="font-mono font-semibold text-slate-100">{p.value} {unit}</span>
                </div>
              );
            }
            if (p.dataKey === 'predictedDemand' && p.value !== undefined) {
              return (
                <div key={i} className="flex justify-between items-center gap-2 py-0.5">
                  <span className="text-teal-400">Forecast:</span>
                  <span className="font-mono font-semibold text-teal-300">{p.value} {unit}</span>
                </div>
              );
            }
            if (p.dataKey === 'upperBound' && p.value !== undefined) {
              return (
                <div key={i} className="flex justify-between items-center gap-2 py-0.5 text-slate-400">
                  <span>95% Interval:</span>
                  <span className="font-mono text-[11px]">
                    {p.payload.lowerBound} – {p.value}
                  </span>
                </div>
              );
            }
            return null;
          })}
        </div>
      );
    }
    return null;
  };

  return (
    <div className={cn('w-full', className)} style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 10, right: 15, left: -10, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
          <XAxis
            dataKey="date"
            tick={{ fill: '#64748B', fontSize: 11 }}
            axisLine={{ stroke: '#E2E8F0' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: '#64748B', fontSize: 11 }}
            axisLine={{ stroke: '#E2E8F0' }}
            tickLine={false}
            width={45}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="top"
            height={36}
            iconType="circle"
            wrapperStyle={{ fontSize: 12, color: '#475569' }}
          />

          {splitDate && (
            <ReferenceLine
              x={splitDate}
              stroke="#D97706"
              strokeDasharray="4 4"
              label={{
                value: 'Forecast Start',
                position: 'top',
                fill: '#D97706',
                fontSize: 10,
              }}
            />
          )}

          {/* Confidence interval area */}
          <Area
            type="monotone"
            dataKey="upperBound"
            stroke="none"
            fill="#0F766E"
            fillOpacity={0.12}
            name="Forecast 95% Band"
          />

          {/* Historical actual demand */}
          <Line
            type="monotone"
            dataKey="actualDemand"
            stroke="#475569"
            strokeWidth={2}
            dot={{ r: 2, fill: '#475569' }}
            activeDot={{ r: 5 }}
            name="Actual Demand"
          />

          {/* Predicted forecast line */}
          <Line
            type="monotone"
            dataKey="predictedDemand"
            stroke="#0F766E"
            strokeWidth={2.5}
            strokeDasharray="5 5"
            dot={{ r: 3, fill: '#0F766E' }}
            activeDot={{ r: 5 }}
            name="Forecasted Demand"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};
