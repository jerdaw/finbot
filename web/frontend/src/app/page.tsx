"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import {
  Activity,
  ArrowRight,
  BarChart3,
  Database,
  FlaskConical,
  Heart,
  LineChart,
  Shuffle,
  TrendingUp,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { StatCard } from "@/components/common/stat-card";
import { PageSkeleton } from "@/components/common/loading-skeleton";
import { apiGet } from "@/lib/api";
import type { DataStatusResponse, FundInfo, StrategyInfo } from "@/types/api";

const FEATURED_LINKS = [
  { label: "Backtesting", href: "/backtesting", icon: Activity, description: "Backtest 12 trading strategies on historical data", color: "from-emerald-500/10 to-emerald-600/5", iconColor: "text-emerald-400" },
  { label: "Monte Carlo", href: "/monte-carlo", icon: Shuffle, description: "Probabilistic simulation with percentile fan charts", color: "from-purple-500/10 to-purple-600/5", iconColor: "text-purple-400" },
  { label: "Simulations", href: "/simulations", icon: LineChart, description: "Compare leveraged fund performance with interactive overlays", color: "from-blue-500/10 to-blue-600/5", iconColor: "text-blue-400" },
];

const MORE_LINKS = [
  { label: "Optimizer", href: "/optimizer", icon: TrendingUp, description: "Optimize DCA parameters", color: "from-amber-500/10 to-amber-600/5", iconColor: "text-amber-400" },
  { label: "Walk-Forward", href: "/walk-forward", icon: BarChart3, description: "Out-of-sample validation", color: "from-cyan-500/10 to-cyan-600/5", iconColor: "text-cyan-400" },
  { label: "Health Economics", href: "/health-economics", icon: Heart, description: "QALY and cost-effectiveness", color: "from-rose-500/10 to-rose-600/5", iconColor: "text-rose-400" },
  { label: "Experiments", href: "/experiments", icon: FlaskConical, description: "Compare backtest runs", color: "from-indigo-500/10 to-indigo-600/5", iconColor: "text-indigo-400" },
  { label: "Data Status", href: "/data-status", icon: Database, description: "Monitor data freshness", color: "from-teal-500/10 to-teal-600/5", iconColor: "text-teal-400" },
];

function ToolCard({
  link,
  large = false,
}: {
  link: (typeof FEATURED_LINKS)[0];
  large?: boolean;
}) {
  const Icon = link.icon;
  return (
    <Link href={link.href}>
      <div className="group relative h-full overflow-hidden rounded-xl border border-border/50 bg-card/50 p-5 transition-all duration-300 hover:border-border hover:bg-card/80 gradient-border">
        <div
          className={`pointer-events-none absolute inset-0 bg-gradient-to-br ${link.color} opacity-0 transition-opacity duration-300 group-hover:opacity-100`}
        />
        <div className="relative">
          <div className="flex items-center justify-between">
            <Icon className={`${large ? "h-6 w-6" : "h-5 w-5"} ${link.iconColor}`} />
            <ArrowRight className="h-4 w-4 text-muted-foreground/0 transition-all duration-300 group-hover:translate-x-0.5 group-hover:text-muted-foreground" />
          </div>
          <h3 className={`mt-3 font-semibold ${large ? "text-base" : "text-sm"}`}>
            {link.label}
          </h3>
          <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
            {link.description}
          </p>
        </div>
      </div>
    </Link>
  );
}

export default function DashboardPage() {
  const { data: funds, isLoading: fundsLoading } = useQuery({
    queryKey: ["funds"],
    queryFn: () => apiGet<FundInfo[]>("/api/simulations/funds"),
  });

  const { data: strategies, isLoading: strategiesLoading } = useQuery({
    queryKey: ["strategies"],
    queryFn: () => apiGet<StrategyInfo[]>("/api/backtesting/strategies"),
  });

  const { data: dataStatus, isLoading: statusLoading } = useQuery({
    queryKey: ["data-status"],
    queryFn: () => apiGet<DataStatusResponse>("/api/data-status/"),
  });

  const isLoading = fundsLoading || strategiesLoading || statusLoading;

  if (isLoading) return <PageSkeleton />;

  const totalSources = dataStatus?.sources.length ?? 0;
  const freshRate =
    totalSources > 0
      ? `${Math.round(((dataStatus?.fresh_count ?? 0) / totalSources) * 100)}%`
      : "N/A";

  return (
    <div className="space-y-10">
      {/* Hero section */}
      <div className="relative">
        <div className="pointer-events-none absolute -top-8 left-0 h-32 w-64 bg-blue-500/5 blur-3xl" />
        <div className="pointer-events-none absolute -top-8 right-0 h-32 w-48 bg-purple-500/5 blur-3xl" />
        <div>
          <h2 className="text-3xl font-bold tracking-tight lg:text-4xl">
            Welcome to <span className="gradient-text">Finbot</span>
          </h2>
          <p className="mt-2 max-w-lg text-sm text-muted-foreground">
            Financial simulation, backtesting, and analysis platform.
            Explore strategies, run simulations, and analyze results.
          </p>
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Available Funds"
          value={String(funds?.length ?? 0)}
          icon={<LineChart className="h-4 w-4" />}
        />
        <StatCard
          label="Strategies"
          value={String(strategies?.length ?? 0)}
          icon={<Activity className="h-4 w-4" />}
        />
        <StatCard
          label="Data Health"
          value={freshRate}
          trend={dataStatus && dataStatus.stale_count === 0 ? "up" : "down"}
          icon={<Database className="h-4 w-4" />}
        />
        <StatCard
          label="Data Sources"
          value={`${dataStatus?.fresh_count ?? 0}/${totalSources} Fresh`}
          trend={dataStatus && dataStatus.stale_count === 0 ? "up" : "down"}
        />
      </div>

      {/* Data freshness badges */}
      {dataStatus && dataStatus.sources.length > 0 && (
        <div className="rounded-xl border border-border/50 bg-card/50 p-5">
          <p className="mb-3 text-xs font-medium tracking-wider text-muted-foreground uppercase">
            Data Freshness
          </p>
          <div className="flex flex-wrap gap-2">
            {dataStatus.sources.map((s) => (
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
                {s.name}: {s.age_str}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Featured tools */}
      <div>
        <p className="mb-4 text-xs font-medium tracking-wider text-muted-foreground uppercase">
          Featured Tools
        </p>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          {FEATURED_LINKS.map((link) => (
            <ToolCard key={link.href} link={link} large />
          ))}
        </div>
      </div>

      {/* More tools */}
      <div>
        <p className="mb-4 text-xs font-medium tracking-wider text-muted-foreground uppercase">
          More Tools
        </p>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {MORE_LINKS.map((link) => (
            <ToolCard key={link.href} link={link} />
          ))}
        </div>
      </div>
    </div>
  );
}
