import { useState } from "react";
import type { PumpConfig } from "../types";

interface Props {
  config: PumpConfig;
  loading: boolean;
  onConfigChange: (config: PumpConfig) => void;
  onSubmit: (file: File) => void;
}

export default function UploadForm({
  config,
  loading,
  onConfigChange,
  onSubmit,
}: Props) {
  const [file, setFile] = useState<File | null>(null);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (file) onSubmit(file);
  }

  function setField(field: keyof PumpConfig, value: string) {
    onConfigChange({ ...config, [field]: Number(value) });
  }

  return (
    <form className="upload-form" onSubmit={handleSubmit}>
      <label className="file-field">
        <span>Glooko export (.zip)</span>
        <input
          type="file"
          accept=".zip"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
      </label>

      <div className="config-fields">
        <label>
          <span>ICR (g/U)</span>
          <input
            type="number"
            step="0.1"
            value={config.icr}
            onChange={(e) => setField("icr", e.target.value)}
          />
        </label>
        <label>
          <span>ISF (mg/dL/U)</span>
          <input
            type="number"
            step="0.1"
            value={config.isf}
            onChange={(e) => setField("isf", e.target.value)}
          />
        </label>
        <label>
          <span>Target (mg/dL)</span>
          <input
            type="number"
            step="1"
            value={config.target_glucose}
            onChange={(e) => setField("target_glucose", e.target.value)}
          />
        </label>
      </div>

      <button type="submit" disabled={!file || loading}>
        {loading ? "Analyzing…" : "Analyze"}
      </button>
    </form>
  );
}
