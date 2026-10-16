import type { Timestamp } from "./types";

export function asDate(value: Timestamp | null | undefined): Date | null {
  if (value === null || value === undefined || value === "") return null;
  const date = new Date(typeof value === "number" ? value * 1000 : value);
  return Number.isNaN(date.getTime()) ? null : date;
}

export function dateTime(value: Timestamp | null | undefined): string {
  return (
    asDate(value)?.toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }) ?? "Not available"
  );
}

export function relative(value: Timestamp | null | undefined): string {
  const date = asDate(value);
  if (!date) return "Not available";
  const seconds = Math.round((date.getTime() - Date.now()) / 1000);
  const abs = Math.abs(seconds);
  if (abs < 60) return seconds > 0 ? "in less than a minute" : "just now";
  const unit = abs < 3600 ? "minute" : abs < 86400 ? "hour" : "day";
  const n = Math.round(
    seconds / (unit === "minute" ? 60 : unit === "hour" ? 3600 : 86400),
  );
  return new Intl.RelativeTimeFormat(undefined, { numeric: "auto" }).format(
    n,
    unit,
  );
}

export function bytes(value: number): string {
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

export function readable(value: string): string {
  return value
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export function describe(value: unknown): string {
  if (typeof value === "string") return value;
  if (value === null || value === undefined) return "None";
  if (typeof value !== "object") return String(value);
  const v = value as Record<string, unknown>;
  return String(
    v.path ??
      v.reference ??
      v.name ??
      v.symbol ??
      v.query ??
      v.message ??
      JSON.stringify(value),
  );
}
