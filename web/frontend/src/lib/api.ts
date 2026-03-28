const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const DEFAULT_TIMEOUT = 120_000;

async function request<T>(
  url: string,
  init: RequestInit,
  timeout: number,
): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  try {
    const res = await fetch(`${BASE_URL}${url}`, {
      ...init,
      signal: controller.signal,
    });

    if (!res.ok) {
      let message = `Request failed (${res.status})`;
      try {
        const body = await res.json();
        if (body.detail) {
          message = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
        }
      } catch {
        // response body was not JSON — use default message
      }
      throw new Error(message);
    }

    return (await res.json()) as T;
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new Error(`Request timed out after ${Math.round(timeout / 1000)}s`);
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }
}

export function apiGet<T>(url: string, timeout = DEFAULT_TIMEOUT): Promise<T> {
  return request<T>(url, { method: "GET" }, timeout);
}

export function apiPost<T>(
  url: string,
  body: unknown,
  timeout = DEFAULT_TIMEOUT,
): Promise<T> {
  return request<T>(
    url,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    },
    timeout,
  );
}
