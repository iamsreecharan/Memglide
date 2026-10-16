export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function errorMessage(body: unknown, fallback: string): string {
  if (!body || typeof body !== "object") return fallback;
  const record = body as Record<string, unknown>;
  const value = record.error ?? record.detail ?? record.message;
  if (typeof value === "string") return value;
  if (Array.isArray(value))
    return value
      .map((item) =>
        typeof item === "object" && item
          ? String(
              (item as Record<string, unknown>).msg ?? JSON.stringify(item),
            )
          : String(item),
      )
      .join("; ");
  if (value && typeof value === "object")
    return String((value as Record<string, unknown>).message ?? fallback);
  return fallback;
}

export async function api<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const method = options.method ?? "GET";
  let response: Response;
  try {
    response = await fetch(`/api${path}`, {
      cache: "no-store",
      ...options,
      headers: {
        Accept: "application/json",
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...(method !== "GET" && method !== "HEAD"
          ? { "X-Memglide-Request": "1" }
          : {}),
        ...options.headers,
      },
    });
  } catch {
    throw new ApiError(
      "Cannot reach the local Memglide service. Start it with memglide serve and try again.",
      0,
    );
  }
  const body: unknown =
    response.status === 204
      ? undefined
      : await response.json().catch(() => undefined);
  if (!response.ok)
    throw new ApiError(
      errorMessage(body, `Request failed (${response.status})`),
      response.status,
    );
  return body as T;
}

export function post<T>(path: string, body: unknown = {}): Promise<T> {
  return api<T>(path, { method: "POST", body: JSON.stringify(body) });
}

export function queryString(
  values: Record<string, string | number | undefined | null>,
): string {
  const params = new URLSearchParams();
  Object.entries(values).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "")
      params.set(key, String(value));
  });
  const result = params.toString();
  return result ? `?${result}` : "";
}

export function list<T>(value: T[] | Record<string, T[]>, key: string): T[] {
  return Array.isArray(value) ? value : (value[key] ?? []);
}

export function message(error: unknown): string {
  return error instanceof Error
    ? error.message
    : "Something went wrong. Please try again.";
}
