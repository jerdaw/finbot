export function formatPercent(value: number | null | undefined): string {
  if (value == null || isNaN(value)) return "N/A";
  return `${(value * 100).toFixed(2)}%`;
}

export function formatNumber(
  value: number | null | undefined,
  decimals = 2,
): string {
  if (value == null || isNaN(value)) return "N/A";
  return value.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function formatCurrency(value: number | null | undefined): string {
  if (value == null || isNaN(value)) return "N/A";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatCurrencyPrecise(value: number | null | undefined): string {
  if (value == null || isNaN(value)) return "N/A";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

export function formatBytes(bytes: number | null | undefined): string {
  if (bytes == null || isNaN(bytes)) return "N/A";
  if (bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  const size = bytes / Math.pow(1024, i);
  return `${size.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}
