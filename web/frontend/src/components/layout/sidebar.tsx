"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { PanelLeftClose, PanelLeft, Menu } from "lucide-react";
import { cn } from "@/lib/utils";
import { NAV_ITEMS, NAV_GROUPS } from "@/lib/constants";
import type { NavItem } from "@/lib/constants";
import { useSidebarStore } from "@/stores/sidebar-store";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { useIsDesktop } from "@/hooks/use-media-query";

function Logo({ collapsed = false }: { collapsed?: boolean }) {
  return (
    <div className={cn("flex items-center gap-2.5", collapsed && "justify-center")}>
      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg shadow-blue-500/20">
        <span className="text-sm font-bold text-white">F</span>
      </div>
      {!collapsed && (
        <span className="text-lg font-bold tracking-tight">Finbot</span>
      )}
    </div>
  );
}

function NavLink({
  item,
  collapsed = false,
  onClick,
}: {
  item: NavItem;
  collapsed?: boolean;
  onClick?: () => void;
}) {
  const pathname = usePathname();
  const isActive =
    pathname === item.href ||
    (item.href !== "/" && pathname.startsWith(item.href));
  const Icon = item.icon;

  const link = (
    <Link
      href={item.href}
      onClick={onClick}
      className={cn(
        "group flex items-center gap-3 rounded-lg px-3 py-2.5 text-[13px] font-medium transition-all duration-200",
        isActive
          ? "nav-active text-foreground"
          : "text-muted-foreground hover:bg-accent/50 hover:text-foreground",
        collapsed && "justify-center px-2",
      )}
    >
      <Icon
        className={cn(
          "h-[18px] w-[18px] shrink-0 transition-colors",
          isActive
            ? "text-blue-400"
            : "text-muted-foreground group-hover:text-foreground",
        )}
      />
      {!collapsed && <span>{item.label}</span>}
    </Link>
  );

  if (collapsed) {
    return (
      <Tooltip delayDuration={0}>
        <TooltipTrigger asChild>{link}</TooltipTrigger>
        <TooltipContent
          side="right"
          className="border-border/50 bg-popover/95 backdrop-blur-sm"
        >
          {item.label}
        </TooltipContent>
      </Tooltip>
    );
  }

  return link;
}

function GroupedNav({
  collapsed = false,
  onNavigate,
}: {
  collapsed?: boolean;
  onNavigate?: () => void;
}) {
  return (
    <nav className="flex-1 overflow-y-auto px-2">
      {NAV_GROUPS.map((group, groupIdx) => {
        const items = NAV_ITEMS.filter((item) => item.group === group);
        if (items.length === 0) return null;

        return (
          <div key={group} className={cn(groupIdx > 0 && "mt-4")}>
            {!collapsed ? (
              <p className="mb-1 px-3 text-[10px] font-semibold tracking-widest text-muted-foreground/60 uppercase">
                {group}
              </p>
            ) : (
              groupIdx > 0 && (
                <div className="mx-3 mb-2 border-t border-border/30" />
              )
            )}
            <div className="space-y-0.5">
              {items.map((item) => (
                <NavLink
                  key={item.href}
                  item={item}
                  collapsed={collapsed}
                  onClick={onNavigate}
                />
              ))}
            </div>
          </div>
        );
      })}
    </nav>
  );
}

/** Desktop sidebar — fixed, collapsible */
export function DesktopSidebar() {
  const { collapsed, toggle } = useSidebarStore();

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 hidden h-screen flex-col border-r border-border/50 bg-sidebar/80 backdrop-blur-xl transition-all duration-300 lg:flex",
        collapsed ? "w-16" : "w-60",
      )}
    >
      <div className="flex h-16 items-center border-b border-border/50 px-4">
        <Logo collapsed={collapsed} />
      </div>

      <div className="flex justify-end px-2 py-2">
        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7 rounded-md text-muted-foreground hover:text-foreground"
          onClick={toggle}
        >
          {collapsed ? (
            <PanelLeft className="h-3.5 w-3.5" />
          ) : (
            <PanelLeftClose className="h-3.5 w-3.5" />
          )}
        </Button>
      </div>

      <GroupedNav collapsed={collapsed} />
    </aside>
  );
}

/** Mobile sidebar — Sheet overlay */
export function MobileSidebar({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="left"
        className="w-60 border-border/50 bg-sidebar/95 p-0 backdrop-blur-xl"
        showCloseButton={false}
      >
        <SheetHeader className="border-b border-border/50 px-4 py-4">
          <SheetTitle className="sr-only">Navigation</SheetTitle>
          <Logo />
        </SheetHeader>
        <GroupedNav onNavigate={() => onOpenChange(false)} />
      </SheetContent>
    </Sheet>
  );
}

/** Mobile menu trigger button for the header */
export function MobileMenuButton({ onClick }: { onClick: () => void }) {
  const isDesktop = useIsDesktop();
  if (isDesktop) return null;

  return (
    <Button
      variant="ghost"
      size="icon"
      className="h-8 w-8 text-muted-foreground hover:text-foreground lg:hidden"
      onClick={onClick}
    >
      <Menu className="h-4 w-4" />
      <span className="sr-only">Open menu</span>
    </Button>
  );
}

/** Legacy export for backward compatibility during migration */
export function Sidebar() {
  return <DesktopSidebar />;
}
