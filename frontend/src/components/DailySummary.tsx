import type { DaySummary } from "../types";

export default function DailySummary({ days }: { days: DaySummary[] }) {
  return (
    <section className="panel">
      <h3>Daily insulin</h3>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th className="bar-head">Basal / bolus split</th>
            <th className="num-col">Basal (U)</th>
            <th className="num-col">Bolus (U)</th>
            <th className="num-col">Total (U)</th>
          </tr>
        </thead>
        <tbody>
          {days.map((d) => (
            <tr key={d.date} className={d.pod_failure ? "pod-failure" : ""}>
              <td>
                {d.date}
                {d.pod_failure && (
                  <span className="pod-flag" title="Pod failure">
                    ⚠ pod
                  </span>
                )}
              </td>
              <td className="bar-cell">
                <div className="split-bar">
                  <span
                    className="seg basal"
                    style={{ width: `${d.basal_pct}%` }}
                  />
                  <span
                    className="seg bolus"
                    style={{ width: `${d.bolus_pct}%` }}
                  />
                </div>
              </td>
              <td className="num-col">{d.total_basal.toFixed(2)}</td>
              <td className="num-col">{d.total_bolus.toFixed(2)}</td>
              <td className="num-col">{d.total_insulin.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
