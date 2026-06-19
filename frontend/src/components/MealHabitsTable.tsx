import { SLOT_ORDER, type MealHabit } from "../types";

function fmtHour(hour: number): string {
  const h = Math.floor(hour);
  const m = Math.round((hour - h) * 60);
  return `${h.toString().padStart(2, "0")}:${m.toString().padStart(2, "0")}`;
}

export default function MealHabitsTable({
  habits,
}: {
  habits: Record<string, MealHabit>;
}) {
  return (
    <section className="panel">
      <h3>Meal habits</h3>
      <table>
        <thead>
          <tr>
            <th>Slot</th>
            <th className="num-col">Events</th>
            <th className="num-col">Avg carbs (g)</th>
            <th className="num-col">Avg bolus (U)</th>
            <th className="num-col">Median time</th>
          </tr>
        </thead>
        <tbody>
          {SLOT_ORDER.filter((slot) => habits[slot]).map((slot) => {
            const h = habits[slot];
            return (
              <tr key={slot}>
                <td>{slot}</td>
                <td className="num-col">{h.events}</td>
                <td className="num-col">{h.avg_carbs.toFixed(1)}</td>
                <td className="num-col">{h.avg_bolus.toFixed(2)}</td>
                <td className="num-col">{fmtHour(h.median_hour)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}
