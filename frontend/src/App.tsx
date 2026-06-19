import { useState } from "react";
import { analyze, DEFAULT_CONFIG } from "./api";
import type { AnalysisResult, PumpConfig } from "./types";
import UploadForm from "./components/UploadForm";
import SummaryChips from "./components/SummaryChips";
import RatioCards from "./components/RatioCards";
import TimeOfDayTable from "./components/TimeOfDayTable";
import MealHabitsTable from "./components/MealHabitsTable";
import DailySummary from "./components/DailySummary";

export default function App() {
  const [config, setConfig] = useState<PumpConfig>(DEFAULT_CONFIG);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(file: File) {
    setLoading(true);
    setError(null);
    try {
      setResult(await analyze(file, config));
    } catch (e) {
      setResult(null);
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Lagom</h1>
        <p>Omnipod 5 bolus ratio analysis</p>
      </header>

      <UploadForm
        config={config}
        loading={loading}
        onConfigChange={setConfig}
        onSubmit={handleSubmit}
      />

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="results">
          <SummaryChips summary={result.summary} />
          <RatioCards isf={result.isf} icr={result.icr} />
          <TimeOfDayTable breakdown={result.time_of_day_breakdown} />
          <MealHabitsTable habits={result.meal_habits} />
          <DailySummary days={result.daily_summary} />
        </div>
      )}
    </div>
  );
}
