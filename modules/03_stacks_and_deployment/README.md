# Module 3 — Stacks and deployment

**Goal:** understand how ZenML separates *what* a pipeline does from *where* it runs.

**Concepts:** stacks, orchestrators, artifact stores, YAML configuration.

A **stack** is a bundle of infrastructure components:

- **orchestrator** — runs the steps (local, Airflow, Kubernetes, Vertex, ...)
- **artifact store** — persists outputs (local FS, S3, GCS, Azure Blob, ...)
- optional: container registry, experiment tracker, model deployer, ...

The pipeline code in this module is identical to module 2. Only the *stack*
changes. That is the whole point: portable ML code.

## Inspect your current stack

```bash
make shell
zenml stack describe    # what's active right now
zenml stack list        # all registered stacks
```

Out of the box you're on the `default` stack: local orchestrator + local
artifact store, backed by the `.zen/` folder in this repo. That's what
modules 1 and 2 used.

## Run it

```bash
make run3
# or: uv run python modules/03_stacks_and_deployment/pipeline.py
```

The script prints the active stack, then runs with `config.yaml` applied.

## Register a second stack (still local, just to practice the commands)

```bash
zenml artifact-store register my_local_store --flavor=local
zenml orchestrator   register my_local_orch  --flavor=local
zenml stack          register my_stack -o my_local_orch -a my_local_store
zenml stack set my_stack

make run3   # same code, different stack
```

## Swapping to the cloud later (preview — don't run now)

```bash
zenml artifact-store register s3_store --flavor=s3 --path=s3://my-bucket
zenml orchestrator   register k8s --flavor=kubernetes \
    --kubernetes_context=my-cluster
zenml stack          register cloud -o k8s -a s3_store
zenml stack set cloud

make run3   # same code, now runs on Kubernetes + S3
```

## Configuration files

See [`config.yaml`](./config.yaml). Anything that changes between environments
(prod vs. dev, CPU vs. GPU, dataset paths) belongs in YAML — not hard-coded
in Python. Applied via `.with_options(config_path=...)`.

## Takeaway

Pipeline = logic. Stack = infrastructure. Config = environment-specific knobs.
Keep them separate and you can move a pipeline from laptop to cloud without
touching the code.
