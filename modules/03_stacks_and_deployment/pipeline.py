"""
Module 3 — Stacks and deployment.

Goal: understand how ZenML separates *what* a pipeline does from *where* it runs.

A "stack" is a bundle of infrastructure components:
    - orchestrator   (runs the steps: local, Airflow, Kubernetes, Vertex, ...)
    - artifact store (persists outputs: local FS, S3, GCS, Azure Blob, ...)
    - + optional: container registry, experiment tracker, model deployer, ...

The pipeline code in this file is identical to module 2 — only the *stack*
changes. That is the whole point: portable ML code.

---

## Inspect your current stack

    zenml stack describe          # what's active right now
    zenml stack list              # all registered stacks

Out of the box you have a `default` stack with a local orchestrator and a
local artifact store — that's what modules 1 and 2 used.

## Register a new stack (example: still local, but with a different name)

    zenml artifact-store register my_local_store --flavor=local
    zenml orchestrator   register my_local_orch  --flavor=local
    zenml stack          register my_stack \\
        -o my_local_orch -a my_local_store
    zenml stack set my_stack

## Swapping to the cloud later (preview — don't run now)

    # Example: S3 + Kubernetes orchestrator
    zenml artifact-store register s3_store --flavor=s3 --path=s3://my-bucket
    zenml orchestrator   register k8s      --flavor=kubernetes \\
        --kubernetes_context=my-cluster
    zenml stack          register cloud    -o k8s -a s3_store
    zenml stack set cloud

    uv run python modules/03_stacks_and_deployment/pipeline.py  # same code, now runs on Kubernetes

## Configuration files

For anything non-trivial, pass runtime config via YAML instead of kwargs.
See `config.yaml` in this repo — applied below via `.with_options(...)`.
"""

from typing import Annotated

import pandas as pd
from sklearn.base import ClassifierMixin
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from zenml import pipeline, step
from zenml.client import Client


@step
def load_data() -> tuple[
    Annotated[pd.DataFrame, "X_train"],
    Annotated[pd.DataFrame, "X_test"],
    Annotated[pd.Series, "y_train"],
    Annotated[pd.Series, "y_test"],
]:
    data = load_iris(as_frame=True)
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.2, random_state=42
    )
    return X_train, X_test, y_train, y_test


@step
def train_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_estimators: int = 50,
) -> Annotated[ClassifierMixin, "random_forest"]:
    model = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
    model.fit(X_train, y_train)
    return model


@step
def evaluate(
    model: ClassifierMixin, X_test: pd.DataFrame, y_test: pd.Series
) -> Annotated[float, "accuracy"]:
    accuracy = float(model.score(X_test, y_test))
    print(f"Test accuracy: {accuracy:.4f}")
    return accuracy


@pipeline
def iris_training_pipeline_deployment(n_estimators: int = 50):
    X_train, X_test, y_train, y_test = load_data()
    model = train_model(X_train, y_train, n_estimators=n_estimators)
    evaluate(model, X_test, y_test)


if __name__ == "__main__":
    # Show which stack is active — this is the one the run will use.
    active_stack = Client().active_stack
    print(f"Active stack: {active_stack.name}")
    print(f"  orchestrator:   {active_stack.orchestrator.name}")
    print(f"  artifact store: {active_stack.artifact_store.name}")
    print()

    # `.with_options(config_path=...)` loads runtime settings from YAML.
    # Keep code clean; keep infra knobs in config.
    iris_training_pipeline_deployment.with_options(
        config_path="modules/03_stacks_and_deployment/config.yaml"
    )(n_estimators=100)
