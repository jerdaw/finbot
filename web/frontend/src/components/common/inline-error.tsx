"use client";

import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface InlineErrorProps {
  message: string;
  onRetry?: () => void;
}

export function InlineError({ message, onRetry }: InlineErrorProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 rounded-xl border border-dashed border-red-500/30 bg-red-500/5 py-16">
      <AlertTriangle className="h-10 w-10 text-red-400/60" />
      <p className="max-w-md text-center text-sm text-red-400">{message}</p>
      {onRetry && (
        <Button
          variant="outline"
          size="sm"
          onClick={onRetry}
          className="border-red-500/30 text-red-400 hover:bg-red-500/10 hover:text-red-300"
        >
          Retry
        </Button>
      )}
    </div>
  );
}
