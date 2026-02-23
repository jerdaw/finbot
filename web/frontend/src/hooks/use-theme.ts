"use client";

import { useEffect } from "react";
import { useThemeStore } from "@/stores/theme-store";

export function useTheme() {
  const { theme, toggle, setTheme } = useThemeStore();

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  }, [theme]);

  return { theme, toggle, setTheme };
}
