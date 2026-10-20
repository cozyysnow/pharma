import React from 'react';
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import { cn } from '../../utils/cn';

export interface TableProps extends React.HTMLAttributes<HTMLTableElement> {
  zebra?: boolean;
}

export const Table = React.forwardRef<HTMLTableElement, TableProps>(
  ({ className, zebra = false, ...props }, ref) => (
    <div className="relative w-full overflow-auto custom-scrollbar border border-slate-200 rounded-lg">
      <table
        ref={ref}
        className={cn('w-full caption-bottom text-sm text-left border-collapse', zebra && 'table-zebra', className)}
        {...props}
      />
    </div>
  )
);
Table.displayName = 'Table';

export const TableHeader = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <thead ref={ref} className={cn('bg-slate-50/90 text-slate-700 text-xs uppercase tracking-wider sticky top-0 z-10 border-b border-slate-200', className)} {...props} />
));
TableHeader.displayName = 'TableHeader';

export const TableBody = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <tbody ref={ref} className={cn('divide-y divide-slate-100 bg-white', className)} {...props} />
));
TableBody.displayName = 'TableBody';

export const TableRow = React.forwardRef<
  HTMLTableRowElement,
  React.HTMLAttributes<HTMLTableRowElement> & { isHoverable?: boolean; isSelected?: boolean }
>(({ className, isHoverable = true, isSelected = false, ...props }, ref) => (
  <tr
    ref={ref}
    className={cn(
      'transition-colors',
      isHoverable && 'hover:bg-slate-50/80 cursor-pointer',
      isSelected && 'bg-primary-50/50',
      className
    )}
    {...props}
  />
));
TableRow.displayName = 'TableRow';

export interface TableHeadProps extends React.ThHTMLAttributes<HTMLTableCellElement> {
  isNumeric?: boolean;
  sortDirection?: 'asc' | 'desc' | false;
  onSort?: () => void;
}

export const TableHead = React.forwardRef<HTMLTableCellElement, TableHeadProps>(
  ({ className, children, isNumeric = false, sortDirection, onSort, ...props }, ref) => (
    <th
      ref={ref}
      className={cn(
        'h-10 px-4 font-semibold text-slate-600 align-middle select-none',
        isNumeric ? 'text-right' : 'text-left',
        onSort && 'cursor-pointer hover:bg-slate-100/80',
        className
      )}
      onClick={onSort}
      {...props}
    >
      <div className={cn('inline-flex items-center gap-1.5', isNumeric && 'justify-end w-full')}>
        <span>{children}</span>
        {onSort && (
          <span className="text-slate-400">
            {sortDirection === 'asc' ? (
              <ArrowUp className="w-3.5 h-3.5 text-primary-700" />
            ) : sortDirection === 'desc' ? (
              <ArrowDown className="w-3.5 h-3.5 text-primary-700" />
            ) : (
              <ArrowUpDown className="w-3 h-3 opacity-40 hover:opacity-100" />
            )}
          </span>
        )}
      </div>
    </th>
  )
);
TableHead.displayName = 'TableHead';

export const TableCell = React.forwardRef<
  HTMLTableCellElement,
  React.TdHTMLAttributes<HTMLTableCellElement> & { isNumeric?: boolean }
>(({ className, isNumeric = false, ...props }, ref) => (
  <td
    ref={ref}
    className={cn(
      'p-3.5 align-middle text-slate-700 text-sm leading-normal',
      isNumeric && 'text-right tabular-nums font-mono text-[13px]',
      className
    )}
    {...props}
  />
));
TableCell.displayName = 'TableCell';
