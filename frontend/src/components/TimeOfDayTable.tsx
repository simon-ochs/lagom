import { SLOT_ORDER, type SlotGrades } from "../types";

export default function TimeOfDayTable({
  breakdown,
}: {
  breakdown: Record<string, SlotGrades>;
}) {
  return (
    <section className="panel">
      <h3>Time-of-day breakdown</h3>
      <table>
        <thead>
          <tr>
            <th>Slot</th>
            <th>Grades</th>
            <th className="num-col">High</th>
            <th className="num-col">OK</th>
            <th className="num-col">Low</th>
          </tr>
        </thead>
        <tbody>
          {SLOT_ORDER.filter((slot) => breakdown[slot]).map((slot) => {
            const g = breakdown[slot];
            const total = g.high + g.ok + g.low || 1;
            return (
              <tr key={slot}>
                <td>{slot}</td>
                <td className="bar-cell">
                  <div className="grade-bar">
                    <span
                      className="seg high"
                      style={{ width: `${(g.high / total) * 100}%` }}
                    />
                    <span
                      className="seg ok"
                      style={{ width: `${(g.ok / total) * 100}%` }}
                    />
                    <span
                      className="seg low"
                      style={{ width: `${(g.low / total) * 100}%` }}
                    />
                  </div>
                </td>
                <td className="num-col">{g.high}</td>
                <td className="num-col">{g.ok}</td>
                <td className="num-col">{g.low}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}
