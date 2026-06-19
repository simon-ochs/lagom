import type { RatioBlock } from "../types";

function tone(recommendation: string): "good" | "attention" {
  return recommendation.toLowerCase().includes("calibrated")
    ? "good"
    : "attention";
}

function Card({
  title,
  unit,
  block,
}: {
  title: string;
  unit: string;
  block: RatioBlock;
}) {
  return (
    <div className={`ratio-card ${tone(block.recommendation)}`}>
      <div className="ratio-head">
        <h3>{title}</h3>
        <span className="ratio-rec">{block.recommendation}</span>
      </div>
      <div className="ratio-numbers">
        <div>
          <span className="num">{block.configured}</span>
          <span className="num-label">configured</span>
        </div>
        <div>
          <span className="num">{block.implied_median.toFixed(1)}</span>
          <span className="num-label">implied median</span>
        </div>
        <div>
          <span className="num">
            {block.suggested === null ? "—" : block.suggested}
          </span>
          <span className="num-label">suggested</span>
        </div>
      </div>
      <p className="ratio-foot">
        {block.evaluated} windows evaluated · {block.trended_high} trended high ·{" "}
        {unit}
      </p>
    </div>
  );
}

export default function RatioCards({
  isf,
  icr,
}: {
  isf: RatioBlock;
  icr: RatioBlock;
}) {
  return (
    <section className="ratio-cards">
      <Card title="ISF" unit="mg/dL per unit" block={isf} />
      <Card title="ICR" unit="g per unit" block={icr} />
    </section>
  );
}
