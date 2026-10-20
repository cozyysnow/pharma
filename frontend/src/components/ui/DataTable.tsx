import React, { useState, useMemo } from 'react';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from './Table';
import { Pagination } from './Pagination';
import { Skeleton } from './Skeleton';
import { Inbox } from 'lucide-react';

export interface ColumnDef<T> {
  key: string;
  header: string;
  cell?: (row: T, index: number) => React.ReactNode;
  isNumeric?: boolean;
  sortable?: boolean;
  sortFn?: (a: T, b: T) => number;
  width?: string;
}

export interface DataTableProps<T> {
  columns: ColumnDef<T>[];
  data: T[];
  keyExtractor: (item: T, index: number) => string | number;
  isLoading?: boolean;
  emptyMessage?: string;
  onRowClick?: (row: T) => void;
  pageSize?: number;
  showPagination?: boolean;
  zebra?: boolean;
  className?: string;
}

export function DataTable<T extends Record<string, any>>({
  columns,
  data,
  keyExtractor,
  isLoading = false,
  emptyMessage = 'No records found',
  onRowClick,
  pageSize = 10,
  showPagination = true,
  zebra = false,
  className,
}: DataTableProps<T>) {
  const [currentPage, setCurrentPage] = useState(1);
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [rowsPerPage, setRowsPerPage] = useState(pageSize);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      if (sortDirection === 'asc') {
        setSortDirection('desc');
      } else {
        setSortKey(null);
        setSortDirection('asc');
      }
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
  };

  const sortedData = useMemo(() => {
    if (!sortKey) return data;
    const col = columns.find((c) => c.key === sortKey);
    return [...data].sort((a, b) => {
      if (col?.sortFn) {
        const res = col.sortFn(a, b);
        return sortDirection === 'asc' ? res : -res;
      }
      const valA = a[sortKey];
      const valB = b[sortKey];
      if (valA === valB) return 0;
      if (valA == null) return 1;
      if (valB == null) return -1;
      const res = valA > valB ? 1 : -1;
      return sortDirection === 'asc' ? res : -res;
    });
  }, [data, sortKey, sortDirection, columns]);

  const totalPages = Math.ceil(sortedData.length / rowsPerPage);
  const paginatedData = useMemo(() => {
    if (!showPagination) return sortedData;
    const start = (currentPage - 1) * rowsPerPage;
    return sortedData.slice(start, start + rowsPerPage);
  }, [sortedData, currentPage, rowsPerPage, showPagination]);

  return (
    <div className={className}>
      <Table zebra={zebra}>
        <TableHeader>
          <TableRow isHoverable={false}>
            {columns.map((col) => (
              <TableHead
                key={col.key}
                isNumeric={col.isNumeric}
                sortDirection={sortKey === col.key ? sortDirection : false}
                onSort={col.sortable ? () => handleSort(col.key) : undefined}
                style={{ width: col.width }}
              >
                {col.header}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>

        <TableBody>
          {isLoading ? (
            Array.from({ length: 5 }).map((_, rIdx) => (
              <TableRow key={rIdx} isHoverable={false}>
                {columns.map((col) => (
                  <TableCell key={col.key} isNumeric={col.isNumeric}>
                    <Skeleton className="h-5 w-full max-w-[140px]" />
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : paginatedData.length === 0 ? (
            <TableRow isHoverable={false}>
              <TableCell colSpan={columns.length} className="text-center py-12 text-slate-500">
                <div className="flex flex-col items-center justify-center gap-2">
                  <Inbox className="w-8 h-8 text-slate-300 stroke-[1.5]" />
                  <p className="text-sm font-medium">{emptyMessage}</p>
                </div>
              </TableCell>
            </TableRow>
          ) : (
            paginatedData.map((row, index) => (
              <TableRow
                key={keyExtractor(row, index)}
                isHoverable={!!onRowClick}
                onClick={() => onRowClick?.(row)}
              >
                {columns.map((col) => (
                  <TableCell key={col.key} isNumeric={col.isNumeric}>
                    {col.cell ? col.cell(row, index) : row[col.key] ?? '—'}
                  </TableCell>
                ))}
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>

      {showPagination && !isLoading && sortedData.length > 0 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          pageSize={rowsPerPage}
          totalItems={sortedData.length}
          onPageChange={setCurrentPage}
          onPageSizeChange={(s) => {
            setRowsPerPage(s);
            setCurrentPage(1);
          }}
        />
      )}
    </div>
  );
}
