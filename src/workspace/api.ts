export type Actor = { name: string; role: "admin" | "operator" | "viewer"; csrf: string; lab_no_login?: boolean };
export type Camera = { id: string; name: string; configured: boolean; running: boolean; online: boolean;
  face_provider: string; plate_provider: string; inference: string; provider_issues: string[] };
export type Event = { id: string; camera_id: string; kind: string; observed_at: string;
  plate_text?: string; face_label?: string; confidence?: number; review_status: string };
export type Provider = { id: string; task: string; installed: boolean; state: string; hardware_validated: boolean };
export const apiRoot = "/garda-api";
export class ApiError extends Error {
  constructor(message: string, public status: number) { super(message); }
}

export async function request<T>(path: string, options: RequestInit = {}, csrf = ""): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body && !(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
  if (csrf) headers.set("X-GARDA-CSRF", csrf);
  const timeout = AbortSignal.timeout(10000);
  const signal = options.signal ? AbortSignal.any([options.signal, timeout]) : timeout;
  const response = await fetch(apiRoot + path, { ...options, headers, credentials: "same-origin", signal });
  const payload = await response.text();
  if (!response.ok) {
    let detail: unknown;
    try { detail = JSON.parse(payload)?.detail; } catch { detail = undefined; }
    const reason = typeof detail === "string" ? detail
      : Array.isArray(detail) ? detail.map(item => typeof item?.msg === "string" ? item.msg : "Invalid field").join("; ")
      : `HTTP ${response.status}`;
    throw new ApiError(response.status === 401 ? "Sesi berakhir. Silakan masuk kembali." : reason, response.status);
  }
  return payload ? JSON.parse(payload) as T : undefined as T;
}
