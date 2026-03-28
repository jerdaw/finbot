import { create } from "zustand";
import { persist } from "zustand/middleware";

interface WatchlistStore {
  symbols: string[];
  addSymbol: (symbol: string) => void;
  removeSymbol: (symbol: string) => void;
  setSymbols: (symbols: string[]) => void;
}

export const useWatchlistStore = create<WatchlistStore>()(
  persist(
    (set) => ({
      symbols: ["SPY", "QQQ", "TLT", "GLD", "VTI"],
      addSymbol: (symbol) =>
        set((s) => ({
          symbols: s.symbols.includes(symbol.toUpperCase())
            ? s.symbols
            : [...s.symbols, symbol.toUpperCase()],
        })),
      removeSymbol: (symbol) =>
        set((s) => ({
          symbols: s.symbols.filter((sym) => sym !== symbol.toUpperCase()),
        })),
      setSymbols: (symbols) =>
        set({ symbols: symbols.map((s) => s.toUpperCase()) }),
    }),
    { name: "finbot-watchlist" },
  ),
);
