# ZenML Tutorial

A hands-on introduction to [ZenML](https://docs.zenml.io/) for our team.
Go from "a script that trains a model" to "a reproducible, portable ML pipeline"
in three short modules.

## Why ZenML?

A typical ML project starts as a single `train.py`:
it loads data, trains a model, saves a pickle, prints some metrics.
It works — until you need to:

- **Reproduce** a run from three weeks ago (which data? which params? which model?)
- **Swap infrastructure** (laptop → Kubernetes → Vertex AI) without rewriting logic
- **Share artifacts** between teammates instead of passing pickles over Slack
- **Cache** expensive steps so you don't re-download 20 GB every iteration

ZenML adds a thin layer on top of your Python code that handles all of the above,
without locking you into a specific cloud or training framework.
The *logic* stays vanilla Python — the **orchestration** becomes declarative.

## Repo layout

```
zenml-tutorial/
├── README.md                 # you are here
├── pyproject.toml            # deps (managed by uv)
├── Makefile                  # make build | up | init | run1..3 | dashboard | ...
├── Dockerfile                # tutorial runtime image
├── docker-compose.yml        # single dev container (zenml local, not server)
└── modules/
    ├── 01_first_pipeline/
    │   ├── README.md         # module notes + exercises
    │   └── pipeline.py
    ├── 02_artifacts_and_caching/
    │   ├── README.md
    │   └── pipeline.py
    └── 03_stacks_and_deployment/
        ├── README.md
        ├── pipeline.py
        └── config.yaml
```

Each module is self-contained: read its `README.md`, run `pipeline.py`,
inspect the result in the dashboard, then move on.

## How it's wired

We use **ZenML in local mode** — a SQLite metadata store + local artifact
store. Pipeline artifacts live in `.zen/`; the ZenML client config lives in
`.zenconfig/`. Both sit inside the repo so container and host see the same
state. No server, no auth, no cloud.

- **Pipelines run inside a Docker dev container** (clean, reproducible Python
  environment — no uv/Python install required on the host).
- **The dashboard also runs inside the container**, bound to `0.0.0.0:8237`
  and exposed to the host. `ZENML_CONFIG_PATH=/workspace/.zenconfig` keeps
  the client config inside the repo so everything stays consistent.

If you'd rather skip Docker entirely, the host-only path (Option B below)
works end-to-end on its own.

## Setup

### Option A — Docker only (recommended)

Requires Docker. No host-side Python or `uv` needed.

```bash
make build        # build the tutorial image
make up           # start the dev container
make init         # one-time: `zenml init` inside the container

make dashboard    # opens http://localhost:8237 (runs inside container)

# in another terminal — run the modules:
make run1
make run2         # run twice to see caching
make run3
```

Other handy targets: `make shell`, `make logs`, `make down`, `make clean`.
Run `make` (no args) for the full list.

### Option B — Host-only with uv

```bash
uv sync
uv run zenml init
uv run zenml login --local        # dashboard at http://localhost:8237

uv run python modules/01_first_pipeline/pipeline.py
uv run python modules/02_artifacts_and_caching/pipeline.py
uv run python modules/03_stacks_and_deployment/pipeline.py
```

## Tutorial modules

| # | Folder | Concepts |
|---|--------|----------|
| 1 | [`modules/01_first_pipeline`](./modules/01_first_pipeline) | `@step`, `@pipeline`, running locally |
| 2 | [`modules/02_artifacts_and_caching`](./modules/02_artifacts_and_caching) | Typed artifacts, caching, multiple outputs |
| 3 | [`modules/03_stacks_and_deployment`](./modules/03_stacks_and_deployment) | Stacks, swapping orchestrators, config files |

After each run, refresh the dashboard to inspect the DAG, artifacts, and logs.

## Suggested reading order

1. Skim this README.
2. Work through module 1. Open the dashboard, click the run, explore the DAG.
3. Run module 2 **twice** — the second run should be fully cached. That's the
   "aha" moment.
4. Work through module 3 at your own pace; it touches infra concepts that
   matter once we move off laptops.

## Troubleshooting

- **Dashboard login prompt?** In local mode there's none — no username, no
  password. If you see an auth screen, you're pointed at a server, not the
  local dashboard. Inside the container: `zenml logout` then re-run
  `make dashboard`. On the host (Option B): swap `zenml` for `uv run zenml`.
- **Port 8237 already in use?** Stop the prior dashboard with
  `docker compose exec tutorial zenml logout --local` (or `uv run zenml logout --local` on the host).
- **`service "tutorial" is not running`?** Run `make up` first.
- **Stuck inside the container?** `make shell`, then `zenml status`,
  `zenml stack describe`, `zenml --help`. The [docs](https://docs.zenml.io/)
  are excellent.
- **Reset everything** (metadata + artifacts): `make clean`.
