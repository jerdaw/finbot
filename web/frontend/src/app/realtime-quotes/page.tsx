"use client";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DataTable } from "@/components/common/data-table";
import { StatCard } from "@/components/common/stat-card";
import { PageHeader } from "@/components/common/page-header";
import { EmptyState } from "@/components/common/empty-state";
import { InlineError } from "@/components/common/inline-error";
import { CardSkeleton } from "@/components/common/loading-skeleton";
import { MetricBadge } from "@/components/common/metric-badge";
import { Zap, Plus, X, RefreshCw } from "lucide-react";
import { apiPost, apiGet } from "@/lib/api";
import { formatNumber, formatCurrency } from "@/lib/format";
import { useWatchlistStore } from "@/stores/watchlist-store";
import type { QuotesResponse, QuoteSchema, ProviderStatusResponse } from "@/types/api";

function QuoteCard({ q }: { q: QuoteSchema }) {
  return (
    <div className="relative overflow-hidden rounded-xl border border-border/50 bg-card/50 p-5 gradient-border">
      <div className="flex items-center justify-between">
        <span className="text-lg font-bold">{q.symbol}</span>
        <Badge variant="outline" className="text-[10px]">{q.provider}</Badge>
      </div>
      <p className="mt-2 text-2xl font-bold stat-value">{formatCurrency(q.price)}</p>
      <div className="mt-1 flex items-center gap-2">
        <MetricBadge value={q.change} format={(v) => `$${v.toFixed(2)}`} />
        <MetricBadge value={q.change_percent} format={(v) => `${v.toFixed(2)}%`} />
      </div>
      <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-muted-foreground">
        <span>Vol: {q.volume?.toLocaleString() ?? "N/A"}</span>
        <span>Open: {formatNumber(q.open)}</span>
        <span>High: {formatNumber(q.high)}</span>
        <span>Low: {formatNumber(q.low)}</span>
      </div>
    </div>
  );
}

function QuoteResults({ data, isPending }: { data: QuotesResponse | undefined; isPending: boolean }) {
  if (isPending) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <CardSkeleton />
        <CardSkeleton />
        <CardSkeleton />
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Quote cards */}
      {data.quotes.length > 0 && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data.quotes.map((q) => (
            <QuoteCard key={q.symbol} q={q} />
          ))}
        </div>
      )}

      {/* Error badges */}
      {Object.keys(data.errors).length > 0 && (
        <div className="flex flex-wrap gap-2">
          {Object.entries(data.errors).map(([symbol, error]) => (
            <Badge
              key={symbol}
              variant="outline"
              className="border-red-500/30 bg-red-500/5 text-red-400"
            >
              {symbol}: {error}
            </Badge>
          ))}
        </div>
      )}

      {/* Detail table */}
      {data.quotes.length > 0 && (
        <DataTable
          columns={[
            { key: "symbol", label: "Symbol" },
            { key: "price", label: "Price", format: (v) => formatCurrency(v as number) },
            { key: "change", label: "Change", format: (v) => v != null ? `$${(v as number).toFixed(2)}` : "N/A" },
            { key: "change_percent", label: "Change %", format: (v) => v != null ? `${(v as number).toFixed(2)}%` : "N/A" },
            { key: "volume", label: "Volume", format: (v) => v != null ? (v as number).toLocaleString() : "N/A" },
            { key: "open", label: "Open", format: (v) => formatNumber(v as number) },
            { key: "high", label: "High", format: (v) => formatNumber(v as number) },
            { key: "low", label: "Low", format: (v) => formatNumber(v as number) },
            { key: "previous_close", label: "Prev Close", format: (v) => formatNumber(v as number) },
            { key: "bid", label: "Bid", format: (v) => formatNumber(v as number) },
            { key: "ask", label: "Ask", format: (v) => formatNumber(v as number) },
            { key: "provider", label: "Provider" },
            { key: "timestamp", label: "Timestamp" },
          ]}
          data={data.quotes}
        />
      )}
    </div>
  );
}

