import type { LucideIcon } from "lucide-react";
import {
  Activity,
  BarChart3,
  Database,
  FlaskConical,
  Heart,
  Layers,
  LineChart,
  PieChart,
  Shield,
  Shuffle,
  TrendingUp,
  Zap,
} from "lucide-react";

export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  group: string;
}

export const NAV_GROUPS = [
  "Analysis",
  "Risk & Portfolio",
  "Clinical Research",
  "Data & Monitoring",
];

export const NAV_ITEMS: NavItem[] = [
  // Analysis
  { label: "Simulations", href: "/simulations", icon: LineChart, group: "Analysis" },
  { label: "Backtesting", href: "/backtesting", icon: Activity, group: "Analysis" },
  { label: "Optimizer", href: "/optimizer", icon: TrendingUp, group: "Analysis" },
  { label: "Monte Carlo", href: "/monte-carlo", icon: Shuffle, group: "Analysis" },
  { label: "Walk-Forward", href: "/walk-forward", icon: BarChart3, group: "Analysis" },
  { label: "Experiments", href: "/experiments", icon: FlaskConical, group: "Analysis" },

  // Risk & Portfolio
  { label: "Risk Analytics", href: "/risk-analytics", icon: Shield, group: "Risk & Portfolio" },
  { label: "Portfolio Analytics", href: "/portfolio-analytics", icon: PieChart, group: "Risk & Portfolio" },
  { label: "Factor Analytics", href: "/factor-analytics", icon: Layers, group: "Risk & Portfolio" },
  { label: "Real-Time Quotes", href: "/realtime-quotes", icon: Zap, group: "Risk & Portfolio" },

  // Clinical Research
  { label: "Health Economics", href: "/health-economics", icon: Heart, group: "Clinical Research" },

  // Data & Monitoring
  { label: "Data Status", href: "/data-status", icon: Database, group: "Data & Monitoring" },
];

export const CHART_COLORS = {
  blue: "#3b82f6",
  green: "#22c55e",
  red: "#ef4444",
  orange: "#f97316",
  purple: "#a855f7",
  cyan: "#06b6d4",
  amber: "#f59e0b",
  rose: "#f43f5e",
  series: [
    "#3b82f6",
    "#22c55e",
    "#f97316",
    "#a855f7",
    "#06b6d4",
    "#f43f5e",
    "#f59e0b",
    "#6366f1",
  ],
};

export const DISCLAIMER_TEXT =
  "Finbot is an educational and research tool only. It does not provide investment advice, financial recommendations, or any form of fiduciary guidance. All simulations, backtests, and analyses are based on historical data and hypothetical scenarios that do not guarantee future results. Past performance is not indicative of future returns. You should consult a qualified financial advisor before making any investment decisions. Use this tool at your own risk.";
