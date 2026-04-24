"use client";

import { usePathname } from "next/navigation";
import { NAV_ITEMS } from "@/lib/constants";

interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: React.ReactNode;
}

export function PageHeader({ title, description, actions }: PageHeaderProps) {
  const pathname = usePathname();
  const current = NAV_ITEMS.find(
    (item) =>
      pathname === item.href ||
      (item.href !== "/" && pathname.startsWith(item.href)),
  );
  const Icon = current?.icon;

  return (
    <div className="border-b border-border/60 pb-5">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <div className="flex min-w-0 items-start gap-3">
          {Icon && (
            <div className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-border/60 bg-card text-muted-foreground shadow-xs">
              <Icon className="h-5 w-5" />
            </div>
          )}
          <div className="min-w-0">
            {current?.group && (
              <p className="mb-1 text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">
                {current.group}
              </p>
            )}
            <h2 className="text-2xl font-semibold tracking-tight text-foreground lg:text-3xl">
              {title}
            </h2>
            {description && (
              <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
                {description}
              </p>
            )}
          </div>
        </div>
        {actions && (
          <div className="flex w-full flex-wrap items-center gap-2 xl:w-auto xl:justify-end">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}