export default function RealtimeQuotesPage() {
  const [symbolInput, setSymbolInput] = useState("");
  const [addInput, setAddInput] = useState("");
  const { symbols: watchlist, addSymbol, removeSymbol } = useWatchlistStore();

  // --- Live Quotes mutation ---
  const liveQuotesMutation = useMutation({
    mutationFn: (symbols: string[]) =>
      apiPost<QuotesResponse>("/api/realtime-quotes/quotes", { symbols }),
    onSuccess: () => toast.success("Quotes fetched"),
    onError: (e) => toast.error(`Failed to fetch quotes: ${e.message}`),
  });

  const handleFetchLive = () => {
    const symbols = symbolInput
      .split(",")
      .map((s) => s.trim().toUpperCase())
      .filter(Boolean);
    if (symbols.length === 0) {
      toast.error("Enter at least one symbol");
      return;
    }
    liveQuotesMutation.mutate(symbols);
  };

  // --- Watchlist mutation ---
  const watchlistMutation = useMutation({
    mutationFn: (symbols: string[]) =>
      apiPost<QuotesResponse>("/api/realtime-quotes/quotes", { symbols }),
    onSuccess: () => toast.success("Watchlist refreshed"),
    onError: (e) => toast.error(`Failed to refresh watchlist: ${e.message}`),
  });

  const handleRefreshWatchlist = () => {
    if (watchlist.length === 0) {
      toast.error("Watchlist is empty. Add some symbols first.");
      return;
    }
    watchlistMutation.mutate(watchlist);
  };

  const handleAddSymbol = () => {
    const sym = addInput.trim().toUpperCase();
    if (!sym) return;
    addSymbol(sym);
    setAddInput("");
  };

  // --- Provider Status ---
  const providerStatusQuery = useQuery({
    queryKey: ["provider-status"],
    queryFn: () => apiGet<ProviderStatusResponse>("/api/realtime-quotes/provider-status"),
    enabled: false,
  });

  const handleCheckStatus = () => {
    providerStatusQuery.refetch();
  };

  // Summary stats for live quotes
  const liveQuotes = liveQuotesMutation.data?.quotes;
  const watchlistQuotes = watchlistMutation.data?.quotes;

  return (
    <div className="space-y-8">
      <PageHeader
        title="Real-Time Quotes"
        description="Fetch live market data from multiple providers with automatic fallback"
      />

      <Tabs defaultValue="live" className="space-y-6">
        <TabsList>
          <TabsTrigger value="live">Live Quotes</TabsTrigger>
          <TabsTrigger value="watchlist">Watchlist</TabsTrigger>
          <TabsTrigger value="providers">Provider Status</TabsTrigger>
        </TabsList>

        {/* ===== Tab 1: Live Quotes ===== */}
        <TabsContent value="live" className="space-y-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
            <div className="flex-1 space-y-2">
              <Label className="text-xs text-muted-foreground">
                Symbols (comma-separated)
              </Label>
              <Input
                placeholder="AAPL, MSFT, GOOGL"
                value={symbolInput}
                onChange={(e) => setSymbolInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleFetchLive();
                }}
                className="border-border/50 bg-background/50"
              />
            </div>
            <Button
              className="bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
              onClick={handleFetchLive}
              disabled={liveQuotesMutation.isPending}
            >
              <Zap className="mr-2 h-4 w-4" />
              {liveQuotesMutation.isPending ? "Fetching..." : "Fetch Quotes"}
            </Button>
          </div>

          {/* Summary stat cards */}
          {liveQuotes && liveQuotes.length > 0 && (
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              <StatCard
                label="Symbols"
                value={String(liveQuotes.length)}
              />
              <StatCard
                label="Avg Price"
                value={formatCurrency(
                  liveQuotes.reduce((sum, q) => sum + q.price, 0) / liveQuotes.length,
                )}
              />
              <StatCard
                label="Top Gainer"
                value={(() => {
                  const best = [...liveQuotes]
                    .filter((q) => q.change_percent != null)
                    .sort((a, b) => (b.change_percent ?? 0) - (a.change_percent ?? 0))[0];
                  return best ? `${best.symbol} ${best.change_percent?.toFixed(2)}%` : "N/A";
                })()}
                trend="up"
              />
              <StatCard
                label="Top Loser"
                value={(() => {
                  const worst = [...liveQuotes]
                    .filter((q) => q.change_percent != null)
                    .sort((a, b) => (a.change_percent ?? 0) - (b.change_percent ?? 0))[0];
                  return worst ? `${worst.symbol} ${worst.change_percent?.toFixed(2)}%` : "N/A";
                })()}
                trend="down"
              />
            </div>
          )}

          <QuoteResults data={liveQuotesMutation.data} isPending={liveQuotesMutation.isPending} />

          {liveQuotesMutation.isError && (
            <InlineError
              message={liveQuotesMutation.error?.message ?? "Failed to fetch quotes"}
              onRetry={handleFetchLive}
            />
          )}

          {!liveQuotesMutation.isPending && !liveQuotesMutation.isError && !liveQuotesMutation.data && (
            <EmptyState
              icon={Zap}
              message="Enter ticker symbols and click Fetch Quotes to see live market data."
              presets={[
                {
                  label: "AAPL, MSFT, GOOGL",
                  onClick: () => {
                    setSymbolInput("AAPL, MSFT, GOOGL");
                  },
                },
                {
                  label: "SPY, QQQ, IWM",
                  onClick: () => {
                    setSymbolInput("SPY, QQQ, IWM");
                  },
                },
                {
                  label: "AMZN, NVDA, META",
                  onClick: () => {
                    setSymbolInput("AMZN, NVDA, META");
                  },
                },
              ]}
            />
          )}
        </TabsContent>

        {/* ===== Tab 2: Watchlist ===== */}
        <TabsContent value="watchlist" className="space-y-6">
          {/* Add symbol + refresh controls */}
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
            <div className="flex-1 space-y-2">
              <Label className="text-xs text-muted-foreground">Add Symbol</Label>
              <div className="flex gap-2">
                <Input
                  placeholder="TSLA"
                  value={addInput}
                  onChange={(e) => setAddInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleAddSymbol();
                  }}
                  className="border-border/50 bg-background/50"
                />
                <Button
                  variant="outline"
                  onClick={handleAddSymbol}
                  className="border-border/50"
                >
                  <Plus className="mr-1 h-4 w-4" />
                  Add
                </Button>
              </div>
            </div>
            <Button
              className="bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
              onClick={handleRefreshWatchlist}
              disabled={watchlistMutation.isPending || watchlist.length === 0}
            >
              <RefreshCw
                className={`mr-2 h-4 w-4 ${watchlistMutation.isPending ? "animate-spin" : ""}`}
              />
              {watchlistMutation.isPending ? "Refreshing..." : "Refresh All"}
            </Button>
          </div>

          {/* Watchlist badges */}
          {watchlist.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {watchlist.map((sym) => (
                <Badge
                  key={sym}
                  variant="outline"
                  className="gap-1 border-border/50 bg-card/50 pr-1 text-sm"
                >
                  {sym}
                  <button
                    onClick={() => removeSymbol(sym)}
                    className="ml-1 rounded-full p-0.5 transition-colors hover:bg-red-500/20 hover:text-red-400"
                    aria-label={`Remove ${sym}`}
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              No symbols in your watchlist. Add some above to get started.
            </p>
          )}

          {/* Summary stat cards */}
          {watchlistQuotes && watchlistQuotes.length > 0 && (
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              <StatCard
                label="Symbols"
                value={String(watchlistQuotes.length)}
              />
              <StatCard
                label="Avg Price"
                value={formatCurrency(
                  watchlistQuotes.reduce((sum, q) => sum + q.price, 0) / watchlistQuotes.length,
                )}
              />
              <StatCard
                label="Top Gainer"
                value={(() => {
                  const best = [...watchlistQuotes]
                    .filter((q) => q.change_percent != null)
                    .sort((a, b) => (b.change_percent ?? 0) - (a.change_percent ?? 0))[0];
                  return best ? `${best.symbol} ${best.change_percent?.toFixed(2)}%` : "N/A";
                })()}
                trend="up"
              />
              <StatCard
                label="Top Loser"
                value={(() => {
                  const worst = [...watchlistQuotes]
                    .filter((q) => q.change_percent != null)
                    .sort((a, b) => (a.change_percent ?? 0) - (b.change_percent ?? 0))[0];
                  return worst ? `${worst.symbol} ${worst.change_percent?.toFixed(2)}%` : "N/A";
                })()}
                trend="down"
              />
            </div>
          )}

          <QuoteResults data={watchlistMutation.data} isPending={watchlistMutation.isPending} />

          {watchlistMutation.isError && (
            <InlineError
              message={watchlistMutation.error?.message ?? "Failed to refresh watchlist"}
              onRetry={handleRefreshWatchlist}
            />
          )}

          {!watchlistMutation.isPending && !watchlistMutation.isError && !watchlistMutation.data && watchlist.length > 0 && (
            <EmptyState
              icon={Zap}
              message="Click Refresh All to fetch live quotes for your watchlist."
            />
          )}
        </TabsContent>

        {/* ===== Tab 3: Provider Status ===== */}
        <TabsContent value="providers" className="space-y-6">
          <div className="flex items-center gap-3">
            <Button
              className="bg-gradient-to-r from-blue-600 to-blue-500 font-medium text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/30"
              onClick={handleCheckStatus}
              disabled={providerStatusQuery.isFetching}
            >
              <RefreshCw
                className={`mr-2 h-4 w-4 ${providerStatusQuery.isFetching ? "animate-spin" : ""}`}
              />
              {providerStatusQuery.isFetching ? "Checking..." : "Check Status"}
            </Button>
          </div>

          {providerStatusQuery.isFetching && !providerStatusQuery.data && (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <CardSkeleton />
              <CardSkeleton />
              <CardSkeleton />
            </div>
          )}

          {providerStatusQuery.data && (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {providerStatusQuery.data.providers.map((p) => (
                <div
                  key={p.provider}
                  className="rounded-xl border border-border/50 bg-card/50 p-5"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold">{p.provider}</span>
                    <Badge
                      variant="outline"
                      className={
                        p.is_available
                          ? "border-emerald-500/30 bg-emerald-500/5 text-emerald-400"
                          : "border-red-500/30 bg-red-500/5 text-red-400"
                      }
                    >
                      {p.is_available ? "Available" : "Unavailable"}
                    </Badge>
                  </div>
                  <div className="mt-3 space-y-1 text-xs text-muted-foreground">
                    <p>Requests: {p.total_requests}</p>
                    <p>Errors: {p.total_errors}</p>
                    {p.last_success && (
                      <p>Last Success: {new Date(p.last_success).toLocaleString()}</p>
                    )}
                    {p.last_error && (
                      <p className="text-red-400">Last Error: {p.last_error}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {providerStatusQuery.isError && (
            <InlineError
              message={providerStatusQuery.error?.message ?? "Failed to check provider status"}
              onRetry={handleCheckStatus}
            />
          )}

          {!providerStatusQuery.isFetching && !providerStatusQuery.isError && !providerStatusQuery.data && (
            <EmptyState
              icon={Zap}
              message="Click Check Status to see the health of all data providers."
            />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
