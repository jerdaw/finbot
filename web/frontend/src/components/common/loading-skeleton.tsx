import { Skeleton } from "@/components/ui/skeleton";

export function CardSkeleton() {
  return (
    <div className="relative overflow-hidden rounded-lg border border-border/60 bg-card p-4 shadow-sm">
      <Skeleton className="h-3 w-1/3 rounded-md" />
      <Skeleton className="mt-4 h-7 w-2/3 rounded-md" />
      <div className="shimmer absolute inset-0 rounded-lg" />
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="relative overflow-hidden rounded-lg border border-border/60 bg-card p-4 shadow-sm">
      <Skeleton className="h-3 w-1/4 rounded-md" />
      <Skeleton className="mt-4 h-[300px] w-full rounded-lg" />
      <div className="shimmer absolute inset-0 rounded-lg" />
    </div>
  );
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="relative overflow-hidden rounded-lg border border-border/60 bg-card p-4 shadow-sm">
      <Skeleton className="h-8 w-full rounded-md" />
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="mt-2 h-6 w-full rounded-md" />
      ))}
      <div className="shimmer absolute inset-0 rounded-lg" />
    </div>
  );
}

export function PageSkeleton() {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <Skeleton className="h-8 w-1/3 rounded-md" />
        <Skeleton className="h-4 w-1/2 rounded-md" />
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <CardSkeleton />
        <CardSkeleton />
        <CardSkeleton />
        <CardSkeleton />
      </div>
      <ChartSkeleton />
      <TableSkeleton />
    </div>
  );
}
