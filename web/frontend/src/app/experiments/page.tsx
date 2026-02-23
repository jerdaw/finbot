"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/common/data-table";
import { PageHeader } from "@/components/common/page-header";
import { ChartCard } from "@/components/common/chart-card";
import { EmptyState } from "@/components/common/empty-state";
import { FlaskConical } from "lucide-react";
import {
  CardSkeleton,
  TableSkeleton,
} from "@/components/common/loading-skeleton";
import { apiGet, apiPost } from "@/lib/api";
import { formatNumber } from "@/lib/format";
import type {
  ExperimentSummary,
  ExperimentCompareResponse,
} from "@/types/api";

function formatSnakeLabel(key: string): string {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function findBestWorst(
  rows: Record<string, unknown>[],
  key: string,
): { bestIdx: number | null; worstIdx: number | null } {
  let bestIdx: number | null = null;
  let worstIdx: number | null = null;
  let bestVal = -Infinity;
  let worstVal = Infinity;

  rows.forEach((row, i) => {
    const v = row[key];
    if (typeof v === "number" && isFinite(v)) {
      if (v > bestVal) {
        bestVal = v;
        bestIdx = i;
      }
      if (v < worstVal) {
        worstVal = v;
        worstIdx = i;
      }
    }
  });

  return { bestIdx, worstIdx };
}

export default function ExperimentsPage() {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  const {
    data: experiments,
    isLoading: loadingExperiments,
    error: experimentsError,
  } = useQuery({
    queryKey: ["experiments-list"],
    queryFn: () => apiGet<ExperimentSummary[]>("/api/experiments/list"),
  });

  if (experimentsError) {
    toast.error(
      `Failed to load experiments: ${(experimentsError as Error).message}`,
    );
  }

  const compareMutation = useMutation({
    mutationFn: (runIds: string[]) =>
      apiPost<ExperimentCompareResponse>("/api/experiments/compare", {
        run_ids: runIds,
      }),
    onSuccess: () => toast.success("Comparison complete"),
    onError: (e) => toast.error(`Comparison failed: ${e.message}`),
  });

  const toggleSelection = (runId: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(runId)) {
        next.delete(runId);
      } else {
        next.add(runId);
      }
      return next;
    });
  };

  const selectAll = () => {
    if (!experiments) return;
    if (selectedIds.size === experiments.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(experiments.map((e) => e.run_id)));
    }
  };

  const handleCompare = () => {
    const ids = Array.from(selectedIds);
    if (ids.length < 2) {
      toast.error("Select at least 2 experiments to compare.");
      return;
    }
    compareMutation.mutate(ids);
  };

  const compareResult = compareMutation.data;

  const metricsColumns: {
    key: string;
    label: string;
    format?: (v: unknown) => string;
  }[] =
    compareResult?.metrics && compareResult.metrics.length > 0
      ? Object.keys(compareResult.metrics[0]).map((key) => ({
          key,
          label: formatSnakeLabel(key),
          format: (v: unknown) => {
            if (v == null) return "N/A";
            if (typeof v === "number") {
              if (Math.abs(v) < 1 && v !== 0) return formatNumber(v, 6);
              return formatNumber(v, 4);
            }
            return String(v);
          },
        }))
      : [];

  const numericMetricKeys =
    compareResult?.metrics && compareResult.metrics.length > 0
      ? Object.keys(compareResult.metrics[0]).filter(
          (k) => typeof compareResult.metrics[0][k] === "number",
        )
      : [];

  const bestWorstMap: Record<
    string,
    { bestIdx: number | null; worstIdx: number | null }
  > = {};
  numericMetricKeys.forEach((key) => {
    bestWorstMap[key] = findBestWorst(compareResult?.metrics ?? [], key);
  });

  return (
    <div className="space-y-8">
      <PageHeader
        title="Experiments"
        description="Compare backtest experiment runs side by side"
      />

      {/* Experiment List */}
      <div className="relative overflow-hidden rounded-xl border border-border/50 bg-card/50">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />
        <div className="flex items-center justify-between border-b border-border/50 px-5 py-4">
          <h3 className="text-xs font-semibold tracking-wider text-muted-foreground uppercase">
            Experiment Runs
          </h3>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={selectAll} className="border-border/50">
              {experiments && selectedIds.size === experiments.length
                ? "Deselect All"
                : "Select All"}
            </Button>
            <Button
              size="sm"
              onClick={handleCompare}
              disabled={selectedIds.size < 2 || compareMutation.isPending}
              className="bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20"
            >
              {compareMutation.isPending
                ? "Comparing..."
                : `Compare (${selectedIds.size})`}
            </Button>
          </div>
        </div>
        <div className="p-5">
          {loadingExperiments && <TableSkeleton rows={5} />}

          {experiments && experiments.length > 0 && (
            <div className="space-y-1">
              <div className="grid grid-cols-[40px_1fr_1fr_1fr_1fr_1fr] gap-2 border-b border-border/30 pb-2 text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">
                <span />
                <span>Run ID</span>
                <span>Engine</span>
                <span>Strategy</span>
                <span>Created</span>
                <span>Config Hash</span>
              </div>

              {experiments.map((exp) => (
                <div
                  key={exp.run_id}
                  className={`grid cursor-pointer grid-cols-[40px_1fr_1fr_1fr_1fr_1fr] gap-2 rounded-lg px-1 py-2.5 text-sm transition-all duration-200 hover:bg-accent/30 ${
                    selectedIds.has(exp.run_id) ? "bg-accent/20" : ""
                  }`}
                  onClick={() => toggleSelection(exp.run_id)}
                >
                  <div className="flex items-center justify-center">
                    <input
                      type="checkbox"
                      checked={selectedIds.has(exp.run_id)}
                      onChange={() => toggleSelection(exp.run_id)}
                      className="h-4 w-4 rounded border-border"
                    />
                  </div>
                  <span className="truncate font-mono text-xs">
                    {exp.run_id}
                  </span>
                  <Badge variant="outline" className="w-fit border-border/50">{exp.engine_name}</Badge>
                  <span>{exp.strategy_name}</span>
                  <span className="text-muted-foreground">
                    {new Date(exp.created_at).toLocaleDateString()}
                  </span>
                  <span className="truncate font-mono text-xs text-muted-foreground">
                    {exp.config_hash}
                  </span>
                </div>
              ))}
            </div>
          )}

          {experiments && experiments.length === 0 && (
            <p className="py-8 text-center text-sm text-muted-foreground">
              No experiment runs found. Run a backtest to create experiments.
            </p>
          )}
        </div>
      </div>

      {/* Comparison Results */}
      {compareMutation.isPending && (
        <>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
          </div>
          <TableSkeleton />
          <TableSkeleton />
        </>
      )}

      {compareResult && (
        <>
          {compareResult.assumptions &&
            compareResult.assumptions.length > 0 && (
              <ChartCard title="Assumptions Comparison">
                <DataTable
                  columns={buildDynamicColumns(compareResult.assumptions)}
                  data={compareResult.assumptions}
                />
              </ChartCard>
            )}

          {compareResult.metrics && compareResult.metrics.length > 0 && (
            <ChartCard title="Metrics Comparison">
              <DataTable
                columns={metricsColumns}
                data={compareResult.metrics.map((row, rowIdx) => {
                  const enriched: Record<string, unknown> = {};
                  Object.entries(row).forEach(([k, v]) => {
                    if (
                      typeof v === "number" &&
                      bestWorstMap[k] !== undefined
                    ) {
                      const { bestIdx, worstIdx } = bestWorstMap[k];
                      if (
                        bestIdx === rowIdx &&
                        bestIdx !== worstIdx
                      ) {
                        enriched[k] = v;
                      } else if (
                        worstIdx === rowIdx &&
                        bestIdx !== worstIdx
                      ) {
                        enriched[k] = v;
                      } else {
                        enriched[k] = v;
                      }
                    } else {
                      enriched[k] = v;
                    }
                  });
                  return enriched;
                })}
              />

              {numericMetricKeys.length > 0 && (
                <div className="mt-4 space-y-2">
                  <p className="text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">
                    Metric Rankings
                  </p>
                  <div className="flex flex-wrap gap-4 text-xs">
                    {numericMetricKeys
                      .filter((k) => {
                        const bw = bestWorstMap[k];
                        return (
                          bw.bestIdx !== null &&
                          bw.worstIdx !== null &&
                          bw.bestIdx !== bw.worstIdx
                        );
                      })
                      .map((key) => {
                        const { bestIdx, worstIdx } = bestWorstMap[key];
                        const bestRow =
                          bestIdx !== null
                            ? compareResult.metrics[bestIdx]
                            : null;
                        const worstRow =
                          worstIdx !== null
                            ? compareResult.metrics[worstIdx]
                            : null;
                        const bestLabel =
                          bestRow?.["run_id"] ??
                          bestRow?.["name"] ??
                          `Row ${bestIdx}`;
                        const worstLabel =
                          worstRow?.["run_id"] ??
                          worstRow?.["name"] ??
                          `Row ${worstIdx}`;

                        return (
                          <div key={key} className="flex items-center gap-1">
                            <span className="font-medium">
                              {formatSnakeLabel(key)}:
                            </span>
                            <Badge
                              variant="outline"
                              className="border-emerald-500/30 bg-emerald-500/10 text-xs text-emerald-400"
                            >
                              Best: {String(bestLabel)}
                            </Badge>
                            <Badge
                              variant="outline"
                              className="border-red-500/30 bg-red-500/10 text-xs text-red-400"
                            >
                              Worst: {String(worstLabel)}
                            </Badge>
                          </div>
                        );
                      })}
                  </div>
                </div>
              )}
            </ChartCard>
          )}
        </>
      )}

      {!compareMutation.isPending && !compareResult && (
        <EmptyState
          icon={FlaskConical}
          message="Select two or more experiments above and click Compare to see a side-by-side analysis."
        />
      )}
    </div>
  );
}

function buildDynamicColumns(
  data: Record<string, unknown>[],
): { key: string; label: string; format?: (v: unknown) => string }[] {
  if (data.length === 0) return [];
  return Object.keys(data[0]).map((key) => ({
    key,
    label: formatSnakeLabel(key),
    format: (v: unknown) => {
      if (v == null) return "N/A";
      if (typeof v === "boolean") return v ? "Yes" : "No";
      if (typeof v === "number") {
        if (Math.abs(v) < 1 && v !== 0) return formatNumber(v, 6);
        return formatNumber(v, 4);
      }
      return String(v);
    },
  }));
}
