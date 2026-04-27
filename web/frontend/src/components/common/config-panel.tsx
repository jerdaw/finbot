"use client";

import { useId, useState, type ReactNode } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface ConfigPanelProps {
  title: string;
  children: ReactNode;
  className?: string;
}

interface ConfigSectionProps {
  title: string;
  children: ReactNode;
  className?: string;
  defaultOpen?: boolean;
  description?: string;
  summary?: ReactNode;
}

export function ConfigPanel({ title, children, className }: ConfigPanelProps) {
  return (
    <div
      className={cn(
        "config-panel relative min-w-0 overflow-hidden rounded-lg border border-border/60 bg-card shadow-sm",
        "h-fit",
        className,
      )}
    >
      <div className="border-b border-border/60 bg-muted/20 px-5 py-4">
        <h3 className="text-xs font-bold tracking-wider text-muted-foreground uppercase">
          {title}
        </h3>
      </div>
      <div
        className={cn(
          "grid min-w-0 grid-cols-1 gap-6 p-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4",
          "[&>*]:min-w-0 [&>button:last-child]:self-end",
        )}
      >
        {children}
      </div>
    </div>
  );
}

export function ConfigSection({
  title,
  children,
  className,
  defaultOpen = true,
  description,
  summary,
}: ConfigSectionProps) {
  const [open, setOpen] = useState(defaultOpen);
  const contentId = useId();

  return (
    <section
      className={cn(
        "config-section col-span-full overflow-hidden rounded-lg border border-border/50 bg-background/30",
        className,
      )}
    >
      <button
        type="button"
        className={cn(
          "flex w-full items-center justify-between gap-4 px-5 py-4 text-left transition-colors hover:bg-muted/20",
          open && "border-b border-border/40",
        )}
        aria-expanded={open}
        aria-controls={contentId}
        onClick={() => setOpen((value) => !value)}
      >
        <span className="min-w-0">
          <span className="block text-xs font-bold tracking-wider text-muted-foreground uppercase">
            {title}
          </span>
          {description && open ? (
            <span className="mt-1 block text-xs leading-relaxed text-muted-foreground/70">
              {description}
            </span>
          ) : null}
        </span>
        {summary ? (
          <span className="ml-auto hidden shrink-0 items-center gap-2 rounded-md border border-border/50 bg-muted/20 px-2 py-1 text-xs font-medium text-muted-foreground sm:inline-flex">
            {summary}
          </span>
        ) : null}
        <ChevronDown
          className={cn(
            "h-4 w-4 shrink-0 text-muted-foreground transition-transform",
            open && "rotate-180",
          )}
        />
      </button>
      {open ? (
        <div
          id={contentId}
          className="grid min-w-0 grid-cols-1 gap-6 p-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 [&>*]:min-w-0"
        >
          {children}
        </div>
      ) : null}
    </section>
  );
}
