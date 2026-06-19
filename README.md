# Lagom

> *Lagom* (Swedish) — not too much, not too little; just the right amount.

An Omnipod 5 companion for bolus ratio analysis.

Omnipod's SmartAdjust algorithm adapts basal rates automatically, but meal and correction boluses are only as good as your configured ICR and ISF - and those don't self-correct. Lagom analyzes your Glooko data and delivers actionable adjustments.

The core logic was proven out in a Jupyter notebook (`validation.ipynb`) and was implemented with FastAPI under `app/`. This will be eventually be deployed in some form to AWS (S3, Lambda, etc.).

## Run API

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

`POST /analyze` takes a `multipart/form-data` request with the Glooko export zip and your pump config:

```bash
curl -F file=@data/export.zip -F config='{"icr":10,"isf":30,"target_glucose":110}' \
  http://127.0.0.1:8000/analyze
```

You can also use the Swagger UI at `http://127.0.0.1:8000/docs`.

## Run Notebook

The original proving ground for the algorithm.

```bash
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

## To-Do

- [ ] Hypo windows are rejected rather than graded "too strong" because rescue carbs confound end glucose the same way a new meal does. Consider capturing them as directionally-too-strong and excluding only from the back-calculation.