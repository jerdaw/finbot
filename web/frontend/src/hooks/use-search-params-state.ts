"use client";

import { useCallback } from "react";
import { useSearchParams, useRouter, usePathname } from "next/navigation";

/**
 * Sync form state with URL search params for shareable/bookmarkable configurations.
 *
 * @param defaults - Default values for each param key
 * @returns [values, setValues] tuple
 */
export function useSearchParamsState<T extends Record<string, string>>(
  defaults: T,
): [T, (updates: Partial<T>) => void] {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  // Read current values from URL, falling back to defaults
  const values = {} as T;
  for (const key of Object.keys(defaults) as (keyof T)[]) {
    const urlValue = searchParams.get(key as string);
    (values as Record<string, string>)[key as string] = urlValue ?? defaults[key];
  }

  const setValues = useCallback(
    (updates: Partial<T>) => {
      const params = new URLSearchParams(searchParams.toString());
      for (const [key, value] of Object.entries(updates)) {
        if (value === undefined || value === null || value === defaults[key as keyof T]) {
          params.delete(key);
        } else {
          params.set(key, value as string);
        }
      }
      const qs = params.toString();
      router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
    },
    [searchParams, router, pathname, defaults],
  );

  return [values, setValues];
}
