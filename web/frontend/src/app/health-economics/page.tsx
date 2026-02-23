"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import {
  AreaChartWrapper,
  BarChartWrapper,
  ScatterChartWrapper,
} from "@/components/charts/recharts-wrappers";
import { DataTable } from "@/components/common/data-table";
import { StatCard } from "@/components/common/stat-card";
import { PageHeader } from "@/components/common/page-header";
import { ConfigPanel } from "@/components/common/config-panel";
import { ChartCard } from "@/components/common/chart-card";
import {
  ChartSkeleton,
  CardSkeleton,
  TableSkeleton,
} from "@/components/common/loading-skeleton";
import { apiPost } from "@/lib/api";
import { formatCurrency, formatNumber } from "@/lib/format";
import type {
  InterventionInput,
  QALYRequest,
  QALYResponse,
  CEARequest,
  CEAResponse,
  TreatmentOptimizerRequest,
  TreatmentOptimizerResponse,
  ScenarioResponse,
} from "@/types/api";

// ---------------------------------------------------------------------------
// Medical disclaimer banner
// ---------------------------------------------------------------------------
function MedicalDisclaimer() {
  return (
    <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 px-5 py-4 text-sm text-amber-200">
      <strong>Medical Disclaimer:</strong> This tool is for educational and
      research purposes only. It does not constitute medical advice. All
      parameters are illustrative. Consult qualified healthcare professionals
      for clinical decisions. Simulated results may differ materially from real
      clinical outcomes.
    </div>
  );
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function formatSnakeLabel(key: string): string {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

// ---------------------------------------------------------------------------
// Default intervention form values
// ---------------------------------------------------------------------------
interface InterventionFormState {
  name: string;
  cost_per_year: number;
  cost_std: number;
  utility_gain: number;
  utility_gain_std: number;
  mortality_reduction: number;
  mortality_reduction_std: number;
}

const DEFAULT_INTERVENTION: InterventionFormState = {
  name: "Treatment A",
  cost_per_year: 5000,
  cost_std: 500,
  utility_gain: 0.05,
  utility_gain_std: 0.01,
  mortality_reduction: 0.02,
  mortality_reduction_std: 0.005,
};

const DEFAULT_COMPARATOR: InterventionFormState = {
  name: "Standard Care",
  cost_per_year: 1000,
  cost_std: 200,
  utility_gain: 0.01,
  utility_gain_std: 0.005,
  mortality_reduction: 0.005,
  mortality_reduction_std: 0.002,
};

function buildInterventionInput(f: InterventionFormState): InterventionInput {
  return {
    name: f.name,
    cost_per_year: f.cost_per_year,
    cost_std: f.cost_std,
    utility_gain: f.utility_gain,
    utility_gain_std: f.utility_gain_std,
    mortality_reduction: f.mortality_reduction,
    mortality_reduction_std: f.mortality_reduction_std,
  };
}

// ---------------------------------------------------------------------------
// Intervention form component
// ---------------------------------------------------------------------------
function InterventionForm({
  state,
  onChange,
  label,
}: {
  state: InterventionFormState;
  onChange: (s: InterventionFormState) => void;
  label: string;
}) {
  const set = <K extends keyof InterventionFormState>(
    key: K,
    value: InterventionFormState[K],
  ) => onChange({ ...state, [key]: value });

  return (
    <div className="relative overflow-hidden rounded-xl border border-border/50 bg-card/50">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />
      <div className="border-b border-border/50 px-5 py-4">
        <h3 className="text-sm font-semibold">{label}</h3>
      </div>
      <div className="space-y-3 p-5">
        <div className="space-y-1">
          <Label className="text-xs text-muted-foreground">Name</Label>
          <Input
            className="border-border/50 bg-background/50"
            value={state.name}
            onChange={(e) => set("name", e.target.value)}
          />
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <Label className="text-xs text-muted-foreground">Cost / Year ($)</Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              value={state.cost_per_year}
              onChange={(e) => set("cost_per_year", Number(e.target.value))}
            />
          </div>
          <div className="space-y-1">
            <Label className="text-xs text-muted-foreground">Cost Std ($)</Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              value={state.cost_std}
              onChange={(e) => set("cost_std", Number(e.target.value))}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <Label className="text-xs text-muted-foreground">Utility Gain</Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              step={0.01}
              value={state.utility_gain}
              onChange={(e) => set("utility_gain", Number(e.target.value))}
            />
          </div>
          <div className="space-y-1">
            <Label className="text-xs text-muted-foreground">Utility Gain Std</Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              step={0.001}
              value={state.utility_gain_std}
              onChange={(e) => set("utility_gain_std", Number(e.target.value))}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <Label className="text-xs text-muted-foreground">Mortality Reduction</Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              step={0.001}
              value={state.mortality_reduction}
              onChange={(e) =>
                set("mortality_reduction", Number(e.target.value))
              }
            />
          </div>
          <div className="space-y-1">
            <Label className="text-xs text-muted-foreground">Mortality Red. Std</Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              step={0.001}
              value={state.mortality_reduction_std}
              onChange={(e) =>
                set("mortality_reduction_std", Number(e.target.value))
              }
            />
          </div>
        </div>
      </div>
    </div>
  );
}

// ===========================================================================
// Tab 1: QALY Simulation
// ===========================================================================
function QALYSimulationTab() {
  const [intervention, setIntervention] =
    useState<InterventionFormState>(DEFAULT_INTERVENTION);
  const [baselineUtility, setBaselineUtility] = useState(0.8);
  const [baselineMortality, setBaselineMortality] = useState(0.01);
  const [timeHorizon, setTimeHorizon] = useState(20);
  const [nSims, setNSims] = useState(5000);
  const [discountRate, setDiscountRate] = useState(0.03);

  const mutation = useMutation({
    mutationFn: (req: QALYRequest) =>
      apiPost<QALYResponse>("/api/health-economics/qaly", req, 120000),
    onSuccess: () => toast.success("QALY simulation complete"),
    onError: (e) => toast.error(`QALY simulation failed: ${e.message}`),
  });

  const handleRun = () => {
    mutation.mutate({
      intervention: buildInterventionInput(intervention),
      baseline_utility: baselineUtility,
      baseline_mortality: baselineMortality,
      time_horizon: timeHorizon,
      n_sims: nSims,
      discount_rate: discountRate,
    });
  };

  const result = mutation.data;

  // Build survival curve data
  const survivalData = result?.survival_curve?.map((v, i) => ({
    year: i,
    survival: v,
  }));

  // Build cost histogram
  const costHistogram = result
    ? buildHistogramData(result.annual_cost_means, "Year", "cost")
    : [];

  // Build QALY histogram
  const qalyHistogram = result
    ? buildHistogramData(result.annual_qaly_means, "Year", "qalys")
    : [];

  return (
    <div className="grid grid-cols-1 gap-8 lg:grid-cols-[350px_1fr]">
      {/* Config panel */}
      <div className="space-y-4">
        <InterventionForm
          state={intervention}
          onChange={setIntervention}
          label="Intervention"
        />
        <div className="relative overflow-hidden rounded-xl border border-border/50 bg-card/50">
          <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />
          <div className="border-b border-border/50 px-5 py-4">
            <h3 className="text-sm font-semibold">Simulation Parameters</h3>
          </div>
          <div className="space-y-3 p-5">
            <div className="grid grid-cols-2 gap-2">
              <div className="space-y-1">
                <Label className="text-xs text-muted-foreground">Baseline Utility</Label>
                <Input
                  className="border-border/50 bg-background/50"
                  type="number"
                  step={0.01}
                  value={baselineUtility}
                  onChange={(e) => setBaselineUtility(Number(e.target.value))}
                />
              </div>
              <div className="space-y-1">
                <Label className="text-xs text-muted-foreground">Baseline Mortality</Label>
                <Input
                  className="border-border/50 bg-background/50"
                  type="number"
                  step={0.001}
                  value={baselineMortality}
                  onChange={(e) => setBaselineMortality(Number(e.target.value))}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="space-y-1">
                <Label className="text-xs text-muted-foreground">Time Horizon (years)</Label>
                <Input
                  className="border-border/50 bg-background/50"
                  type="number"
                  value={timeHorizon}
                  onChange={(e) => setTimeHorizon(Number(e.target.value))}
                  min={1}
                />
              </div>
              <div className="space-y-1">
                <Label className="text-xs text-muted-foreground">Simulations</Label>
                <Input
                  className="border-border/50 bg-background/50"
                  type="number"
                  value={nSims}
                  onChange={(e) => setNSims(Number(e.target.value))}
                  min={100}
                  max={50000}
                />
              </div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Discount Rate</Label>
              <Input
                className="border-border/50 bg-background/50"
                type="number"
                step={0.01}
                value={discountRate}
                onChange={(e) => setDiscountRate(Number(e.target.value))}
              />
            </div>
            <Button
              className="w-full bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
              onClick={handleRun}
              disabled={mutation.isPending}
            >
              {mutation.isPending ? "Running..." : "Run QALY Simulation"}
            </Button>
          </div>
        </div>
      </div>

      {/* Results panel */}
      <div className="space-y-8">
        {mutation.isPending && (
          <>
            <div className="grid grid-cols-2 gap-4">
              <CardSkeleton />
              <CardSkeleton />
            </div>
            <ChartSkeleton />
            <ChartSkeleton />
          </>
        )}

        {result && (
          <>
            {/* Stat cards */}
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              <StatCard
                label="Mean Cost"
                value={formatCurrency(result.mean_cost)}
              />
              <StatCard
                label="Mean QALYs"
                value={formatNumber(result.mean_qaly, 3)}
                trend="up"
              />
              <StatCard
                label="Cost p5"
                value={formatCurrency(result.cost_percentiles?.["p5"] ?? null)}
              />
              <StatCard
                label="Cost p95"
                value={formatCurrency(result.cost_percentiles?.["p95"] ?? null)}
              />
            </div>

            {/* Survival curve */}
            {survivalData && survivalData.length > 0 && (
              <ChartCard title="Survival Curve">
                <AreaChartWrapper
                  data={survivalData as Record<string, unknown>[]}
                  xKey="year"
                  series={[{ key: "survival" }]}
                  height={300}
                />
              </ChartCard>
            )}

            {/* Annual cost means */}
            {costHistogram.length > 0 && (
              <ChartCard title="Annual Mean Costs">
                <BarChartWrapper
                  data={costHistogram}
                  xKey="year"
                  yKey="cost"
                  height={250}
                />
              </ChartCard>
            )}

            {/* Annual QALY means */}
            {qalyHistogram.length > 0 && (
              <ChartCard title="Annual Mean QALYs">
                <BarChartWrapper
                  data={qalyHistogram}
                  xKey="year"
                  yKey="qalys"
                  height={250}
                />
              </ChartCard>
            )}

            {/* Percentile tables */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <ChartCard title="Cost Percentiles">
                <DataTable
                  columns={[
                    { key: "percentile", label: "Percentile" },
                    {
                      key: "value",
                      label: "Cost",
                      format: (v) => formatCurrency(v as number),
                    },
                  ]}
                  data={Object.entries(result.cost_percentiles).map(
                    ([k, v]) => ({
                      percentile: k,
                      value: v,
                    }),
                  )}
                />
              </ChartCard>
              <ChartCard title="QALY Percentiles">
                <DataTable
                  columns={[
                    { key: "percentile", label: "Percentile" },
                    {
                      key: "value",
                      label: "QALYs",
                      format: (v) => formatNumber(v as number, 4),
                    },
                  ]}
                  data={Object.entries(result.qaly_percentiles).map(
                    ([k, v]) => ({
                      percentile: k,
                      value: v,
                    }),
                  )}
                />
              </ChartCard>
            </div>
          </>
        )}

        {!mutation.isPending && !result && (
          <div className="flex items-center justify-center rounded-xl border border-dashed border-border/50 bg-card/20 py-16 text-sm text-muted-foreground">
            Configure intervention parameters and click Run to see QALY
            simulation results.
          </div>
        )}
      </div>
    </div>
  );
}

// ===========================================================================
// Tab 2: Cost-Effectiveness Analysis
// ===========================================================================
function CostEffectivenessTab() {
  const [interventionA, setInterventionA] =
    useState<InterventionFormState>(DEFAULT_INTERVENTION);
  const [interventionB, setInterventionB] =
    useState<InterventionFormState>(DEFAULT_COMPARATOR);
  const [comparator, setComparator] = useState("Standard Care");
  const [baselineUtility, setBaselineUtility] = useState(0.8);
  const [baselineMortality, setBaselineMortality] = useState(0.01);
  const [timeHorizon, setTimeHorizon] = useState(20);
  const [nSims, setNSims] = useState(5000);
  const [discountRate, setDiscountRate] = useState(0.03);
  const [wtpMin, setWtpMin] = useState(0);
  const [wtpMax, setWtpMax] = useState(100000);
  const [wtpStep, setWtpStep] = useState(10000);

  const mutation = useMutation({
    mutationFn: (req: CEARequest) =>
      apiPost<CEAResponse>("/api/health-economics/cea", req, 180000),
    onSuccess: () => toast.success("Cost-effectiveness analysis complete"),
    onError: (e) => toast.error(`CEA failed: ${e.message}`),
  });

  const handleRun = () => {
    const buildQALYReq = (
      f: InterventionFormState,
    ): QALYRequest => ({
      intervention: buildInterventionInput(f),
      baseline_utility: baselineUtility,
      baseline_mortality: baselineMortality,
      time_horizon: timeHorizon,
      n_sims: nSims,
      discount_rate: discountRate,
    });

    // Build WTP thresholds array
    const thresholds: number[] = [];
    for (let t = wtpMin; t <= wtpMax; t += wtpStep) {
      thresholds.push(t);
    }
    if (thresholds.length === 0) thresholds.push(50000);

    mutation.mutate({
      interventions: [buildQALYReq(interventionA), buildQALYReq(interventionB)],
      comparator,
      wtp_thresholds: thresholds,
    });
  };

  const result = mutation.data;

  // Build CE plane scatter data
  const cePlaneData: { x: number; y: number; label?: string }[] = [];
  if (result?.ce_plane) {
    Object.entries(result.ce_plane).forEach(([name, points]) => {
      points.forEach((pt) => {
        if (pt.delta_cost != null && pt.delta_qaly != null) {
          cePlaneData.push({
            x: pt.delta_qaly as number,
            y: pt.delta_cost as number,
            label: name,
          });
        }
      });
    });
  }

  // Build CEAC line data
  const ceacData: Record<string, unknown>[] = [];
  if (result?.ceac && result.ceac.length > 0) {
    result.ceac.forEach((row) => {
      ceacData.push(row);
    });
  }

  // Extract series keys from CEAC data (excluding the wtp key)
  const ceacSeriesKeys =
    ceacData.length > 0
      ? Object.keys(ceacData[0]).filter(
          (k) => k !== "wtp" && k !== "wtp_threshold",
        )
      : [];

  return (
    <div className="space-y-8">
      {/* Intervention forms side by side */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <InterventionForm
          state={interventionA}
          onChange={setInterventionA}
          label="Intervention A"
        />
        <InterventionForm
          state={interventionB}
          onChange={setInterventionB}
          label="Intervention B"
        />
      </div>

      {/* Shared parameters */}
      <div className="relative overflow-hidden rounded-xl border border-border/50 bg-card/50">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />
        <div className="border-b border-border/50 px-5 py-4">
          <h3 className="text-sm font-semibold">Analysis Parameters</h3>
        </div>
        <div className="space-y-3 p-5">
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Comparator</Label>
              <Select value={comparator} onValueChange={setComparator}>
                <SelectTrigger className="border-border/50 bg-background/50">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={interventionA.name}>
                    {interventionA.name}
                  </SelectItem>
                  <SelectItem value={interventionB.name}>
                    {interventionB.name}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Baseline Utility</Label>
              <Input
                className="border-border/50 bg-background/50"
                type="number"
                step={0.01}
                value={baselineUtility}
                onChange={(e) => setBaselineUtility(Number(e.target.value))}
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Baseline Mortality</Label>
              <Input
                className="border-border/50 bg-background/50"
                type="number"
                step={0.001}
                value={baselineMortality}
                onChange={(e) => setBaselineMortality(Number(e.target.value))}
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Time Horizon</Label>
              <Input
                className="border-border/50 bg-background/50"
                type="number"
                value={timeHorizon}
                onChange={(e) => setTimeHorizon(Number(e.target.value))}
                min={1}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Simulations</Label>
              <Input
                className="border-border/50 bg-background/50"
                type="number"
                value={nSims}
                onChange={(e) => setNSims(Number(e.target.value))}
                min={100}
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Discount Rate</Label>
              <Input
                className="border-border/50 bg-background/50"
                type="number"
                step={0.01}
                value={discountRate}
                onChange={(e) => setDiscountRate(Number(e.target.value))}
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">WTP Min ($)</Label>
              <Input
                className="border-border/50 bg-background/50"
                type="number"
                value={wtpMin}
                onChange={(e) => setWtpMin(Number(e.target.value))}
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">WTP Max ($)</Label>
              <Input
                className="border-border/50 bg-background/50"
                type="number"
                value={wtpMax}
                onChange={(e) => setWtpMax(Number(e.target.value))}
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">WTP Step ($)</Label>
              <Input
                className="border-border/50 bg-background/50"
                type="number"
                value={wtpStep}
                onChange={(e) => setWtpStep(Number(e.target.value))}
              />
            </div>
          </div>
          <Button
            className="w-full bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
            onClick={handleRun}
            disabled={mutation.isPending}
          >
            {mutation.isPending ? "Running..." : "Run CEA"}
          </Button>
        </div>
      </div>

      {/* Results */}
      {mutation.isPending && (
        <>
          <TableSkeleton />
          <ChartSkeleton />
          <ChartSkeleton />
        </>
      )}

      {result && (
        <>
          {/* ICER Table */}
          {result.icer_table && result.icer_table.length > 0 && (
            <ChartCard title="ICER Results">
              <DataTable
                columns={buildDynamicColumns(result.icer_table)}
                data={result.icer_table}
              />
            </ChartCard>
          )}

          {/* CE Plane Scatter */}
          {cePlaneData.length > 0 && (
            <ChartCard title="Cost-Effectiveness Plane">
              <ScatterChartWrapper
                data={cePlaneData}
                xLabel="Incremental QALYs"
                yLabel="Incremental Cost ($)"
                height={400}
              />
            </ChartCard>
          )}

          {/* CEAC Line Chart */}
          {ceacData.length > 0 && ceacSeriesKeys.length > 0 && (
            <ChartCard title="Cost-Effectiveness Acceptability Curve (CEAC)">
              <AreaChartWrapper
                data={ceacData}
                xKey={
                  ceacData[0]["wtp_threshold"] !== undefined
                    ? "wtp_threshold"
                    : "wtp"
                }
                series={ceacSeriesKeys.map((k) => ({ key: k }))}
                height={350}
              />
            </ChartCard>
          )}

          {/* NMB Table */}
          {result.nmb && result.nmb.length > 0 && (
            <ChartCard title="Net Monetary Benefit">
              <DataTable
                columns={buildDynamicColumns(result.nmb)}
                data={result.nmb}
              />
            </ChartCard>
          )}

          {/* Summary Table */}
          {result.summary && result.summary.length > 0 && (
            <ChartCard title="Summary">
              <DataTable
                columns={buildDynamicColumns(result.summary)}
                data={result.summary}
              />
            </ChartCard>
          )}
        </>
      )}

      {!mutation.isPending && !result && (
        <div className="flex items-center justify-center rounded-xl border border-dashed border-border/50 bg-card/20 py-16 text-sm text-muted-foreground">
          Configure two interventions and click Run CEA to compare
          cost-effectiveness.
        </div>
      )}
    </div>
  );
}

// ===========================================================================
// Tab 3: Treatment Optimizer
// ===========================================================================
function TreatmentOptimizerTab() {
  const [costPerDose, setCostPerDose] = useState(100);
  const [costPerDoseStd, setCostPerDoseStd] = useState(10);
  const [qalyGainPerDose, setQalyGainPerDose] = useState(0.01);
  const [qalyGainPerDoseStd, setQalyGainPerDoseStd] = useState(0.002);
  const [frequencies, setFrequencies] = useState("1,2,4,12");
  const [durations, setDurations] = useState("1,2,5,10");
  const [wtpThreshold, setWtpThreshold] = useState(50000);
  const [nSims, setNSims] = useState(5000);

  const mutation = useMutation({
    mutationFn: (req: TreatmentOptimizerRequest) =>
      apiPost<TreatmentOptimizerResponse>(
        "/api/health-economics/treatment-optimizer",
        req,
        180000,
      ),
    onSuccess: () => toast.success("Treatment optimization complete"),
    onError: (e) => toast.error(`Optimization failed: ${e.message}`),
  });

  const handleRun = () => {
    const freqList = frequencies
      .split(",")
      .map((s) => Number(s.trim()))
      .filter((n) => !isNaN(n) && n > 0);
    const durList = durations
      .split(",")
      .map((s) => Number(s.trim()))
      .filter((n) => !isNaN(n) && n > 0);

    if (freqList.length === 0 || durList.length === 0) {
      toast.error("Please provide valid frequency and duration values.");
      return;
    }

    mutation.mutate({
      cost_per_dose: costPerDose,
      cost_per_dose_std: costPerDoseStd,
      qaly_gain_per_dose: qalyGainPerDose,
      qaly_gain_per_dose_std: qalyGainPerDoseStd,
      frequencies: freqList,
      durations: durList,
      wtp_threshold: wtpThreshold,
      n_sims: nSims,
    });
  };

  const result = mutation.data;
  const best = result?.best_schedule;

  return (
    <div className="grid grid-cols-1 gap-8 lg:grid-cols-[350px_1fr]">
      {/* Config panel */}
      <ConfigPanel title="Configuration">
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <Label className="text-xs text-muted-foreground">Cost / Dose ($)</Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              value={costPerDose}
              onChange={(e) => setCostPerDose(Number(e.target.value))}
            />
          </div>
          <div className="space-y-1">
            <Label className="text-xs text-muted-foreground">Cost / Dose Std ($)</Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              value={costPerDoseStd}
              onChange={(e) => setCostPerDoseStd(Number(e.target.value))}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <Label className="text-xs text-muted-foreground">QALY Gain / Dose</Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              step={0.001}
              value={qalyGainPerDose}
              onChange={(e) => setQalyGainPerDose(Number(e.target.value))}
            />
          </div>
          <div className="space-y-1">
            <Label className="text-xs text-muted-foreground">QALY Gain Std</Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              step={0.0001}
              value={qalyGainPerDoseStd}
              onChange={(e) => setQalyGainPerDoseStd(Number(e.target.value))}
            />
          </div>
        </div>
        <div className="space-y-1">
          <Label className="text-xs text-muted-foreground">Frequencies (per year)</Label>
          <Input
            className="border-border/50 bg-background/50"
            value={frequencies}
            onChange={(e) => setFrequencies(e.target.value)}
            placeholder="e.g. 1,2,4,12"
          />
          <p className="text-xs text-muted-foreground">
            Comma-separated dose frequencies per year
          </p>
        </div>
        <div className="space-y-1">
          <Label className="text-xs text-muted-foreground">Durations (years)</Label>
          <Input
            className="border-border/50 bg-background/50"
            value={durations}
            onChange={(e) => setDurations(e.target.value)}
            placeholder="e.g. 1,2,5,10"
          />
          <p className="text-xs text-muted-foreground">
            Comma-separated treatment durations in years
          </p>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <Label className="text-xs text-muted-foreground">WTP Threshold ($)</Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              value={wtpThreshold}
              onChange={(e) => setWtpThreshold(Number(e.target.value))}
            />
          </div>
          <div className="space-y-1">
            <Label className="text-xs text-muted-foreground">Simulations</Label>
            <Input
              className="border-border/50 bg-background/50"
              type="number"
              value={nSims}
              onChange={(e) => setNSims(Number(e.target.value))}
              min={100}
            />
          </div>
        </div>
        <Button
          className="w-full bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
          onClick={handleRun}
          disabled={mutation.isPending}
        >
          {mutation.isPending ? "Optimizing..." : "Optimize Schedule"}
        </Button>
      </ConfigPanel>

      {/* Results panel */}
      <div className="space-y-8">
        {mutation.isPending && (
          <>
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              <CardSkeleton />
              <CardSkeleton />
              <CardSkeleton />
              <CardSkeleton />
            </div>
            <TableSkeleton />
          </>
        )}

        {result && (
          <>
            {/* Best schedule cards */}
            {best && (
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                <StatCard
                  label="Best Frequency"
                  value={`${best["frequency"] ?? best["freq"] ?? "N/A"}x/yr`}
                  trend="up"
                />
                <StatCard
                  label="Best Duration"
                  value={`${best["duration"] ?? best["dur"] ?? "N/A"} yrs`}
                  trend="up"
                />
                <StatCard
                  label="NMB"
                  value={formatCurrency(
                    (best["nmb"] ?? best["net_monetary_benefit"]) as
                      | number
                      | null,
                  )}
                  trend="up"
                />
                <StatCard
                  label="Total Cost"
                  value={formatCurrency(
                    (best["total_cost"] ?? best["cost"]) as number | null,
                  )}
                />
              </div>
            )}

            {/* Results table */}
            {result.results && result.results.length > 0 && (
              <ChartCard title="All Schedule Results">
                <DataTable
                  columns={buildDynamicColumns(result.results)}
                  data={result.results}
                />
              </ChartCard>
            )}
          </>
        )}

        {!mutation.isPending && !result && (
          <div className="flex items-center justify-center rounded-xl border border-dashed border-border/50 bg-card/20 py-16 text-sm text-muted-foreground">
            Configure dose parameters and click Optimize Schedule to find the
            optimal treatment schedule.
          </div>
        )}
      </div>
    </div>
  );
}

// ===========================================================================
// Tab 4: Clinical Scenarios
// ===========================================================================
const CLINICAL_SCENARIOS = [
  { id: "cancer_screening", label: "Cancer Screening" },
  { id: "hypertension", label: "Hypertension" },
  { id: "vaccine", label: "Vaccine" },
] as const;

function ClinicalScenariosTab() {
  const [wtpThreshold, setWtpThreshold] = useState(50000);
  const [nSims, setNSims] = useState(5000);
  const [results, setResults] = useState<ScenarioResponse[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const handleRunAll = async () => {
    setIsRunning(true);
    setResults([]);

    try {
      const responses: ScenarioResponse[] = [];
      for (const scenario of CLINICAL_SCENARIOS) {
        const res = await apiPost<ScenarioResponse>(
          "/api/health-economics/scenarios",
          {
            scenario: scenario.id,
            n_sims: nSims,
            wtp_threshold: wtpThreshold,
          },
          120000,
        );
        responses.push(res);
      }
      setResults(responses);
      toast.success("All clinical scenarios complete");
    } catch (e) {
      toast.error(`Scenario run failed: ${(e as Error).message}`);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Config */}
      <div className="relative overflow-hidden rounded-xl border border-border/50 bg-card/50">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />
        <div className="border-b border-border/50 px-5 py-4">
          <h3 className="text-sm font-semibold">Run Clinical Scenarios</h3>
        </div>
        <div className="space-y-4 p-5">
          <p className="text-sm text-muted-foreground">
            Run all pre-configured clinical scenarios (cancer screening,
            hypertension treatment, vaccination) and compare cost-effectiveness
            at the specified willingness-to-pay threshold.
          </p>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">WTP Threshold ($)</Label>
              <Input
                className="border-border/50 bg-background/50"
                type="number"
                value={wtpThreshold}
                onChange={(e) => setWtpThreshold(Number(e.target.value))}
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Simulations</Label>
              <Input
                className="border-border/50 bg-background/50"
                type="number"
                value={nSims}
                onChange={(e) => setNSims(Number(e.target.value))}
                min={100}
              />
            </div>
            <div className="flex items-end">
              <Button
                className="w-full bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
                onClick={handleRunAll}
                disabled={isRunning}
              >
                {isRunning ? "Running..." : "Run All Scenarios"}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Loading state */}
      {isRunning && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
          </div>
          <TableSkeleton />
        </>
      )}

      {/* Results */}
      {results.length > 0 && (
        <>
          {/* Summary stat cards per scenario */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {results.map((r) => (
              <div
                key={r.scenario_name}
                className="relative overflow-hidden rounded-xl border border-border/50 bg-card/50"
              >
                <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-border to-transparent" />
                <div className="flex items-center justify-between border-b border-border/30 px-5 py-3.5">
                  <h3 className="text-sm font-semibold">
                    {r.scenario_name}
                  </h3>
                  <Badge
                    variant="outline"
                    className={
                      r.is_cost_effective
                        ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                        : "border-red-500/30 bg-red-500/10 text-red-400"
                    }
                  >
                    {r.is_cost_effective
                      ? "Cost-Effective"
                      : "Not Cost-Effective"}
                  </Badge>
                </div>
                <div className="space-y-1 p-5 text-sm">
                  <p>
                    <span className="text-muted-foreground">
                      Intervention:
                    </span>{" "}
                    {r.intervention_name}
                  </p>
                  <p>
                    <span className="text-muted-foreground">vs:</span>{" "}
                    {r.comparator_name}
                  </p>
                  <p>
                    <span className="text-muted-foreground">ICER:</span>{" "}
                    {r.icer != null ? formatCurrency(r.icer) : "Dominant"}
                  </p>
                  <p>
                    <span className="text-muted-foreground">NMB:</span>{" "}
                    {formatCurrency(r.nmb)}
                  </p>
                  <p>
                    <span className="text-muted-foreground">QALY Gain:</span>{" "}
                    {formatNumber(r.qaly_gain, 4)}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* Summary comparison table */}
          <ChartCard title="Scenario Comparison">
            <DataTable
              columns={[
                { key: "scenario_name", label: "Scenario" },
                { key: "intervention_name", label: "Intervention" },
                { key: "comparator_name", label: "Comparator" },
                {
                  key: "icer",
                  label: "ICER",
                  format: (v) =>
                    v != null ? formatCurrency(v as number) : "Dominant",
                },
                {
                  key: "nmb",
                  label: "NMB",
                  format: (v) => formatCurrency(v as number),
                },
                {
                  key: "qaly_gain",
                  label: "QALY Gain",
                  format: (v) => formatNumber(v as number, 4),
                },
                {
                  key: "cost_difference",
                  label: "Cost Diff",
                  format: (v) => formatCurrency(v as number),
                },
                {
                  key: "is_cost_effective",
                  label: "Cost-Effective",
                  format: (v) => (v ? "Yes" : "No"),
                },
                {
                  key: "n_simulations",
                  label: "N Sims",
                  format: (v) => formatNumber(v as number, 0),
                },
              ]}
              data={results as unknown as Record<string, unknown>[]}
            />
          </ChartCard>
        </>
      )}

      {!isRunning && results.length === 0 && (
        <div className="flex items-center justify-center rounded-xl border border-dashed border-border/50 bg-card/20 py-16 text-sm text-muted-foreground">
          Click Run All Scenarios to evaluate pre-configured clinical
          scenarios.
        </div>
      )}
    </div>
  );
}

// ===========================================================================
// Utility: Build histogram from annual array data
// ===========================================================================
function buildHistogramData(
  values: number[] | undefined,
  xLabel: string,
  yKey: string,
): Record<string, unknown>[] {
  if (!values || values.length === 0) return [];
  return values.map((v, i) => ({
    [xLabel.toLowerCase()]: i,
    [yKey]: v,
  }));
}

// ===========================================================================
// Utility: Build dynamic columns from record keys
// ===========================================================================
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
        if (Math.abs(v) >= 100) return formatCurrency(v);
        if (Math.abs(v) < 1 && v !== 0) return formatNumber(v, 4);
        return formatNumber(v, 2);
      }
      return String(v);
    },
  }));
}

// ===========================================================================
// Main Page Component
// ===========================================================================
export default function HealthEconomicsPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Health Economics"
        description="QALY simulation, cost-effectiveness analysis, treatment optimization, and clinical scenarios"
      />

      <MedicalDisclaimer />

      <Tabs defaultValue="qaly">
        <TabsList className="bg-muted/30">
          <TabsTrigger value="qaly">QALY Simulation</TabsTrigger>
          <TabsTrigger value="cea">Cost-Effectiveness</TabsTrigger>
          <TabsTrigger value="optimizer">Treatment Optimizer</TabsTrigger>
          <TabsTrigger value="scenarios">Clinical Scenarios</TabsTrigger>
        </TabsList>

        <TabsContent value="qaly" className="mt-6">
          <QALYSimulationTab />
        </TabsContent>

        <TabsContent value="cea" className="mt-6">
          <CostEffectivenessTab />
        </TabsContent>

        <TabsContent value="optimizer" className="mt-6">
          <TreatmentOptimizerTab />
        </TabsContent>

        <TabsContent value="scenarios" className="mt-6">
          <ClinicalScenariosTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
