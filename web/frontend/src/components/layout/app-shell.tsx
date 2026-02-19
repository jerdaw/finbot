"use client";

import { useState, useCallback, type ReactNode } from "react";
import { DesktopSidebar, MobileSidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { CommandPalette } from "@/components/layout/command-palette";
import { DisclaimerModal } from "@/components/common/disclaimer-modal";
import { PageTransition } from "@/components/layout/page-transition";
import { ErrorBoundary } from "@/components/common/error-boundary";
import { useSidebarStore } from "@/stores/sidebar-store";
import { useIsDesktop } from "@/hooks/use-media-query";
import { cn } from "@/lib/utils";

export function AppShell({ children }: { children: ReactNode }) {
  const collapsed = useSidebarStore((s) => s.collapsed);
  const isDesktop = useIsDesktop();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);

  const handleMobileMenuOpen = useCallback(() => setMobileMenuOpen(true), []);
  const handleCommandPaletteOpen = useCallback(() => setCommandPaletteOpen(true), []);

  return (
    <>
      <DisclaimerModal />
      <DesktopSidebar />
      <MobileSidebar open={mobileMenuOpen} onOpenChange={setMobileMenuOpen} />
      <CommandPalette open={commandPaletteOpen} onOpenChange={setCommandPaletteOpen} />
      <div
        className={cn(
          "min-h-screen transition-all duration-300",
          isDesktop ? (collapsed ? "ml-16" : "ml-60") : "ml-0",
        )}
      >
        <Header
          onMobileMenuOpen={!isDesktop ? handleMobileMenuOpen : undefined}
          onCommandPaletteOpen={handleCommandPaletteOpen}
        />
        <main className="p-4 sm:p-6 lg:p-8">
          <ErrorBoundary>
            <PageTransition>{children}</PageTransition>
          </ErrorBoundary>
        </main>
      </div>
    </>
  );
}
