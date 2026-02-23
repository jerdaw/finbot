"use client";

import { useEffect, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { DISCLAIMER_TEXT } from "@/lib/constants";

const STORAGE_KEY = "finbot-disclaimer-accepted";

export function DisclaimerModal() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const accepted = localStorage.getItem(STORAGE_KEY);
    if (!accepted) {
      setOpen(true);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem(STORAGE_KEY, "true");
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="border-border/50 bg-card/95 backdrop-blur-xl sm:max-w-lg">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-blue-500/30 to-transparent" />
        <DialogHeader>
          <DialogTitle className="text-xl font-bold">
            Important Disclaimer
          </DialogTitle>
          <DialogDescription className="pt-4 text-sm leading-relaxed text-muted-foreground">
            {DISCLAIMER_TEXT}
          </DialogDescription>
        </DialogHeader>
        <div className="mt-4 flex justify-end">
          <Button
            onClick={handleAccept}
            className="bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg shadow-blue-500/20 transition-shadow hover:shadow-blue-500/30"
          >
            I Understand
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
