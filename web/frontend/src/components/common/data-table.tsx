"use client";

import { useState } from "react";
import { ArrowDown, ArrowUp, ChevronsUpDown } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type DataRow = Record<string, any>;

interface DataTableProps {
  columns: { key: string; label: string; format?: (v: unknown) => string }[];
  data: DataRow[];
  className?: string;
  initialRows?: number;
}

export function DataTable({ columns, data, className, initialRows }: DataTableProps) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const [expanded, setExpanded] = useState(false);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  const sorted = sortKey
    ? [...data].sort((a, b) => {
        const va = a[sortKey];
        const vb = b[sortKey];
        if (va == null && vb == null) return 0;
        if (va == null) return 1;
        if (vb == null) return -1;
        const cmp = va < vb ? -1 : va > vb ? 1 : 0;
        return sortDir === "asc" ? cmp : -cmp;
      })
    : data;
  const hasRowLimit = initialRows != null && sorted.length > initialRows;
  const visibleRows = hasRowLimit && !expanded ? sorted.slice(0, initialRows) : sorted;

  return (
    <div className={cn("w-full min-w-0", className)}>
      <div className="space-y-2 md:hidden">
        {visibleRows.length === 0 ? (
          <div className="rounded-lg border border-border/60 bg-card px-4 py-8 text-center text-sm text-muted-foreground">
            No rows available
          </div>
        ) : (
          visibleRows.map((row, i) => (
            <div
              key={i}
              className="rounded-lg border border-border/60 bg-card p-3 shadow-sm"
            >
              <dl className="grid grid-cols-1 gap-2">
                {columns.map((col) => (
                  <div
                    key={col.key}
                    className="flex min-w-0 items-start justify-between gap-3 border-b border-border/30 pb-2 last:border-0 last:pb-0"
                  >
                    <dt className="shrink-0 text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">
                      {col.label}
                    </dt>
                    <dd className="min-w-0 break-words text-right text-sm text-foreground">
                      {col.format
                        ? col.format(row[col.key])
                        : String(row[col.key] ?? "")}
                    </dd>
                  </div>
                ))}
              </dl>
            </div>
          ))
        )}
      </div>

      <div className="hidden w-full min-w-0 overflow-x-auto rounded-lg border border-border/60 bg-card md:block">
        <Table>
          <TableHeader className="bg-muted/30">
            <TableRow className="border-border/50 hover:bg-transparent">
              {columns.map((col) => (
                <TableHead
                  key={col.key}
                  className="h-9 cursor-pointer select-none text-[11px] font-semibold tracking-wider text-muted-foreground uppercase transition-colors hover:text-foreground"
                  onClick={() => handleSort(col.key)}
                >
                  <span className="inline-flex items-center gap-1.5">
                    {col.label}
                    {sortKey === col.key ? (
                      sortDir === "asc" ? (
                        <ArrowUp className="h-3 w-3 text-primary" />
                      ) : (
                        <ArrowDown className="h-3 w-3 text-primary" />
                      )
                    ) : (
                      <ChevronsUpDown className="h-3 w-3 text-muted-foreground/40" />
                    )}
                  </span>
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {visibleRows.length === 0 ? (
              <TableRow className="border-border/30">
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center text-sm text-muted-foreground"
                >
                  No rows available
                </TableCell>
              </TableRow>
            ) : (
              visibleRows.map((row, i) => (
                <TableRow
                  key={i}
                  className="border-border/30 transition-colors hover:bg-accent/30"
                >
                  {columns.map((col) => (
                    <TableCell key={col.key} className="text-sm">
                      {col.format
                        ? col.format(row[col.key])
                        : String(row[col.key] ?? "")}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {hasRowLimit && (
        <div className="mt-3 flex justify-center">
          <button
            type="button"
            className="rounded-md border border-border/60 bg-card px-3 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:text-foreground"
            onClick={() => setExpanded((value) => !value)}
          >
            {expanded ? "Show fewer rows" : `Show all ${sorted.length} rows`}
          </button>
        </div>
      )}
    </div>
  );
}
