export type Task = {
  id: string;
  name: string;
  description: string;
  state: string;
  spec: string;
  tests: string;
  code: string;
  certification_notes: string;
  red_report_path: string | null;
  green_report_path: string | null;
  confidence: number;
  grounding: string[];
  created_at: string;
  updated_at: string;
  history: Array<{ from: string; to: string; notes: string; at: string }>;
};

export type ModelInfo = {
  id: string;
  name: string;
  backend: string;
  available: boolean;
  size_gb?: number | null;
  quantization?: string | null;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export function listTasks(state?: string) {
  const q = state ? `?state=${encodeURIComponent(state)}` : "";
  return request<Task[]>(`/api/tasks${q}`);
}

export function getTask(id: string) {
  return request<Task>(`/api/tasks/${id}`);
}

export function createTask(name: string, description = "") {
  return request<Task>("/api/tasks", {
    method: "POST",
    body: JSON.stringify({ name, description }),
  });
}

export function updateTask(id: string, body: Partial<Pick<Task, "spec" | "tests" | "code" | "confidence">>) {
  return request<Task>(`/api/tasks/${id}`, { method: "PATCH", body: JSON.stringify(body) });
}

export function certifyTask(id: string, approved: boolean, notes = "") {
  return request<Task>(`/api/tasks/${id}/certify`, {
    method: "POST",
    body: JSON.stringify({ approved, notes }),
  });
}

export function attachRedReport(id: string) {
  return request<Task>(`/api/tasks/${id}/red-report`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export function listModels() {
  return request<ModelInfo[]>("/api/models");
}

export function health() {
  return request<{ status: string; version: string }>("/api/health");
}

export function relativeTime(iso: string): string {
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return iso;
  const delta = Date.now() - then;
  const mins = Math.round(delta / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.round(hours / 24);
  return `${days}d ago`;
}
