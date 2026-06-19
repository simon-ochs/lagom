import type { AnalysisResult, PumpConfig } from "./types";

export const DEFAULT_CONFIG: PumpConfig = {
  icr: 10,
  isf: 30,
  target_glucose: 110,
};

export async function analyze(
  file: File,
  config: PumpConfig,
): Promise<AnalysisResult> {
  const form = new FormData();
  form.append("file", file);
  form.append("config", JSON.stringify(config));

  const res = await fetch("/analyze", { method: "POST", body: form });

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      // non-JSON error body; keep the status-based message
    }
    throw new Error(detail);
  }

  return res.json();
}
