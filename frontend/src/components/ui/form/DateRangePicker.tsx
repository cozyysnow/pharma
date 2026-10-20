import React from 'react';
import { Calendar } from 'lucide-react';
import { format, subDays, startOfYear } from 'date-fns';
import { cn } from '../../../utils/cn';

export interface DateRange {
  startDate: string;
  endDate: string;
}

export interface DateRangePickerProps {
  value: DateRange;
  onChange: (range: DateRange) => void;
  className?: string;
  showPresets?: boolean;
}

export const DateRangePicker: React.FC<DateRangePickerProps> = ({
  value,
  onChange,
  className,
  showPresets = true,
}) => {
  const setPreset = (days: number) => {
    const end = new Date();
    const start = subDays(end, days);
    onChange({
      startDate: format(start, 'yyyy-MM-dd'),
      endDate: format(end, 'yyyy-MM-dd'),
    });
  };

  const setYTD = () => {
    const end = new Date();
    const start = startOfYear(end);
    onChange({
      startDate: format(start, 'yyyy-MM-dd'),
      endDate: format(end, 'yyyy-MM-dd'),
    });
  };

  return (
    <div className={cn('flex flex-wrap items-center gap-2', className)}>
      <div className="flex items-center gap-1.5 bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 shadow-xs">
        <Calendar className="w-3.5 h-3.5 text-slate-400 shrink-0" />
        <input
          type="date"
          value={value.startDate}
          onChange={(e) => onChange({ ...value, startDate: e.target.value })}
          className="bg-transparent border-0 p-0 text-xs text-slate-800 focus:outline-none focus:ring-0"
        />
        <span className="text-slate-400">to</span>
        <input
          type="date"
          value={value.endDate}
          onChange={(e) => onChange({ ...value, endDate: e.target.value })}
          className="bg-transparent border-0 p-0 text-xs text-slate-800 focus:outline-none focus:ring-0"
        />
      </div>

      {showPresets && (
        <div className="hidden sm:flex items-center gap-1">
          <button
            type="button"
            onClick={() => setPreset(7)}
            className="text-[11px] font-medium text-slate-500 hover:text-slate-800 px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 transition-colors"
          >
            7D
          </button>
          <button
            type="button"
            onClick={() => setPreset(30)}
            className="text-[11px] font-medium text-slate-500 hover:text-slate-800 px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 transition-colors"
          >
            30D
          </button>
          <button
            type="button"
            onClick={() => setPreset(90)}
            className="text-[11px] font-medium text-slate-500 hover:text-slate-800 px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 transition-colors"
          >
            90D
          </button>
          <button
            type="button"
            onClick={setYTD}
            className="text-[11px] font-medium text-slate-500 hover:text-slate-800 px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 transition-colors"
          >
            YTD
          </button>
        </div>
      )}
    </div>
  );
};
