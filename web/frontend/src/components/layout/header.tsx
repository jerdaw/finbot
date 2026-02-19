"use client";

import { usePathname } from "next/navigation";
import { Moon, Sun, Search } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { NAV_ITEMS } from "@/lib/constants";
import { useTheme } from "@/hooks/use-theme";
import { MobileMenuButton } from "@/components/layout/sidebar";

interface HeaderProps {
  onMobileMenuOpen?: () => void;
  onCommandPaletteOpen?: () => void;
}

export function Header({ onMobileMenuOpen, onCommandPaletteOpen }: HeaderProps) {
  const pathname = usePathname();
  const { theme, toggle: toggleTheme } = useTheme();

  const current = NAV_ITEMS.find(
    (item) =>
      pathname === item.href ||
      (item.href !== "/" && pathname.startsWith(item.href)),
  );
  const title = current?.label || "Dashboard";

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b border-border/50 bg-background/60 px-4 backdrop-blur-xl lg:px-6">
      {onMobileMenuOpen && <MobileMenuButton onClick={onMobileMenuOpen} />}

      <h1 className="text-sm font-semibold tracking-wide text-muted-foreground uppercase">
        {title}
      </h1>

      <div className="ml-auto flex items-center gap-2">
        {/* Command palette trigger */}
        {onCommandPaletteOpen && (
          <Tooltip delayDuration={0}>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size="sm"
                className="hidden h-8 gap-2 border-border/50 bg-card/50 px-3 text-xs text-muted-foreground hover:text-foreground sm:flex"
                onClick={onCommandPaletteOpen}
              >
                <Search className="h-3.5 w-3.5" />
                <span className="hidden md:inline">Search...</span>
                <kbd className="pointer-events-none hidden rounded border border-border/50 bg-muted/50 px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground md:inline">
                  {typeof navigator !== "undefined" && /Mac/.test(navigator.userAgent) ? "\u2318K" : "Ctrl+K"}
                </kbd>
              </Button>
            </TooltipTrigger>
            <TooltipContent className="border-border/50 bg-popover/95 backdrop-blur-sm">
              Command palette
            </TooltipContent>
          </Tooltip>
        )}

        {/* Theme toggle */}
        <Tooltip delayDuration={0}>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-muted-foreground hover:text-foreground"
              onClick={toggleTheme}
            >
              {theme === "dark" ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
              <span className="sr-only">Toggle theme</span>
            </Button>
          </TooltipTrigger>
          <TooltipContent className="border-border/50 bg-popover/95 backdrop-blur-sm">
            {theme === "dark" ? "Light mode" : "Dark mode"}
          </TooltipContent>
        </Tooltip>

        <Badge
          variant="outline"
          className="border-yellow-500/30 bg-yellow-500/5 text-[10px] font-medium tracking-wider text-yellow-500 uppercase"
        >
          Educational Only
        </Badge>
      </div>
    </header>
  );
}
