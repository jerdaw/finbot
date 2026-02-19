"use client";

import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/common/data-table";
import { StatCard } from "@/components/common/stat-card";
import { PageHeader } from "@/components/common/page-header";
import { ChartCard } from "@/components/common/chart-card";
import {
  CardSkeleton,
  TableSkeleton,
} from "@/components/common/loading-skeleton";
import { EmptyState } from "@/components/common/empty-state";
import { Database } from "lucide-react";
import { apiGet } from "@/lib/api";
import { formatBytes, formatNumber } from "@/lib/format";
import type { DataStatusResponse } from "@/types/api";

export default function DataStatusPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["data-status"],
    queryFn: () => apiGet<DataStatusResponse>("/api/data-status/"),
    refetchInterval: 5 * 60 * 1000,
  });

  if (error) {
    toast.error(`Failed to load data status: ${(error as Error).message}`);
  }

  const sources = data?.sources ?? [];
  const totalSources = sources.length;
  const totalFiles = data?.total_files ?? 0;
  const freshCount = data?.fresh_count ?? 0;
  const staleCount = data?.stale_count ?? 0;

  return (
    <div className="space-y-8">
      <PageHeader
        title="Data Status"
        description="Monitor data freshness and source health across all data pipelines"
      />

      {/* Consolidated stat cards */}
      {isLoading ? (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <StatCard
            label="Total Sources"
            value={formatNumber(totalSources, 0)}
          />
          <StatCard
            label="Total Files"
            value={formatNumber(totalFiles, 0)}
          />
          <StatCard
            label="Fresh Rate"
            value={
              totalSources > 0
                ? `${((freshCount / totalSources) * 100).toFixed(0)}%`
                : "N/A"
            }
            trend={
              totalSources > 0 && freshCount / totalSources >= 0.5
                ? "up"
                : "down"
            }
          />
          <StatCard
            label="Total Size"
            value={data ? formatBytes(data.total_size_bytes) : "N/A"}
          />
        </div>
      )}

      {/* Source detail table */}
      {isLoading ? (
        <TableSkeleton rows={7} />
      ) : sources.length > 0 ? (
        <ChartCard title="Data Source Details">
          <DataTable
            columns={[
              { key: "name", label: "Source" },
              { key: "description", label: "Description" },
              {
                key: "file_count",
                label: "Files",
                format: (v) => formatNumber(v as number, 0),
              },
              { key: "age_str", label: "Age" },
              { key: "size_str", label: "Size" },
              {
                key: "max_age_days",
                label: "Max Age (days)",
                format: (v) => formatNumber(v as number, 1),
              },
              {
                key: "newest_file",
                label: "Newest File",
                format: (v) =>
                  v != null ? String(v) : "N/A",
              },
              {
                key: "is_stale",
                label: "Status",
                format: (v) => (v ? "Stale" : "Fresh"),
              },
            ]}
            data={sources.map((s) => ({
              ...s,
              _status_badge: s.is_stale ? "stale" : "fresh",
            }))}
          />

          <div className="mt-4 flex flex-wrap gap-2">
            {sources.map((s) => (
              <Badge
                key={s.name}
                variant="outline"
                className={
                  s.is_stale
                    ? "border-red-500/30 bg-red-500/5 text-red-400"
                    : "border-emerald-500/30 bg-emerald-500/5 text-emerald-400"
                }
              >
                <span className={`mr-1.5 inline-block h-1.5 w-1.5 rounded-full ${s.is_stale ? "bg-red-400" : "bg-emerald-400"}`} />
                {s.name}: {s.is_stale ? "Stale" : "Fresh"}
              </Badge>
            ))}
          </div>
        </ChartCard>
      ) : (
        <EmptyState
          icon={Database}
          message="No data sources found. Run the data pipeline to populate data sources."
        />
      )}
    </div>
  );
}
