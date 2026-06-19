# Lagom

> *Lagom* (Swedish) — not too much, not too little; just the right amount.

An Omnipod 5 companion for bolus ratio analysis.

Omnipod's SmartAdjust algorithm adapts basal rates automatically, but meal and correction boluses are only as good as your configured ICR and ISF - and those don't self-correct. Lagom analyzes your Glooko data and delivers actionable adjustments.

> [!NOTE]
> Currently in the algorithm-proving stage - a Jupyter notebook validates the core logic against real export data prior to a full build-out.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
jupyter lab
```

Expects a Glooko export zip in the `data/` directory.

## Glossary

| Term | Definition |
| --- | --- |
| **ICR** (Insulin-to-Carb Ratio) | Grams of carbohydrate covered by one unit of insulin. A higher ICR means each unit covers more carbs. |
| **ISF** (Insulin Sensitivity Factor) | How much one unit of insulin lowers blood glucose (mg/dL per unit). |
| **SmartAdjust** | Omnipod 5's automated basal adjustment algorithm. Adapts basal insulin in response to CGM trends but does not adjust bolus ratios. |
| **CGM** (Continuous Glucose Monitor) | Sensor that measures interstitial glucose every few minutes. |
| **Clean window** | A post-bolus CGM window free of confounding events — used for ratio back-calculation. |
| **Back-calculation** | Deriving the ICR or ISF that *would have* produced an on-target outcome, given actual carbs, insulin, and glucose change. |
| **Glooko** | Diabetes data aggregation platform; exports CGM, bolus, and pump event data used as input here. |

## TODO

- [ ] Hypo windows are rejected rather than graded "too strong" because rescue carbs confound end glucose the same way a new meal does. Consider capturing them as directionally-too-strong and excluding only from the back-calculation.