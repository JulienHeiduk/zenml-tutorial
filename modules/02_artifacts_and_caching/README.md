# Module 2 — Artifacts and caching

**Goal:** see how ZenML treats step outputs as first-class, versioned artifacts,
and why caching makes iteration cheap.

**Concepts:** typed outputs with `Annotated`, multiple named outputs,
step-level caching, **per-step resource settings**.

## Run it — twice

```bash
make run2     # first run: everything executes
make run2     # second run: every step should show CACHED
```

The second run is the "aha" moment: no work, but you still get a full
lineage record for that run.

## What to look at

1. In the dashboard, compare the two runs side by side.
2. On run #2, every node is green with a "cached" badge.
3. Click any artifact (e.g. `random_forest`, `accuracy`). Notice it has a
   **version**, a **producer**, and all the **runs that consumed it**.

## Things to try

- Change `n_estimators` in `iris_training_pipeline(n_estimators=100)` and
  re-run. `load_data` stays cached; only the downstream steps rerun.
- Edit the body of `train_model` (e.g. add a `print`) and re-run. The cache is
  invalidated for that step: ZenML hashes the code, not just the inputs.
- Set `@step(enable_cache=False)` on `load_data` and re-run — it will always
  execute, even with unchanged inputs.

## Per-step resource settings

Each step declares its own CPU / memory / GPU requirements via
`ResourceSettings`:

```python
from zenml.config import ResourceSettings

@step(settings={"resources": ResourceSettings(cpu_count=4, memory="2GB")})
def train_model(...): ...

@step(settings={"resources": ResourceSettings(cpu_count=1, memory="512MB")})
def evaluate(...): ...
```

**Why this matters:** in a real pipeline, `load_data` might be I/O-heavy but
need 1 CPU, while `train_model` needs 16 cores or a GPU. You don't have to
size the *whole* pipeline for the heaviest step — each step asks for what it
actually needs.

| Orchestrator | What resource settings mean |
|---|---|
| `local` (what you're using now) | Informational — logged + shown in the dashboard, not enforced. |
| `kubernetes` | Translated into pod `resources.requests` / `limits`. |
| `vertex`, `sagemaker`, `kubeflow` | Translated into the job/pod/machine spec of that platform. |

For GPU steps, add `gpu_count=1` (and pick a GPU-enabled orchestrator). The
code in `pipeline.py` has a commented example on `train_model`.

**Keep them out of the code when it gets noisy.** Resource settings also
belong naturally in `config.yaml` (see module 3), so infra knobs don't
pollute step definitions:

```yaml
steps:
  train_model:
    settings:
      resources:
        cpu_count: 4
        memory: "2GB"
        gpu_count: 1
```

## Takeaway

Every step output is a versioned artifact tied to the exact code + inputs that
produced it. That's what makes runs reproducible — and caching is the direct
consequence.

And: **each step owns its own resource budget**. Right-size per step, not per
pipeline.
