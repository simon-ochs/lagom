import type { Summary } from "../types";

const LABELS: Array<[keyof Summary, string]> = [
  ["cgm_readings", "CGM readings"],
  ["bolus_events", "Bolus events"],
  ["clean_windows", "Clean windows"],
  ["rejected_windows", "Rejected windows"],
  ["pod_failures", "Pod failures"],
];

export default function SummaryChips({ summary }: { summary: Summary }) {
  return (
    <section className="chips">
      {LABELS.map(([key, label]) => (
        <div className="chip" key={key}>
          <span className="chip-value">{summary[key].toLocaleString()}</span>
          <span className="chip-label">{label}</span>
        </div>
      ))}
    </section>
  );
}
