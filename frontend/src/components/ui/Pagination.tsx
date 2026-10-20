import React from 'react';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
import { cn } from '../../utils/cn';

export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  pageSize?: number;
  totalItems?: number;
  onPageChange: (page: number) => void;
  onPageSizeChange?: (pageSize: number) => void;
  pageSizeOptions?: number[];
  className?: string;
}

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  pageSize = 20,
  totalItems,
  onPageChange,
  onPageSizeChange,
  pageSizeOptions = [10, 25, 50, 100],
  className,
}) => {
  const hasItemsCount = totalItems !== undefined;
  const startItem = hasItemsCount ? (totalItems === 0 ? 0 : (currentPage - 1) * pageSize + 1) : null;
  const endItem = hasItemsCount ? Math.min(currentPage * pageSize, totalItems) : null;

  return (
    <div
      className={cn(
        'flex flex-col sm:flex-row items-center justify-between gap-4 py-3 px-4 border-t border-slate-200 text-xs text-slate-600',
        className
      )}
    >
      {/* Items count & page size select */}
      <div className="flex items-center gap-3">
        {hasItemsCount && (
          <span>
            Showing <span className="font-semibold text-slate-900">{startItem}</span> to{' '}
            <span className="font-semibold text-slate-900">{endItem}</span> of{' '}
            <span className="font-semibold text-slate-900">{totalItems}</span> results
          </span>
        )}

        {onPageSizeChange && (
          <div className="flex items-center gap-1.5 ml-2 border-l border-slate-200 pl-3">
            <span>Rows:</span>
            <select
              value={pageSize}
              onChange={(e) => onPageSizeChange(Number(e.target.value))}
              className="rounded border border-slate-300 bg-white py-1 px-2 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-primary-700"
            >
              {pageSizeOptions.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Navigation buttons */}
      <div className="flex items-center gap-1">
        <button
          type="button"
          onClick={() => onPageChange(1)}
          disabled={currentPage <= 1}
          aria-label="First page"
          className="p-1.5 rounded border border-slate-300 hover:bg-slate-100 disabled:opacity-40 disabled:pointer-events-none text-slate-600"
        >
          <ChevronsLeft className="w-4 h-4" />
        </button>
        <button
          type="button"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage <= 1}
          aria-label="Previous page"
          className="p-1.5 rounded border border-slate-300 hover:bg-slate-100 disabled:opacity-40 disabled:pointer-events-none text-slate-600"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>

        <span className="px-2 text-slate-700">
          Page <span className="font-semibold">{currentPage}</span> of{' '}
          <span className="font-semibold">{Math.max(1, totalPages)}</span>
        </span>

        <button
          type="button"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage >= totalPages}
          aria-label="Next page"
          className="p-1.5 rounded border border-slate-300 hover:bg-slate-100 disabled:opacity-40 disabled:pointer-events-none text-slate-600"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
        <button
          type="button"
          onClick={() => onPageChange(totalPages)}
          disabled={currentPage >= totalPages}
          aria-label="Last page"
          className="p-1.5 rounded border border-slate-300 hover:bg-slate-100 disabled:opacity-40 disabled:pointer-events-none text-slate-600"
        >
          <ChevronsRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
