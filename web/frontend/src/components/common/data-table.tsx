"use client";

import { useState } from "react";
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
}

export function DataTable({ columns, data, className }: DataTableProps) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

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

  return (
    <div className={cn("overflow-hidden rounded-lg", className)}>
      <Table>
        <TableHeader>
          <TableRow className="border-border/50 hover:bg-transparent">
            {columns.map((col) => (
              <TableHead
                key={col.key}
                className="cursor-pointer select-none text-[11px] font-semibold tracking-wider text-muted-foreground uppercase transition-colors hover:text-foreground"
                onClick={() => handleSort(col.key)}
              >
                {col.label}
                {sortKey === col.key && (
                  <span className="ml-1 text-blue-400">
                    {sortDir === "asc" ? "\u25b2" : "\u25bc"}
                  </span>
                )}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.map((row, i) => (
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
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
