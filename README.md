# Lagom

> *Lagom* (Swedish) - not too much, not too little; just the right amount.

An [Omnipod 5](#glossary) companion for bolus ratio analysis.

Omnipod's [SmartAdjust](#glossary) algorithm adapts basal rates automatically, but meal and correction boluses are only as good as your configured [ICR](#glossary) and [ISF](#glossary) which do not self-correct. Lagom analyzes your [Glooko](#glossary) data and delivers actionable adjustments to those configurations.

## Run

To run the full app locally, do:

```bash
make install     # backend (.venv) + frontend dependencies
make run         # API on :8000 and UI on :5173 together
```

Then navigate to the web UI at `http://localhost:5173/`

Alternatively, you can call the API directly with a `POST: multipart/form-data` request:

```bash
curl -F file=@tests/data/sample_export.zip -F config='{"icr":10,"isf":30,"target_glucose":110}' \
  http://127.0.0.1:8000/analyze
```

...or via the Swagger UI at `http://127.0.0.1:8000/docs`

## Tests

The analysis is deterministic, so it's guarded by a [characterization test](#glossary) that runs against a sample export (`tests/data/sample_export.zip`).  

A failing test will flag any changes in output:

```bash
make test
```

If the change is intended/desired, you can [bless](#glossary) the updated snapshot and commit it:

```bash
make bless
```

## Glossary

| Term | Definition |
| --- | --- |
| **ICR** (Insulin-to-Carb Ratio) | Grams of carbohydrate covered by one unit of insulin. A higher ICR means each unit covers more carbs. |
| **ISF** (Insulin Sensitivity Factor) | How much one unit of insulin lowers blood glucose (mg/dL per unit). |
| **SmartAdjust** | Omnipod 5's automated basal adjustment algorithm. Adapts basal insulin in response to CGM trends but does not adjust bolus ratios. |
| **CGM** (Continuous Glucose Monitor) | Sensor that measures interstitial glucose every few minutes. |
| **Clean window** | A post-bolus CGM window free of confounding events - used for ratio back-calculation. |
| **Back-calculation** | Deriving the ICR or ISF that *would have* produced an on-target outcome, given actual carbs, insulin, and glucose change. |
| **Glooko** | Diabetes data aggregation platform; exports CGM, bolus, and pump event data used as input here. |
| **Omnipod 5** | A tubeless, wearable insulin pump by Insulet that integrates with CGM for automated insulin delivery via the SmartAdjust algorithm. |
| **Characterization test** | A test that captures the code's current output as a baseline, so unintended changes surface as a diff. Pins down what the code *does*, not what it *should* do. |
| **Bless** | To accept a changed test output as the new baseline, after reviewing the diff to confirm the change was intended. |

## To-Do

- [ ] Hypo windows are rejected rather than graded "too strong" because rescue carbs confound end glucose the same way a new meal does. Consider capturing them as directionally-too-strong and excluding only from the back-calculation.