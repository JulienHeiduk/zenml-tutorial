# Module 1 — Your first ZenML pipeline

**Goal:** turn a plain training script into a ZenML pipeline.

**Concepts:** `@step`, `@pipeline`, running locally.

## Run it

```bash
make run1
# or:
uv run python modules/01_first_pipeline/pipeline.py
```

## What to look at

1. Open the dashboard at http://localhost:8237.
2. Click the latest run — you should see a 3-node DAG:
   `load_data → train_model → evaluate`.
3. Click a node. Inspect its inputs, outputs, logs, and code.

## Things to try

- Change `n_estimators=50` to `100` inside `train_model` and re-run.
  Notice that only the downstream steps are re-executed next time (teaser for
  module 2).
- Try removing a `@step` decorator — the pipeline will error at import time.
  That's the contract: pipelines are DAGs of steps, not of arbitrary functions.

## Takeaway

Your pipeline is still ordinary Python. No YAML, no DSL. ZenML *reads* the
pipeline function to build the DAG — the decorator is the only magic.
